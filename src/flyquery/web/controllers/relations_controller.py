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

"""Relations controller.

GET  /api/v1/datasets/{dataset_id}/relations   -- list proposed/approved relations
POST /api/v1/relations/{relation_id}:approve   -- approve a PROPOSED relation
POST /api/v1/relations/{relation_id}:reject    -- reject a PROPOSED relation

The controller is a thin HTTP adapter -- all SQL lives in
:class:`RelationRepository` via :class:`RelationService`. Responses
flow through typed DTOs (:class:`RelationRead`,
:class:`RelationApprovalRead`, :class:`RelationRejectionRead`) so
the OpenAPI spec carries real schemas instead of ``dict``.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import PathVar, QueryParam, get_mapping, post_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.relations.relation_service import RelationService
from flyquery.interfaces.pagination import Paginated
from flyquery.interfaces.relations import (
    RelationApprovalRead,
    RelationRead,
    RelationRejectionRead,
)
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1")
class RelationsController:
    """REST adapter for dataset relations (heuristic + agent-proposed)."""

    def __init__(self, service: RelationService) -> None:
        self._service = service

    @get_mapping("/datasets/{dataset_id}/relations")
    async def list_relations(
        self,
        http_request: Request,
        dataset_id: PathVar[uuid.UUID],
        status: QueryParam[str] = None,
    ) -> Paginated[RelationRead]:
        """List relations for a dataset (all statuses by default).

        Optional ``status`` filter restricts to one of ``PROPOSED``,
        ``APPROVED``, ``REJECTED``.
        """
        ctx = tenant_context_from_request(http_request)
        rows = await self._service.list_for_dataset(dataset_id, tenant_id=ctx.tenant_id, status=status)
        items = [_row_to_read(r) for r in rows]
        return Paginated.of(items, total=len(items))

    @post_mapping("/relations/{relation_id}:approve", status_code=200)
    async def approve_relation(
        self,
        http_request: Request,
        relation_id: PathVar[uuid.UUID],
    ) -> RelationApprovalRead:
        """Approve a PROPOSED relation."""
        ctx = tenant_context_from_request(http_request)
        row = await self._service.approve(
            relation_id,
            tenant_id=ctx.tenant_id,
            approved_by=ctx.actor or ctx.tenant_id,
        )
        if row is None:
            raise ResourceNotFound(f"relation {relation_id!r} not found")
        return RelationApprovalRead.model_validate(row)

    @post_mapping("/relations/{relation_id}:reject", status_code=200)
    async def reject_relation(
        self,
        http_request: Request,
        relation_id: PathVar[uuid.UUID],
    ) -> RelationRejectionRead:
        """Reject a PROPOSED relation."""
        ctx = tenant_context_from_request(http_request)
        row = await self._service.reject(relation_id, tenant_id=ctx.tenant_id)
        if row is None:
            raise ResourceNotFound(f"relation {relation_id!r} not found")
        return RelationRejectionRead.model_validate(row)


def _row_to_read(row: dict) -> RelationRead:
    return RelationRead(
        id=row["id"],
        dataset_id=row["dataset_id"],
        from_table_id=row["from_table_id"],
        from_table_name=row.get("from_table_name"),
        from_column_name=row["from_column_name"],
        to_table_id=row["to_table_id"],
        to_table_name=row.get("to_table_name"),
        to_column_name=row["to_column_name"],
        kind=row["kind"],
        confidence=row["confidence"],
        reason=row.get("reason"),
        status=row["status"],
        approved_by=row.get("approved_by"),
        created_at=row["created_at"],
        updated_at=row.get("updated_at"),
    )
