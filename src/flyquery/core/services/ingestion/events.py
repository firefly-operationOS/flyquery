# Copyright 2026 Firefly Software Solutions Inc
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

import logging
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


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
    """
    try:
        async with session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    "INSERT INTO flyquery_ingest_events "
                    "(tenant_id, workspace_id, ingest_job_id, stage, status, message, payload_json) "
                    "VALUES (:tenant, :ws, :job_id, :stage, :status, :msg, CAST(:payload AS jsonb))"
                ),
                {
                    "tenant": tenant_id,
                    "ws": workspace_id,
                    "job_id": ingest_job_id,
                    "stage": stage,
                    "status": status,
                    "msg": message,
                    "payload": _to_jsonb(payload or {}),
                },
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "ingest_event write failed job_id=%s stage=%s: %s",
            ingest_job_id,
            stage,
            exc,
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


def _to_jsonb(obj: Any) -> str:
    """Serialise a dict to a JSON string for Postgres JSONB binding."""
    import json

    def _default(o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        raise TypeError(f"Object of type {type(o).__name__!r} is not JSON serialisable")

    return json.dumps(obj, default=_default)
