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

"""Agent-tier semantic metrics controller.

``/api/v1/agent/semantic/metrics`` — mirror of the user-tier metrics surface,
gated by agent token scopes:

* writes (create/update/publish/retire) — ``flyquery.semantic:author``
* reads (list/get/history) — ``flyquery.semantic:read``
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
from flyquery.core.services.semantic.semantic_service import SemanticService
from flyquery.interfaces.pagination import Paginated
from flyquery.interfaces.semantic import (
    SemanticMetricCreate,
    SemanticMetricRead,
    SemanticMetricUpdate,
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
@request_mapping("/api/v1/agent/semantic/metrics")
class AgentSemanticMetricsController:
    """Agent-tier mirror of ``/api/v1/semantic/metrics``."""

    def __init__(
        self,
        service: SemanticService,
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
        self, http_request: Request, body: Valid[Body[SemanticMetricCreate]]
    ) -> SemanticMetricRead:
        """Create a metric in DRAFT (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        row = await self._service.create(ctx.tenant_id, ws, body, actor=ctx.actor or "agent")
        return SemanticMetricRead.model_validate(row)

    @get_mapping("")
    async def list_metrics(
        self,
        http_request: Request,
        dataset_id: QueryParam[uuid.UUID] = None,
        status: QueryParam[str] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[SemanticMetricRead]:
        """List metrics for the caller's workspace (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        rows = await self._service.list(ctx.tenant_id, ws, dataset_id=dataset_id, status=status)
        items = [SemanticMetricRead.model_validate(r) for r in rows]
        sliced = items[offset : offset + limit]
        return Paginated.of(sliced, total=len(items), limit=limit, offset=offset)

    @get_mapping("/{metric_id}")
    async def get_metric(self, http_request: Request, metric_id: PathVar[uuid.UUID]) -> SemanticMetricRead:
        """Fetch a single metric (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.get(ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), metric_id)
        if row is None:
            raise ResourceNotFound(f"metric {metric_id!r} not found")
        return SemanticMetricRead.model_validate(row)

    @put_mapping("/{metric_id}")
    async def update(
        self,
        http_request: Request,
        metric_id: PathVar[uuid.UUID],
        body: Valid[Body[SemanticMetricUpdate]],
    ) -> SemanticMetricRead:
        """Sparse-update a metric (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.update(
            ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), metric_id, body, actor=ctx.actor or "agent"
        )
        return SemanticMetricRead.model_validate(row)

    @post_mapping("/{metric_id}:publish")
    async def publish(self, http_request: Request, metric_id: PathVar[uuid.UUID]) -> SemanticMetricRead:
        """Publish a metric (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.publish(ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), metric_id)
        return SemanticMetricRead.model_validate(row)

    @post_mapping("/{metric_id}:retire")
    async def retire(self, http_request: Request, metric_id: PathVar[uuid.UUID]) -> SemanticMetricRead:
        """Retire a metric (agent-tier)."""
        await self._verify(http_request, _SCOPE_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        row = await self._service.retire(ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), metric_id)
        return SemanticMetricRead.model_validate(row)

    @get_mapping("/{metric_id}/history")
    async def history(
        self, http_request: Request, metric_id: PathVar[uuid.UUID]
    ) -> Paginated[SemanticVersionRead]:
        """Return version history for a metric (agent-tier)."""
        await self._verify(http_request, _SCOPE_READ)
        ctx = tenant_context_from_request(http_request)
        rows = await self._service.list_history(ctx.tenant_id, uuid.UUID(str(ctx.workspace_id)), metric_id)
        items = [SemanticVersionRead.model_validate(r) for r in rows]
        return Paginated.of(items, total=len(items))
