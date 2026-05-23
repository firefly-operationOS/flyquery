# Copyright 2026 Firefly Software Solutions Inc
"""Tables controller.

GET  /api/v1/datasets/{dataset_id}/tables  -- list tables for a dataset
GET  /api/v1/tables/{table_id}             -- get single table (with n_columns from current snap)
GET  /api/v1/tables/{table_id}/snapshots  -- list snapshots
GET  /api/v1/tables/{table_id}/changes    -- list schema changes
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from pyfly.container import rest_controller
from pyfly.web import PathVar, get_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from flyquery.interfaces.files import SchemaChangeRead, SnapshotRead, TableRead
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1")
class TablesController:
    """REST adapter for schema knowledge-base tables."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    # ------------------------------------------------------------------ #
    # List tables for a dataset                                           #
    # ------------------------------------------------------------------ #

    @get_mapping("/datasets/{dataset_id}/tables")
    async def list_tables(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> dict:
        ctx = tenant_context_from_request(http_request)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT
                        t.*,
                        ss.n_columns
                    FROM flyquery_tables t
                    LEFT JOIN flyquery_schema_snapshots ss
                        ON ss.id = t.current_snapshot_id
                    WHERE t.dataset_id = :ds_id
                      AND t.tenant_id = :tenant
                      AND t.is_active = true
                    ORDER BY t.created_at
                    """
                ),
                {"ds_id": dataset_id, "tenant": ctx.tenant_id},
            )
            rows = [dict(r) for r in result.mappings().all()]
        return {
            "items": [_table_row_to_read(r).model_dump(mode="json") for r in rows]
        }

    # ------------------------------------------------------------------ #
    # Get single table                                                    #
    # ------------------------------------------------------------------ #

    @get_mapping("/tables/{table_id}")
    async def get_table(
        self,
        http_request: Request,
        table_id: PathVar[uuid.UUID],
    ) -> TableRead:
        ctx = tenant_context_from_request(http_request)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT
                        t.*,
                        ss.n_columns
                    FROM flyquery_tables t
                    LEFT JOIN flyquery_schema_snapshots ss
                        ON ss.id = t.current_snapshot_id
                    WHERE t.id = :tid AND t.tenant_id = :tenant
                    """
                ),
                {"tid": table_id, "tenant": ctx.tenant_id},
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise ResourceNotFound(f"table {table_id!r} not found")
        return _table_row_to_read(dict(row))

    # ------------------------------------------------------------------ #
    # List snapshots                                                      #
    # ------------------------------------------------------------------ #

    @get_mapping("/tables/{table_id}/snapshots")
    async def list_snapshots(
        self,
        http_request: Request,
        table_id: PathVar[uuid.UUID],
    ) -> dict:
        ctx = tenant_context_from_request(http_request)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT *
                    FROM flyquery_schema_snapshots
                    WHERE table_id = :tid AND tenant_id = :tenant
                    ORDER BY taken_at
                    """
                ),
                {"tid": table_id, "tenant": ctx.tenant_id},
            )
            rows = [dict(r) for r in result.mappings().all()]
        return {
            "items": [
                SnapshotRead(
                    id=r["id"],
                    table_id=r["table_id"],
                    taken_at=r["taken_at"],
                    n_columns=r["n_columns"],
                    n_rows_actual=r.get("n_rows_actual"),
                    n_rows_estimate=r.get("n_rows_estimate"),
                    parquet_byte_size=r.get("parquet_byte_size"),
                    status=r["status"],
                    triggered_by=r["triggered_by"],
                ).model_dump(mode="json")
                for r in rows
            ]
        }

    # ------------------------------------------------------------------ #
    # List schema changes                                                 #
    # ------------------------------------------------------------------ #

    @get_mapping("/tables/{table_id}/changes")
    async def list_changes(
        self,
        http_request: Request,
        table_id: PathVar[uuid.UUID],
    ) -> dict:
        ctx = tenant_context_from_request(http_request)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT *
                    FROM flyquery_schema_changes
                    WHERE table_id = :tid AND tenant_id = :tenant
                    ORDER BY created_at
                    """
                ),
                {"tid": table_id, "tenant": ctx.tenant_id},
            )
            rows = [dict(r) for r in result.mappings().all()]
        return {
            "items": [
                SchemaChangeRead(
                    id=r["id"],
                    table_id=r["table_id"],
                    prev_snapshot_id=r.get("prev_snapshot_id"),
                    next_snapshot_id=r["next_snapshot_id"],
                    column_name=r["column_name"],
                    change=r["change"],
                    before_json=r.get("before_json"),
                    after_json=r.get("after_json"),
                    llm_rationale=r.get("llm_rationale"),
                    approved_by=r.get("approved_by"),
                    approved_at=r.get("approved_at"),
                    created_at=r["created_at"],
                ).model_dump(mode="json")
                for r in rows
            ]
        }


# ------------------------------------------------------------------ #
# Helper                                                              #
# ------------------------------------------------------------------ #


def _table_row_to_read(row: dict) -> TableRead:
    return TableRead(
        id=row["id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        dataset_id=row["dataset_id"],
        source_file_id=row.get("source_file_id"),
        name=row["name"],
        qualified_name=row["qualified_name"],
        kind=row.get("kind", "UPLOADED"),
        sheet_or_json_path=row.get("sheet_or_json_path"),
        current_snapshot_id=row.get("current_snapshot_id"),
        description=row.get("description"),
        description_source=row.get("description_source"),
        business_owner=row.get("business_owner"),
        is_active=row.get("is_active", True),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        n_columns=row.get("n_columns"),
    )
