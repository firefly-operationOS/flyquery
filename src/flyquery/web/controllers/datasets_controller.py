# Copyright 2026 Firefly Software Solutions Inc
"""Dataset REST controller.

``/api/v1/datasets`` -- CRUD + search/filter for flyquery_datasets.

Path conventions:
* ``POST   /api/v1/datasets``                   -- create (201)
* ``GET    /api/v1/datasets``                   -- list + search/filter
* ``GET    /api/v1/datasets/by-name/{name}``    -- resolve by (workspace, name)
* ``GET    /api/v1/datasets/{dataset_id}``      -- fetch single by id
* ``PUT    /api/v1/datasets/{dataset_id}``      -- sparse update
* ``DELETE /api/v1/datasets/{dataset_id}``      -- archive (200)

List supports query params: ``q`` (free-text on name + description),
``name`` (exact), ``status``, ``workspace_id`` (optional override of
``X-Workspace-Id`` header -- pass blank to span every workspace in
the tenant), ``limit``, ``offset``. Response is an envelope:
``{items, total, limit, offset, has_more}``.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import (
    Body,
    PathVar,
    QueryParam,
    Valid,
    delete_mapping,
    get_mapping,
    post_mapping,
    put_mapping,
    request_mapping,
)
from starlette.requests import Request

from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.core.services.ops.audit_event_service import AuditEventService
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.interfaces.datasets import (
    DatasetCreate,
    DatasetRead,
    DatasetUpdate,
)
from flyquery.interfaces.lifecycle import PurgeAccepted
from flyquery.interfaces.pagination import Paginated
from flyquery.web.conventions import (
    HEADER_CORRELATION_ID,
    ResourceNotFound,
    tenant_context_from_request,
)


@rest_controller
@request_mapping("/api/v1/datasets")
class DatasetsController:
    """REST adapter for ``flyquery_datasets`` CRUD."""

    def __init__(
        self,
        service: DatasetService,
        object_store: ObjectStore,
        audit: AuditEventService,
    ) -> None:
        self._service = service
        self._object_store = object_store
        self._audit = audit

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[DatasetCreate]],
    ) -> DatasetRead:
        """Create a dataset; tenant + workspace come from request headers."""
        ctx = tenant_context_from_request(http_request)
        row = await self._service.create(ctx.tenant_id, ctx.workspace_id, body)
        # Audit: dataset.created. Best-effort -- a failed audit never
        # breaks the create.
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        await self._audit.record(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            actor=ctx.actor or "anonymous",
            event_type="dataset.created",
            resource_kind="dataset",
            resource_id=str(row["id"]),
            correlation_id=http_request.headers.get(HEADER_CORRELATION_ID),
            payload={"name": body.name},
        )
        return DatasetRead.model_validate(row)

    @get_mapping("")
    async def list_datasets(
        self,
        http_request: Request,
        q: QueryParam[str] = None,
        name: QueryParam[str] = None,
        status: QueryParam[str] = None,
        workspace_id: QueryParam[uuid.UUID] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[DatasetRead]:
        """Search/filter datasets for the caller's tenant.

        Query parameters
        ----------------
        * ``q``            -- free-text substring against ``name`` or
                              ``description`` (case-insensitive ``ILIKE``).
        * ``name``         -- exact match -- gives you name-based lookup
                              with zero extra round-trips.
        * ``status``       -- ``ACTIVE`` / ``ARCHIVED`` / ``PURGING``.
        * ``workspace_id`` -- restrict to a single workspace; defaults to
                              ``X-Workspace-Id`` header. Pass another UUID
                              explicitly to override the header.
        * ``limit``        -- page size, clamped to [1, 1000]. Default 100.
        * ``offset``       -- starting offset. Default 0.

        Response envelope: ``{items, total, limit, offset, has_more}``.
        """
        ctx = tenant_context_from_request(http_request)
        effective_ws: uuid.UUID
        if workspace_id is not None:
            effective_ws = workspace_id
        else:
            effective_ws = (
                uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
            )
        rows, total = await self._service.list_filtered(
            ctx.tenant_id,
            workspace_id=effective_ws,
            q=q,
            name=name,
            status=status,
            limit=limit,
            offset=offset,
        )
        items = [DatasetRead.model_validate(r) for r in rows]
        return Paginated.of(items, total=total, limit=limit, offset=offset)

    @get_mapping("/by-name/{name}")
    async def read_by_name(
        self,
        http_request: Request,
        name: PathVar[str],
    ) -> DatasetRead:
        """Resolve a dataset by ``(tenant_id, workspace_id, name)``.

        Reads the workspace scope from ``X-Workspace-Id``. Datasets enforce
        ``UNIQUE(workspace_id, name)`` so the lookup always returns 0 or 1.
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        row = await self._service.get_by_name(ctx.tenant_id, ws, name)
        if row is None:
            raise ResourceNotFound(f"dataset with name {name!r} not found in this workspace")
        return DatasetRead.model_validate(row)

    @get_mapping("/{dataset_id}")
    async def read(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> DatasetRead:
        """Fetch a single dataset by id. Returns 404 if not found."""
        row = await self._service.get(dataset_id)
        if row is None:
            raise ResourceNotFound(f"dataset {dataset_id!r} not found")
        return DatasetRead.model_validate(row)

    @put_mapping("/{dataset_id}")
    async def update(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
        body: Valid[Body[DatasetUpdate]],
    ) -> DatasetRead:
        """Sparse-update a dataset. Only fields present in body are changed."""
        ctx = tenant_context_from_request(http_request)
        row = await self._service.update(dataset_id, body)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        await self._audit.record(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            actor=ctx.actor or "anonymous",
            event_type="dataset.updated",
            resource_kind="dataset",
            resource_id=str(dataset_id),
            correlation_id=http_request.headers.get(HEADER_CORRELATION_ID),
            payload=body.model_dump(exclude_unset=True, exclude_none=True, mode="json"),
        )
        return DatasetRead.model_validate(row)

    @delete_mapping("/{dataset_id}")
    async def archive(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> DatasetRead:
        """Archive a dataset (set status=ARCHIVED).

        Soft-delete only -- the underlying Parquet sample / snapshot /
        result blobs stay on the object store. Use
        ``DELETE /datasets/{id}:purge`` to additionally reclaim storage.
        """
        ctx = tenant_context_from_request(http_request)
        await self._service.archive(dataset_id)
        row = await self._service.get(dataset_id)
        assert row is not None
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        await self._audit.record(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            actor=ctx.actor or "anonymous",
            event_type="dataset.archived",
            resource_kind="dataset",
            resource_id=str(dataset_id),
            correlation_id=http_request.headers.get(HEADER_CORRELATION_ID),
        )
        return DatasetRead.model_validate(row)

    @delete_mapping("/{dataset_id}:purge", status_code=202)
    async def purge(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
    ) -> PurgeAccepted:
        """Hard-delete: flip status to PURGING and reclaim every blob.

        Walks ``flyquery/{tenant}/{workspace}/{dataset}/`` on the object
        store and removes every key -- samples, snapshots, derived
        Parquets, query results. Returns 202 with a tombstone hint.

        The SQL row stays in place with ``status=PURGING`` so audit /
        lineage references survive. A separate retention job (90-day
        window, mirroring ``conv_ttl_days``) is responsible for the
        final row delete.
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        ds = await self._service.get(dataset_id)
        if ds is None:
            raise ResourceNotFound(f"dataset {dataset_id!r} not found")
        await self._service.purge(
            dataset_id,
            object_store=self._object_store,
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
        )
        await self._audit.record(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            actor=ctx.actor or "anonymous",
            event_type="dataset.purged",
            resource_kind="dataset",
            resource_id=str(dataset_id),
            correlation_id=http_request.headers.get(HEADER_CORRELATION_ID),
        )
        return PurgeAccepted(status="accepted", tombstone_expires_at="+90d")
