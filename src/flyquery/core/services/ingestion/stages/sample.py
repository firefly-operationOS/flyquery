# Copyright 2026 Firefly Software Solutions Inc
"""Stage 4 — sample (PII-gated).

For each new/changed column in the snapshot:
1. Skip if pii_tag is already set (and != 'NONE') — column is known PII.
2. Read N values from the Parquet snapshot (DuckDB).
3. Pass each value through PiiScanner.scan_single() — refuse to persist if PII.
4. Persist clean samples to flyquery_schema_objects.sample_values_json.

CRITICAL ordering guarantee (per spec): PII inline gate runs BEFORE persisting
any sample. A value that triggers scan_single is silently dropped; if ALL
values are PII-tainted, no sample is persisted for that column.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.services.pii.factory import build_pii_scanner

logger = logging.getLogger(__name__)


async def run_sample(
    *,
    tenant_id: str,
    snapshot_id: uuid.UUID,
    parquet_key: str,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
) -> dict[str, Any]:
    """Execute Stage 4: PII-gated column sampling.

    Returns a summary dict with column_id → sample count.
    """
    scanner = build_pii_scanner(settings.pii_scanner)
    n = settings.sample_n

    # Load all active COLUMN objects for this snapshot
    columns = await _load_columns(tenant_id, snapshot_id, session_factory)

    sampled: dict[str, int] = {}

    for col in columns:
        col_id: uuid.UUID = col["id"]
        col_name: str = col["qualified_name"].rsplit(".", 1)[-1]
        pii_tag: str | None = col["pii_tag"]

        # Skip columns already known to carry PII
        if pii_tag is not None and pii_tag != "NONE":
            logger.debug(
                "stage=sample skip col=%s reason=pii_flagged tag=%s",
                col_name,
                pii_tag,
            )
            continue

        # Read raw values from Parquet
        raw_values = await asyncio.to_thread(_read_parquet_column, parquet_key, col_name, n)

        if not raw_values:
            continue

        # PII inline gate: keep only clean values
        clean_samples: list[str] = []
        for v in raw_values:
            finding = await scanner.scan_single(str(v))
            if finding is None:
                clean_samples.append(str(v))

        if not clean_samples:
            logger.info(
                "stage=sample col=%s all_values_pii_tainted n=%d",
                col_name,
                len(raw_values),
            )
            continue

        await _persist_samples(col_id, clean_samples, tenant_id, session_factory)
        sampled[str(col_id)] = len(clean_samples)
        logger.debug(
            "stage=sample col=%s samples=%d/%d_raw",
            col_name,
            len(clean_samples),
            len(raw_values),
        )

    logger.info(
        "stage=sample snapshot_id=%s columns_sampled=%d",
        snapshot_id,
        len(sampled),
    )
    return {"snapshot_id": str(snapshot_id), "sampled_columns": len(sampled)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_parquet_column(parquet_key: str, col_name: str, n: int) -> list[Any]:
    """Read up to n non-null values from a Parquet file for a given column."""
    try:
        import duckdb

        conn = duckdb.connect()
        try:
            # Use parameterised query to avoid SQL injection via col_name
            # (DuckDB doesn't support ? in column identifiers, so we escape manually)
            safe_col = _quote_ident(col_name)
            rows = conn.execute(
                f"SELECT {safe_col} FROM read_parquet(?) WHERE {safe_col} IS NOT NULL LIMIT {n}",
                [parquet_key],
            ).fetchall()
            return [r[0] for r in rows]
        finally:
            conn.close()
    except Exception as exc:
        logger.warning("stage=sample read_parquet failed col=%s: %s", col_name, exc)
        return []


def _quote_ident(name: str) -> str:
    """Wrap a column name in double-quotes, escaping embedded quotes."""
    return '"' + name.replace('"', '""') + '"'


async def _load_columns(
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> list[dict[str, Any]]:
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT id, qualified_name, pii_tag
                FROM flyquery_schema_objects
                WHERE snapshot_id = :sid
                  AND tenant_id = :tenant
                  AND kind = 'COLUMN'
                  AND is_active = true
                ORDER BY qualified_name
                """
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        return [dict(r) for r in result.mappings().all()]


async def _persist_samples(
    col_id: uuid.UUID,
    samples: list[str],
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                UPDATE flyquery_schema_objects
                SET sample_values_json = CAST(:samples AS jsonb),
                    sample_taken_at = now()
                WHERE id = :id AND tenant_id = :tenant
                """
            ),
            {
                "id": col_id,
                "tenant": tenant_id,
                "samples": json.dumps(samples),
            },
        )
