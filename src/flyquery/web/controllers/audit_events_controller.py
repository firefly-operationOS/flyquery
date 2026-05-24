# Copyright 2026 Firefly Software Solutions Inc
"""Audit events REST controller.

``GET /api/v1/audit-events`` -- paginated read over the audit ledger.

This endpoint fulfils the audit roadmap item flagged as ``v1+`` in
``docs/api-reference.md`` (the write side was added alongside this
controller in :class:`AuditEventService`). Today writes land from a
small set of mutating handlers (workspace + dataset CRUD,
agent-token mint / revoke); more callsites will follow.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pyfly.container import rest_controller
from pyfly.web import QueryParam, get_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.ops.audit_event_service import AuditEventService
from flyquery.interfaces.ops import AuditEventRead
from flyquery.interfaces.pagination import Paginated
from flyquery.web.conventions import tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/audit-events")
class AuditEventsController:
    """REST adapter for ``flyquery_audit_events`` reads."""

    def __init__(self, service: AuditEventService) -> None:
        self._service = service

    @get_mapping("")
    async def list_events(
        self,
        http_request: Request,
        event_type: QueryParam[str] = None,
        actor: QueryParam[str] = None,
        resource_kind: QueryParam[str] = None,
        date_from: QueryParam[datetime] = None,
        date_to: QueryParam[datetime] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[AuditEventRead]:
        """List audit events for the caller's workspace, newest first.

        Filters
        -------
        * ``event_type``    -- exact match (e.g. ``dataset.created``)
        * ``actor``         -- exact match
        * ``resource_kind`` -- exact match (``dataset`` / ``agent_token`` / ...)
        * ``date_from``     -- inclusive lower bound on ``created_at``
        * ``date_to``       -- exclusive upper bound on ``created_at``
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        rows, total = await self._service.list_filtered(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            event_type=event_type,
            actor=actor,
            resource_kind=resource_kind,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        items = [AuditEventRead.model_validate(r) for r in rows]
        return Paginated.of(items, total=total, limit=limit, offset=offset)


__all__ = ["AuditEventsController"]
