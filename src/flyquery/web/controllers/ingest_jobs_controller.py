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

"""IngestJobs controller.

POST   /api/v1/ingest-jobs                        -- start REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS
GET    /api/v1/ingest-jobs                        -- paginated list + filters
GET    /api/v1/ingest-jobs/{id}                   -- single job
GET    /api/v1/ingest-jobs/{id}/stream            -- SSE event stream
GET    /api/v1/ingest-jobs/{id}/events            -- paginated event ledger
POST   /api/v1/ingest-jobs/{id}:cancel            -- cooperative cancel
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

from pyfly.container import rest_controller
from pyfly.web import Body, PathVar, Valid, get_mapping, post_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import StreamingResponse

from flyquery.core.services.callbacks.callback_repository import CallbackOutboxRepository
from flyquery.core.services.ingest_jobs.ingest_job_repository import IngestJobRepository
from flyquery.core.services.ingest_jobs.ingest_job_service import IngestJobService
from flyquery.interfaces.ingest_jobs import (
    CallbackDeliveryListResponse,
    CallbackDeliveryRead,
    CancelResponse,
    IngestEventListResponse,
    IngestJobCreate,
    IngestJobListResponse,
    IngestJobRead,
)
from flyquery.web.conventions import InvalidRequest, ResourceNotFound, tenant_context_from_request

logger = logging.getLogger(__name__)

# SSE polling interval (ms) — low enough for interactive demos
_SSE_POLL_MS = 250
# Sentinel stages that close the SSE stream
_TERMINAL_STAGES = frozenset({"final", "error"})
# Hard timeout for SSE streams (seconds) to prevent leaking connections
_SSE_MAX_SECONDS = 600


@rest_controller
@request_mapping("/api/v1/ingest-jobs")
class IngestJobsController:
    """REST adapter for ingest job lifecycle + SSE streaming."""

    def __init__(
        self,
        ingest_job_service: IngestJobService,
        ingest_job_repository: IngestJobRepository,
        callback_outbox_repository: CallbackOutboxRepository,
        session: async_sessionmaker[AsyncSession],
    ) -> None:
        self._service = ingest_job_service
        self._repo = ingest_job_repository
        self._callbacks = callback_outbox_repository
        self._session_factory = session

    @post_mapping("", status_code=201)
    async def create_job(
        self,
        http_request: Request,
        body: Valid[Body[IngestJobCreate]],
    ) -> IngestJobRead:
        """Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).

        ``body`` is declared as ``Valid[Body[IngestJobCreate]]`` (not
        read from ``http_request.json()``) so FastAPI / pyfly publish
        the request schema into ``openapi.json`` -- the older manual
        decode kept ``IngestJobCreate`` (and now the nested
        ``CallbackConfig`` field) invisible to SDK generators.
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        try:
            return await self._service.create_job(
                tenant_id=ctx.tenant_id,
                workspace_id=workspace_id,
                body=body,
                session_factory=self._session_factory,
            )
        except ValueError as exc:
            raise InvalidRequest(str(exc)) from exc

    @get_mapping("")
    async def list_jobs(self, http_request: Request) -> IngestJobListResponse:
        """List ingest jobs with optional filters."""
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)
        params = http_request.query_params

        statuses = _split_param(params.get("status"))
        job_kinds = _split_param(params.get("kind"))
        dataset_id = _opt_uuid(params.get("dataset_id"))
        table_id = _opt_uuid(params.get("table_id"))
        limit = min(int(params.get("limit", "50")), 200)
        offset = int(params.get("offset", "0"))

        return await self._service.list_jobs(
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            statuses=statuses,
            job_kinds=job_kinds,
            dataset_id=dataset_id,
            table_id=table_id,
            limit=limit,
            offset=offset,
        )

    @get_mapping("/{job_id}")
    async def get_job(self, http_request: Request, job_id: PathVar[uuid.UUID]) -> IngestJobRead:
        """Get a single ingest job."""
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)
        job = await self._service.get_job(job_id, tenant_id=ctx.tenant_id, workspace_id=workspace_id)
        if job is None:
            raise ResourceNotFound(f"ingest job {job_id!r} not found")
        return job

    @get_mapping("/{job_id}/callbacks")
    async def list_callbacks(
        self,
        http_request: Request,
        job_id: PathVar[uuid.UUID],
    ) -> CallbackDeliveryListResponse:
        """Audit log of webhook delivery attempts for this job.

        Returns one row per outbox entry: the URL we posted to, the
        terminal event we tried to deliver (``ingest.succeeded`` or
        ``ingest.failed``), the current status (``PENDING``,
        ``DELIVERED``, ``FAILED``, ``DEAD``), the attempt count + the
        last HTTP status code / error, and the next scheduled retry.

        Callers SHOULD poll this endpoint after a webhook outage to
        confirm that the in-flight retry storm has cleared (DEAD rows
        require manual replay or a follow-up REPARSE job).
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        # Verify job exists -- so we 404 instead of returning an empty list
        # for a wrong job_id (silent empty results are a classic source of
        # client-side confusion).
        job = await self._service.get_job(job_id, tenant_id=ctx.tenant_id, workspace_id=workspace_id)
        if job is None:
            raise ResourceNotFound(f"ingest job {job_id!r} not found")

        params = http_request.query_params
        statuses = _split_param(params.get("status"))
        limit = min(int(params.get("limit", "50")), 200)
        offset = int(params.get("offset", "0"))

        items, total = await self._callbacks.list_for_job(
            job_id,
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            statuses=statuses,
            limit=limit,
            offset=offset,
        )
        reads = [
            CallbackDeliveryRead(
                id=row["id"],
                ingest_job_id=row["ingest_job_id"],
                callback_url=row["callback_url"],
                event_type=row["event_type"],
                status=row["status"],
                attempts=row["attempts"],
                last_attempt_at=row["last_attempt_at"],
                last_status_code=row["last_status_code"],
                last_error=row["last_error"],
                next_attempt_at=row["next_attempt_at"],
                created_at=row["created_at"],
                finished_at=row["finished_at"],
            )
            for row in items
        ]
        return CallbackDeliveryListResponse(items=reads, total=total, limit=limit, offset=offset)

    @get_mapping("/{job_id}/events")
    async def list_events(self, http_request: Request, job_id: PathVar[uuid.UUID]) -> IngestEventListResponse:
        """Paginated event ledger for a job."""
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)
        params = http_request.query_params
        after_id = _opt_int(params.get("after_id"))
        limit = min(int(params.get("limit", "200")), 500)
        offset = int(params.get("offset", "0"))

        # Verify job exists
        job = await self._service.get_job(job_id, tenant_id=ctx.tenant_id, workspace_id=workspace_id)
        if job is None:
            raise ResourceNotFound(f"ingest job {job_id!r} not found")

        return await self._service.list_events(
            job_id,
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            after_id=after_id,
            limit=limit,
            offset=offset,
        )

    @get_mapping("/{job_id}/stream")
    async def stream_job(self, http_request: Request, job_id: PathVar[uuid.UUID]) -> StreamingResponse:
        """SSE stream for real-time job progress.

        Mirrors canon's ingest_jobs_controller SSE pattern:
        1. Emit all existing events for the job (catch-up replay)
        2. Poll for new events every 250ms
        3. Close stream when a ``final`` or ``error`` event is emitted
        4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        # Verify the job exists before opening the stream
        job = await self._service.get_job(job_id, tenant_id=ctx.tenant_id, workspace_id=workspace_id)
        if job is None:
            raise ResourceNotFound(f"ingest job {job_id!r} not found")

        tenant_id = ctx.tenant_id

        async def _event_generator() -> AsyncIterator[bytes]:
            last_id = 0
            deadline = asyncio.get_event_loop().time() + _SSE_MAX_SECONDS
            terminal_seen = False

            # Send a keep-alive comment immediately so the client knows
            # the stream is open before any events arrive.
            yield b": connected\n\n"

            while not terminal_seen:
                if asyncio.get_event_loop().time() > deadline:
                    yield _sse_frame("timeout", {"reason": "SSE stream max duration reached"})
                    break

                # Poll for new events since last_id
                new_events = await _repo_list_events_since(
                    repo=self._repo,
                    job_id=job_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    after_id=last_id,
                )

                for ev in new_events:
                    last_id = ev["id"]
                    stage = ev["stage"]
                    data = {
                        "id": ev["id"],
                        "stage": stage,
                        "status": ev["status"],
                        "message": ev.get("message"),
                        "payload": ev.get("payload_json") or {},
                    }
                    yield _sse_frame(stage, data)

                    if stage in _TERMINAL_STAGES:
                        terminal_seen = True
                        break

                if not terminal_seen:
                    await asyncio.sleep(_SSE_POLL_MS / 1000.0)

        return StreamingResponse(
            _event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    @post_mapping("/{job_id}:cancel", status_code=200)
    async def cancel_job(self, http_request: Request, job_id: PathVar[uuid.UUID]) -> CancelResponse:
        """Cooperatively cancel a job (idempotent for terminal jobs)."""
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)
        result = await self._service.cancel_job(job_id, tenant_id=ctx.tenant_id, workspace_id=workspace_id)
        if result is None:
            raise ResourceNotFound(f"ingest job {job_id!r} not found")
        return result


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------


def _sse_frame(event_type: str, data: Any) -> bytes:
    """Format one SSE frame: ``event: <type>\\ndata: <json>\\n\\n``."""
    data_json = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {data_json}\n\n".encode()


async def _repo_list_events_since(
    *,
    repo: IngestJobRepository,
    job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    after_id: int,
) -> list[dict[str, Any]]:
    return await repo.list_events_since(
        job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        after_id=after_id,
    )


# ---------------------------------------------------------------------------
# Parameter helpers
# ---------------------------------------------------------------------------


def _parse_workspace_id(workspace_id_str: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(workspace_id_str))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"workspace_id header {workspace_id_str!r} is not a valid UUID") from exc


def _split_param(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def _opt_uuid(value: str | None) -> uuid.UUID | None:
    if not value:
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


def _opt_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
