# Copyright 2026 Firefly Software Solutions Inc
"""Semantic dimensions REST controller.

``/api/v1/semantic/dimensions`` — CRUD + lifecycle for flyquery_semantic_dimensions.

Path conventions:
* ``POST   /api/v1/semantic/dimensions``               -- create (201)
* ``GET    /api/v1/semantic/dimensions``               -- list
* ``GET    /api/v1/semantic/dimensions/{id}``          -- get single
* ``PUT    /api/v1/semantic/dimensions/{id}``          -- sparse update
* ``POST   /api/v1/semantic/dimensions/{id}:publish``  -- publish (compiles SQL)
* ``POST   /api/v1/semantic/dimensions/{id}:retire``   -- retire
* ``GET    /api/v1/semantic/dimensions/{id}/history``  -- version history
"""

from __future__ import annotations

import uuid
from typing import Optional

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

from flyquery.core.services.semantic.semantic_dimensions_service import (
    SemanticDimensionsService,
)
from flyquery.interfaces.semantic import (
    SemanticDimensionCreate,
    SemanticDimensionRead,
    SemanticDimensionUpdate,
    SemanticVersionRead,
)
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/semantic/dimensions")
class SemanticDimensionsController:
    """REST adapter for ``flyquery_semantic_dimensions`` CRUD + lifecycle."""

    def __init__(self, service: SemanticDimensionsService) -> None:
        self._service = service

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[SemanticDimensionCreate]],
    ) -> SemanticDimensionRead:
        """Create a new semantic dimension in DRAFT status."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        row = await self._service.create(ctx.tenant_id, ws, body)
        return SemanticDimensionRead.model_validate(row)

    @get_mapping("")
    async def list_dimensions(
        self,
        http_request: Request,
        dataset_id: QueryParam[Optional[uuid.UUID]] = None,
    ) -> dict:
        """List all semantic dimensions for the caller's workspace."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        rows = await self._service.list(ctx.tenant_id, ws, dataset_id=dataset_id)
        return {"items": [SemanticDimensionRead.model_validate(r).model_dump(mode="json") for r in rows]}

    @get_mapping("/{dimension_id}")
    async def get_dimension(self, dimension_id: PathVar[uuid.UUID]) -> SemanticDimensionRead:
        """Fetch a single semantic dimension by id."""
        row = await self._service.get(dimension_id)
        if row is None:
            raise ResourceNotFound(f"dimension {dimension_id!r} not found")
        return SemanticDimensionRead.model_validate(row)

    @put_mapping("/{dimension_id}")
    async def update(
        self,
        dimension_id: PathVar[uuid.UUID],
        body: Valid[Body[SemanticDimensionUpdate]],
    ) -> SemanticDimensionRead:
        """Sparse-update a dimension; re-validates YAML if definition changes."""
        row = await self._service.update(dimension_id, body)
        return SemanticDimensionRead.model_validate(row)

    @post_mapping("/{dimension_id}:publish")
    async def publish(self, dimension_id: PathVar[uuid.UUID]) -> SemanticDimensionRead:
        """Validate, compile, and publish a dimension (status → PUBLISHED)."""
        row = await self._service.publish(dimension_id)
        return SemanticDimensionRead.model_validate(row)

    @post_mapping("/{dimension_id}:retire")
    async def retire(self, dimension_id: PathVar[uuid.UUID]) -> SemanticDimensionRead:
        """Retire a dimension (status → RETIRED)."""
        row = await self._service.retire(dimension_id)
        return SemanticDimensionRead.model_validate(row)

    @get_mapping("/{dimension_id}/history")
    async def history(self, dimension_id: PathVar[uuid.UUID]) -> dict:
        """Return version history for a dimension, oldest first."""
        rows = await self._service.list_history(dimension_id)
        return {"items": [SemanticVersionRead.model_validate(r).model_dump(mode="json") for r in rows]}
