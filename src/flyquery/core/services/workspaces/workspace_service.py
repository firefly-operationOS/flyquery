# Copyright 2026 Firefly Software Solutions Inc
"""Workspace service: defaults + invariants."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.workspaces.workspace_repository import WorkspaceRepository
from flyquery.interfaces.workspaces import WorkspaceCreate, WorkspaceUpdate


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]: ...
    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update(self, workspace_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def archive(self, workspace_id: uuid.UUID) -> None: ...


@service_bean
class WorkspaceService:
    def __init__(self, repo: WorkspaceRepository) -> None:
        self._repo: _Repo = repo

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

    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None:
        return await self._repo.get(workspace_id)

    async def update(self, workspace_id: uuid.UUID, body: WorkspaceUpdate) -> dict[str, Any]:
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        return await self._repo.update(workspace_id, **fields)

    async def archive(self, workspace_id: uuid.UUID) -> None:
        await self._repo.archive(workspace_id)
