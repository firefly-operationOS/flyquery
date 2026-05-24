# Copyright 2026 Firefly Software Solutions Inc
"""Service layer for ingest job lifecycle management."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from pyfly.container import service as service_bean

from flyquery.config import FlyquerySettings
from flyquery.core.eda.ingest_publisher import IngestPublisher, IngestRequestedEvent
from flyquery.core.services.ingest_jobs.ingest_job_repository import IngestJobRepository
from flyquery.core.services.ingestion.events import emit_queued
from flyquery.interfaces.ingest_jobs import (
    CancelResponse,
    IngestEventListResponse,
    IngestEventRead,
    IngestJobCreate,
    IngestJobListResponse,
    IngestJobRead,
)


@service_bean
class IngestJobService:
    """Business logic for POST /ingest-jobs, GET /ingest-jobs, :cancel."""

    def __init__(
        self,
        repository: IngestJobRepository,
        publisher: IngestPublisher,
        settings: FlyquerySettings,
    ) -> None:
        self._repo = repository
        self._publisher = publisher
        self._settings = settings

    async def create_job(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: IngestJobCreate,
        session_factory: Any,  # async_sessionmaker[AsyncSession]
    ) -> IngestJobRead:
        """Create a PENDING job, emit queued event, publish IngestRequested."""
        body.validate_startable()
        return await self._enqueue(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            table_id=body.table_id,
            file_id=body.file_id,
            job_kind=body.job_kind,
            request_json=body.request_json,
            session_factory=session_factory,
        )

    async def mark_already_received(self, job_id: uuid.UUID) -> None:
        """Flip the job's ``request_json.already_received`` flag to ``true``.

        Called by the async upload endpoint after queueing the job so
        the worker's PARSE_AND_INGEST handler skips Stage 1 (the
        endpoint already ran it).
        """
        await self._repo.merge_request_json(job_id, {"already_received": True})

    async def enqueue_parse_and_ingest(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        file_id: uuid.UUID,
        actor: str,
        dataset_name: str,
        session_factory: Any,
    ) -> IngestJobRead:
        """Queue a PARSE_AND_INGEST job for the async upload endpoint.

        ``PARSE_AND_INGEST`` is intentionally excluded from
        :meth:`IngestJobCreate.validate_startable` because it has a
        canonical entry point (``POST /datasets/{id}/files``). The
        async upload endpoint is the second canonical entry point and
        bypasses that check here. The worker's ``_run_reparse`` handler
        loads the file via ``file_id`` and runs stages 1-3 + 9-10 --
        Stage 1 (receive) was already run synchronously by the
        upload endpoint so the bytes + ``flyquery_files`` row exist.
        """
        return await self._enqueue(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            table_id=None,
            file_id=file_id,
            job_kind="PARSE_AND_INGEST",
            request_json={"actor": actor, "dataset_name": dataset_name},
            session_factory=session_factory,
        )

    async def _enqueue(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        table_id: uuid.UUID | None,
        file_id: uuid.UUID | None,
        job_kind: str,
        request_json: dict[str, Any] | None,
        session_factory: Any,
    ) -> IngestJobRead:
        """Shared implementation for both startable + internal job kinds."""
        row = await self._repo.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            table_id=table_id,
            file_id=file_id,
            job_kind=job_kind,
            request_json=request_json or {},
        )

        job_id = row["id"]

        # Emit queued event to the event ledger
        await emit_queued(
            ingest_job_id=job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            job_kind=job_kind,
            session_factory=session_factory,
        )

        # Publish IngestRequested to the EDA bus
        await self._publisher.publish_ingest_requested(
            IngestRequestedEvent(ingest_job_id=job_id),
            ingest_topic=self._settings.ingest_topic,
        )

        return _to_read(row)

    async def get_job(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> IngestJobRead | None:
        row = await self._repo.get(job_id, tenant_id=tenant_id, workspace_id=workspace_id)
        return _to_read(row) if row else None

    async def list_jobs(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        statuses: Sequence[str] | None = None,
        job_kinds: Sequence[str] | None = None,
        dataset_id: uuid.UUID | None = None,
        table_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> IngestJobListResponse:
        items, total = await self._repo.list_jobs(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            statuses=statuses,
            job_kinds=job_kinds,
            dataset_id=dataset_id,
            table_id=table_id,
            limit=limit,
            offset=offset,
        )
        return IngestJobListResponse(
            items=[_to_read(r) for r in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def cancel_job(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> CancelResponse | None:
        row = await self._repo.cancel(job_id, tenant_id=tenant_id, workspace_id=workspace_id)
        if row is None:
            return None
        return CancelResponse(
            id=row["id"],
            status=row["status"],
            message=(
                "Job cancelled successfully"
                if row["status"] == "CANCELLED"
                else f"Job is already in terminal state {row['status']!r}"
            ),
        )

    async def list_events(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        after_id: int | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> IngestEventListResponse:
        items, total = await self._repo.list_events(
            job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            after_id=after_id,
            limit=limit,
            offset=offset,
        )
        return IngestEventListResponse(
            items=[_to_event_read(e) for e in items],
            total=total,
            limit=limit,
            offset=offset,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_read(row: dict[str, Any]) -> IngestJobRead:
    return IngestJobRead(
        id=row["id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        dataset_id=row["dataset_id"],
        table_id=row.get("table_id"),
        file_id=row.get("file_id"),
        snapshot_id=row.get("snapshot_id"),
        job_kind=row["job_kind"],
        status=row["status"],
        attempts=row["attempts"],
        request_json=row.get("request_json") or {},
        result_json=row.get("result_json") or {},
        cost_cents=row.get("cost_cents") or 0,
        elapsed_ms=row.get("elapsed_ms"),
        started_at=row.get("started_at"),
        finished_at=row.get("finished_at"),
    )


def _to_event_read(row: dict[str, Any]) -> IngestEventRead:
    return IngestEventRead(
        id=row["id"],
        ingest_job_id=row["ingest_job_id"],
        stage=row["stage"],
        status=row["status"],
        message=row.get("message"),
        payload_json=row.get("payload_json") or {},
        created_at=row["created_at"],
    )
