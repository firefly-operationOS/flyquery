# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_workspaces."""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **fields: Any) -> dict[str, Any]:
        # Serialise metadata_json dict to a JSON string for the CAST
        if "metadata_json" in fields and isinstance(fields["metadata_json"], dict):
            fields = {**fields, "metadata_json": json.dumps(fields["metadata_json"])}
        result = await self._session.execute(
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
        result = await self._session.execute(
            sa.text(
                "SELECT * FROM flyquery_workspaces WHERE tenant_id = :tenant_id ORDER BY created_at"
            ),
            {"tenant_id": tenant_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None:
        result = await self._session.execute(
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
            f"{k} = CAST(:{k} AS jsonb)" if k == "metadata_json" else f"{k} = :{k}"
            for k in fields
        )
        result = await self._session.execute(
            sa.text(
                f"UPDATE flyquery_workspaces SET {sets}, updated_at = now() "
                "WHERE id = :id RETURNING *"
            ),
            {"id": workspace_id, **fields},
        )
        return dict(result.mappings().one())

    async def archive(self, workspace_id: uuid.UUID) -> None:
        await self._session.execute(
            sa.text("UPDATE flyquery_workspaces SET status='ARCHIVED', updated_at=now() WHERE id = :id"),
            {"id": workspace_id},
        )
