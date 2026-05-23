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

    async def get(self, dataset_id: uuid.UUID) -> dict[str, Any] | None:
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_datasets WHERE id = :id"),
                {"id": dataset_id},
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
