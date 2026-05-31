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

"""Version identity endpoints.

* ``GET /api/v1/version``       -- user-tier (public), no auth required.
* ``GET /api/v1/agent/version`` -- agent-tier, requires X-Agent-Token with
  ``flyquery.audit:read`` scope.
"""

from __future__ import annotations

from pyfly.container import rest_controller
from pyfly.web import get_mapping, request_mapping
from starlette.requests import Request

from flyquery import __version__
from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    tenant_context_from_request,
)


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


@rest_controller
@request_mapping("/api/v1")
class VersionController:
    """Service identity -- user-tier, no auth required."""

    @get_mapping("/version")
    async def version(self) -> dict:
        """Return service name + CalVer version tag."""
        return {"name": "flyquery", "version": __version__}


@rest_controller
@request_mapping("/api/v1/agent")
class AgentVersionController:
    """Service identity -- agent-tier, gated by ``flyquery.audit:read`` scope."""

    def __init__(self, agent_token_service: AgentTokenService) -> None:
        self._service = agent_token_service

    @get_mapping("/version")
    async def version(self, http_request: Request) -> dict:
        """Return service name + CalVer version tag.

        Requires a valid ``X-Agent-Token`` with ``flyquery.audit:read`` scope.
        Missing or invalid tokens return 401 / 403 respectively.
        """
        token = http_request.headers.get(HEADER_AGENT_TOKEN)
        if not token:
            raise MissingAgentToken("X-Agent-Token header is required for /api/v1/agent/* routes.")
        ctx = tenant_context_from_request(http_request)
        await self._service.verify(
            token,
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.workspace_id,
            scope="flyquery.audit:read",
        )
        return {"name": "flyquery", "version": __version__}


__all__ = ["AgentVersionController", "VersionController"]
