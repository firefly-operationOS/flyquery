# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_ingest_events.

Promotes the function-based ``emit_*`` helpers in
:mod:`flyquery.core.services.ingestion.events` to a class-based
``@repository`` bean. The helpers stay as thin wrappers for the
existing call sites in ingestion stages + the worker (which take a
``session_factory`` parameter rather than the repo), but new callers
should depend on this class.

Like the audit + cost event repos, writes are best-effort -- a broken
event row never aborts the main pipeline stage. The job itself is
durable truth in ``flyquery_ingest_jobs``; events are an audit + SSE
trail layered on top.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


@repository
class IngestEventRepository:
    """Repository over ``flyquery_ingest_events``."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def insert_event(
        self,
        *,
        ingest_job_id: uuid.UUID,
        tenant_id: str,
        workspace_id: uuid.UUID,
        stage: str,
        status: str,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Write one progress event row.

        Best-effort: a failed insert is logged and swallowed so the
        ingestion pipeline never aborts because the SSE trail is
        misbehaving.
        """
        await _insert_event(
            session_factory=self._factory,
            ingest_job_id=ingest_job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            stage=stage,
            status=status,
            message=message,
            payload=payload,
        )


async def _insert_event(
    *,
    session_factory: async_sessionmaker[AsyncSession],
    ingest_job_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    stage: str,
    status: str,
    message: str | None,
    payload: dict[str, Any] | None,
) -> None:
    """Module-level helper used by both the repo and the legacy emit_* helpers.

    Centralises the SQL + JSON serialisation + error swallow policy so
    both call paths stay in lockstep.
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


def _to_jsonb(obj: Any) -> str:
    """Serialise a dict to a JSON string for Postgres JSONB binding."""

    def _default(o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        raise TypeError(f"Object of type {type(o).__name__!r} is not JSON serialisable")

    return json.dumps(obj, default=_default)
