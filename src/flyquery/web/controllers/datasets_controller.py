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
from typing import Optional

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
from flyquery.interfaces.datasets import (
    DatasetCreate,
    DatasetRead,
    DatasetUpdate,
)
from flyquery.web.conventions import (
    ResourceNotFound,
    tenant_context_from_request,
)


@rest_controller
@request_mapping("/api/v1/datasets")
class DatasetsController:
    """REST adapter for ``flyquery_datasets`` CRUD."""

    def __init__(self, service: DatasetService) -> None:
        self._service = service

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[DatasetCreate]],
    ) -> DatasetRead:
        """Create a dataset; tenant + workspace come from request headers."""
        ctx = tenant_context_from_request(http_request)
        row = await self._service.create(ctx.tenant_id, ctx.workspace_id, body)
        return DatasetRead.model_validate(row)

    @get_mapping("")
    async def list_datasets(
        self,
        http_request: Request,
        q: QueryParam[Optional[str]] = None,
        name: QueryParam[Optional[str]] = None,
        status: QueryParam[Optional[str]] = None,
        workspace_id: QueryParam[Optional[uuid.UUID]] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> dict:
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
        items = [DatasetRead.model_validate(r).model_dump(mode="json") for r in rows]
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(items)) < total,
        }

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
        dataset_id: PathVar[uuid.UUID],
        body: Valid[Body[DatasetUpdate]],
    ) -> DatasetRead:
        """Sparse-update a dataset. Only fields present in body are changed."""
        row = await self._service.update(dataset_id, body)
        return DatasetRead.model_validate(row)

    @delete_mapping("/{dataset_id}")
    async def archive(self, dataset_id: PathVar[uuid.UUID]) -> DatasetRead:
        """Archive a dataset (set status=ARCHIVED)."""
        await self._service.archive(dataset_id)
        row = await self._service.get(dataset_id)
        assert row is not None
        return DatasetRead.model_validate(row)
