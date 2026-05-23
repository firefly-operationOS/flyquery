# Copyright 2026 Firefly Software Solutions Inc
"""Dataset REST controller.

``/api/v1/datasets`` -- CRUD for flyquery_datasets.

Path conventions:
* ``POST   /api/v1/datasets``               -- create (201)
* ``GET    /api/v1/datasets``               -- list for tenant+workspace
* ``GET    /api/v1/datasets/{dataset_id}``  -- fetch single
* ``PUT    /api/v1/datasets/{dataset_id}``  -- sparse update
* ``DELETE /api/v1/datasets/{dataset_id}``  -- archive (200)
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import (
    Body,
    PathVar,
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
    async def list_datasets(self, http_request: Request) -> dict:
        """Return all datasets for the caller's tenant+workspace."""
        ctx = tenant_context_from_request(http_request)
        rows = await self._service.list(ctx.tenant_id, ctx.workspace_id)
        return {"items": [DatasetRead.model_validate(r).model_dump(mode="json") for r in rows]}

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
