# Copyright 2026 Firefly Software Solutions Inc
"""Examples REST controller.

``/api/v1/examples`` — CRUD for flyquery_examples.

Path conventions:
* ``POST /api/v1/examples``                    -- create (201)
* ``GET  /api/v1/examples``                    -- list (quality, dataset_id filters)
* ``POST /api/v1/examples/{example_id}:approve`` -- approve → APPROVED
* ``POST /api/v1/examples/{example_id}:reject``  -- reject  → REJECTED
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
    request_mapping,
)
from starlette.requests import Request

from flyquery.core.services.examples.examples_service import ExamplesService
from flyquery.interfaces.examples import ExampleCreate, ExampleRead
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/examples")
class ExamplesController:
    """REST adapter for ``flyquery_examples`` CRUD + approval workflow."""

    def __init__(self, service: ExamplesService) -> None:
        self._service = service

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[ExampleCreate]],
    ) -> ExampleRead:
        """Create an example; defaults to source=USER_CURATED, quality=PROPOSED."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        row = await self._service.create(ctx.tenant_id, ws, body)
        return ExampleRead.model_validate(row)

    @get_mapping("")
    async def list_examples(
        self,
        http_request: Request,
        quality: QueryParam[str | None] = None,
        dataset_id: QueryParam[uuid.UUID | None] = None,
    ) -> dict:
        """List examples for the caller's workspace, with optional filters."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        rows = await self._service.list(
            ctx.tenant_id,
            ws,
            quality=quality,
            dataset_id=dataset_id,
        )
        return {"items": [ExampleRead.model_validate(r).model_dump(mode="json") for r in rows]}

    @post_mapping("/{example_id}:approve")
    async def approve(self, example_id: PathVar[uuid.UUID]) -> ExampleRead:
        """Approve an example (quality → APPROVED)."""
        row = await self._service.approve(example_id)
        if row is None:
            raise ResourceNotFound(f"example {example_id!r} not found")
        return ExampleRead.model_validate(row)

    @post_mapping("/{example_id}:reject")
    async def reject(self, example_id: PathVar[uuid.UUID]) -> ExampleRead:
        """Reject an example (quality → REJECTED)."""
        row = await self._service.reject(example_id)
        if row is None:
            raise ResourceNotFound(f"example {example_id!r} not found")
        return ExampleRead.model_validate(row)
