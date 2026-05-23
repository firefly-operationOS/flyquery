# Copyright 2026 Firefly Software Solutions Inc
"""Tables controller.

GET  /api/v1/tables                         -- list + search/filter (NEW)
GET  /api/v1/tables/by-name/{name}          -- resolve by dataset + name (NEW)
GET  /api/v1/datasets/{dataset_id}/tables   -- list tables for a dataset
GET  /api/v1/tables/{table_id}              -- get single table
GET  /api/v1/tables/{table_id}/snapshots    -- list snapshots
GET  /api/v1/tables/{table_id}/objects      -- list schema_objects (cols+table)
GET  /api/v1/tables/{table_id}/changes      -- list schema changes

The ``/tables`` list takes ``q`` (free-text on name + qualified_name),
``name`` (exact), ``dataset_id``, ``kind`` (UPLOADED/VIEW/DERIVED),
``is_active``, ``limit``, ``offset``. Response is an envelope with
``{items, total, limit, offset, has_more}``.
"""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import rest_controller
from pyfly.web import PathVar, QueryParam, get_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from flyquery.interfaces.files import SchemaChangeRead, SchemaObjectRead, SnapshotRead, TableRead
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
        return {"items": [_table_row_to_read(r).model_dump(mode="json") for r in rows]}

    # ------------------------------------------------------------------ #
    # Search/filter tables across one or all datasets                     #
    # ------------------------------------------------------------------ #

    @get_mapping("/tables")
    async def search_tables(
        self,
        http_request: Request,
        q: QueryParam[str | None] = None,
        name: QueryParam[str | None] = None,
        dataset_id: QueryParam[uuid.UUID | None] = None,
        kind: QueryParam[str | None] = None,
        is_active: QueryParam[bool | None] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> dict:
        """Search/filter tables across the caller's workspace.

        Query parameters
        ----------------
        * ``q``          -- substring match on ``name`` or ``qualified_name``
                            (case-insensitive ``ILIKE``).
        * ``name``       -- exact match on ``name``.
        * ``dataset_id`` -- restrict to a single dataset.
        * ``kind``       -- ``UPLOADED`` / ``VIEW`` / ``DERIVED``.
        * ``is_active``  -- default ``true``; pass ``false`` to include
                            archived tables.
        * ``limit``      -- page size, clamped to [1, 1000]. Default 100.
        * ``offset``     -- starting offset. Default 0.

        Response envelope: ``{items, total, limit, offset, has_more}``.
        """
        ctx = tenant_context_from_request(http_request)
        like = f"%{q}%" if q else None
        clamped_limit = max(1, min(1000, int(limit)))
        clamped_offset = max(0, int(offset))
        effective_active = True if is_active is None else bool(is_active)
        params: dict[str, Any] = {
            "tenant": ctx.tenant_id,
            "workspace": uuid.UUID(ctx.workspace_id)
            if isinstance(ctx.workspace_id, str)
            else ctx.workspace_id,
            "q": like,
            "name": name,
            "ds_id": dataset_id,
            "kind": kind,
            "active": effective_active,
            "limit": clamped_limit,
            "offset": clamped_offset,
        }
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT
                        t.*,
                        ss.n_columns,
                        COUNT(*) OVER () AS _total
                    FROM flyquery_tables t
                    LEFT JOIN flyquery_schema_snapshots ss
                        ON ss.id = t.current_snapshot_id
                    WHERE t.tenant_id = :tenant
                      AND t.workspace_id = :workspace
                      AND t.is_active = :active
                      AND (CAST(:ds_id AS uuid) IS NULL OR t.dataset_id = CAST(:ds_id AS uuid))
                      AND (CAST(:kind AS text) IS NULL OR t.kind = CAST(:kind AS text))
                      AND (CAST(:name AS text) IS NULL OR t.name = CAST(:name AS text))
                      AND (CAST(:q AS text) IS NULL
                           OR t.name ILIKE CAST(:q AS text)
                           OR t.qualified_name ILIKE CAST(:q AS text))
                    ORDER BY t.created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                params,
            )
            rows = [dict(r) for r in result.mappings().all()]
        if rows:
            total = int(rows[0].pop("_total"))
            for r in rows[1:]:
                r.pop("_total", None)
        else:
            total = await self._count_tables(params)
        items = [_table_row_to_read(r).model_dump(mode="json") for r in rows]
        return {
            "items": items,
            "total": total,
            "limit": clamped_limit,
            "offset": clamped_offset,
            "has_more": (clamped_offset + len(items)) < total,
        }

    async def _count_tables(self, params: dict[str, Any]) -> int:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT COUNT(*) AS n
                    FROM flyquery_tables t
                    WHERE t.tenant_id = :tenant
                      AND t.workspace_id = :workspace
                      AND t.is_active = :active
                      AND (CAST(:ds_id AS uuid) IS NULL OR t.dataset_id = CAST(:ds_id AS uuid))
                      AND (CAST(:kind AS text) IS NULL OR t.kind = CAST(:kind AS text))
                      AND (CAST(:name AS text) IS NULL OR t.name = CAST(:name AS text))
                      AND (CAST(:q AS text) IS NULL
                           OR t.name ILIKE CAST(:q AS text)
                           OR t.qualified_name ILIKE CAST(:q AS text))
                    """
                ),
                params,
            )
            return int(result.scalar_one())

    # ------------------------------------------------------------------ #
    # Resolve a table by (dataset_id, name)                               #
    # ------------------------------------------------------------------ #

    @get_mapping("/tables/by-name/{name}")
    async def get_table_by_name(
        self,
        http_request: Request,
        name: PathVar[str],
        dataset_id: QueryParam[uuid.UUID | None] = None,
    ) -> TableRead:
        """Resolve a table by ``name`` within the caller's workspace.

        Pass ``?dataset_id=...`` to scope the lookup to a single dataset.
        Returns 404 if the name is not unique within the scope or no
        match is found.
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT t.*, ss.n_columns
                    FROM flyquery_tables t
                    LEFT JOIN flyquery_schema_snapshots ss
                        ON ss.id = t.current_snapshot_id
                    WHERE t.tenant_id = :tenant
                      AND t.workspace_id = :workspace
                      AND t.name = :name
                      AND t.is_active = true
                      AND (CAST(:ds_id AS uuid) IS NULL OR t.dataset_id = CAST(:ds_id AS uuid))
                    LIMIT 2
                    """
                ),
                {
                    "tenant": ctx.tenant_id,
                    "workspace": ws,
                    "name": name,
                    "ds_id": dataset_id,
                },
            )
            rows = [dict(r) for r in result.mappings().all()]
        if not rows:
            raise ResourceNotFound(f"table with name {name!r} not found")
        if len(rows) > 1:
            raise ResourceNotFound(
                f"table name {name!r} matches multiple datasets; pass ?dataset_id= to disambiguate"
            )
        return _table_row_to_read(rows[0])

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
    # List schema objects (columns + table rows) for current snapshot    #
    # ------------------------------------------------------------------ #

    @get_mapping("/tables/{table_id}/objects")
    async def list_objects(
        self,
        http_request: Request,
        table_id: PathVar[uuid.UUID],
    ) -> dict:
        """List schema_objects for the table's current snapshot."""
        ctx = tenant_context_from_request(http_request)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT so.*
                    FROM flyquery_schema_objects so
                    JOIN flyquery_tables t ON t.current_snapshot_id = so.snapshot_id
                    WHERE t.id = :tid AND t.tenant_id = :tenant
                      AND so.tenant_id = :tenant
                    ORDER BY so.kind DESC, so.qualified_name
                    """
                ),
                {"tid": table_id, "tenant": ctx.tenant_id},
            )
            rows = [dict(r) for r in result.mappings().all()]
        return {
            "items": [
                SchemaObjectRead(
                    id=r["id"],
                    tenant_id=r["tenant_id"],
                    workspace_id=r["workspace_id"],
                    table_id=r["table_id"],
                    snapshot_id=r["snapshot_id"],
                    kind=r["kind"],
                    qualified_name=r["qualified_name"],
                    data_type=r.get("data_type"),
                    is_nullable=r.get("is_nullable"),
                    description=r.get("description"),
                    description_source=r.get("description_source"),
                    synonyms_json=r.get("synonyms_json"),
                    pii_tag=r.get("pii_tag"),
                    pii_source=r.get("pii_source"),
                    business_owner=r.get("business_owner"),
                    governance_json=r.get("governance_json"),
                    is_active=r.get("is_active", True),
                    created_at=r["created_at"],
                    last_changed_at=r["last_changed_at"],
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
