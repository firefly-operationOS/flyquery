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

"""Agent-tier examples controller.

``/api/v1/agent/examples`` — subset of the user-tier examples surface,
gated by agent token scopes:

* ``POST /api/v1/agent/examples`` — ``flyquery.examples:author``
* ``GET  /api/v1/agent/examples`` — ``flyquery.examples:read``
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import Body, QueryParam, Valid, get_mapping, post_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.core.services.examples.examples_service import ExamplesService
from flyquery.interfaces.examples import ExampleCreate, ExampleRead
from flyquery.interfaces.pagination import Paginated
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    IdempotencyStore,
    tenant_context_from_request,
)
from flyquery.web.idempotent_handler import replay_dedup

_SCOPE_EXAMPLES_AUTHOR = "flyquery.examples:author"
_SCOPE_EXAMPLES_READ = "flyquery.examples:read"


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


@rest_controller
@request_mapping("/api/v1/agent")
class AgentExamplesController:
    """Agent-tier mirror of the examples surface.

    POST requires ``flyquery.examples:author`` scope.
    GET  requires ``flyquery.examples:read`` scope.

    :param examples_service: service over flyquery_examples
    :param agent_token_service: verifies the agent token + scope
    """

    def __init__(
        self,
        examples_service: ExamplesService,
        agent_token_service: AgentTokenService,
        idempotency_store: IdempotencyStore,
    ) -> None:
        self._service = examples_service
        self._token_service = agent_token_service
        self._idempotency_store = idempotency_store

    async def _verify(self, http_request: Request, scope: str) -> None:
        """Verify X-Agent-Token with the given scope.

        :param http_request: Starlette request
        :param scope: required scope string
        :raises MissingAgentToken: when header is absent
        """
        token = http_request.headers.get(HEADER_AGENT_TOKEN)
        if not token:
            raise MissingAgentToken("X-Agent-Token header is required for /api/v1/agent/* routes.")
        ctx = tenant_context_from_request(http_request)
        await self._token_service.verify(
            token,
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.workspace_id,
            scope=scope,
        )

    @post_mapping("/examples", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[ExampleCreate]],
    ) -> ExampleRead:
        """Create an example (agent-tier — source=AGENT_LEARNED, quality=PROPOSED).

        Replay-dedup'd via ``Idempotency-Key`` (required). Without
        this gate an agent retrying a network blip would persist
        duplicate (question, SQL) PROPOSED rows that an operator
        would then have to manually reject.
        """
        await self._verify(http_request, _SCOPE_EXAMPLES_AUTHOR)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))

        async def _do_create() -> ExampleRead:
            row = await self._service.create(
                ctx.tenant_id,
                ws,
                body,
                source="AGENT_LEARNED",
                quality="PROPOSED",
                actor=ctx.actor or "agent",
            )
            return ExampleRead.model_validate(row)

        return await replay_dedup(
            request=http_request,
            store=self._idempotency_store,
            tenant_id=ctx.tenant_id,
            route="POST /api/v1/agent/examples",
            handler=_do_create,
            status_code=201,
            require_key=True,
        )

    @get_mapping("/examples")
    async def list_examples(
        self,
        http_request: Request,
        quality: QueryParam[str] = None,
        dataset_id: QueryParam[uuid.UUID] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[ExampleRead]:
        """List examples for the caller's workspace (agent-tier).

        :param http_request: Starlette request
        :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED)
        :param dataset_id: optional dataset filter
        :param limit: page size (default 100)
        :param offset: starting offset (default 0)
        :return: Paginated[ExampleRead]
        """
        await self._verify(http_request, _SCOPE_EXAMPLES_READ)
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(str(ctx.workspace_id))
        rows = await self._service.list(
            ctx.tenant_id,
            ws,
            quality=quality,
            dataset_id=dataset_id,
        )
        items = [ExampleRead.model_validate(r) for r in rows]
        sliced = items[offset : offset + limit]
        return Paginated.of(sliced, total=len(items), limit=limit, offset=offset)
