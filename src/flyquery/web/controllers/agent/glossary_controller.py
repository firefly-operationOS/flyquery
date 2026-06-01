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

"""Agent-tier glossary controller.

``/api/v1/agent/glossary`` — mirror of the user-tier glossary surface, gated
by ``flyquery.semantic:author`` (writes) / ``flyquery.semantic:read`` (reads).
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

from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.core.services.glossary.glossary_service import GlossaryService
from flyquery.interfaces.glossary import (
    GlossaryTermCreate,
    GlossaryTermRead,
    GlossaryTermUpdate,
)
from flyquery.interfaces.pagination import Paginated
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    ResourceNotFound,
    tenant_context_from_request,
)

_SCOPE_AUTHOR = "flyquery.semantic:author"
_SCOPE_READ = "flyquery.semantic:read"


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


@rest_controller
@request_mapping("/api/v1/agent/glossary")
class AgentGlossaryController:
    """Agent-tier mirror of ``/api/v1/glossary``."""

    def __init__(
        self,
        service: GlossaryService,
        agent_token_service: AgentTokenService,
    ) -> None:
        self._service = service
        self._token_service = agent_token_service

    async def _verify(self, http_request: Request, scope: str) -> None:
        token = http_request.headers.get(HEADER_AGENT_TOKEN)
        if not token:
            raise MissingAgentToken("X-Agent-Token header is required for /api/v1/agent/* routes.")
        ctx = tenant_context_from_request(http_request)
        await self._token_service.verify(
            token, tenant_id=ctx.tenant_id, workspace_id=ctx.workspace_id, scope=scope
        )

    @post_mapping("", status_code=201)
    async def create(
        self, http_request: Request, body: Valid[Body[GlossaryTermCreate]]
    ) -> GlossaryTermRead:
        """Create a glossary term (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        row = await self._service.create(ctx.tenant_id, ws, body)
        return GlossaryTermRead.model_validate(row)

    @get_mapping("")
    async def list_terms(
        self,
        http_request: Request,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[GlossaryTermRead]:
        """List glossary terms for the caller's workspace (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        rows = await self._service.list(ctx.tenant_id, ws, limit=limit, offset=offset)
        items = [GlossaryTermRead.model_validate(r) for r in rows]
        return Paginated.of(items, limit=limit, offset=offset)

    @get_mapping("/{term_id}")
    async def get_term(
        self, http_request: Request, term_id: PathVar[uuid.UUID]
    ) -> GlossaryTermRead:
        """Fetch a single glossary term (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        row = await self._service.get(term_id)
        if row is None:
            raise ResourceNotFound(f"glossary term {term_id!r} not found")
        return GlossaryTermRead.model_validate(row)

    @put_mapping("/{term_id}")
    async def update(
        self,
        http_request: Request,
        term_id: PathVar[uuid.UUID],
        body: Valid[Body[GlossaryTermUpdate]],
    ) -> GlossaryTermRead:
        """Sparse-update a glossary term (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        row = await self._service.update(term_id, body)
        return GlossaryTermRead.model_validate(row)

    @delete_mapping("/{term_id}", status_code=204)
    async def delete(self, http_request: Request, term_id: PathVar[uuid.UUID]) -> Response:
        """Hard-delete a glossary term (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        term = await self._service.get(term_id)
        if term is None:
            raise ResourceNotFound(f"glossary term {term_id!r} not found")
        await self._service.delete(term_id)
        return Response(status_code=204)
