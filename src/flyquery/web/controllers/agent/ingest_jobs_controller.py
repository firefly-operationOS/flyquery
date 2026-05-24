# Copyright 2026 Firefly Software Solutions Inc
"""Agent-tier ingest-jobs controller.

``/api/v1/agent/ingest-jobs`` -- agent-token-gated mirror of the
user-tier ingest-jobs surface. Until this surface existed, agents that
kicked off uploads (or schedulers running on the agent surface) had
no way to monitor the resulting jobs -- they only saw the 201 from the
file upload and were blind to the async pipeline state.

Path conventions and scopes:
* ``POST /api/v1/agent/ingest-jobs``              -- start (201). Scope: ``flyquery.ingest:run``.
* ``GET  /api/v1/agent/ingest-jobs``              -- list + filters. Scope: ``flyquery.ingest:read``.
* ``GET  /api/v1/agent/ingest-jobs/{id}``         -- single job. Scope: ``flyquery.ingest:read``.
* ``GET  /api/v1/agent/ingest-jobs/{id}/events``  -- event ledger. Scope: ``flyquery.ingest:read``.
* ``GET  /api/v1/agent/ingest-jobs/{id}/stream``  -- SSE progress. Scope: ``flyquery.ingest:read``.
* ``POST /api/v1/agent/ingest-jobs/{id}:cancel``  -- cancel. Scope: ``flyquery.ingest:run``.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import PathVar, get_mapping, post_mapping, request_mapping
from starlette.requests import Request
from starlette.responses import StreamingResponse

from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.interfaces.ingest_jobs import (
    CancelResponse,
    IngestEventListResponse,
    IngestJobListResponse,
    IngestJobRead,
)
from flyquery.web.controllers.ingest_jobs_controller import (
    IngestJobsController as _UserIngestJobsController,
)
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    IdempotencyStore,
    tenant_context_from_request,
)
from flyquery.web.idempotent_handler import replay_dedup

_SCOPE_INGEST_READ = "flyquery.ingest:read"
_SCOPE_INGEST_RUN = "flyquery.ingest:run"


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


@rest_controller
@request_mapping("/api/v1/agent")
class AgentIngestJobsController:
    """Agent-tier mirror of :class:`IngestJobsController`.

    Delegates by composition (matches :class:`AgentSqlExecuteController`)
    and re-applies token + scope verification at the agent boundary.
    """

    def __init__(
        self,
        user_ingest_jobs_controller: _UserIngestJobsController,
        agent_token_service: AgentTokenService,
        idempotency_store: IdempotencyStore,
    ) -> None:
        self._delegate = user_ingest_jobs_controller
        self._token_service = agent_token_service
        self._idempotency_store = idempotency_store

    async def _verify(self, http_request: Request, scope: str) -> None:
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

    @post_mapping("/ingest-jobs", status_code=201)
    async def create_job(self, http_request: Request):
        """Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...)."""
        await self._verify(http_request, _SCOPE_INGEST_RUN)
        ctx = tenant_context_from_request(http_request)

        async def _do_create() -> IngestJobRead:
            return await self._delegate.create_job(http_request)

        return await replay_dedup(
            request=http_request,
            store=self._idempotency_store,
            tenant_id=ctx.tenant_id,
            route="POST /api/v1/agent/ingest-jobs",
            handler=_do_create,
            status_code=201,
            require_key=True,
        )

    @get_mapping("/ingest-jobs")
    async def list_jobs(self, http_request: Request) -> IngestJobListResponse:
        await self._verify(http_request, _SCOPE_INGEST_READ)
        return await self._delegate.list_jobs(http_request)

    @get_mapping("/ingest-jobs/{job_id}")
    async def get_job(
        self,
        http_request: Request,
        job_id: PathVar[uuid.UUID],
    ) -> IngestJobRead:
        await self._verify(http_request, _SCOPE_INGEST_READ)
        return await self._delegate.get_job(http_request, job_id)

    @get_mapping("/ingest-jobs/{job_id}/events")
    async def list_events(
        self,
        http_request: Request,
        job_id: PathVar[uuid.UUID],
    ) -> IngestEventListResponse:
        await self._verify(http_request, _SCOPE_INGEST_READ)
        return await self._delegate.list_events(http_request, job_id)

    @get_mapping("/ingest-jobs/{job_id}/stream")
    async def stream_job(
        self,
        http_request: Request,
        job_id: PathVar[uuid.UUID],
    ) -> StreamingResponse:
        """SSE progress stream. The underlying delegate handles framing,
        terminal-stage close, and SSE max duration."""
        await self._verify(http_request, _SCOPE_INGEST_READ)
        return await self._delegate.stream_job(http_request, job_id)

    @post_mapping("/ingest-jobs/{job_id}:cancel", status_code=200)
    async def cancel_job(
        self,
        http_request: Request,
        job_id: PathVar[uuid.UUID],
    ) -> CancelResponse:
        """Cooperatively cancel a running job.

        Replay-dedup'd via ``Idempotency-Key`` (required). The
        underlying service is itself idempotent on terminal jobs, but
        we still cache the response so a retried cancel returns the
        same wire envelope (same ``status`` field).
        """
        await self._verify(http_request, _SCOPE_INGEST_RUN)
        ctx = tenant_context_from_request(http_request)

        async def _do_cancel() -> CancelResponse:
            return await self._delegate.cancel_job(http_request, job_id)

        return await replay_dedup(
            request=http_request,
            store=self._idempotency_store,
            tenant_id=ctx.tenant_id,
            route=f"POST /api/v1/agent/ingest-jobs/{job_id}:cancel",
            handler=_do_cancel,
            status_code=200,
            require_key=True,
        )


__all__ = ["AgentIngestJobsController"]
