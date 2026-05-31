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

"""Typed per-stage emission helpers for flyquery_ingest_events.

Each stage in the ingestion pipeline calls one of the helpers here to
emit a consistent SSE-compatible event row. The shape:

    {stage, status, message, payload_json}

mirrors canon's ingest_job_events contract so the SSE endpoint can
replay events with the same framing.

Stages emitted by the ingestion pipeline:

    queued        — job created, waiting for worker
    running       — worker claimed the job
    received      — stage 1 complete (receive)
    parsed        — stage 2 complete (parse → Parquet)
    reconciled    — stage 3 complete (snapshot + diff)
    sampled       — stage 4 complete (sample; Phase D)
    profiled      — stage 5 complete (profile; Phase D)
    relations     — stage 6 complete (heuristic + agent; Phase E)
    described     — stage 7 complete (DescribeAgent; Phase E)
    pii_tagged    — stage 8 complete (PII tag; Phase D)
    embedded      — stage 9 complete (embed + tsvector)
    published     — stage 10 complete (atomic READY swap)
    final         — terminal success sentinel (SSE close signal)
    error         — terminal failure sentinel (SSE close signal)
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.services.ingestion.ingest_event_repository import _insert_event


async def emit_event(
    *,
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    stage: str,
    status: str,
    message: str | None = None,
    payload: dict[str, Any] | None = None,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Write one progress event row to flyquery_ingest_events.

    Swallows DB errors so a broken event-write never aborts the main
    pipeline stage. The job itself is the durable truth; events are
    best-effort audit/SSE trail.

    Delegates to :func:`_insert_event` in
    :mod:`flyquery.core.services.ingestion.ingest_event_repository`
    so the SQL + JSON + error policy lives in one place.
    """
    await _insert_event(
        session_factory=session_factory,
        ingest_job_id=ingest_job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        stage=stage,
        status=status,
        message=message,
        payload=payload,
    )


async def emit_queued(
    *,
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    job_kind: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await emit_event(
        ingest_job_id=ingest_job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        stage="queued",
        status="ok",
        message=f"job queued kind={job_kind}",
        payload={"job_kind": job_kind},
        session_factory=session_factory,
    )


async def emit_running(
    *,
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await emit_event(
        ingest_job_id=ingest_job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        stage="running",
        status="ok",
        message="worker claimed job",
        session_factory=session_factory,
    )


async def emit_stage(
    *,
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    stage: str,
    message: str | None = None,
    payload: dict[str, Any] | None = None,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Generic stage-complete emission."""
    await emit_event(
        ingest_job_id=ingest_job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        stage=stage,
        status="ok",
        message=message,
        payload=payload,
        session_factory=session_factory,
    )


async def emit_final(
    *,
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    summary: dict[str, Any] | None = None,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Emit terminal success event (SSE close signal)."""
    await emit_event(
        ingest_job_id=ingest_job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        stage="final",
        status="ok",
        message="job completed successfully",
        payload=summary or {},
        session_factory=session_factory,
    )


async def emit_error(
    *,
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    exc: BaseException,
    stage: str = "error",
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Emit terminal failure event (SSE close signal)."""
    await emit_event(
        ingest_job_id=ingest_job_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        stage="error",
        status="error",
        message=str(exc),
        payload={"error_type": type(exc).__name__, "failed_stage": stage},
        session_factory=session_factory,
    )
