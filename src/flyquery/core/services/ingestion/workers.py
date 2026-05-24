# Copyright 2026 Firefly Software Solutions Inc
"""IngestWorker — pyfly-registered EDA subscriber for flyquery ingestion jobs.

Consumes IngestRequested events from the FLYQUERY_INGEST_TOPIC, loads the
flyquery_ingest_jobs row, and runs the appropriate pipeline stages based on
the job kind:

    PARSE_AND_INGEST  — full stages 1-10 (upload-driven synchronous path;
                        the worker only handles it if re-queued by the API)
    REPARSE           — stages 1-3 + 9-10 on the existing file
    SAMPLE_REFRESH    — stage 4 only
    DESCRIBE_PASS     — stage 7 only
    RELATION_PASS     — stage 6 only

Cooperative cancel: the worker checks flyquery_ingest_jobs.status='CANCELLED'
between stages and exits gracefully.

Bounded concurrency: one asyncio.Semaphore per worker instance caps inflight
handler tasks at settings.ingest_worker_concurrency (default 4).
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from pyfly.container import service as service_bean
from pyfly.eda import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.config import FlyquerySettings
from flyquery.core.eda.ingest_publisher import INGEST_REQUESTED_EVENT, IngestPublisher
from flyquery.core.services.callbacks.callback_repository import (
    CallbackOutboxRepository,
)
from flyquery.core.services.ingestion.events import (
    emit_error,
    emit_final,
    emit_running,
    emit_stage,
)

logger = logging.getLogger(__name__)


@service_bean
class IngestWorker:
    """EDA subscriber that executes ingestion pipeline stages asynchronously.

    Registered as a ``@service`` bean so pyfly auto-discovers it at boot.
    On ``run_forever()`` it subscribes to the ingest topic and blocks until
    stopped.
    """

    def __init__(
        self,
        event_publisher: EventPublisher,
        settings: FlyquerySettings,
        session: async_sessionmaker[AsyncSession],
        ingest_publisher: IngestPublisher,
        callback_outbox_repository: CallbackOutboxRepository,
    ) -> None:
        self._publisher = event_publisher
        # The high-level wrapper used to publish SchemaUpdated from
        # within the per-table loop. DI-injected so it shares the same
        # real EventPublisher as the rest of the service.
        self._ingest_publisher = ingest_publisher
        self._callback_outbox_repository = callback_outbox_repository
        self._settings = settings
        self._session_factory = session
        self._stop_event = asyncio.Event()
        self._sem = asyncio.Semaphore(settings.ingest_worker_concurrency)
        self._inflight: set[asyncio.Task[None]] = set()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def run_forever(self) -> None:
        """Subscribe to the ingest topic and block until stopped."""
        subscribe = getattr(self._publisher, "subscribe", None)
        if subscribe is not None:
            subscribe(
                INGEST_REQUESTED_EVENT,
                self._make_dispatcher(),
            )

        start = getattr(self._publisher, "start", None)
        if start is not None:
            await start()

        logger.info(
            "IngestWorker started topic=%s concurrency=%d timeout_s=%d",
            self._settings.ingest_topic,
            self._settings.ingest_worker_concurrency,
            self._settings.ingest_handler_timeout_s,
        )

        try:
            await self._stop_event.wait()
        finally:
            await self._drain_inflight()
            stop_fn = getattr(self._publisher, "stop", None)
            if stop_fn is not None:
                await stop_fn()
            logger.info("IngestWorker stopped")

    def stop(self) -> None:
        """Signal the worker loop to exit."""
        self._stop_event.set()

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def _make_dispatcher(self):
        """Return a coroutine the EDA bus can subscribe directly."""

        async def _dispatch(envelope: Any) -> None:
            if self._stop_event.is_set():
                logger.debug("IngestWorker stopping; dropping event")
                return
            task = asyncio.create_task(
                self._guarded_handle(envelope),
                name="flyquery-ingest-worker",
            )
            self._inflight.add(task)
            task.add_done_callback(self._inflight.discard)

        return _dispatch

    async def _guarded_handle(self, envelope: Any) -> None:
        async with self._sem:
            started = time.perf_counter()
            try:
                await asyncio.wait_for(
                    self._handle_ingest_requested(envelope),
                    timeout=self._settings.ingest_handler_timeout_s,
                )
                logger.debug(
                    "IngestWorker handler ok elapsed_ms=%d",
                    int((time.perf_counter() - started) * 1000),
                )
            except TimeoutError:
                logger.warning(
                    "IngestWorker handler timed out timeout_s=%d",
                    self._settings.ingest_handler_timeout_s,
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("IngestWorker handler failed: %s", exc)

    async def _drain_inflight(self) -> None:
        if not self._inflight:
            return
        grace = self._settings.ingest_shutdown_grace_s
        logger.info("IngestWorker draining inflight=%d grace_s=%d", len(self._inflight), grace)
        try:
            await asyncio.wait_for(
                asyncio.gather(*list(self._inflight), return_exceptions=True),
                timeout=grace,
            )
        except TimeoutError:
            logger.warning("IngestWorker drain timed out; cancelling %d task(s)", len(self._inflight))
            for task in list(self._inflight):
                task.cancel()
            # asyncio.timeout is an ASYNC context manager -- `with`
            # raises TypeError. Use a wait_for fallback so the
            # post-cancel cleanup gets at most 5s before we give up.
            try:
                await asyncio.wait_for(
                    asyncio.gather(*list(self._inflight), return_exceptions=True),
                    timeout=5,
                )
            except TimeoutError:
                logger.error("IngestWorker drain hard-timeout; leaking %d task(s)", len(self._inflight))

    # ------------------------------------------------------------------
    # Handler
    # ------------------------------------------------------------------

    async def _handle_ingest_requested(self, envelope: Any) -> None:
        """Main handler: load job row, run stages, update status."""
        payload = self._payload_of(envelope)
        job_id_raw = payload.get("ingest_job_id") or payload.get("job_id")
        if not job_id_raw:
            logger.warning("IngestRequested without ingest_job_id — dropping")
            return

        try:
            job_id = uuid.UUID(str(job_id_raw))
        except ValueError:
            logger.warning("IngestRequested malformed ingest_job_id=%r — dropping", job_id_raw)
            return

        # Load job row (cross-workspace: worker has BYPASSRLS privilege)
        job = await self._load_job(job_id)
        if job is None:
            logger.warning("IngestRequested unknown job_id=%s — dropping", job_id)
            return

        tenant_id: str = job["tenant_id"]
        workspace_id: uuid.UUID = uuid.UUID(str(job["workspace_id"]))
        job_kind: str = job["job_kind"]

        # --- Cooperative cancel guard ---
        if job["status"] == "CANCELLED":
            logger.info("job %s already CANCELLED — skipping", job_id)
            return

        # --- Terminal-state guard (idempotency on EDA redelivery) ---
        if job["status"] in ("SUCCEEDED", "FAILED"):
            logger.info("job %s already in terminal state %s — skipping", job_id, job["status"])
            return

        # --- Claim the job ---
        claimed = await self._mark_running(job_id)
        if not claimed:
            logger.info(
                "job %s could not be claimed (held by another worker or already terminal) — skipping", job_id
            )
            return

        await emit_running(
            ingest_job_id=job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            session_factory=self._session_factory,
        )

        try:
            await self._run_stages(
                job_id=job_id,
                job=job,
                job_kind=job_kind,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
            await self._mark_succeeded(job_id)
            await emit_final(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                summary={"job_kind": job_kind},
                session_factory=self._session_factory,
            )
            logger.info("ingest job succeeded id=%s kind=%s", job_id, job_kind)

        except Exception as exc:  # noqa: BLE001
            failed_stage = getattr(exc, "_stage", "unknown")
            await emit_error(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                exc=exc,
                stage=failed_stage,
                session_factory=self._session_factory,
            )
            await self._mark_failed(job_id, exc)
            logger.warning("ingest job failed id=%s kind=%s error=%s", job_id, job_kind, exc)

    async def _run_stages(
        self,
        *,
        job_id: uuid.UUID,
        job: dict[str, Any],
        job_kind: str,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> None:
        """Dispatch to the appropriate stage sequence based on job_kind.

        Between each stage, check for cooperative cancellation.
        """
        if job_kind == "REPARSE":
            await self._run_reparse(
                job_id=job_id,
                job=job,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
        elif job_kind == "PARSE_AND_INGEST":
            # PARSE_AND_INGEST is normally driven synchronously by the upload
            # path (IngestService). If it arrives here (e.g., re-queued after
            # a transient failure), run the same REPARSE logic as a fallback.
            await self._run_reparse(
                job_id=job_id,
                job=job,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
        elif job_kind == "SAMPLE_REFRESH":
            await self._run_sample_refresh(
                job_id=job_id,
                job=job,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
        elif job_kind == "DESCRIBE_PASS":
            await self._run_describe_pass(
                job_id=job_id,
                job=job,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
        elif job_kind == "RELATION_PASS":
            await self._run_relation_pass(
                job_id=job_id,
                job=job,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
        else:
            raise ValueError(f"unknown job_kind={job_kind!r}")

    async def _run_reparse(
        self,
        *,
        job_id: uuid.UUID,
        job: dict[str, Any],
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> None:
        """Run stages 1-3 + 9-10 for REPARSE / PARSE_AND_INGEST jobs."""
        from flyquery.core.services.ingestion.stages.embed import run_embed
        from flyquery.core.services.ingestion.stages.parse import run_parse
        from flyquery.core.services.ingestion.stages.publish import run_publish
        from flyquery.core.services.ingestion.stages.receive import run_receive
        from flyquery.core.services.ingestion.stages.reconcile import run_reconcile
        from flyquery.core.services.storage.object_store_factory import build_object_store
        from flyquery.core.services.workspaces.workspace_service import WorkspaceService

        dataset_id = uuid.UUID(str(job["dataset_id"]))
        file_id_raw = job.get("file_id")
        table_id_raw = job.get("table_id")
        request_json = job.get("request_json") or {}

        # Reconstruct the original filename + bytes from object-store
        # via the flyquery_files row referenced by file_id.
        file_info = await self._load_file(file_id_raw) if file_id_raw else None
        if file_info is None:
            raise RuntimeError(f"REPARSE job {job_id} has no resolvable file_id={file_id_raw!r}")

        object_store = build_object_store(self._settings)

        # Cooperative cancel before each stage
        await self._check_cancelled(job_id)

        # Load file bytes from object store. ObjectStore.get() returns
        # AsyncIterator[bytes]; materialise chunks here once so downstream
        # consumers can use it as a plain ``bytes`` value (len/hash/slice).
        try:
            stream = await object_store.get(file_info["object_store_key"])
            chunks: list[bytes] = []
            async for chunk in stream:
                chunks.append(chunk)
            file_bytes = b"".join(chunks)
        except Exception as exc:
            exc._stage = "receive"  # type: ignore[attr-defined]
            raise

        # Stage 1: receive
        await self._check_cancelled(job_id)
        from flyquery.core.services.workspaces.workspace_repository import WorkspaceRepository

        ws_repo = WorkspaceRepository(self._session_factory)
        ws_service = WorkspaceService(ws_repo)
        ws = await ws_service.get(workspace_id)
        storage_used = ws["storage_used_bytes"] if ws else 0

        # When the async upload endpoint queued this job it already
        # ran Stage 1 (the file row + bytes exist). Re-running run_receive
        # would create a duplicate file_id + duplicate object-store key,
        # so honour the ``already_received`` flag and reuse the existing
        # row instead. REPARSE callers and the legacy
        # PARSE_AND_INGEST re-queue path still get a fresh receive (which
        # is what they want -- new file_id + new snapshot version).
        already_received = bool(request_json.get("already_received"))
        if already_received:
            # Synthesise a ReceiveResult-ish shim so the rest of the
            # function keeps using the same field names. We need a local
            # temp file for the parse stage; persist the bytes once here.
            import tempfile as _tempfile

            ext = _suffix_from_key(str(file_info["object_store_key"]))
            fd, local_temp_path = _tempfile.mkstemp(suffix=ext)
            try:
                with open(fd, "wb") as fh:
                    fh.write(file_bytes)
            except Exception:
                import os as _os

                _os.close(fd)
                raise
            from flyquery.core.services.ingestion.format_detect import detect_format

            file_format, compression = detect_format(file_info["original_filename"], file_bytes[:512])
            recv = _AlreadyReceived(
                file_id=uuid.UUID(str(file_info["id"])),
                file_format=file_format,
                compression=compression,
                size_bytes=len(file_bytes),
                object_store_key=str(file_info["object_store_key"]),
                local_temp_path=local_temp_path,
            )
            await emit_stage(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                stage="received",
                message="stage 1 skipped (already received via async upload)",
                payload={"file_id": str(recv.file_id), "skipped": True},
                session_factory=self._session_factory,
            )
            # Storage already tracked by the endpoint -- do NOT track again.
        else:
            recv = await run_receive(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                filename=file_info["original_filename"],
                file_bytes=file_bytes,
                actor=request_json.get("actor", "worker"),
                object_store=object_store,
                session_factory=self._session_factory,
                settings=self._settings,
                workspace_storage_used_bytes=storage_used,
            )
            await emit_stage(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                stage="received",
                message="stage 1 complete",
                payload={"file_id": str(recv.file_id)},
                session_factory=self._session_factory,
            )
            await ws_service.track_storage(workspace_id, recv.size_bytes)

        # Stage 2: parse
        await self._check_cancelled(job_id)
        existing_table_id = uuid.UUID(str(table_id_raw)) if table_id_raw else None
        dataset_name = request_json.get("dataset_name", "dataset")
        locale = request_json.get("locale", self._settings.default_locale)

        parsed_tables = await run_parse(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            file_id=recv.file_id,
            local_temp_path=recv.local_temp_path,
            file_format=recv.file_format,
            compression=recv.compression,
            object_store=object_store,
            session_factory=self._session_factory,
            settings=self._settings,
            existing_table_id=existing_table_id,
            dataset_name=dataset_name,
            workspace_locale=locale,
            original_filename=file_info["original_filename"],
        )
        await emit_stage(
            ingest_job_id=job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            stage="parsed",
            message=f"stage 2 complete: {len(parsed_tables)} table(s)",
            payload={"n_tables": len(parsed_tables)},
            session_factory=self._session_factory,
        )

        # Stages 3, 9, 10 per table -- use the DI-injected publisher
        # so SchemaUpdated reaches other consumers (flycanon's KB,
        # flyradar's relation harvester) instead of dying in-memory.
        publisher = self._ingest_publisher

        for pt in parsed_tables:
            await self._check_cancelled(job_id)

            # Stage 3: reconcile
            rec = await run_reconcile(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                parsed=pt,
                actor=request_json.get("actor", "worker"),
                # ``ck_snapshots_trigger`` only allows
                # ('USER','AGENT','SCHEDULED','REPARSE'). A
                # PARSE_AND_INGEST job is, by definition, the
                # worker re-parsing an already-uploaded file -> REPARSE.
                triggered_by="REPARSE",
                session_factory=self._session_factory,
            )
            await emit_stage(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                stage="reconciled",
                message="stage 3 complete",
                payload={"table_id": str(pt.table_id), "snapshot_id": str(rec.snapshot_id)},
                session_factory=self._session_factory,
            )

            await self._check_cancelled(job_id)

            # Stage 9: embed
            await run_embed(
                tenant_id=tenant_id,
                snapshot_id=rec.snapshot_id,
                session_factory=self._session_factory,
            )
            await emit_stage(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                stage="embedded",
                message="stage 9 complete",
                payload={"snapshot_id": str(rec.snapshot_id)},
                session_factory=self._session_factory,
            )

            await self._check_cancelled(job_id)

            # Stage 10: publish
            await run_publish(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                table_id=pt.table_id,
                snapshot_id=rec.snapshot_id,
                n_columns=rec.n_columns,
                n_rows_actual=rec.n_rows_actual,
                publisher=publisher,
                session_factory=self._session_factory,
            )
            await emit_stage(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                stage="published",
                message="stage 10 complete",
                payload={"table_id": str(pt.table_id), "snapshot_id": str(rec.snapshot_id)},
                session_factory=self._session_factory,
            )

    async def _run_sample_refresh(
        self,
        *,
        job_id: uuid.UUID,
        job: dict[str, Any],
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> None:
        """Run Stage 4 (sample) for SAMPLE_REFRESH jobs."""
        from flyquery.core.services.ingestion.stages.sample import run_sample

        table_id_raw = job.get("table_id")
        if not table_id_raw:
            raise RuntimeError(f"SAMPLE_REFRESH job {job_id} missing table_id")

        # Load the current snapshot for the table
        snapshot_id, parquet_key = await self._load_current_snapshot(uuid.UUID(str(table_id_raw)), tenant_id)
        if snapshot_id is None:
            raise RuntimeError(f"SAMPLE_REFRESH job {job_id}: table has no READY snapshot")

        await self._check_cancelled(job_id)
        result = await run_sample(
            tenant_id=tenant_id,
            snapshot_id=snapshot_id,
            parquet_key=parquet_key,
            session_factory=self._session_factory,
            settings=self._settings,
        )
        await emit_stage(
            ingest_job_id=job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            stage="sampled",
            message="stage 4 complete (SAMPLE_REFRESH)",
            payload=result,
            session_factory=self._session_factory,
        )

    async def _run_describe_pass(
        self,
        *,
        job_id: uuid.UUID,
        job: dict[str, Any],
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> None:
        """Run Stage 7 (describe) for DESCRIBE_PASS jobs.

        DESCRIBE_PASS applies to all tables in the dataset (or the specific
        table_id if provided).
        """
        from flyquery.core.services.ingestion.stages.describe import run_describe

        dataset_id_raw = job.get("dataset_id")
        if not dataset_id_raw:
            raise RuntimeError(f"DESCRIBE_PASS job {job_id} missing dataset_id")

        dataset_id = uuid.UUID(str(dataset_id_raw))
        table_id_raw = job.get("table_id")

        snapshots = await self._load_dataset_snapshots(
            tenant_id,
            dataset_id,
            table_id=uuid.UUID(str(table_id_raw)) if table_id_raw else None,
        )

        for snap in snapshots:
            await self._check_cancelled(job_id)
            result = await run_describe(
                tenant_id=tenant_id,
                snapshot_id=snap["id"],
                session_factory=self._session_factory,
                settings=self._settings,
            )
            await emit_stage(
                ingest_job_id=job_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                stage="described",
                message=f"stage 7 complete (DESCRIBE_PASS snapshot={snap['id']})",
                payload=result,
                session_factory=self._session_factory,
            )

    async def _run_relation_pass(
        self,
        *,
        job_id: uuid.UUID,
        job: dict[str, Any],
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> None:
        """Run Stage 6 (relations) for RELATION_PASS jobs."""
        from flyquery.core.services.ingestion.stages.relations import run_relations

        dataset_id_raw = job.get("dataset_id")
        if not dataset_id_raw:
            raise RuntimeError(f"RELATION_PASS job {job_id} missing dataset_id")

        dataset_id = uuid.UUID(str(dataset_id_raw))

        await self._check_cancelled(job_id)
        result = await run_relations(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            session_factory=self._session_factory,
            settings=self._settings,
        )
        await emit_stage(
            ingest_job_id=job_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            stage="relations_proposed",
            message="stage 6 complete (RELATION_PASS)",
            payload=result,
            session_factory=self._session_factory,
        )

    # ------------------------------------------------------------------
    # Cooperative cancel
    # ------------------------------------------------------------------

    async def _check_cancelled(self, job_id: uuid.UUID) -> None:
        """Raise CancelledError if the job has been flipped to CANCELLED."""
        job = await self._load_job(job_id)
        if job is not None and job["status"] == "CANCELLED":
            logger.info("ingest job %s cancelled cooperatively", job_id)
            raise asyncio.CancelledError(f"job {job_id} cancelled by user")

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------

    async def _load_job(self, job_id: uuid.UUID) -> dict[str, Any] | None:
        async with self._session_factory() as s:
            result = await s.execute(
                sa.text(
                    "SELECT id, tenant_id, workspace_id, dataset_id, table_id, file_id, "
                    "job_kind, status, request_json "
                    "FROM flyquery_ingest_jobs WHERE id = :id"
                ),
                {"id": job_id},
            )
            row = result.mappings().first()
            return dict(row) if row else None

    async def _load_file(self, file_id: Any) -> dict[str, Any] | None:
        from flyquery.core.services.files.file_repository import FileRepository

        repo = FileRepository(self._session_factory)
        return await repo.get(file_id)

    async def _mark_running(self, job_id: uuid.UUID) -> bool:
        """Atomic claim: flip PENDING → RUNNING. Returns True on success."""
        async with self._session_factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    "UPDATE flyquery_ingest_jobs "
                    "SET status = 'RUNNING', started_at = now(), attempts = attempts + 1 "
                    "WHERE id = :id AND status = 'PENDING' "
                    "RETURNING id"
                ),
                {"id": job_id},
            )
            return result.first() is not None

    async def _mark_succeeded(self, job_id: uuid.UUID) -> None:
        async with self._session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    "UPDATE flyquery_ingest_jobs "
                    "SET status = 'SUCCEEDED', finished_at = now() "
                    "WHERE id = :id AND status = 'RUNNING'"
                ),
                {"id": job_id},
            )
            # Same txn as the status flip: either both happen and the
            # callback is durably queued, or both roll back. Without
            # this atomicity a process crash between the two writes
            # would silently drop the webhook for a "succeeded" job.
            await self._enqueue_callback_terminal(
                session=s,
                job_id=job_id,
                status="SUCCEEDED",
                result_json={},
            )

    async def _mark_failed(self, job_id: uuid.UUID, exc: BaseException) -> None:
        error_json = {"error_type": type(exc).__name__, "message": str(exc)}
        async with self._session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    "UPDATE flyquery_ingest_jobs "
                    "SET status = 'FAILED', finished_at = now(), result_json = CAST(:err AS jsonb) "
                    "WHERE id = :id AND status IN ('RUNNING', 'PENDING')"
                ),
                {"id": job_id, "err": _json_dumps(error_json)},
            )
            await self._enqueue_callback_terminal(
                session=s,
                job_id=job_id,
                status="FAILED",
                result_json=error_json,
            )

    async def _enqueue_callback_terminal(
        self,
        *,
        session: AsyncSession,
        job_id: uuid.UUID,
        status: str,
        result_json: dict[str, Any],
    ) -> None:
        """Enqueue one outbox row when the job's row has a ``callback_url``.

        Shares ``session`` so the outbox insert commits with the status
        flip. No-op when the job has no callback configured.
        """
        result = await session.execute(
            sa.text(
                """
                SELECT id, tenant_id, workspace_id, dataset_id, table_id,
                       file_id, snapshot_id, job_kind, attempts,
                       request_json, callback_url, callback_secret,
                       callback_headers
                FROM flyquery_ingest_jobs
                WHERE id = :id
                """
            ),
            {"id": job_id},
        )
        row = result.mappings().first()
        if row is None or not row["callback_url"]:
            return

        payload = {
            "ingest_job_id": str(row["id"]),
            "tenant_id": row["tenant_id"],
            "workspace_id": str(row["workspace_id"]),
            "dataset_id": str(row["dataset_id"]) if row["dataset_id"] else None,
            "table_id": str(row["table_id"]) if row["table_id"] else None,
            "file_id": str(row["file_id"]) if row["file_id"] else None,
            "snapshot_id": str(row["snapshot_id"]) if row["snapshot_id"] else None,
            "job_kind": row["job_kind"],
            "status": status,
            "attempts": row["attempts"],
            "request_json": row["request_json"] or {},
            "result_json": result_json,
        }
        await self._callback_outbox_repository.enqueue_terminal(
            session=session,
            ingest_job_id=uuid.UUID(str(row["id"])),
            tenant_id=row["tenant_id"],
            workspace_id=uuid.UUID(str(row["workspace_id"])),
            callback_url=row["callback_url"],
            callback_secret=row["callback_secret"],
            callback_headers=row["callback_headers"] or {},
            event_type=f"ingest.{status.lower()}",
            payload=payload,
        )

    # ------------------------------------------------------------------
    async def _load_current_snapshot(
        self, table_id: uuid.UUID, tenant_id: str
    ) -> tuple[uuid.UUID | None, str]:
        """Return (snapshot_id, parquet_key) for the table's current READY snapshot."""
        async with self._session_factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT sn.id, sn.parquet_object_key
                    FROM flyquery_tables t
                    JOIN flyquery_schema_snapshots sn ON sn.id = t.current_snapshot_id
                    WHERE t.id = :tid AND t.tenant_id = :tenant
                    """
                ),
                {"tid": table_id, "tenant": tenant_id},
            )
            row = result.mappings().first()
            if not row:
                return None, ""
            return uuid.UUID(str(row["id"])), row["parquet_object_key"] or ""

    async def _load_dataset_snapshots(
        self,
        tenant_id: str,
        dataset_id: uuid.UUID,
        table_id: uuid.UUID | None = None,
    ) -> list[dict[str, Any]]:
        """Return all READY snapshot records for the dataset (or a specific table)."""
        async with self._session_factory() as s:
            where = "WHERE t.dataset_id = :ds AND t.tenant_id = :tenant AND sn.status = 'READY'"
            params: dict[str, Any] = {"ds": dataset_id, "tenant": tenant_id}
            if table_id is not None:
                where += " AND t.id = :tid"
                params["tid"] = table_id
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT sn.id, sn.parquet_object_key, sn.n_rows_actual, t.id AS table_id
                    FROM flyquery_tables t
                    JOIN flyquery_schema_snapshots sn ON sn.id = t.current_snapshot_id
                    {where}
                    """
                ),
                params,
            )
            return [dict(r) for r in result.mappings().all()]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _payload_of(envelope: Any) -> dict[str, Any]:
        payload = getattr(envelope, "payload", None)
        if isinstance(payload, dict):
            return payload
        return {}


def _json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj)


def _suffix_from_key(key: str) -> str:
    """Recover the file suffix from an object-store key.

    Receive writes keys like ``flyquery/.../files/{uuid}.csv.gz`` -- we
    need the same suffix when re-materialising the bytes to a local temp
    file so the parse stage's format detection still works on the path.
    """
    import os

    base = os.path.basename(key)
    # Strip the UUID prefix and keep everything after the first dot.
    dot = base.find(".")
    return base[dot:] if dot >= 0 else ""


@dataclass
class _AlreadyReceived:
    """Drop-in replacement for ReceiveResult used by the ``already_received`` branch.

    Mirrors :class:`ReceiveResult` shape so downstream stages don't need
    to know they got a synthesised value instead of a real Stage 1 run.
    """

    file_id: uuid.UUID
    file_format: str
    compression: str
    size_bytes: int
    object_store_key: str
    local_temp_path: str
