# Copyright 2026 Firefly Software Solutions Inc
"""Dataset service: defaults + invariants."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.datasets.dataset_repository import DatasetRepository
from flyquery.interfaces.datasets import DatasetCreate, DatasetUpdate


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list(self, tenant_id: str, workspace_id: uuid.UUID) -> list[dict[str, Any]]: ...
    async def get(self, dataset_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update(self, dataset_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def archive(self, dataset_id: uuid.UUID) -> None: ...


@service_bean
class DatasetService:
    def __init__(self, repo: DatasetRepository) -> None:
        self._repo: _Repo = repo

    async def create(self, tenant_id: str, workspace_id: uuid.UUID, body: DatasetCreate) -> dict[str, Any]:
        return await self._repo.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            name=body.name,
            description=body.description,
            drift_policy=body.drift_policy,
            default_locale=body.default_locale,
            ingest_policy_json=body.ingest_policy_json,
            metadata_json=body.metadata_json,
            status="ACTIVE",
        )

    async def list(self, tenant_id: str, workspace_id: uuid.UUID) -> list[dict[str, Any]]:
        return await self._repo.list(tenant_id, workspace_id)

    async def get(self, dataset_id: uuid.UUID) -> dict[str, Any] | None:
        return await self._repo.get(dataset_id)

    async def update(self, dataset_id: uuid.UUID, body: DatasetUpdate) -> dict[str, Any]:
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        return await self._repo.update(dataset_id, **fields)

    async def archive(self, dataset_id: uuid.UUID) -> None:
        await self._repo.archive(dataset_id)
