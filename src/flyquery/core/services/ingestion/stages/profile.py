# Copyright 2026 Firefly Software Solutions Inc
"""Stage 5 — profile.

For each active COLUMN in the snapshot, compute via a single DuckDB query:
  - null_fraction
  - approx_count_distinct (via approx_count_distinct())
  - min / max (numeric + temporal columns only)
  - top 5 values (low-cardinality only: distinct_estimate ≤ 100)

Skips the whole column if the snapshot's n_rows_actual exceeds
FLYQUERY_PROFILE_ROW_THRESHOLD (default 10M rows).

Persists to flyquery_schema_objects.profile_json.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

# Data-type compatibility groups
_NUMERIC_TYPES = frozenset(
    {
        "integer",
        "int",
        "int4",
        "int8",
        "bigint",
        "smallint",
        "tinyint",
        "float",
        "double",
        "real",
        "decimal",
        "numeric",
        "hugeint",
        "ubigint",
    }
)
_TEMPORAL_TYPES = frozenset(
    {
        "date",
        "timestamp",
        "timestamp with time zone",
        "timestamptz",
        "time",
        "interval",
    }
)


def _is_numeric(data_type: str) -> bool:
    return data_type.lower().split("(")[0].strip() in _NUMERIC_TYPES


def _is_temporal(data_type: str) -> bool:
    return data_type.lower().split("(")[0].strip() in _TEMPORAL_TYPES


async def run_profile(
    *,
    tenant_id: str,
    snapshot_id: uuid.UUID,
    parquet_key: str,
    n_rows_actual: int,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
) -> dict[str, Any]:
    """Execute Stage 5: profile."""
    if n_rows_actual > settings.profile_row_threshold:
        logger.info(
            "stage=profile skip snapshot_id=%s n_rows=%d threshold=%d",
            snapshot_id,
            n_rows_actual,
            settings.profile_row_threshold,
        )
        return {"snapshot_id": str(snapshot_id), "skipped": True, "reason": "row_threshold"}

    columns = await _load_columns(tenant_id, snapshot_id, session_factory)
    profiled = 0

    for col in columns:
        col_id: uuid.UUID = col["id"]
        col_name: str = col["qualified_name"].rsplit(".", 1)[-1]
        data_type: str = col["data_type"] or ""

        profile = await asyncio.to_thread(
            _profile_column_sync, parquet_key, col_name, data_type, n_rows_actual
        )
        if profile is not None:
            await _persist_profile(col_id, profile, tenant_id, session_factory)
            profiled += 1

    logger.info(
        "stage=profile snapshot_id=%s columns_profiled=%d",
        snapshot_id,
        profiled,
    )
    return {"snapshot_id": str(snapshot_id), "columns_profiled": profiled}


# ---------------------------------------------------------------------------
# DuckDB profiling (runs in thread)
# ---------------------------------------------------------------------------


def _profile_column_sync(
    parquet_key: str,
    col_name: str,
    data_type: str,
    n_rows_actual: int,
) -> dict[str, Any] | None:
    """Run a single DuckDB query to compute profile metrics for one column."""
    try:
        import duckdb

        conn = duckdb.connect()
        try:
            safe_col = '"' + col_name.replace('"', '""') + '"'

            # Base query: null_fraction + approx_count_distinct
            base_rows = conn.execute(
                f"SELECT "
                f"  count(*) AS total_rows, "
                f"  sum(CASE WHEN {safe_col} IS NULL THEN 1 ELSE 0 END) AS null_count, "
                f"  approx_count_distinct({safe_col}) AS distinct_estimate "
                f"FROM read_parquet(?)",
                [parquet_key],
            ).fetchone()

            if base_rows is None:
                return None

            total, null_count, distinct_estimate = base_rows
            null_fraction = (null_count / total) if total > 0 else 0.0

            profile: dict[str, Any] = {
                "null_fraction": null_fraction,
                "distinct_estimate": distinct_estimate,
                "n_rows": total,
            }

            # min / max for numeric + temporal
            if _is_numeric(data_type) or _is_temporal(data_type):
                minmax = conn.execute(
                    f"SELECT min({safe_col}), max({safe_col}) FROM read_parquet(?)",
                    [parquet_key],
                ).fetchone()
                if minmax:
                    col_min, col_max = minmax
                    profile["min"] = str(col_min) if col_min is not None else None
                    profile["max"] = str(col_max) if col_max is not None else None

            # Top values for low-cardinality columns (distinct ≤ 100)
            if distinct_estimate <= 100 and distinct_estimate > 0:
                top_rows = conn.execute(
                    f"SELECT {safe_col}, count(*) AS cnt "
                    f"FROM read_parquet(?) "
                    f"WHERE {safe_col} IS NOT NULL "
                    f"GROUP BY {safe_col} "
                    f"ORDER BY cnt DESC "
                    f"LIMIT 5",
                    [parquet_key],
                ).fetchall()
                profile["top_values"] = [{"value": str(r[0]), "count": r[1]} for r in top_rows]

            return profile

        finally:
            conn.close()

    except Exception as exc:
        logger.warning("stage=profile column_profile failed col=%s: %s", col_name, exc)
        return None


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def _load_columns(
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> list[dict[str, Any]]:
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT id, qualified_name, data_type
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


async def _persist_profile(
    col_id: uuid.UUID,
    profile: dict[str, Any],
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                UPDATE flyquery_schema_objects
                SET profile_json = CAST(:profile AS jsonb)
                WHERE id = :id AND tenant_id = :tenant
                """
            ),
            {
                "id": col_id,
                "tenant": tenant_id,
                "profile": json.dumps(profile),
            },
        )
