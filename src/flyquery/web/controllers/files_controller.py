# Copyright 2026 Firefly Software Solutions Inc
"""Files controller.

POST   /api/v1/datasets/{dataset_id}/files            -- single multipart upload
POST   /api/v1/datasets/{dataset_id}/files:bulk       -- multi-file multipart upload
PUT    /api/v1/datasets/{dataset_id}/tables/{table_id}:upload  -- re-upload
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from pyfly.container import rest_controller
from pyfly.web import PathVar, post_mapping, put_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import JSONResponse

from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.core.services.ingest_jobs.ingest_job_service import IngestJobService
from flyquery.core.services.ingestion.ingest_service import IngestService
from flyquery.core.services.ingestion.stages.receive import run_receive
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.files import (
    AsyncFileUploadAccepted,
    BulkFileResult,
    BulkFileUploadResponse,
    FileUploadResponse,
    ReuploadResponse,
    TableSummary,
)
from flyquery.web.conventions import (
    IdempotencyStore,
    ResourceNotFound,
    tenant_context_from_request,
)
from flyquery.web.idempotent_handler import replay_dedup

logger = logging.getLogger(__name__)


@rest_controller
@request_mapping("/api/v1/datasets")
class FilesController:
    """REST adapter for file uploads + re-uploads."""

    def __init__(
        self,
        ingest_service: IngestService,
        dataset_service: DatasetService,
        ingest_job_service: IngestJobService,
        workspace_service: WorkspaceService,
        object_store: ObjectStore,
        session: async_sessionmaker[AsyncSession],
        idempotency_store: IdempotencyStore,
        settings: Any = None,
    ) -> None:
        self._ingest = ingest_service
        self._datasets = dataset_service
        self._ingest_jobs = ingest_job_service
        self._workspaces = workspace_service
        self._object_store = object_store
        self._session_factory = session
        self._idempotency_store = idempotency_store
        # Settings is optional -- run_receive needs it but DI may inject
        # it lazily; we resolve from the ingest service when unset.
        self._settings = settings if settings is not None else ingest_service._settings  # type: ignore[attr-defined]

    @post_mapping("/{dataset_id}/files", status_code=201)
    async def upload_file(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> FileUploadResponse:
        """Accept a multipart file upload and run the synchronous ingestion pipeline."""
        ctx = tenant_context_from_request(http_request)

        # --- Parse the multipart body using Starlette's native support ---
        form = await http_request.form()
        upload = form.get("file")
        if upload is None:
            from flyquery.web.conventions.exceptions import InvalidRequest

            raise InvalidRequest("missing 'file' field in multipart form")

        filename: str = getattr(upload, "filename", None) or "upload.bin"
        file_bytes: bytes = await upload.read()

        # --- Look up the dataset to get its name (for qualified_name prefix) ---
        ds = await self._datasets.get(dataset_id)
        if ds is None:
            raise ResourceNotFound(f"dataset {dataset_id!r} not found")

        # Inject actor: use ctx.actor or fall back to tenant_id
        actor = ctx.actor or ctx.tenant_id

        # --- Parse workspace_id from header (may come as slug or UUID) ---
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        result = await self._ingest.ingest_upload(
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            filename=filename,
            file_bytes=file_bytes,
            actor=actor,
            dataset_name=ds["name"],
        )

        return FileUploadResponse(
            file_id=result.file_id,
            tables=[
                TableSummary(
                    table_id=t.table_id,
                    name=t.name,
                    n_columns=t.n_columns,
                    n_rows_estimate=t.n_rows_estimate,
                )
                for t in result.tables
            ],
        )

    @post_mapping("/{dataset_id}/files:bulk", status_code=201)
    async def upload_files_bulk(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> BulkFileUploadResponse:
        """Accept multiple files in one multipart request and ingest each.

        Each ``files`` part is processed through the same per-file pipeline
        as ``POST /files`` (receive -> parse -> reconcile -> sample ->
        profile -> describe -> embed -> publish), and the per-file results
        run **in parallel** through ``asyncio.gather`` -- a 5-file upload
        finishes in roughly the time of a single file.

        Per-file failures do NOT abort the bulk. The response carries one
        ``BulkFileResult`` per submitted file with either ``status="OK"``
        + ``file_id`` + ``tables`` or ``status="FAILED"`` + ``error``.
        Aggregate ``succeeded`` / ``failed`` counts let a UI render
        progress without scanning the list.

        Replay-dedup'd via ``Idempotency-Key`` when present (optional on
        user tier). A retried bulk upload with the same key returns the
        cached envelope without re-ingesting -- important because the
        pipeline is heavy (parse + profile + describe + embed per file)
        and a duplicate run would double-write Parquet snapshots.
        """
        ctx = tenant_context_from_request(http_request)

        form = await http_request.form()
        # ``form.getlist("files")`` returns every part with name="files",
        # matching the standard multipart pattern for bulk uploads.
        uploads = form.getlist("files")
        if not uploads:
            # Backwards-friendly: allow a single "file" part as a degenerate
            # bulk so a client that hits this endpoint with the singleton
            # field still gets a usable response.
            single = form.get("file")
            if single is not None:
                uploads = [single]
        if not uploads:
            from flyquery.web.conventions.exceptions import InvalidRequest

            raise InvalidRequest(
                "missing multipart 'files' field(s) -- bulk uploads expect "
                "one or more parts with name='files'"
            )

        ds = await self._datasets.get(dataset_id)
        if ds is None:
            raise ResourceNotFound(f"dataset {dataset_id!r} not found")

        actor = ctx.actor or ctx.tenant_id
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        # Read all bytes upfront -- Starlette's UploadFile is a stream
        # backed by a temp file; reading them here means we don't keep
        # the request body alive throughout the async parallel section.
        prepared: list[tuple[int, str, bytes]] = []
        for i, upload in enumerate(uploads):
            filename = getattr(upload, "filename", None) or f"upload-{i}.bin"
            data = await upload.read()
            prepared.append((i, filename, data))

        async def _ingest_one(idx: int, filename: str, blob: bytes) -> BulkFileResult:
            try:
                result = await self._ingest.ingest_upload(
                    tenant_id=ctx.tenant_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset_id,
                    filename=filename,
                    file_bytes=blob,
                    actor=actor,
                    dataset_name=ds["name"],
                )
                return BulkFileResult(
                    index=idx,
                    original_filename=filename,
                    status="OK",
                    file_id=result.file_id,
                    tables=[
                        TableSummary(
                            table_id=t.table_id,
                            name=t.name,
                            n_columns=t.n_columns,
                            n_rows_estimate=t.n_rows_estimate,
                        )
                        for t in result.tables
                    ],
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "bulk-upload file failed idx=%d filename=%s err=%s",
                    idx,
                    filename,
                    exc,
                )
                return BulkFileResult(
                    index=idx,
                    original_filename=filename,
                    status="FAILED",
                    error=str(exc),
                )

        async def _do_bulk() -> BulkFileUploadResponse:
            results = await asyncio.gather(*[_ingest_one(idx, name, blob) for idx, name, blob in prepared])
            succeeded = sum(1 for r in results if r.status == "OK")
            return BulkFileUploadResponse(
                results=list(results),
                total_files=len(results),
                succeeded=succeeded,
                failed=len(results) - succeeded,
            )

        return await replay_dedup(
            request=http_request,
            store=self._idempotency_store,
            tenant_id=ctx.tenant_id,
            route=f"POST /api/v1/datasets/{dataset_id}/files:bulk",
            handler=_do_bulk,
            status_code=201,
        )

    @post_mapping("/{dataset_id}/files:async", status_code=202)
    async def upload_file_async(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> JSONResponse:
        """Async alternative to ``POST /datasets/{ds}/files``.

        Stage 1 (receive: caps check, hash, format detect, store bytes,
        write ``flyquery_files`` row, track workspace storage) runs
        *synchronously* -- it's bounded by IO + a single Postgres
        insert, not by parse/profile/describe cost. Stages 2-10 are
        queued as a ``PARSE_AND_INGEST`` ingest job that the worker
        consumes; the response 202 carries the ``job_id`` plus a
        ``Location`` header so clients can poll
        ``GET /ingest-jobs/{job_id}`` or stream
        ``GET /ingest-jobs/{job_id}/stream``.

        Use this in place of the synchronous endpoint when a single
        file exceeds the request-timeout budget of the deployment
        (typically anything above a few MB with cold-cache LLM
        describe calls).

        Stage 1's SHA-256 content hash provides natural dedup at the
        file level -- re-uploading the same bytes is detected at
        ``flyquery_files`` UNIQUE-on-(tenant, dataset, content_hash)
        -- so we do NOT layer Idempotency-Key replay caching here;
        the underlying ``IngestJobService`` is also idempotent by
        construction.
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        form = await http_request.form()
        upload = form.get("file")
        if upload is None:
            from flyquery.web.conventions.exceptions import InvalidRequest

            raise InvalidRequest("missing 'file' field in multipart form")

        filename: str = getattr(upload, "filename", None) or "upload.bin"
        file_bytes: bytes = await upload.read()

        # Optional webhook callback: the caller may attach a delivery
        # target either via multipart form fields or via the matching
        # ``X-Flyquery-Callback-*`` request headers. Form fields take
        # precedence (headers are a UA / SDK convenience). Custom
        # downstream headers can be threaded as a JSON-encoded
        # ``callback_headers`` form field; reserved keys are rejected
        # at the CallbackConfig DTO so the dispatcher can own
        # ``X-Flyquery-Signature`` etc.
        callback_url = _form_or_header(form, http_request, "callback_url")
        callback_secret = _form_or_header(form, http_request, "callback_secret")
        callback_headers_raw = _form_or_header(form, http_request, "callback_headers")
        callback_headers: dict[str, str] = {}
        if callback_headers_raw:
            import json as _json

            try:
                parsed = _json.loads(callback_headers_raw)
                if isinstance(parsed, dict):
                    callback_headers = {str(k): str(v) for k, v in parsed.items()}
            except _json.JSONDecodeError as exc:
                from flyquery.web.conventions.exceptions import InvalidRequest

                raise InvalidRequest("callback_headers must be valid JSON object string") from exc

        ds = await self._datasets.get(dataset_id)
        if ds is None:
            raise ResourceNotFound(f"dataset {dataset_id!r} not found")

        actor = ctx.actor or ctx.tenant_id

        # Stage 1: receive -- writes bytes + file row synchronously.
        ws = await self._workspaces.get(workspace_id)
        storage_used = ws["storage_used_bytes"] if ws else 0
        recv = await run_receive(
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            filename=filename,
            file_bytes=file_bytes,
            actor=actor,
            object_store=self._object_store,
            session_factory=self._session_factory,
            settings=self._settings,
            workspace_storage_used_bytes=storage_used,
        )
        # Track storage now (mirrors the sync path); the
        # ``already_received`` branch in the worker will NOT track again.
        await self._workspaces.track_storage(workspace_id, recv.size_bytes)

        # Queue the remaining stages.
        job = await self._ingest_jobs.enqueue_parse_and_ingest(
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            file_id=recv.file_id,
            actor=actor,
            dataset_name=ds["name"],
            session_factory=self._session_factory,
            callback_url=callback_url,
            callback_secret=callback_secret,
            callback_headers=callback_headers or None,
        )
        # The worker must know Stage 1 already ran to skip it.
        await self._ingest_jobs.mark_already_received(job.id)

        body = AsyncFileUploadAccepted(
            job_id=job.id,
            file_id=recv.file_id,
            dataset_id=dataset_id,
        )
        return JSONResponse(
            status_code=202,
            content=body.model_dump(mode="json"),
            headers={"Location": f"/api/v1/ingest-jobs/{job.id}"},
        )

    @put_mapping("/{dataset_id}/tables/{table_id}:upload", status_code=201)
    async def reupload_file(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
        table_id: PathVar[uuid.UUID],
    ) -> ReuploadResponse:
        """Re-upload into an existing table slot; creates a new snapshot."""
        ctx = tenant_context_from_request(http_request)

        form = await http_request.form()
        upload = form.get("file")
        if upload is None:
            from flyquery.web.conventions.exceptions import InvalidRequest

            raise InvalidRequest("missing 'file' field in multipart form")

        filename: str = getattr(upload, "filename", None) or "upload.bin"
        file_bytes: bytes = await upload.read()

        ds = await self._datasets.get(dataset_id)
        if ds is None:
            raise ResourceNotFound(f"dataset {dataset_id!r} not found")

        actor = ctx.actor or ctx.tenant_id
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        result = await self._ingest.ingest_reupload(
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            table_id=table_id,
            filename=filename,
            file_bytes=file_bytes,
            actor=actor,
            dataset_name=ds["name"],
        )

        if not result.tables:
            raise ResourceNotFound(f"table {table_id!r} not found or no tables parsed from upload")

        first = result.tables[0]
        return ReuploadResponse(
            file_id=result.file_id,
            snapshot_id=first.snapshot_id,
            n_columns=first.n_columns,
            n_rows_actual=first.n_rows_estimate,
        )


def _form_or_header(form: Any, request: Any, name: str) -> str | None:
    """Read ``name`` from the multipart form, falling back to the matching header.

    Order:
      1. Form field ``name`` (canonical -- explicit and visible in cURL).
      2. ``X-Flyquery-Callback-{Name}`` request header (SDK convenience).

    Returns ``None`` if neither is present so the caller branches on
    "no callback configured" cleanly. We return ``None`` for empty
    strings too so a stray ``-F callback_url=`` doesn't enqueue.
    """
    value = form.get(name)
    if value is not None and isinstance(value, str) and value.strip():
        return value.strip()
    header_name = "X-Flyquery-Callback-" + name.removeprefix("callback_").replace("_", "-").title()
    header_value = request.headers.get(header_name)
    if header_value:
        return header_value.strip() or None
    return None


def _parse_workspace_id(workspace_id_str: str) -> uuid.UUID:
    """Convert workspace_id header value to UUID.

    The header may arrive as a full UUID (from tests + most callers) or
    as a slug (human-friendly). For slug-based IDs we'd need a DB lookup,
    but the integration test always passes the real UUID returned from
    POST /api/v1/workspaces, so UUID parse is the safe fast path.
    """
    try:
        return uuid.UUID(str(workspace_id_str))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"workspace_id header {workspace_id_str!r} is not a valid UUID") from exc
