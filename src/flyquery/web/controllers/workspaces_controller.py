# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Workspace REST controller.

``/api/v1/workspaces`` -- CRUD + search/filter for flyquery_workspaces.

Path conventions:
* ``POST   /api/v1/workspaces``                          -- create (201)
* ``GET    /api/v1/workspaces``                          -- list + search/filter
* ``GET    /api/v1/workspaces/by-slug/{slug}``           -- lookup by slug
* ``GET    /api/v1/workspaces/{workspace_id}``           -- fetch single by id
* ``PUT    /api/v1/workspaces/{workspace_id}``           -- sparse update
* ``DELETE /api/v1/workspaces/{workspace_id}:purge``     -- purge (202)

List supports query params: ``q`` (free-text against slug + name),
``slug`` (exact), ``status``, ``limit``, ``offset``. Response is an
envelope: ``{items, total, limit, offset, has_more}``.
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

from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.pagination import Paginated
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
    async def list_workspaces(
        self,
        http_request: Request,
        q: QueryParam[str] = None,
        slug: QueryParam[str] = None,
        status: QueryParam[str] = None,
        limit: QueryParam[int] = 100,
        offset: QueryParam[int] = 0,
    ) -> Paginated[WorkspaceRead]:
        """Search/filter workspaces for the caller's tenant.

        Query parameters
        ----------------
        * ``q``      -- free-text substring match against ``slug`` or ``name``
                        (case-insensitive ``ILIKE``).
        * ``slug``   -- exact match on ``slug`` -- gives you slug-based lookup
                        with zero extra round trips.
        * ``status`` -- exact match (``ACTIVE``, ``ARCHIVED``, ``PURGING``).
        * ``limit``  -- page size, clamped to [1, 1000]. Default 100.
        * ``offset`` -- starting offset. Default 0.

        Returns :class:`~flyquery.interfaces.pagination.Paginated`
        with ``total`` populated from the un-paginated match count.
        """
        ctx = tenant_context_from_request(http_request)
        rows, total = await self._service.list_filtered(
            ctx.tenant_id,
            q=q,
            slug=slug,
            status=status,
            limit=limit,
            offset=offset,
        )
        items = [WorkspaceRead.model_validate(r) for r in rows]
        return Paginated.of(items, total=total, limit=limit, offset=offset)

    @get_mapping("/by-slug/{slug}")
    async def read_by_slug(
        self,
        http_request: Request,
        slug: PathVar[str],
    ) -> WorkspaceRead:
        """Fetch a workspace by its ``(tenant_id, slug)`` natural key.

        Lets SDKs and CLIs resolve a workspace from a memorable identifier
        instead of carrying around a UUID. Returns 404 if no match.
        """
        ctx = tenant_context_from_request(http_request)
        row = await self._service.get_by_slug(ctx.tenant_id, slug)
        if row is None:
            raise ResourceNotFound(f"workspace with slug {slug!r} not found")
        return WorkspaceRead.model_validate(row)

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
