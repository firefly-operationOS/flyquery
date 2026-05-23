# Copyright 2026 Firefly Software Solutions Inc
"""Stage 6 — relation discovery (heuristic 6a + agent-proposed 6b).

Stage 6a (heuristic):
  For each pair of tables in the dataset, match columns by:
    - identical column name (case-insensitive)
    - compatible data type (numeric ↔ numeric, text ↔ text, temporal ↔ temporal)
    - one side has profile_json.distinct_estimate ≥ 0.95 × n_rows_actual (PK-like)
  Insert flyquery_relations rows with kind='HEURISTIC', status='PROPOSED'.
  Confidence = uniqueness_score × name_specificity_score.
  UPSERT on (from_table_id, from_column_name, to_table_id, to_column_name) to
  avoid duplicates on re-run.

Stage 6b (agent-proposed):
  Gather dataset schema_objects → prompt RelationProposerAgent.
  Persist results as kind='AGENT_PROPOSED', status='PROPOSED'.
  Skipped when FLYQUERY_RELATION_PROPOSER_ENABLED=false or agent unavailable.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type compatibility
# ---------------------------------------------------------------------------
_NUMERIC_GROUP = frozenset(
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
_TEXT_GROUP = frozenset({"varchar", "text", "char", "bpchar", "string"})
_TEMPORAL_GROUP = frozenset(
    {
        "date",
        "timestamp",
        "timestamp with time zone",
        "timestamptz",
        "time",
        "interval",
    }
)


def _type_group(dt: str) -> str:
    base = dt.lower().split("(")[0].strip()
    if base in _NUMERIC_GROUP:
        return "numeric"
    if base in _TEXT_GROUP:
        return "text"
    if base in _TEMPORAL_GROUP:
        return "temporal"
    return "other"


def _types_compatible(a: str, b: str) -> bool:
    ga, gb = _type_group(a), _type_group(b)
    if ga == "other" or gb == "other":
        return False
    return ga == gb


# ---------------------------------------------------------------------------
# Name specificity score — generic names like "id" are low-value
# ---------------------------------------------------------------------------
_GENERIC_NAMES = frozenset({"id", "uuid", "key", "code", "no", "num", "number"})


def _name_specificity(name: str) -> float:
    """Score 0..1 for how specific a column name is (e.g. customer_id > id)."""
    lower = name.lower()
    if lower in _GENERIC_NAMES:
        return 0.3
    if lower.endswith("_id") or lower.endswith("_uuid") or lower.endswith("_key"):
        return 0.8
    return 0.6


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def run_relations(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
) -> dict[str, Any]:
    """Execute Stage 6: heuristic + agent-proposed relation discovery."""

    # ---- 6a: heuristic ----
    heuristic_count = await _run_heuristic(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        dataset_id=dataset_id,
        session_factory=session_factory,
        settings=settings,
    )

    # ---- 6b: agent-proposed ----
    agent_count = 0
    if settings.relation_proposer_enabled:
        try:
            agent_count = await _run_agent_proposed(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                session_factory=session_factory,
                settings=settings,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("stage=relations agent_proposed failed (graceful skip): %s", exc)

    logger.info(
        "stage=relations dataset_id=%s heuristic=%d agent=%d",
        dataset_id,
        heuristic_count,
        agent_count,
    )
    return {
        "dataset_id": str(dataset_id),
        "heuristic_proposed": heuristic_count,
        "agent_proposed": agent_count,
    }


# ---------------------------------------------------------------------------
# 6a: heuristic
# ---------------------------------------------------------------------------


async def _run_heuristic(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,
) -> int:
    tables = await _load_dataset_tables(tenant_id, dataset_id, session_factory)
    if len(tables) < 2:
        return 0

    # Build column index: table_id → [column dicts]
    table_columns: dict[uuid.UUID, list[dict[str, Any]]] = {}
    for tbl in tables:
        table_columns[tbl["id"]] = await _load_table_columns(
            tenant_id, tbl["id"], tbl["current_snapshot_id"], session_factory
        )

    inserted = 0
    seen_pairs: set[tuple[uuid.UUID, str, uuid.UUID, str]] = set()

    for i, tbl_a in enumerate(tables):
        cols_a = table_columns[tbl_a["id"]]
        for tbl_b in tables[i + 1 :]:
            cols_b = table_columns[tbl_b["id"]]
            # name lookup: lowercase → column info
            b_by_name: dict[str, dict[str, Any]] = {c["col_name"].lower(): c for c in cols_b}

            for col_a in cols_a:
                name_lower = col_a["col_name"].lower()
                col_b = b_by_name.get(name_lower)
                if col_b is None:
                    continue

                if not _types_compatible(col_a["data_type"] or "", col_b["data_type"] or ""):
                    continue

                # Determine which side is the "unique" (PK-like) side
                unique_a = _is_pk_like(col_a, tbl_a)
                unique_b = _is_pk_like(col_b, tbl_b)

                if not unique_a and not unique_b:
                    continue  # neither side looks like a PK

                # Confidence
                uniqueness_score = 1.0 if (unique_a or unique_b) else 0.5
                name_spec = _name_specificity(col_a["col_name"])
                confidence = min(1.0, uniqueness_score * name_spec)

                if confidence < settings.relation_heuristic_min_confidence:
                    continue

                # Determine canonical from (unique) → to (non-unique) direction
                if unique_a:
                    from_tid, from_col = tbl_a["id"], col_a["col_name"]
                    to_tid, to_col = tbl_b["id"], col_b["col_name"]
                else:
                    from_tid, from_col = tbl_b["id"], col_b["col_name"]
                    to_tid, to_col = tbl_a["id"], col_a["col_name"]

                pair = (from_tid, from_col, to_tid, to_col)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                await _upsert_relation(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset_id,
                    from_table_id=from_tid,
                    from_column_name=from_col,
                    to_table_id=to_tid,
                    to_column_name=to_col,
                    kind="HEURISTIC",
                    confidence=confidence,
                    reason=f"name+type match; name_specificity={name_spec:.2f}",
                    session_factory=session_factory,
                )
                inserted += 1

    return inserted


def _is_pk_like(col: dict[str, Any], tbl: dict[str, Any]) -> bool:
    """Return True if this column looks like the unique/PK side.

    Primary check: profile_json.distinct_estimate >= 95% of n_rows_actual.
    Fallback (when profile stage hasn't run yet): treat *_id / *_uuid / *_key
    column names as PK-like — this covers v0 where only sync stages 1-3+9+10
    have run.
    """
    profile = col.get("profile_json") or {}
    distinct_estimate = profile.get("distinct_estimate")
    if distinct_estimate is not None:
        n_rows_actual = tbl.get("n_rows_actual") or 1
        return distinct_estimate >= 0.95 * n_rows_actual
    # Profile not available — fall back to name heuristic
    col_name = (col.get("col_name") or "").lower()
    return (
        col_name.endswith("_id")
        or col_name.endswith("_uuid")
        or col_name.endswith("_key")
        or col_name == "id"
    )


# ---------------------------------------------------------------------------
# 6b: agent-proposed
# ---------------------------------------------------------------------------


async def _run_agent_proposed(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,
) -> int:
    from flyquery.core.agents.relation_proposer_agent import build_relation_proposer_agent

    tables = await _load_dataset_tables(tenant_id, dataset_id, session_factory)
    if len(tables) < 2:
        return 0

    # Build schema context for the prompt
    schema_lines: list[str] = []
    for tbl in tables:
        cols = await _load_table_columns(tenant_id, tbl["id"], tbl["current_snapshot_id"], session_factory)
        col_summaries = []
        for c in cols[:30]:  # cap per table to keep prompt size manageable
            samples = json.dumps((c.get("sample_values_json") or [])[:3])
            col_summaries.append(
                f"  {c['col_name']}: {c['data_type']} "
                f"(distinct≈{c.get('distinct_estimate', '?')}, samples={samples})"
            )
        tbl_desc = tbl.get("description") or ""
        schema_lines.append(f"- {tbl['name']}: {tbl_desc}\n" + "\n".join(col_summaries))

    prompt = (
        f"Dataset: {dataset_id}\n\n"
        f"Tables:\n" + "\n\n".join(schema_lines) + "\n\n"
        f"Find cross-table join candidates NOT covered by exact name+type matching "
        f"(heuristic detector already handles those). Max {settings.relation_proposer_max_per_pair} "
        f"proposals per table pair."
    )

    agent = build_relation_proposer_agent(settings)
    result = await agent.run(prompt)
    proposals = result.output.items

    # Build table name → id lookup
    name_to_id = {tbl["name"]: tbl["id"] for tbl in tables}

    inserted = 0
    for prop in proposals:
        from_tid = name_to_id.get(prop.from_table)
        to_tid = name_to_id.get(prop.to_table)
        if from_tid is None or to_tid is None:
            logger.warning(
                "stage=relations agent_proposed skip — unknown table from=%s to=%s",
                prop.from_table,
                prop.to_table,
            )
            continue
        if prop.confidence < 0.0 or prop.confidence > 1.0:
            continue

        await _upsert_relation(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            from_table_id=from_tid,
            from_column_name=prop.from_column,
            to_table_id=to_tid,
            to_column_name=prop.to_column,
            kind="AGENT_PROPOSED",
            confidence=prop.confidence,
            reason=prop.reason,
            session_factory=session_factory,
        )
        inserted += 1

    return inserted


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def _load_dataset_tables(
    tenant_id: str,
    dataset_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> list[dict[str, Any]]:
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT t.id, t.name, t.current_snapshot_id,
                       sn.n_rows_actual,
                       so.description
                FROM flyquery_tables t
                LEFT JOIN flyquery_schema_snapshots sn
                  ON sn.id = t.current_snapshot_id
                LEFT JOIN flyquery_schema_objects so
                  ON so.snapshot_id = t.current_snapshot_id
                  AND so.kind = 'TABLE'
                  AND so.tenant_id = :tenant
                WHERE t.dataset_id = :ds
                  AND t.tenant_id = :tenant
                  AND t.current_snapshot_id IS NOT NULL
                """
            ),
            {"ds": dataset_id, "tenant": tenant_id},
        )
        return [dict(r) for r in result.mappings().all()]


async def _load_table_columns(
    tenant_id: str,
    table_id: uuid.UUID,
    snapshot_id: uuid.UUID | None,
    session_factory: async_sessionmaker[AsyncSession],
) -> list[dict[str, Any]]:
    if snapshot_id is None:
        return []
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT
                    qualified_name,
                    qualified_name::text AS col_name_full,
                    data_type,
                    profile_json,
                    sample_values_json,
                    description
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
        rows = []
        for r in result.mappings().all():
            d = dict(r)
            # Extract col_name from qualified_name (last segment)
            d["col_name"] = (d.get("qualified_name") or "").rsplit(".", 1)[-1]
            profile = d.get("profile_json") or {}
            d["distinct_estimate"] = profile.get("distinct_estimate")
            rows.append(d)
        return rows


async def _upsert_relation(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    from_table_id: uuid.UUID,
    from_column_name: str,
    to_table_id: uuid.UUID,
    to_column_name: str,
    kind: str,
    confidence: float,
    reason: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Insert or update a flyquery_relations row.

    UPSERT key: (from_table_id, from_column_name, to_table_id, to_column_name)
    so re-runs don't create duplicates.
    """
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_relations (
                    id, tenant_id, workspace_id, dataset_id,
                    from_table_id, from_column_name, to_table_id, to_column_name,
                    kind, confidence, reason, status
                ) VALUES (
                    gen_random_uuid(), :tenant_id, :workspace_id, :dataset_id,
                    :from_tid, :from_col, :to_tid, :to_col,
                    :kind, :confidence, :reason, 'PROPOSED'
                )
                ON CONFLICT (from_table_id, from_column_name, to_table_id, to_column_name)
                DO UPDATE SET
                    confidence = EXCLUDED.confidence,
                    reason = EXCLUDED.reason,
                    kind = EXCLUDED.kind,
                    updated_at = now()
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "dataset_id": dataset_id,
                "from_tid": from_table_id,
                "from_col": from_column_name,
                "to_tid": to_table_id,
                "to_col": to_column_name,
                "kind": kind,
                "confidence": confidence,
                "reason": reason,
            },
        )
