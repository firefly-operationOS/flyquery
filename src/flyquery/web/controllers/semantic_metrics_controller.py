# Copyright 2026 Firefly Software Solutions Inc
"""Semantic metrics REST controller.

``/api/v1/semantic/metrics`` — CRUD + lifecycle for flyquery_semantic_metrics.

Path conventions:
* ``POST   /api/v1/semantic/metrics``               -- create (201)
* ``GET    /api/v1/semantic/metrics``               -- list
* ``GET    /api/v1/semantic/metrics/{id}``          -- get single
* ``PUT    /api/v1/semantic/metrics/{id}``          -- sparse update
* ``POST   /api/v1/semantic/metrics/{id}:publish``  -- publish (compiles SQL)
* ``POST   /api/v1/semantic/metrics/{id}:retire``   -- retire
* ``GET    /api/v1/semantic/metrics/{id}/history``  -- version history
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import (
    Body,
    PathVar,
    QueryParam,
    Valid,
    get_mapping,
    post_mapping,
    put_mapping,
    request_mapping,
)
from starlette.requests import Request

from flyquery.core.services.semantic.semantic_service import SemanticService
from flyquery.interfaces.semantic import (
    SemanticMetricCreate,
    SemanticMetricRead,
    SemanticMetricUpdate,
    SemanticVersionRead,
)
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/semantic/metrics")
class SemanticMetricsController:
    """REST adapter for ``flyquery_semantic_metrics`` CRUD + lifecycle."""

    def __init__(self, service: SemanticService) -> None:
        self._service = service

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[SemanticMetricCreate]],
    ) -> SemanticMetricRead:
        """Create a new semantic metric in DRAFT status."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        row = await self._service.create(ctx.tenant_id, ws, body)
        return SemanticMetricRead.model_validate(row)

    @get_mapping("")
    async def list_metrics(
        self,
        http_request: Request,
        dataset_id: QueryParam[uuid.UUID | None] = None,
    ) -> dict:
        """List all semantic metrics for the caller's workspace."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        rows = await self._service.list(ctx.tenant_id, ws, dataset_id=dataset_id)
        return {"items": [SemanticMetricRead.model_validate(r).model_dump(mode="json") for r in rows]}

    @get_mapping("/{metric_id}")
    async def get_metric(self, metric_id: PathVar[uuid.UUID]) -> SemanticMetricRead:
        """Fetch a single semantic metric by id."""
        row = await self._service.get(metric_id)
        if row is None:
            raise ResourceNotFound(f"metric {metric_id!r} not found")
        return SemanticMetricRead.model_validate(row)

    @put_mapping("/{metric_id}")
    async def update(
        self,
        metric_id: PathVar[uuid.UUID],
        body: Valid[Body[SemanticMetricUpdate]],
    ) -> SemanticMetricRead:
        """Sparse-update a metric; re-validates YAML if definition changes."""
        row = await self._service.update(metric_id, body)
        return SemanticMetricRead.model_validate(row)

    @post_mapping("/{metric_id}:publish")
    async def publish(self, metric_id: PathVar[uuid.UUID]) -> SemanticMetricRead:
        """Validate, compile, and publish a metric (status → PUBLISHED)."""
        row = await self._service.publish(metric_id)
        return SemanticMetricRead.model_validate(row)

    @post_mapping("/{metric_id}:retire")
    async def retire(self, metric_id: PathVar[uuid.UUID]) -> SemanticMetricRead:
        """Retire a metric (status → RETIRED)."""
        row = await self._service.retire(metric_id)
        return SemanticMetricRead.model_validate(row)

    @get_mapping("/{metric_id}/history")
    async def history(self, metric_id: PathVar[uuid.UUID]) -> dict:
        """Return version history for a metric, oldest first."""
        rows = await self._service.list_history(metric_id)
        return {"items": [SemanticVersionRead.model_validate(r).model_dump(mode="json") for r in rows]}
