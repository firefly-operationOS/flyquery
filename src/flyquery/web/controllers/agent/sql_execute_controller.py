# Copyright 2026 Firefly Software Solutions Inc
"""Agent-tier SQL execute controller.

``/api/v1/agent/sql:execute`` — same as the user-tier ``/api/v1/sql:execute``
but requires a valid ``X-Agent-Token`` with ``flyquery.sql:execute`` scope.

Path conventions:
* ``POST /api/v1/agent/sql:execute``        -- sync execution
* ``POST /api/v1/agent/sql:execute/stream`` -- SSE stream
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import Body, Valid, post_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import StreamingResponse

from flyquery.config import FlyquerySettings
from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.core.services.query.query_repository import QueryRepository
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.tables.schema_snapshot_repository import (
    SchemaSnapshotRepository,
)
from flyquery.core.services.tables.table_repository import TableRepository
from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.sql_execute import SqlExecuteRequest, SqlExecuteResponse
from flyquery.web.controllers.sql_execute_controller import (
    SqlExecuteController as _UserSqlExecuteController,
)
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    IdempotencyStore,
    InvalidRequest,
    tenant_context_from_request,
)
from flyquery.web.idempotent_handler import replay_dedup

_SCOPE_SQL_EXECUTE = "flyquery.sql:execute"


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


def _parse_workspace_id(s: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(s))
    except (ValueError, AttributeError) as exc:
        raise InvalidRequest(f"workspace_id {s!r} is not a valid UUID") from exc


@rest_controller
@request_mapping("/api/v1/agent")
class AgentSqlExecuteController:
    """Agent-tier mirror of :class:`SqlExecuteController`.

    Requires ``X-Agent-Token`` with ``flyquery.sql:execute`` scope.
    Delegates to the same execution pipeline as the user-tier controller.

    :param settings: application settings
    :param session: async session factory
    :param object_store: blob store for result Parquet
    :param query_repository: repository for flyquery_queries
    :param workspace_service: checks allow_direct_sql workspace flag
    :param agent_token_service: verifies the agent token + scope
    """

    def __init__(
        self,
        settings: FlyquerySettings,
        session: async_sessionmaker[AsyncSession],
        object_store: ObjectStore,
        query_repository: QueryRepository,
        workspace_service: WorkspaceService,
        table_repository: TableRepository,
        schema_snapshot_repository: SchemaSnapshotRepository,
        agent_token_service: AgentTokenService,
        idempotency_store: IdempotencyStore,
    ) -> None:
        self._settings = settings
        self._session_factory = session
        self._object_store = object_store
        self._query_repo = query_repository
        self._workspace_service = workspace_service
        self._token_service = agent_token_service
        self._idempotency_store = idempotency_store

        # Reuse the user-tier controller's pipeline logic.
        self._delegate = _UserSqlExecuteController(
            settings=settings,
            session=session,
            object_store=object_store,
            query_repository=query_repository,
            workspace_service=workspace_service,
            table_repository=table_repository,
            schema_snapshot_repository=schema_snapshot_repository,
        )

    async def _verify(self, http_request: Request) -> None:
        """Verify X-Agent-Token with flyquery.sql:execute scope.

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
            scope=_SCOPE_SQL_EXECUTE,
        )

    @post_mapping("/sql:execute")
    async def execute(
        self,
        http_request: Request,
        body: Valid[Body[SqlExecuteRequest]],
    ) -> SqlExecuteResponse:
        """Execute SQL directly (agent-tier).

        Replay-dedup'd via ``Idempotency-Key`` -- required, because a
        retried direct-SQL execution would re-scan the dataset and
        burn query budget for no caller benefit.
        """
        await self._verify(http_request)
        ctx = tenant_context_from_request(http_request)

        async def _do_execute() -> SqlExecuteResponse:
            return await self._delegate.execute(http_request, body)

        return await replay_dedup(
            request=http_request,
            store=self._idempotency_store,
            tenant_id=ctx.tenant_id,
            route="POST /api/v1/agent/sql:execute",
            handler=_do_execute,
            status_code=200,
            require_key=True,
        )

    @post_mapping("/sql:execute/stream")
    async def execute_stream(
        self,
        http_request: Request,
        body: Valid[Body[SqlExecuteRequest]],
    ) -> StreamingResponse:
        """Execute SQL as SSE stream (agent-tier).

        :param http_request: Starlette request
        :param body: validated SqlExecuteRequest
        :return: StreamingResponse with text/event-stream
        """
        await self._verify(http_request)
        return await self._delegate.execute_stream(http_request, body)
