# Copyright 2026 Firefly Software Solutions Inc
"""Schema changes controller.

POST /api/v1/schema-changes/{change_id}:confirm
  -- flip RENAMED_CANDIDATE → RENAMED + record approver

The controller is a thin HTTP adapter -- all SQL + the
RENAMED_CANDIDATE -> RENAMED state machine live in
:class:`SchemaChangeService`.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import PathVar, post_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.schema_changes.schema_change_service import (
    SchemaChangeNotFound,
    SchemaChangeService,
    SchemaChangeWrongState,
)
from flyquery.interfaces.files import SchemaChangeRead
from flyquery.web.conventions import InvalidRequest, ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/schema-changes")
class SchemaChangesController:
    """REST adapter for schema change lifecycle actions."""

    def __init__(self, service: SchemaChangeService) -> None:
        self._service = service

    @post_mapping("/{change_id}:confirm", status_code=200)
    async def confirm(
        self,
        http_request: Request,
        change_id: PathVar[uuid.UUID],
    ) -> SchemaChangeRead:
        """Flip a RENAMED_CANDIDATE row to RENAMED.

        Validates that the change exists and is in state RENAMED_CANDIDATE.
        Sets approved_by (the current actor / tenant_id), approved_at (now),
        change = 'RENAMED'.
        Also updates last_changed_at on the corresponding schema_objects column row.
        """
        ctx = tenant_context_from_request(http_request)
        try:
            confirmed = await self._service.confirm(
                change_id,
                tenant_id=ctx.tenant_id,
                approved_by=ctx.actor or ctx.tenant_id,
            )
        except SchemaChangeNotFound as exc:
            raise ResourceNotFound(str(exc)) from exc
        except SchemaChangeWrongState as exc:
            raise InvalidRequest(str(exc)) from exc

        row = confirmed.row
        return SchemaChangeRead(
            id=row["id"],
            table_id=row["table_id"],
            prev_snapshot_id=row.get("prev_snapshot_id"),
            next_snapshot_id=row["next_snapshot_id"],
            column_name=row["column_name"],
            change="RENAMED",
            before_json=row.get("before_json"),
            after_json=row.get("after_json"),
            llm_rationale=row.get("llm_rationale"),
            approved_by=confirmed.approved_by,
            approved_at=confirmed.approved_at,
            created_at=row["created_at"],
        )
