# Copyright 2026 Firefly Software Solutions Inc
"""Relations controller.

GET  /api/v1/datasets/{dataset_id}/relations   -- list proposed/approved relations
POST /api/v1/relations/{relation_id}:approve   -- approve a PROPOSED relation
POST /api/v1/relations/{relation_id}:reject    -- reject a PROPOSED relation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from pyfly.container import rest_controller
from pyfly.web import PathVar, get_mapping, post_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1")
class RelationsController:
    """REST adapter for dataset relations (heuristic + agent-proposed)."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    @get_mapping("/datasets/{dataset_id}/relations")
    async def list_relations(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> dict:
        """List relations for a dataset (all statuses by default)."""
        ctx = tenant_context_from_request(http_request)
        params = http_request.query_params
        status_filter = params.get("status")

        async with self._factory() as s:
            query = """
                SELECT r.*,
                       ft.name AS from_table_name,
                       tt.name AS to_table_name
                FROM flyquery_relations r
                LEFT JOIN flyquery_tables ft ON ft.id = r.from_table_id
                LEFT JOIN flyquery_tables tt ON tt.id = r.to_table_id
                WHERE r.dataset_id = :ds_id AND r.tenant_id = :tenant
            """
            params_dict: dict = {"ds_id": dataset_id, "tenant": ctx.tenant_id}
            if status_filter:
                query += " AND r.status = :status"
                params_dict["status"] = status_filter
            query += " ORDER BY r.confidence DESC, r.created_at"

            result = await s.execute(sa.text(query), params_dict)
            rows = [dict(r) for r in result.mappings().all()]

        return {
            "items": [
                {
                    "id": str(r["id"]),
                    "dataset_id": str(r["dataset_id"]),
                    "from_table_id": str(r["from_table_id"]),
                    "from_table_name": r.get("from_table_name"),
                    "from_column_name": r["from_column_name"],
                    "to_table_id": str(r["to_table_id"]),
                    "to_table_name": r.get("to_table_name"),
                    "to_column_name": r["to_column_name"],
                    "kind": r["kind"],
                    "confidence": r["confidence"],
                    "reason": r.get("reason"),
                    "status": r["status"],
                    "approved_by": r.get("approved_by"),
                    "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
                    "updated_at": r["updated_at"].isoformat() if r.get("updated_at") else None,
                }
                for r in rows
            ]
        }

    @post_mapping("/relations/{relation_id}:approve", status_code=200)
    async def approve_relation(
        self,
        http_request: Request,
        relation_id: PathVar[uuid.UUID],
    ) -> dict:
        """Approve a PROPOSED relation."""
        ctx = tenant_context_from_request(http_request)
        approved_by = ctx.actor or ctx.tenant_id
        now = datetime.now(timezone.utc)

        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_relations
                    SET status = 'APPROVED', approved_by = :approved_by, updated_at = :now
                    WHERE id = :rid AND tenant_id = :tenant
                    RETURNING id, status, approved_by, updated_at
                    """
                ),
                {"rid": relation_id, "tenant": ctx.tenant_id, "approved_by": approved_by, "now": now},
            )
            row = result.mappings().one_or_none()

        if row is None:
            raise ResourceNotFound(f"relation {relation_id!r} not found")
        return dict(row)

    @post_mapping("/relations/{relation_id}:reject", status_code=200)
    async def reject_relation(
        self,
        http_request: Request,
        relation_id: PathVar[uuid.UUID],
    ) -> dict:
        """Reject a PROPOSED relation."""
        ctx = tenant_context_from_request(http_request)
        now = datetime.now(timezone.utc)

        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_relations
                    SET status = 'REJECTED', updated_at = :now
                    WHERE id = :rid AND tenant_id = :tenant
                    RETURNING id, status, updated_at
                    """
                ),
                {"rid": relation_id, "tenant": ctx.tenant_id, "now": now},
            )
            row = result.mappings().one_or_none()

        if row is None:
            raise ResourceNotFound(f"relation {relation_id!r} not found")
        return dict(row)
