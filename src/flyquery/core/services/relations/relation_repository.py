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

"""Async SQLAlchemy repository for flyquery_relations.

Two read shapes + two state-machine writes:

* :meth:`list_for_dataset` -- JOIN flyquery_tables to enrich each row
  with ``from_table_name`` / ``to_table_name`` (saves a downstream
  N+1 lookup at the API edge). Filtered by status optionally.
* :meth:`approve` / :meth:`reject` -- UPDATE status to APPROVED /
  REJECTED, set approved_by + updated_at, return the post-update row.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class RelationRepository:
    """Repository over ``flyquery_relations``."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def list_for_dataset(
        self,
        dataset_id: uuid.UUID,
        *,
        tenant_id: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List relations (proposed + approved + rejected) for one dataset.

        Joins ``flyquery_tables`` twice so each row carries the
        from/to table *names* in addition to ids -- saves consumers a
        per-row table fetch.
        """
        params: dict[str, Any] = {"ds_id": dataset_id, "tenant": tenant_id}
        status_clause = ""
        if status:
            status_clause = " AND r.status = :status"
            params["status"] = status
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT r.*,
                           ft.name AS from_table_name,
                           tt.name AS to_table_name
                    FROM flyquery_relations r
                    LEFT JOIN flyquery_tables ft ON ft.id = r.from_table_id
                    LEFT JOIN flyquery_tables tt ON tt.id = r.to_table_id
                    WHERE r.dataset_id = :ds_id
                      AND r.tenant_id = :tenant
                      {status_clause}
                    ORDER BY r.confidence DESC, r.created_at
                    """
                ),
                params,
            )
            return [dict(r) for r in result.mappings().all()]

    async def approve(
        self,
        relation_id: uuid.UUID,
        *,
        tenant_id: str,
        approved_by: str,
        approved_at: datetime,
    ) -> dict[str, Any] | None:
        """Flip a relation to APPROVED. Returns the updated row or ``None``."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    "UPDATE flyquery_relations "
                    "SET status = 'APPROVED', approved_by = :approved_by, updated_at = :now "
                    "WHERE id = :rid AND tenant_id = :tenant "
                    "RETURNING id, status, approved_by, updated_at"
                ),
                {
                    "rid": relation_id,
                    "tenant": tenant_id,
                    "approved_by": approved_by,
                    "now": approved_at,
                },
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def reject(
        self,
        relation_id: uuid.UUID,
        *,
        tenant_id: str,
        updated_at: datetime,
    ) -> dict[str, Any] | None:
        """Flip a relation to REJECTED. Returns the updated row or ``None``."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    "UPDATE flyquery_relations "
                    "SET status = 'REJECTED', updated_at = :now "
                    "WHERE id = :rid AND tenant_id = :tenant "
                    "RETURNING id, status, updated_at"
                ),
                {"rid": relation_id, "tenant": tenant_id, "now": updated_at},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None
