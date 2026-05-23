# Copyright 2026 Firefly Software Solutions Inc
"""Stage 3 — reconcile: snapshot insert (PARTIAL) + schema diff + objects.

For each ParsedTable:
- Insert flyquery_schema_snapshots row (status='PARTIAL')
- Insert flyquery_schema_objects: one TABLE object + one COLUMN per column
- If a prev snapshot exists, compute diff → write flyquery_schema_changes
- Annotation transplant: carry HUMAN-set fields from old → new schema_objects
- Return the created snapshot_id
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.services.ingestion.reader import ColumnSchema
from flyquery.core.services.ingestion.stages.parse import ParsedTable

logger = logging.getLogger(__name__)


@dataclass
class ReconcileResult:
    snapshot_id: uuid.UUID
    table_id: uuid.UUID
    n_columns: int
    n_rows_actual: int
    added_columns: list[str]
    removed_columns: list[str]
    type_changed: list[str]


async def run_reconcile(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    parsed: ParsedTable,
    actor: str,
    triggered_by: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> ReconcileResult:
    """Execute Stage 3: reconcile."""
    mat = parsed.result
    snapshot_id = uuid.uuid4()

    # Snapshot hash = hash of (column_name, data_type) pairs for change detection
    col_sig = sorted(
        (c.name, c.data_type) for c in mat.columns
    )
    snapshot_hash = hashlib.sha256(json.dumps(col_sig).encode()).hexdigest()

    # --- Insert snapshot (PARTIAL) ---
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_schema_snapshots (
                    id, tenant_id, workspace_id, dataset_id, table_id,
                    snapshot_hash, n_columns, n_rows_estimate, n_rows_actual,
                    parquet_object_key, parquet_byte_size, status,
                    triggered_by, created_by
                ) VALUES (
                    :id, :tenant_id, :workspace_id, :dataset_id, :table_id,
                    :snapshot_hash, :n_columns, :n_rows_estimate, :n_rows_actual,
                    :parquet_object_key, :parquet_byte_size, 'PARTIAL',
                    :triggered_by, :created_by
                )
                """
            ),
            {
                "id": snapshot_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "dataset_id": dataset_id,
                "table_id": parsed.table_id,
                "snapshot_hash": snapshot_hash,
                "n_columns": len(mat.columns),
                "n_rows_estimate": mat.n_rows_actual,
                "n_rows_actual": mat.n_rows_actual,
                "parquet_object_key": parsed.parquet_key,
                "parquet_byte_size": mat.parquet_byte_size,
                "triggered_by": triggered_by,
                "created_by": actor,
            },
        )

    # --- Find previous snapshot for diff ---
    prev_snapshot = await _get_latest_ready_snapshot(
        tenant_id, parsed.table_id, snapshot_id, session_factory
    )
    prev_columns: dict[str, str] = {}  # name → data_type
    if prev_snapshot:
        prev_columns = await _get_snapshot_columns(
            prev_snapshot["id"], tenant_id, session_factory
        )

    new_columns: dict[str, str] = {c.name: c.data_type for c in mat.columns}

    # --- Compute diff ---
    added = [name for name in new_columns if name not in prev_columns]
    removed = [name for name in prev_columns if name not in new_columns]
    type_changed = [
        name
        for name in new_columns
        if name in prev_columns and new_columns[name] != prev_columns[name]
    ]

    prev_snap_id = prev_snapshot["id"] if prev_snapshot else None

    # --- Write schema_changes ---
    if prev_snapshot and (added or removed or type_changed):
        await _write_schema_changes(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            table_id=parsed.table_id,
            prev_snapshot_id=prev_snap_id,
            next_snapshot_id=snapshot_id,
            prev_columns=prev_columns,
            new_columns=new_columns,
            added=added,
            removed=removed,
            type_changed=type_changed,
            session_factory=session_factory,
        )

    # --- Load annotation transplant candidates from previous snapshot ---
    human_annotations: dict[str, dict[str, Any]] = {}
    if prev_snapshot:
        human_annotations = await _load_human_annotations(
            prev_snap_id, tenant_id, session_factory
        )

    # --- Insert schema_objects (TABLE + per-column COLUMN) ---
    table_obj_id = uuid.uuid4()
    table_source_hash = hashlib.sha256(
        f"{parsed.qualified_name}:TABLE".encode()
    ).hexdigest()
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_schema_objects (
                    id, tenant_id, workspace_id, table_id, snapshot_id,
                    kind, qualified_name, source_hash
                ) VALUES (
                    :id, :tenant_id, :workspace_id, :table_id, :snapshot_id,
                    'TABLE', :qualified_name, :source_hash
                )
                """
            ),
            {
                "id": table_obj_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "table_id": parsed.table_id,
                "snapshot_id": snapshot_id,
                "qualified_name": parsed.qualified_name,
                "source_hash": table_source_hash,
            },
        )

        for col in mat.columns:
            col_qualified = f"{parsed.qualified_name}.{col.name}"
            col_hash = hashlib.sha256(
                f"{col_qualified}:{col.data_type}".encode()
            ).hexdigest()
            col_obj_id = uuid.uuid4()

            # Transplant human annotations if this column existed before
            annotation = human_annotations.get(col.name, {})

            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_schema_objects (
                        id, tenant_id, workspace_id, table_id, snapshot_id,
                        kind, parent_id, qualified_name, data_type, is_nullable,
                        source_hash,
                        description, description_source,
                        synonyms_json, pii_tag, pii_source,
                        business_owner, governance_json
                    ) VALUES (
                        :id, :tenant_id, :workspace_id, :table_id, :snapshot_id,
                        'COLUMN', :parent_id, :qualified_name, :data_type, :is_nullable,
                        :source_hash,
                        :description, :description_source,
                        CAST(:synonyms_json AS jsonb), :pii_tag, :pii_source,
                        :business_owner, CAST(:governance_json AS jsonb)
                    )
                    """
                ),
                {
                    "id": col_obj_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "table_id": parsed.table_id,
                    "snapshot_id": snapshot_id,
                    "parent_id": table_obj_id,
                    "qualified_name": col_qualified,
                    "data_type": col.data_type,
                    "is_nullable": col.is_nullable,
                    "source_hash": col_hash,
                    "description": annotation.get("description"),
                    "description_source": annotation.get("description_source"),
                    "synonyms_json": json.dumps(annotation["synonyms_json"])
                    if annotation.get("synonyms_json")
                    else "null",
                    "pii_tag": annotation.get("pii_tag"),
                    "pii_source": annotation.get("pii_source"),
                    "business_owner": annotation.get("business_owner"),
                    "governance_json": json.dumps(annotation["governance_json"])
                    if annotation.get("governance_json")
                    else "null",
                },
            )

    logger.info(
        "stage=reconcile snapshot_id=%s table_id=%s added=%d removed=%d type_changed=%d",
        snapshot_id,
        parsed.table_id,
        len(added),
        len(removed),
        len(type_changed),
    )

    return ReconcileResult(
        snapshot_id=snapshot_id,
        table_id=parsed.table_id,
        n_columns=len(mat.columns),
        n_rows_actual=mat.n_rows_actual,
        added_columns=added,
        removed_columns=removed,
        type_changed=type_changed,
    )


async def _get_latest_ready_snapshot(
    tenant_id: str,
    table_id: uuid.UUID,
    exclude_snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, Any] | None:
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT id, n_columns, taken_at
                FROM flyquery_schema_snapshots
                WHERE tenant_id = :tenant AND table_id = :tid
                  AND status = 'READY'
                  AND id != :excl
                ORDER BY taken_at DESC
                LIMIT 1
                """
            ),
            {"tenant": tenant_id, "tid": table_id, "excl": exclude_snapshot_id},
        )
        row = result.mappings().one_or_none()
        return dict(row) if row else None


async def _get_snapshot_columns(
    snapshot_id: uuid.UUID,
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, str]:
    """Return {column_name: data_type} for a snapshot."""
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT qualified_name, data_type
                FROM flyquery_schema_objects
                WHERE snapshot_id = :sid AND tenant_id = :tenant AND kind = 'COLUMN'
                """
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        rows = result.mappings().all()
        # qualified_name is like "dataset.table.col_name"; extract last part
        return {
            row["qualified_name"].rsplit(".", 1)[-1]: row["data_type"] or ""
            for row in rows
        }


async def _load_human_annotations(
    snapshot_id: uuid.UUID,
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, dict[str, Any]]:
    """Load HUMAN-set annotations from the previous snapshot (keyed by column name)."""
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT
                    qualified_name,
                    description, description_source,
                    synonyms_json, pii_tag, pii_source,
                    business_owner, governance_json
                FROM flyquery_schema_objects
                WHERE snapshot_id = :sid AND tenant_id = :tenant AND kind = 'COLUMN'
                  AND (
                    description_source = 'HUMAN'
                    OR pii_source = 'HUMAN'
                    OR business_owner IS NOT NULL
                  )
                """
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        out: dict[str, dict[str, Any]] = {}
        for row in result.mappings().all():
            col_name = row["qualified_name"].rsplit(".", 1)[-1]
            out[col_name] = {
                "description": row["description"],
                "description_source": row["description_source"],
                "synonyms_json": row["synonyms_json"],
                "pii_tag": row["pii_tag"],
                "pii_source": row["pii_source"],
                "business_owner": row["business_owner"],
                "governance_json": row["governance_json"],
            }
        return out


async def _write_schema_changes(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    table_id: uuid.UUID,
    prev_snapshot_id: uuid.UUID | None,
    next_snapshot_id: uuid.UUID,
    prev_columns: dict[str, str],
    new_columns: dict[str, str],
    added: list[str],
    removed: list[str],
    type_changed: list[str],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as s, s.begin():
        for col_name in added:
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_schema_changes (
                        id, tenant_id, workspace_id, table_id,
                        prev_snapshot_id, next_snapshot_id,
                        column_name, change, before_json, after_json
                    ) VALUES (
                        :id, :tenant_id, :workspace_id, :table_id,
                        :prev_snap, :next_snap,
                        :col, 'ADDED', null, CAST(:after AS jsonb)
                    )
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "table_id": table_id,
                    "prev_snap": prev_snapshot_id,
                    "next_snap": next_snapshot_id,
                    "col": col_name,
                    "after": json.dumps({"data_type": new_columns[col_name]}),
                },
            )
        for col_name in removed:
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_schema_changes (
                        id, tenant_id, workspace_id, table_id,
                        prev_snapshot_id, next_snapshot_id,
                        column_name, change, before_json, after_json
                    ) VALUES (
                        :id, :tenant_id, :workspace_id, :table_id,
                        :prev_snap, :next_snap,
                        :col, 'REMOVED', CAST(:before AS jsonb), null
                    )
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "table_id": table_id,
                    "prev_snap": prev_snapshot_id,
                    "next_snap": next_snapshot_id,
                    "col": col_name,
                    "before": json.dumps({"data_type": prev_columns[col_name]}),
                },
            )
        for col_name in type_changed:
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_schema_changes (
                        id, tenant_id, workspace_id, table_id,
                        prev_snapshot_id, next_snapshot_id,
                        column_name, change, before_json, after_json
                    ) VALUES (
                        :id, :tenant_id, :workspace_id, :table_id,
                        :prev_snap, :next_snap,
                        :col, 'TYPE_CHANGED', CAST(:before AS jsonb), CAST(:after AS jsonb)
                    )
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "table_id": table_id,
                    "prev_snap": prev_snapshot_id,
                    "next_snap": next_snapshot_id,
                    "col": col_name,
                    "before": json.dumps({"data_type": prev_columns[col_name]}),
                    "after": json.dumps({"data_type": new_columns[col_name]}),
                },
            )
