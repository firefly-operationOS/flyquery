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

"""Agent-tier relations read mirror.

``/api/v1/agent/datasets/{dataset_id}/relations`` -- agent-token-gated
read mirror of the user-tier relations list. Approve / reject remain
operator-gated on the user surface; agents only see what's there.

Path conventions and scopes:
* ``GET /api/v1/agent/datasets/{dataset_id}/relations`` -- Scope: ``flyquery.relations:read``.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import PathVar, QueryParam, get_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.interfaces.pagination import Paginated
from flyquery.interfaces.relations import RelationRead
from flyquery.web.controllers.relations_controller import (
    RelationsController as _UserRelationsController,
)
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    tenant_context_from_request,
)

_SCOPE_RELATIONS_READ = "flyquery.relations:read"


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


@rest_controller
@request_mapping("/api/v1/agent")
class AgentRelationsController:
    """Agent-tier read mirror of :class:`RelationsController`."""

    def __init__(
        self,
        user_relations_controller: _UserRelationsController,
        agent_token_service: AgentTokenService,
    ) -> None:
        self._delegate = user_relations_controller
        self._token_service = agent_token_service

    async def _verify(self, http_request: Request) -> None:
        token = http_request.headers.get(HEADER_AGENT_TOKEN)
        if not token:
            raise MissingAgentToken("X-Agent-Token header is required for /api/v1/agent/* routes.")
        ctx = tenant_context_from_request(http_request)
        await self._token_service.verify(
            token,
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.workspace_id,
            scope=_SCOPE_RELATIONS_READ,
        )

    @get_mapping("/datasets/{dataset_id}/relations")
    async def list_relations(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
        status: QueryParam[str] = None,
    ) -> Paginated[RelationRead]:
        await self._verify(http_request)
        return await self._delegate.list_relations(http_request, dataset_id, status=status)


__all__ = ["AgentRelationsController"]
