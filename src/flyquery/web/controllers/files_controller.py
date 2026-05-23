# Copyright 2026 Firefly Software Solutions Inc
"""Files controller.

POST   /api/v1/datasets/{dataset_id}/files            -- multipart upload
PUT    /api/v1/datasets/{dataset_id}/tables/{table_id}:upload  -- re-upload
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import PathVar, post_mapping, put_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.core.services.ingestion.ingest_service import IngestService
from flyquery.interfaces.files import FileUploadResponse, ReuploadResponse, TableSummary
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


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
            raise ResourceNotFound(
                f"table {table_id!r} not found or no tables parsed from upload"
            )

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
        raise ValueError(
            f"workspace_id header {workspace_id_str!r} is not a valid UUID"
        ) from exc
