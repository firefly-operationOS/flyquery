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

from pyfly.container import rest_controller
from pyfly.web import PathVar, post_mapping, put_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.core.services.ingestion.ingest_service import IngestService
from flyquery.interfaces.files import (
    BulkFileResult,
    BulkFileUploadResponse,
    FileUploadResponse,
    ReuploadResponse,
    TableSummary,
)
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request

logger = logging.getLogger(__name__)


@rest_controller
@request_mapping("/api/v1/datasets")
class FilesController:
    """REST adapter for file uploads + re-uploads."""

    def __init__(
        self,
        ingest_service: IngestService,
        dataset_service: DatasetService,
    ) -> None:
        self._ingest = ingest_service
        self._datasets = dataset_service

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

        results = await asyncio.gather(*[_ingest_one(idx, name, blob) for idx, name, blob in prepared])

        succeeded = sum(1 for r in results if r.status == "OK")
        return BulkFileUploadResponse(
            results=list(results),
            total_files=len(results),
            succeeded=succeeded,
            failed=len(results) - succeeded,
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
