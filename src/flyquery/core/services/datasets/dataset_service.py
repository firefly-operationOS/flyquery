# Copyright 2026 Firefly Software Solutions Inc
"""Dataset service: defaults + invariants."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.datasets.dataset_repository import DatasetRepository
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.interfaces.datasets import DatasetCreate, DatasetUpdate


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list(self, tenant_id: str, workspace_id: uuid.UUID) -> list[dict[str, Any]]: ...
    async def list_filtered(
        self,
        tenant_id: str,
        *,
        workspace_id: uuid.UUID | None = None,
        q: str | None = None,
        name: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]: ...
    async def get(self, dataset_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def get_by_name(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        name: str,
    ) -> dict[str, Any] | None: ...
    async def update(self, dataset_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def archive(self, dataset_id: uuid.UUID) -> None: ...
    async def mark_purging(self, dataset_id: uuid.UUID) -> None: ...


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

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        workspace_id: uuid.UUID | None = None,
        q: str | None = None,
        name: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Filtered + paginated list. ``limit`` clamped to [1, 1000]."""
        limit = max(1, min(1000, int(limit)))
        offset = max(0, int(offset))
        return await self._repo.list_filtered(
            tenant_id,
            workspace_id=workspace_id,
            q=q,
            name=name,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def get(self, dataset_id: uuid.UUID) -> dict[str, Any] | None:
        return await self._repo.get(dataset_id)

    async def get_by_name(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        name: str,
    ) -> dict[str, Any] | None:
        return await self._repo.get_by_name(tenant_id, workspace_id, name)

    async def update(self, dataset_id: uuid.UUID, body: DatasetUpdate) -> dict[str, Any]:
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        return await self._repo.update(dataset_id, **fields)

    async def archive(self, dataset_id: uuid.UUID) -> None:
        await self._repo.archive(dataset_id)

    async def purge(
        self,
        dataset_id: uuid.UUID,
        *,
        object_store: ObjectStore,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> None:
        """Hard-delete a dataset's blobs and flip status to PURGING.

        Mirrors :meth:`WorkspaceService.purge` at one level down --
        ``DELETE /datasets/{id}`` only archived (status='ARCHIVED'),
        leaving the dataset's sample / snapshot / result / derived
        Parquet blobs orphaned on the object store. This method:

        1. Flips ``status`` to ``PURGING`` so concurrent reads see the
           in-flight purge.
        2. Walks the canonical dataset prefix
           ``flyquery/{tenant}/{workspace}/{dataset}/`` and deletes
           every key under it. The four subprefixes that exist today
           are ``files/``, ``tables/``, ``derived/`` and ``results/``;
           all are reclaimed in one walk.
        3. Leaves the SQL row in place with status=PURGING. A separate
           retention job is expected to hard-delete the row after the
           tombstone window (90 days by convention -- same as
           ``conv_ttl_days``). Keeping the row preserves audit + lineage
           pointers for any historical reference.

        Caller is responsible for ensuring the dataset belongs to the
        passed ``(tenant_id, workspace_id)`` before invoking this --
        the controller checks tenant context, then forwards.
        """
        await self._repo.mark_purging(dataset_id)
        prefix = f"flyquery/{tenant_id}/{workspace_id}/{dataset_id}/"
        async for meta in await object_store.list(prefix):
            await object_store.delete(meta.key)
