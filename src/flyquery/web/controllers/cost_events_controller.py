# Copyright 2026 Firefly Software Solutions Inc
"""Cost events REST controller.

``GET /api/v1/cost-events`` -- paginated read over the per-call LLM
cost ledger. Powers the billing roadmap (``/api/v1/billing`` is a
future rollup endpoint on top of this raw stream).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pyfly.container import rest_controller
from pyfly.web import QueryParam, get_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.ops.cost_event_service import CostEventService
from flyquery.interfaces.ops import CostEventRead
from flyquery.interfaces.pagination import Paginated
from flyquery.web.conventions import tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/cost-events")
class CostEventsController:
    """REST adapter for ``flyquery_cost_events`` reads."""

    def __init__(self, service: CostEventService) -> None:
        self._service = service

    @get_mapping("")
    async def list_events(
        self,
        http_request: Request,
        actor: QueryParam[str] = None,
        model: QueryParam[str] = None,
        operation: QueryParam[str] = None,
        date_from: QueryParam[datetime] = None,
        date_to: QueryParam[datetime] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[CostEventRead]:
        """List cost events for the caller's workspace, newest first.

        Filters
        -------
        * ``actor``     -- exact match
        * ``model``     -- exact match (``anthropic:claude-sonnet-4-6`` etc.)
        * ``operation`` -- exact match (``grounding`` / ``generation`` / ...)
        * ``date_from`` -- inclusive lower bound on ``created_at``
        * ``date_to``   -- exclusive upper bound on ``created_at``
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        rows, total = await self._service.list_filtered(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            actor=actor,
            model=model,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        items = [CostEventRead.model_validate(r) for r in rows]
        return Paginated.of(items, total=total, limit=limit, offset=offset)


__all__ = ["CostEventsController"]
