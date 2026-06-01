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

"""Agent-tier semantic dimensions controller.

``/api/v1/agent/semantic/dimensions`` — mirror of the user-tier dimensions
surface, gated by ``flyquery.semantic:author`` (writes) /
``flyquery.semantic:read`` (reads).
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

from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.core.services.semantic.semantic_dimensions_service import (
    SemanticDimensionsService,
)
from flyquery.interfaces.pagination import Paginated
from flyquery.interfaces.semantic import (
    SemanticDimensionCreate,
    SemanticDimensionRead,
    SemanticDimensionUpdate,
    SemanticVersionRead,
)
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
@request_mapping("/api/v1/agent/semantic/dimensions")
class AgentSemanticDimensionsController:
    """Agent-tier mirror of ``/api/v1/semantic/dimensions``."""

    def __init__(
        self,
        service: SemanticDimensionsService,
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
        self, http_request: Request, body: Valid[Body[SemanticDimensionCreate]]
    ) -> SemanticDimensionRead:
        """Create a dimension in DRAFT (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        row = await self._service.create(ctx.tenant_id, ws, body, actor=ctx.actor or "agent")
        return SemanticDimensionRead.model_validate(row)

    @get_mapping("")
    async def list_dimensions(
        self,
        http_request: Request,
        dataset_id: QueryParam[uuid.UUID] = None,
        status: QueryParam[str] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[SemanticDimensionRead]:
        """List dimensions for the caller's workspace (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        rows = await self._service.list(ctx.tenant_id, ws, dataset_id=dataset_id, status=status)
        items = [SemanticDimensionRead.model_validate(r) for r in rows]
        sliced = items[offset : offset + limit]
        return Paginated.of(sliced, total=len(items), limit=limit, offset=offset)

    @get_mapping("/{dimension_id}")
    async def get_dimension(
        self, http_request: Request, dimension_id: PathVar[uuid.UUID]
    ) -> SemanticDimensionRead:
        """Fetch a single dimension (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.get(ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), dimension_id)
        if row is None:
            raise ResourceNotFound(f"dimension {dimension_id!r} not found")
        return SemanticDimensionRead.model_validate(row)

    @put_mapping("/{dimension_id}")
    async def update(
        self,
        http_request: Request,
        dimension_id: PathVar[uuid.UUID],
        body: Valid[Body[SemanticDimensionUpdate]],
    ) -> SemanticDimensionRead:
        """Sparse-update a dimension (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.update(
            ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), dimension_id, body, actor=ctx.actor or "agent"
        )
        return SemanticDimensionRead.model_validate(row)

    @post_mapping("/{dimension_id}:publish")
    async def publish(
        self, http_request: Request, dimension_id: PathVar[uuid.UUID]
    ) -> SemanticDimensionRead:
        """Publish a dimension (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.publish(
            ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), dimension_id
        )
        return SemanticDimensionRead.model_validate(row)

    @post_mapping("/{dimension_id}:retire")
    async def retire(
        self, http_request: Request, dimension_id: PathVar[uuid.UUID]
    ) -> SemanticDimensionRead:
        """Retire a dimension (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.retire(
            ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), dimension_id
        )
        return SemanticDimensionRead.model_validate(row)

    @get_mapping("/{dimension_id}/history")
    async def history(
        self, http_request: Request, dimension_id: PathVar[uuid.UUID]
    ) -> Paginated[SemanticVersionRead]:
        """Return version history for a dimension (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        rows = await self._service.list_history(
            ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), dimension_id
        )
        items = [SemanticVersionRead.model_validate(r) for r in rows]
        return Paginated.of(items, total=len(items))
