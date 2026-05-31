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

"""``require_agent_token`` -- per-route dep for /api/v1/agent/* endpoints.

Layered on top of ``flyquery.web.conventions.require_tenant_context``:
the canonical header parser produces a ``TenantContext``; this dep
additionally verifies ``X-Agent-Token`` against the agent_tokens
table and overwrites ``ctx.actor`` with the verified token's actor
string.

The route's ``scope`` argument (e.g. ``"agent.discoveries:validate"``)
is matched against the token's ``scopes_json`` list (``"*"``
matches everything).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Header

from flyquery.core.services.auth.agent_token_service import (
    AgentTokenService,
)
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    HEADER_AUTHORIZATION,
    HEADER_CORRELATION_ID,
    HEADER_TENANT_ID,
    HEADER_WORKSPACE_ID,
    FireflyHTTPException,
    TenantContext,
)


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


def require_agent_token(*, scope: str, service: Callable[[], AgentTokenService]) -> Callable[..., Any]:
    """Return a FastAPI dep factory for an agent-tier route.

    ``scope`` is the per-route scope string the token must carry
    (e.g. ``"agent.discoveries:validate"``). ``service`` is a
    zero-arg callable returning the (DI-injected) ``AgentTokenService``.
    Using a factory avoids tying the dep to a global singleton -- the
    bean factory + pyfly's DI provide the actual service at call
    time.

    Usage::

        from flyquery.core.configuration import get_agent_token_service

        @router.post("/agent/discoveries:validate")
        async def _validate(
            ctx: TenantContext = Depends(
                require_agent_token(
                    scope="agent.discoveries:validate",
                    service=get_agent_token_service,
                ),
            ),
        ) -> ValidationResponse:
            ...
    """

    async def _dep(
        x_tenant_id: str | None = Header(default=None, alias=HEADER_TENANT_ID),
        x_workspace_id: str | None = Header(default=None, alias=HEADER_WORKSPACE_ID),
        x_correlation_id: str | None = Header(default=None, alias=HEADER_CORRELATION_ID),
        authorization: str | None = Header(default=None, alias=HEADER_AUTHORIZATION),
        x_agent_token: str | None = Header(default=None, alias=HEADER_AGENT_TOKEN),
    ) -> TenantContext:
        if not x_agent_token:
            raise MissingAgentToken("X-Agent-Token header is required for /api/v1/agent/* routes.")
        # Build the canonical TenantContext from headers using the same
        # validators the conventions dep uses. Lazy import to avoid a
        # circular import at module load.
        from flyquery.web.conventions.deps import tenant_context_from_headers

        ctx = tenant_context_from_headers(
            x_tenant_id=x_tenant_id,
            x_workspace_id=x_workspace_id,
            x_correlation_id=x_correlation_id,
            authorization=authorization,
            x_agent_token=x_agent_token,
        )
        verified = await service().verify(
            x_agent_token,
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.workspace_id,
            scope=scope,
        )
        # Overwrite actor with the verified agent actor (more authoritative
        # than the prefix-only one the conventions dep would produce).
        return TenantContext(
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.workspace_id,
            actor=verified.actor,
            correlation_id=ctx.correlation_id,
        )

    return _dep
