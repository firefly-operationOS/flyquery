# Copyright 2026 Firefly Software Solutions Inc
"""Schema changes controller.

POST /api/v1/schema-changes/{change_id}:confirm
  -- flip RENAMED_CANDIDATE → RENAMED + record approver
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from pyfly.container import rest_controller
from pyfly.web import PathVar, post_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from flyquery.interfaces.files import SchemaChangeRead
from flyquery.web.conventions import InvalidRequest, ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/schema-changes")
class SchemaChangesController:
    """REST adapter for schema change lifecycle actions."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

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
        approved_by = ctx.actor or ctx.tenant_id
        now = datetime.now(timezone.utc)

        async with self._factory() as s, s.begin():
            # --- Load the change row ---
            result = await s.execute(
                sa.text(
                    """
                    SELECT * FROM flyquery_schema_changes
                    WHERE id = :cid AND tenant_id = :tenant
                    FOR UPDATE
                    """
                ),
                {"cid": change_id, "tenant": ctx.tenant_id},
            )
            row = result.mappings().one_or_none()

            if row is None:
                raise ResourceNotFound(f"schema change {change_id!r} not found")

            row = dict(row)

            if row["change"] != "RENAMED_CANDIDATE":
                raise InvalidRequest(
                    f"change {change_id!r} has status {row['change']!r}; "
                    f"only RENAMED_CANDIDATE rows can be confirmed"
                )

            # --- Flip to RENAMED ---
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_changes
                    SET change = 'RENAMED', approved_by = :approved_by, approved_at = :approved_at
                    WHERE id = :cid
                    """
                ),
                {"cid": change_id, "approved_by": approved_by, "approved_at": now},
            )

            # --- Update last_changed_at on the target schema_objects row.
            # The after_json has {"candidates": [new_col_names]} or similar.
            # We update the table-level schema_object's last_changed_at.
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET last_changed_at = :now
                    WHERE snapshot_id = :snap_id
                      AND tenant_id = :tenant
                      AND kind = 'COLUMN'
                      AND qualified_name LIKE :pattern
                    """
                ),
                {
                    "now": now,
                    "snap_id": row["next_snapshot_id"],
                    "tenant": ctx.tenant_id,
                    "pattern": f"%.{row['column_name']}",
                },
            )

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
            approved_by=approved_by,
            approved_at=now,
            created_at=row["created_at"],
        )
