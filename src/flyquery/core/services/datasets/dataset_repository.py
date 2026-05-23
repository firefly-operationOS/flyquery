# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_datasets."""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class DatasetRepository:
    """Repository over ``flyquery_datasets``.

    Takes an ``async_sessionmaker`` so each operation owns its own
    session + transaction lifetime. Pyfly's relational auto-configuration
    exposes ``async_session_factory`` as an ``async_sessionmaker[AsyncSession]``
    bean -- the DI container wires it here by type.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create(self, **fields: Any) -> dict[str, Any]:
        for key in ("ingest_policy_json", "metadata_json"):
            if key in fields and isinstance(fields[key], dict):
                fields = {**fields, key: json.dumps(fields[key])}
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_datasets
                        (tenant_id, workspace_id, name, description, drift_policy,
                         default_locale, ingest_policy_json, metadata_json)
                    VALUES
                        (:tenant_id, :workspace_id, :name, :description, :drift_policy,
                         :default_locale,
                         CAST(:ingest_policy_json AS jsonb), CAST(:metadata_json AS jsonb))
                    RETURNING id, tenant_id, workspace_id, name, description, drift_policy,
                              default_locale, ingest_policy_json, status,
                              created_at, updated_at, metadata_json
                    """
                ),
                fields,
            )
            row = result.mappings().one()
            return dict(row)

    async def list(self, tenant_id: str, workspace_id: uuid.UUID) -> list[dict[str, Any]]:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    "SELECT * FROM flyquery_datasets "
                    "WHERE tenant_id = :tenant_id AND workspace_id = :workspace_id "
                    "ORDER BY created_at"
                ),
                {"tenant_id": tenant_id, "workspace_id": workspace_id},
            )
            return [dict(row) for row in result.mappings().all()]

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        workspace_id: uuid.UUID | None = None,
        q: str | None = None,
        name: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search/filter + paginate datasets.

        ``workspace_id`` is optional: when omitted, the search spans every
        workspace in the tenant. With it, the search is scoped to that
        workspace -- equivalent to the original list endpoint.

        Returns ``(rows, total_unpaginated_count)``.
        """
        like = f"%{q}%" if q else None
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "q": like,
            "name": name,
            "status": status,
            "limit": int(limit),
            "offset": int(offset),
        }
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT *, COUNT(*) OVER () AS _total
                    FROM flyquery_datasets
                    WHERE tenant_id = :tenant_id
                      AND (CAST(:workspace_id AS uuid) IS NULL OR workspace_id = CAST(:workspace_id AS uuid))
                      AND (CAST(:name AS text) IS NULL OR name = CAST(:name AS text))
                      AND (CAST(:status AS text) IS NULL OR status = CAST(:status AS text))
                      AND (CAST(:q AS text) IS NULL
                           OR name ILIKE CAST(:q AS text)
                           OR COALESCE(description, '') ILIKE CAST(:q AS text))
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                params,
            )
            rows = [dict(r) for r in result.mappings().all()]
        if not rows:
            return [], await self._count_filtered(
                tenant_id,
                workspace_id=workspace_id,
                q=q,
                name=name,
                status=status,
            )
        total = int(rows[0].pop("_total"))
        for r in rows[1:]:
            r.pop("_total", None)
        return rows, total

    async def _count_filtered(
        self,
        tenant_id: str,
        *,
        workspace_id: uuid.UUID | None,
        q: str | None,
        name: str | None,
        status: str | None,
    ) -> int:
        like = f"%{q}%" if q else None
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT COUNT(*) AS n
                    FROM flyquery_datasets
                    WHERE tenant_id = :tenant_id
                      AND (CAST(:workspace_id AS uuid) IS NULL OR workspace_id = CAST(:workspace_id AS uuid))
                      AND (CAST(:name AS text) IS NULL OR name = CAST(:name AS text))
                      AND (CAST(:status AS text) IS NULL OR status = CAST(:status AS text))
                      AND (CAST(:q AS text) IS NULL
                           OR name ILIKE CAST(:q AS text)
                           OR COALESCE(description, '') ILIKE CAST(:q AS text))
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "q": like,
                    "name": name,
                    "status": status,
                },
            )
            return int(result.scalar_one())

    async def get(self, dataset_id: uuid.UUID) -> dict[str, Any] | None:
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_datasets WHERE id = :id"),
                {"id": dataset_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def get_by_name(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        name: str,
    ) -> dict[str, Any] | None:
        """Resolve a dataset by ``(tenant_id, workspace_id, name)``."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    "SELECT * FROM flyquery_datasets "
                    "WHERE tenant_id = :tenant_id "
                    "AND workspace_id = :workspace_id "
                    "AND name = :name"
                ),
                {"tenant_id": tenant_id, "workspace_id": workspace_id, "name": name},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update(self, dataset_id: uuid.UUID, **fields: Any) -> dict[str, Any]:
        if not fields:
            row = await self.get(dataset_id)
            assert row is not None
            return row
        for key in ("ingest_policy_json", "metadata_json"):
            if key in fields and isinstance(fields[key], dict):
                fields = {**fields, key: json.dumps(fields[key])}
        sets = ", ".join(
            f"{k} = CAST(:{k} AS jsonb)" if k in ("ingest_policy_json", "metadata_json") else f"{k} = :{k}"
            for k in fields
        )
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    f"UPDATE flyquery_datasets SET {sets}, updated_at = now() WHERE id = :id RETURNING *"
                ),
                {"id": dataset_id, **fields},
            )
            return dict(result.mappings().one())

    async def archive(self, dataset_id: uuid.UUID) -> None:
        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text("UPDATE flyquery_datasets SET status='ARCHIVED', updated_at=now() WHERE id = :id"),
                {"id": dataset_id},
            )
