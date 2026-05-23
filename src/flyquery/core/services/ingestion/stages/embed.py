# Copyright 2026 Firefly Software Solutions Inc
"""Stage 9 — embed: build embedding text per schema object + update content_tsv.

For each flyquery_schema_objects row in the snapshot:
- Build embedding text: "<qualified_name>: <data_type>\\n<description>\\nSynonyms: <list>"
- Call OpenAI text-embedding-3-small (1536-d) if OPENAI_API_KEY is available
- Persist embedding + embedding_model columns
- Refresh content_tsv via PostgreSQL to_tsvector

If OPENAI_API_KEY is not set, embedding is skipped (NULL) and embeddings_written=0
is emitted. The pipeline does not fail.
"""

from __future__ import annotations

import logging
import os
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL = "text-embedding-3-small"
_EMBEDDING_DIMS = 1536


async def run_embed(
    *,
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict:
    """Execute Stage 9: embed + index.

    Returns a result dict with embeddings_written count.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    embedder = _build_embedder(api_key)

    # Load all schema_objects for this snapshot
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT id, qualified_name, data_type, description, synonyms_json
                FROM flyquery_schema_objects
                WHERE snapshot_id = :sid AND tenant_id = :tenant
                ORDER BY kind, qualified_name
                """
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        rows = [dict(r) for r in result.mappings().all()]

    embeddings_written = 0

    for row in rows:
        embed_text = _build_embed_text(row)

        vector: list[float] | None = None
        model_name: str | None = None

        if embedder is not None:
            try:
                vector = await embedder(embed_text)
                model_name = _EMBEDDING_MODEL
                embeddings_written += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "embed failed for object %s: %s", row["id"], exc, exc_info=True
                )

        # Update embedding + content_tsv
        await _update_object(
            object_id=row["id"],
            embed_vector=vector,
            model_name=model_name,
            embed_text=embed_text,
            tenant_id=tenant_id,
            session_factory=session_factory,
        )

    logger.info(
        "stage=embed snapshot_id=%s objects=%d embeddings_written=%d",
        snapshot_id,
        len(rows),
        embeddings_written,
    )
    return {"embeddings_written": embeddings_written, "objects_processed": len(rows)}


def _build_embed_text(row: dict) -> str:
    parts = [row.get("qualified_name") or ""]
    if row.get("data_type"):
        parts[0] += f": {row['data_type']}"
    if row.get("description"):
        parts.append(row["description"])
    synonyms = row.get("synonyms_json")
    if synonyms:
        if isinstance(synonyms, list):
            parts.append("Synonyms: " + ", ".join(str(s) for s in synonyms))
        elif isinstance(synonyms, dict):
            flat = list(synonyms.values())
            if flat:
                parts.append("Synonyms: " + ", ".join(str(s) for s in flat))
    return "\n".join(p for p in parts if p)


def _build_embedder(api_key: str):
    """Return an async callable (text → list[float]) or None."""
    if not api_key:
        logger.info("OPENAI_API_KEY not set — embedding step skipped (NULL)")
        return None

    async def _embed(text: str) -> list[float]:
        try:
            from openai import AsyncOpenAI  # type: ignore[import]
        except ImportError:
            logger.warning("openai package not installed — skipping embedding")
            raise

        client = AsyncOpenAI(api_key=api_key)
        resp = await client.embeddings.create(
            model=_EMBEDDING_MODEL,
            input=text,
            dimensions=_EMBEDDING_DIMS,
        )
        return resp.data[0].embedding

    return _embed


async def _update_object(
    *,
    object_id: uuid.UUID,
    embed_vector: list[float] | None,
    model_name: str | None,
    embed_text: str,
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Persist embedding (if available) + refresh content_tsv."""
    # Build tsvector search text from embed_text (or qualified_name + description)
    tsv_input = embed_text[:4096]  # PostgreSQL tsvector limit guard

    async with session_factory() as s, s.begin():
        if embed_vector is not None:
            # Store the embedding vector as a PostgreSQL vector literal
            vec_str = "[" + ",".join(f"{v:.8f}" for v in embed_vector) + "]"
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET
                        embedding = CAST(:vec AS vector),
                        embedding_model = :model,
                        content_tsv = to_tsvector('english', :tsv_input)
                    WHERE id = :oid AND tenant_id = :tenant
                    """
                ),
                {
                    "vec": vec_str,
                    "model": model_name,
                    "tsv_input": tsv_input,
                    "oid": object_id,
                    "tenant": tenant_id,
                },
            )
        else:
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET content_tsv = to_tsvector('english', :tsv_input)
                    WHERE id = :oid AND tenant_id = :tenant
                    """
                ),
                {
                    "tsv_input": tsv_input,
                    "oid": object_id,
                    "tenant": tenant_id,
                },
            )
