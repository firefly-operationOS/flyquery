# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_schema_changes.

The schema-change row is the audit trail for column-level renames
detected between snapshots. The repo exposes the three operations the
controller + service need:

* :meth:`get_for_update` -- lock the row for the confirm flow.
* :meth:`mark_renamed`   -- flip RENAMED_CANDIDATE -> RENAMED.
* :meth:`touch_column_object` -- bump the corresponding
  ``flyquery_schema_objects`` row's ``last_changed_at`` so consumers
  invalidate caches.

All three operations run inside a single transaction owned by
:meth:`confirm_transaction` so the lock + flip + touch happen
atomically.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class SchemaChangeRepository:
    """Repository over ``flyquery_schema_changes``."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def confirm_transaction(
        self,
        change_id: uuid.UUID,
        *,
        tenant_id: str,
        approved_by: str,
        approved_at: datetime,
    ) -> tuple[dict[str, Any] | None, str | None]:
        """Atomically lock + flip a RENAMED_CANDIDATE row to RENAMED.

        Returns ``(row, error)`` where ``error`` is one of:
        * ``None`` -- success; ``row`` is the pre-update snapshot of the
          row, with the new ``change/approved_by/approved_at`` values
          NOT applied. Callers must overlay the new values for the
          response shape.
        * ``"not_found"`` -- the row doesn't exist for this tenant.
        * ``"wrong_state"`` -- the row exists but isn't in
          ``RENAMED_CANDIDATE``; the caller maps to 422.

        The transaction also touches the corresponding column-level
        schema_object row so downstream caches invalidate.
        """
        async with self._factory() as s, s.begin():
            locked = await s.execute(
                sa.text(
                    "SELECT * FROM flyquery_schema_changes WHERE id = :cid AND tenant_id = :tenant FOR UPDATE"
                ),
                {"cid": change_id, "tenant": tenant_id},
            )
            row = locked.mappings().one_or_none()
            if row is None:
                return None, "not_found"
            row = dict(row)
            if row["change"] != "RENAMED_CANDIDATE":
                return row, "wrong_state"

            await s.execute(
                sa.text(
                    "UPDATE flyquery_schema_changes "
                    "SET change = 'RENAMED', "
                    "    approved_by = :approved_by, "
                    "    approved_at = :approved_at "
                    "WHERE id = :cid"
                ),
                {
                    "cid": change_id,
                    "approved_by": approved_by,
                    "approved_at": approved_at,
                },
            )

            # Bump last_changed_at on the column row so downstream
            # consumers invalidate caches. The column qualified_name is
            # ``{table_qn}.{column_name}``; we match on suffix.
            await s.execute(
                sa.text(
                    "UPDATE flyquery_schema_objects "
                    "SET last_changed_at = :now "
                    "WHERE snapshot_id = :snap_id "
                    "  AND tenant_id = :tenant "
                    "  AND kind = 'COLUMN' "
                    "  AND qualified_name LIKE :pattern"
                ),
                {
                    "now": approved_at,
                    "snap_id": row["next_snapshot_id"],
                    "tenant": tenant_id,
                    "pattern": f"%.{row['column_name']}",
                },
            )

            return row, None
