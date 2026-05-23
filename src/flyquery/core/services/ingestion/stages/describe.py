# Copyright 2026 Firefly Software Solutions Inc
"""Stage 7 — DescribeAgent (batched, budget-capped).

For each batch of columns where description IS NULL:
  1. Build prompt with (qualified_name, data_type, samples, table_context).
  2. Call DescribeAgent.
  3. Persist description + synonyms_json with description_source='AGENT'.
  4. Track cost via result.usage(); stop when FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN hit.
     Remaining columns are deferred (the IngestWorker picks them up via DESCRIBE_PASS).

Graceful skip: if the agent call raises (no API key, budget exceeded), the
pipeline continues without hard-failing — descriptions are optional enrichment.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

# Approximate cost per 1M tokens for haiku (in cents, conservative estimate)
# Haiku 4.5: ~$0.80/M input + $4/M output; round to $5/M ≈ 0.0005 cents/token
_CENTS_PER_INPUT_TOKEN = 0.00008  # $0.80 / 1M
_CENTS_PER_OUTPUT_TOKEN = 0.0004  # $4 / 1M

_NO_AGENT_WARNING_ISSUED = False


async def run_describe(
    *,
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
) -> dict[str, Any]:
    """Execute Stage 7: describe."""
    columns = await _load_undescribed_columns(tenant_id, snapshot_id, session_factory)

    if not columns:
        return {"snapshot_id": str(snapshot_id), "described": 0, "deferred": 0}

    try:
        from flyquery.core.agents.describe_agent import build_describe_agent

        agent = build_describe_agent(settings)
    except (ImportError, RuntimeError) as exc:
        global _NO_AGENT_WARNING_ISSUED
        if not _NO_AGENT_WARNING_ISSUED:
            logger.warning("stage=describe agent unavailable (graceful skip): %s", exc)
            _NO_AGENT_WARNING_ISSUED = True
        return {"snapshot_id": str(snapshot_id), "described": 0, "deferred": len(columns), "reason": str(exc)}

    batch_size = settings.describe_batch
    budget_cents = settings.describe_budget_cents_per_run
    spent_cents = 0.0
    described = 0
    deferred = 0

    for batch_start in range(0, len(columns), batch_size):
        batch = columns[batch_start : batch_start + batch_size]

        if spent_cents >= budget_cents:
            deferred += len(batch)
            logger.info(
                "stage=describe budget exhausted spent_cents=%.4f budget=%d deferred=%d",
                spent_cents,
                budget_cents,
                deferred,
            )
            continue

        # Build the prompt payload
        prompt_data = _build_prompt(batch, session_factory)

        try:
            result = await agent.run(json.dumps(prompt_data))
        except Exception as exc:  # noqa: BLE001
            logger.warning("stage=describe agent.run failed (graceful skip batch): %s", exc)
            deferred += len(batch)
            continue

        # Track cost
        try:
            usage = result.usage()
            if usage is not None:
                input_tokens = getattr(usage, "input_tokens", 0) or 0
                output_tokens = getattr(usage, "output_tokens", 0) or 0
                batch_cost = input_tokens * _CENTS_PER_INPUT_TOKEN + output_tokens * _CENTS_PER_OUTPUT_TOKEN
                spent_cents += batch_cost
        except Exception:  # noqa: BLE001
            pass  # cost tracking failure must never break the pipeline

        # Persist descriptions
        described_objs = result.output.columns
        qualified_to_output: dict[str, Any] = {d.qualified_name: d for d in described_objs}

        for col in batch:
            described_col = qualified_to_output.get(col["qualified_name"])
            if described_col is None:
                deferred += 1
                continue
            await _persist_description(
                col_id=col["id"],
                description=described_col.description,
                synonyms=described_col.synonyms,
                semantic_type=getattr(described_col, "semantic_type", None),
                tenant_id=tenant_id,
                session_factory=session_factory,
            )
            described += 1

    logger.info(
        "stage=describe snapshot_id=%s described=%d deferred=%d spent_cents=%.4f",
        snapshot_id,
        described,
        deferred,
        spent_cents,
    )
    return {
        "snapshot_id": str(snapshot_id),
        "described": described,
        "deferred": deferred,
        "spent_cents": round(spent_cents, 4),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_prompt(
    columns: list[dict[str, Any]],
    session_factory: Any,
) -> list[dict[str, Any]]:
    """Build the JSON payload for the DescribeAgent prompt."""
    out = []
    for col in columns:
        table_context = col.get("sibling_names") or []
        out.append(
            {
                "qualified_name": col["qualified_name"],
                "data_type": col["data_type"] or "UNKNOWN",
                "samples": (col.get("sample_values_json") or [])[:5],
                "table_context": table_context[:20],
            }
        )
    return out


async def _load_undescribed_columns(
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> list[dict[str, Any]]:
    """Load active COLUMN objects with no description yet, plus sibling context."""
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT
                    c.id,
                    c.qualified_name,
                    c.data_type,
                    c.sample_values_json,
                    c.parent_id
                FROM flyquery_schema_objects c
                WHERE c.snapshot_id = :sid
                  AND c.tenant_id = :tenant
                  AND c.kind = 'COLUMN'
                  AND c.is_active = true
                  AND c.description IS NULL
                  AND c.description_source IS NULL
                ORDER BY c.qualified_name
                """
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        rows = [dict(r) for r in result.mappings().all()]

    if not rows:
        return rows

    # Load sibling names for table context
    parent_ids = {r["parent_id"] for r in rows if r["parent_id"]}
    sibling_map: dict[uuid.UUID, list[str]] = {}
    if parent_ids:
        async with session_factory() as s:
            for parent_id in parent_ids:
                sibling_result = await s.execute(
                    sa.text(
                        """
                        SELECT qualified_name
                        FROM flyquery_schema_objects
                        WHERE parent_id = :pid AND kind = 'COLUMN'
                          AND tenant_id = :tenant
                        ORDER BY qualified_name
                        """
                    ),
                    {"pid": parent_id, "tenant": tenant_id},
                )
                names = [r["qualified_name"].rsplit(".", 1)[-1] for r in sibling_result.mappings().all()]
                sibling_map[parent_id] = names

    for row in rows:
        row["sibling_names"] = sibling_map.get(row["parent_id"], [])

    return rows


async def _persist_description(
    *,
    col_id: uuid.UUID,
    description: str,
    synonyms: list[str],
    semantic_type: str | None,
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Persist the AI description + synonyms + semantic type.

    ``semantic_type`` lives inside ``governance_json`` (existing
    JSONB column) so no schema migration is required. The
    schema_objects controller reads it back from there.
    """
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                UPDATE flyquery_schema_objects
                SET description = :description,
                    description_source = 'AGENT',
                    synonyms_json = CAST(:synonyms AS jsonb),
                    governance_json = COALESCE(governance_json, '{}'::jsonb)
                                      || CAST(:gov AS jsonb)
                WHERE id = :id AND tenant_id = :tenant
                """
            ),
            {
                "id": col_id,
                "tenant": tenant_id,
                "description": description,
                "synonyms": json.dumps(synonyms),
                "gov": json.dumps({"semantic_type": semantic_type or "unknown"} if semantic_type else {}),
            },
        )
