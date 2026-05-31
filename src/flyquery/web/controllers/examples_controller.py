# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
from flyquery.interfaces.pagination import Paginated
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
        quality: QueryParam[str] = None,
        dataset_id: QueryParam[uuid.UUID] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[ExampleRead]:
        """List examples for the caller's workspace, with optional filters."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        rows = await self._service.list(
            ctx.tenant_id,
            ws,
            quality=quality,
            dataset_id=dataset_id,
        )
        items = [ExampleRead.model_validate(r) for r in rows]
        # The service does not paginate yet -- we apply the slice here
        # so the wire contract is stable. When the service grows real
        # pagination this becomes a no-op.
        sliced = items[offset : offset + limit]
        return Paginated.of(sliced, total=len(items), limit=limit, offset=offset)

    @get_mapping("/{example_id}")
    async def get_example(self, example_id: PathVar[uuid.UUID]) -> ExampleRead:
        """Fetch a single example by id. Returns 404 if not found."""
        row = await self._service.get(example_id)
        if row is None:
            raise ResourceNotFound(f"example {example_id!r} not found")
        return ExampleRead.model_validate(row)

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
