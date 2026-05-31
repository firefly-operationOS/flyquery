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

"""Async SQLAlchemy repository for flyquery_workspaces."""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class WorkspaceRepository:
    """Repository over ``flyquery_workspaces``.

    Takes an ``async_sessionmaker`` so each operation owns its own
    session + transaction lifetime. Pyfly's relational auto-configuration
    exposes ``async_session_factory`` as an ``async_sessionmaker[AsyncSession]``
    bean -- the DI container wires it here by type.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create(self, **fields: Any) -> dict[str, Any]:
        if "metadata_json" in fields and isinstance(fields["metadata_json"], dict):
            fields = {**fields, "metadata_json": json.dumps(fields["metadata_json"])}
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_workspaces
                        (tenant_id, slug, name, kms_key_uri, retention_days,
                         allow_direct_sql, default_locale, metadata_json)
                    VALUES
                        (:tenant_id, :slug, :name, :kms_key_uri, :retention_days,
                         :allow_direct_sql, :default_locale, CAST(:metadata_json AS jsonb))
                    RETURNING id, tenant_id, slug, name, kms_key_uri, retention_days,
                              allow_direct_sql, default_locale, storage_used_bytes,
                              status, created_at, updated_at, metadata_json
                    """
                ),
                fields,
            )
            row = result.mappings().one()
            return dict(row)

    async def list_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_workspaces WHERE tenant_id = :tenant_id ORDER BY created_at"),
                {"tenant_id": tenant_id},
            )
            return [dict(row) for row in result.mappings().all()]

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
        """Search/filter + paginate. Returns ``(rows, total_unpaginated_count)``.

        Filters
        -------
        * ``q``      -- case-insensitive substring against ``slug`` OR ``name``.
        * ``slug``   -- exact match on ``slug``.
        * ``status`` -- exact match on ``status`` (e.g. ``ACTIVE``).

        ``total`` is the full match count BEFORE limit/offset so SDKs can
        paginate without a second round-trip.
        """
        like = f"%{q}%" if q else None
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "q": like,
            "slug": slug,
            "status": status,
            "limit": int(limit),
            "offset": int(offset),
        }
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT *, COUNT(*) OVER () AS _total
                    FROM flyquery_workspaces
                    WHERE tenant_id = :tenant_id
                      AND (CAST(:slug AS text) IS NULL OR slug = CAST(:slug AS text))
                      AND (CAST(:status AS text) IS NULL OR status = CAST(:status AS text))
                      AND (CAST(:q AS text) IS NULL
                           OR name ILIKE CAST(:q AS text)
                           OR slug ILIKE CAST(:q AS text))
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                params,
            )
            rows = [dict(r) for r in result.mappings().all()]
        if not rows:
            # No rows; need a separate count query since the window can't run.
            return [], await self._count_filtered(tenant_id, q=q, slug=slug, status=status)
        total = int(rows[0].pop("_total"))
        for r in rows[1:]:
            r.pop("_total", None)
        return rows, total

    async def _count_filtered(
        self,
        tenant_id: str,
        *,
        q: str | None,
        slug: str | None,
        status: str | None,
    ) -> int:
        like = f"%{q}%" if q else None
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT COUNT(*) AS n
                    FROM flyquery_workspaces
                    WHERE tenant_id = :tenant_id
                      AND (CAST(:slug AS text) IS NULL OR slug = CAST(:slug AS text))
                      AND (CAST(:status AS text) IS NULL OR status = CAST(:status AS text))
                      AND (CAST(:q AS text) IS NULL
                           OR name ILIKE CAST(:q AS text)
                           OR slug ILIKE CAST(:q AS text))
                    """
                ),
                {"tenant_id": tenant_id, "q": like, "slug": slug, "status": status},
            )
            return int(result.scalar_one())

    async def get_by_slug(self, tenant_id: str, slug: str) -> dict[str, Any] | None:
        """Return the (at most one) workspace with matching ``tenant_id`` + ``slug``."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_workspaces WHERE tenant_id = :tenant_id AND slug = :slug"),
                {"tenant_id": tenant_id, "slug": slug},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None:
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_workspaces WHERE id = :id"),
                {"id": workspace_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update(self, workspace_id: uuid.UUID, **fields: Any) -> dict[str, Any]:
        if not fields:
            row = await self.get(workspace_id)
            assert row is not None
            return row
        if "metadata_json" in fields and isinstance(fields["metadata_json"], dict):
            fields = {**fields, "metadata_json": json.dumps(fields["metadata_json"])}
        sets = ", ".join(
            f"{k} = CAST(:{k} AS jsonb)" if k == "metadata_json" else f"{k} = :{k}" for k in fields
        )
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    f"UPDATE flyquery_workspaces SET {sets}, updated_at = now() WHERE id = :id RETURNING *"
                ),
                {"id": workspace_id, **fields},
            )
            return dict(result.mappings().one())

    async def archive(self, workspace_id: uuid.UUID) -> None:
        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text("UPDATE flyquery_workspaces SET status='ARCHIVED', updated_at=now() WHERE id = :id"),
                {"id": workspace_id},
            )

    async def mark_purging(self, workspace_id: uuid.UUID) -> None:
        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text("UPDATE flyquery_workspaces SET status='PURGING', updated_at=now() WHERE id = :id"),
                {"id": workspace_id},
            )

    async def increment_storage(self, workspace_id: uuid.UUID, delta_bytes: int) -> int:
        """Atomically add *delta_bytes* to storage_used_bytes; returns new total.

        Negative values are used on deletion to reclaim quota.
        The column is clamped to 0 to guard against underflow from
        concurrent deletes.
        """
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_workspaces
                    SET storage_used_bytes = GREATEST(0, storage_used_bytes + :delta),
                        updated_at = now()
                    WHERE id = :id
                    RETURNING storage_used_bytes
                    """
                ),
                {"id": workspace_id, "delta": delta_bytes},
            )
            return result.scalar_one()
