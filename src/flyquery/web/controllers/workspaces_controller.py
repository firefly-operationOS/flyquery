# Copyright 2026 Firefly Software Solutions Inc
"""Workspace REST controller.

``/api/v1/workspaces`` -- CRUD for flyquery_workspaces.

Path conventions:
* ``POST   /api/v1/workspaces``                  -- create (201)
* ``GET    /api/v1/workspaces``                  -- list for tenant
* ``GET    /api/v1/workspaces/{workspace_id}``   -- fetch single
* ``PUT    /api/v1/workspaces/{workspace_id}``   -- sparse update
* ``DELETE /api/v1/workspaces/{workspace_id}:purge`` -- purge (202)
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

from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from flyquery.web.conventions import (
    ResourceNotFound,
    tenant_context_from_request,
)


@rest_controller
@request_mapping("/api/v1/workspaces")
class WorkspacesController:
    """REST adapter for ``flyquery_workspaces`` CRUD."""

    def __init__(self, service: WorkspaceService, object_store: ObjectStore) -> None:
        self._service = service
        self._object_store = object_store

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[WorkspaceCreate]],
    ) -> WorkspaceRead:
        """Create a workspace; tenant comes from ``X-Tenant-Id`` header."""
        ctx = tenant_context_from_request(http_request)
        row = await self._service.create(ctx.tenant_id, body)
        return WorkspaceRead.model_validate(row)

    @get_mapping("")
    async def list_workspaces(self, http_request: Request) -> dict:
        """Return all workspaces for the caller's tenant."""
        ctx = tenant_context_from_request(http_request)
        rows = await self._service.list(ctx.tenant_id)
        return {"items": [WorkspaceRead.model_validate(r).model_dump(mode="json") for r in rows]}

    @get_mapping("/{workspace_id}")
    async def read(
        self,
        http_request: Request,
        workspace_id: PathVar[uuid.UUID],
    ) -> WorkspaceRead:
        """Fetch a single workspace by id. Returns 404 if not found."""
        row = await self._service.get(workspace_id)
        if row is None:
            raise ResourceNotFound(f"workspace {workspace_id!r} not found")
        return WorkspaceRead.model_validate(row)

    @put_mapping("/{workspace_id}")
    async def update(
        self,
        workspace_id: PathVar[uuid.UUID],
        body: Valid[Body[WorkspaceUpdate]],
    ) -> WorkspaceRead:
        """Sparse-update a workspace. Only fields present in body are changed."""
        row = await self._service.update(workspace_id, body)
        return WorkspaceRead.model_validate(row)

    @delete_mapping("/{workspace_id}:purge", status_code=202)
    async def purge(
        self,
        http_request: Request,
        workspace_id: PathVar[uuid.UUID],
    ) -> dict:
        """Purge a workspace: mark PURGING + walk + delete all blobs.

        Returns 202 Accepted with a tombstone placeholder.
        """
        ctx = tenant_context_from_request(http_request)
        await self._service.purge(workspace_id, self._object_store, ctx.tenant_id)
        return {"status": "accepted", "tombstone_expires_at": "+30d"}
