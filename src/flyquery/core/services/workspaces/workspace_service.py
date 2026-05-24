# Copyright 2026 Firefly Software Solutions Inc
"""Workspace service: defaults + invariants."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.workspaces.workspace_repository import WorkspaceRepository
from flyquery.interfaces.workspaces import WorkspaceCreate, WorkspaceUpdate


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]: ...
    async def list_filtered(
        self,
        tenant_id: str,
        *,
        q: str | None = None,
        slug: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]: ...
    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def get_by_slug(self, tenant_id: str, slug: str) -> dict[str, Any] | None: ...
    async def update(self, workspace_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def archive(self, workspace_id: uuid.UUID) -> None: ...
    async def mark_purging(self, workspace_id: uuid.UUID) -> None: ...
    async def increment_storage(self, workspace_id: uuid.UUID, delta_bytes: int) -> int: ...


@service_bean
class WorkspaceService:
    def __init__(self, workspace_repository: WorkspaceRepository) -> None:
        # Parameter renamed from ``repo`` to match snake-cased bean name.
        self._repo: _Repo = workspace_repository

    async def create(self, tenant_id: str, body: WorkspaceCreate) -> dict[str, Any]:
        return await self._repo.create(
            tenant_id=tenant_id,
            slug=body.slug,
            name=body.name,
            kms_key_uri=body.kms_key_uri,
            retention_days=body.retention_days,
            allow_direct_sql=body.allow_direct_sql,
            default_locale=body.default_locale,
            metadata_json=body.metadata_json,
            status="ACTIVE",
        )

    async def list(self, tenant_id: str) -> list[dict[str, Any]]:
        return await self._repo.list_by_tenant(tenant_id)

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        q: str | None = None,
        slug: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Filtered + paginated list. ``limit`` is clamped to [1, 1000]."""
        limit = max(1, min(1000, int(limit)))
        offset = max(0, int(offset))
        return await self._repo.list_filtered(
            tenant_id,
            q=q,
            slug=slug,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None:
        return await self._repo.get(workspace_id)

    async def get_by_slug(self, tenant_id: str, slug: str) -> dict[str, Any] | None:
        return await self._repo.get_by_slug(tenant_id, slug)

    async def update(self, workspace_id: uuid.UUID, body: WorkspaceUpdate) -> dict[str, Any]:
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        return await self._repo.update(workspace_id, **fields)

    async def archive(self, workspace_id: uuid.UUID) -> None:
        await self._repo.archive(workspace_id)

    async def track_storage(self, workspace_id: uuid.UUID, delta_bytes: int) -> int:
        """Atomically update storage_used_bytes by *delta_bytes*; returns new total.

        Use positive delta on upload, negative on deletion.
        """
        return await self._repo.increment_storage(workspace_id, delta_bytes)

    async def purge(self, workspace_id: uuid.UUID, object_store: ObjectStore, tenant_id: str) -> None:
        # 1. Archive in DB (sets status=PURGING → tombstone for 30 days)
        await self._repo.mark_purging(workspace_id)
        # 2. Walk the workspace prefix and delete every key
        prefix = f"flyquery/{tenant_id}/{workspace_id}/"
        async for meta in await object_store.list(prefix):
            await object_store.delete(meta.key)
        # 3. Terminal audit event written elsewhere (Plan 2: audit service)
