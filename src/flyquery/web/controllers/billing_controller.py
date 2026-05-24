# Copyright 2026 Firefly Software Solutions Inc
"""Billing rollup REST controller (v1.0 -- new in 26.5.10).

``GET /api/v1/billing`` -- aggregates ``flyquery_cost_events`` into
day / week / month buckets and returns a flat envelope. Sits on top of
the per-call ledger that the agent pipeline writes -- consumers wanting
raw rows should hit ``GET /api/v1/cost-events`` instead.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pyfly.container import rest_controller
from pyfly.web import QueryParam, get_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.ops.billing_service import BillingService
from flyquery.interfaces.ops import BillingBreakdownItem, BillingRollup
from flyquery.web.conventions import InvalidRequest, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/billing")
class BillingController:
    """REST adapter for the billing rollup."""

    def __init__(self, service: BillingService) -> None:
        self._service = service

    @get_mapping("")
    async def rollup(
        self,
        http_request: Request,
        period: QueryParam[str] = "day",
        date_from: QueryParam[datetime] = None,
        date_to: QueryParam[datetime] = None,
    ) -> BillingRollup:
        """Aggregate LLM cost into ``day`` / ``week`` / ``month`` buckets.

        Query params
        ------------
        * ``period``    -- ``day`` (default) / ``week`` / ``month``
        * ``date_from`` -- inclusive lower bound on ``created_at``
        * ``date_to``   -- exclusive upper bound on ``created_at``

        Response shape: :class:`BillingRollup`. Buckets with zero
        cost are omitted from the breakdown (no empty days).
        """
        if period not in ("day", "week", "month"):
            raise InvalidRequest(f"period must be one of day | week | month; got {period!r}")
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        total, breakdown = await self._service.rollup(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            period=period,  # type: ignore[arg-type]  -- validated above
            date_from=date_from,
            date_to=date_to,
        )
        return BillingRollup(
            period=period,
            date_from=date_from,
            date_to=date_to,
            total_cost_cents=total,
            breakdown=[BillingBreakdownItem.model_validate(b) for b in breakdown],
        )


__all__ = ["BillingController"]
