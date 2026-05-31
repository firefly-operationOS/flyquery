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

"""Glossary REST controller.

``/api/v1/glossary`` — CRUD for flyquery_glossary_terms.

Path conventions:
* ``POST   /api/v1/glossary``         -- create (201)
* ``GET    /api/v1/glossary``         -- list (paginated)
* ``PUT    /api/v1/glossary/{id}``    -- sparse update
* ``DELETE /api/v1/glossary/{id}``    -- hard delete (204)
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import (
    Body,
    PathVar,
    QueryParam,
    Valid,
    delete_mapping,
    get_mapping,
    post_mapping,
    put_mapping,
    request_mapping,
)
from starlette.requests import Request
from starlette.responses import Response

from flyquery.core.services.glossary.glossary_service import GlossaryService
from flyquery.interfaces.glossary import (
    GlossaryTermCreate,
    GlossaryTermRead,
    GlossaryTermUpdate,
)
from flyquery.interfaces.pagination import Paginated
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/glossary")
class GlossaryController:
    """REST adapter for ``flyquery_glossary_terms`` CRUD."""

    def __init__(self, service: GlossaryService) -> None:
        self._service = service

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[GlossaryTermCreate]],
    ) -> GlossaryTermRead:
        """Create a glossary term; (workspace_id, term) must be unique."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        row = await self._service.create(ctx.tenant_id, ws, body)
        return GlossaryTermRead.model_validate(row)

    @get_mapping("")
    async def list_terms(
        self,
        http_request: Request,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[GlossaryTermRead]:
        """Return paginated glossary terms for the caller's workspace.

        ``total`` is not populated -- the underlying service does not
        compute a COUNT(*); consumers use ``has_more`` to decide
        whether to fetch another page.
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id)
        rows = await self._service.list(ctx.tenant_id, ws, limit=limit, offset=offset)
        items = [GlossaryTermRead.model_validate(r) for r in rows]
        return Paginated.of(items, limit=limit, offset=offset)

    @get_mapping("/{term_id}")
    async def get_term(self, term_id: PathVar[uuid.UUID]) -> GlossaryTermRead:
        """Fetch a single glossary term by id. Returns 404 if not found."""
        row = await self._service.get(term_id)
        if row is None:
            raise ResourceNotFound(f"glossary term {term_id!r} not found")
        return GlossaryTermRead.model_validate(row)

    @put_mapping("/{term_id}")
    async def update(
        self,
        term_id: PathVar[uuid.UUID],
        body: Valid[Body[GlossaryTermUpdate]],
    ) -> GlossaryTermRead:
        """Sparse-update a glossary term."""
        row = await self._service.update(term_id, body)
        return GlossaryTermRead.model_validate(row)

    @delete_mapping("/{term_id}", status_code=204)
    async def delete(self, term_id: PathVar[uuid.UUID]) -> Response:
        """Hard-delete a glossary term."""
        term = await self._service.get(term_id)
        if term is None:
            raise ResourceNotFound(f"glossary term {term_id!r} not found")
        await self._service.delete(term_id)
        return Response(status_code=204)
