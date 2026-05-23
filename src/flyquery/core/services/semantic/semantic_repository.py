# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_semantic_metrics + versions."""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class SemanticRepository:
    """Repository over ``flyquery_semantic_metrics`` + ``flyquery_semantic_versions``.

    Every write operation also appends a history row to
    ``flyquery_semantic_versions`` so full audit + rollback is possible.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    # ------------------------------------------------------------------
    # Metrics CRUD
    # ------------------------------------------------------------------

    async def create_metric(self, **fields: Any) -> dict[str, Any]:
        """Insert a new metric in DRAFT status and return the full record."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_semantic_metrics
                        (tenant_id, workspace_id, dataset_id, name, label,
                         description, definition_yaml, metric_type, status, current_version)
                    VALUES
                        (:tenant_id, :workspace_id, :dataset_id, :name, :label,
                         :description, :definition_yaml, :metric_type, 'DRAFT', 1)
                    RETURNING id, tenant_id, workspace_id, dataset_id, name, label,
                              description, definition_yaml, compiled_sql_template,
                              metric_type, status, current_version, created_at, updated_at
                    """
                ),
                fields,
            )
            row = dict(result.mappings().one())
            # Seed history version 1
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_semantic_versions
                        (tenant_id, workspace_id, kind, parent_id, version,
                         definition_yaml, compiled_sql_template, created_by)
                    VALUES
                        (:tenant_id, :workspace_id, 'metric', :parent_id, 1,
                         :definition_yaml, NULL, :created_by)
                    """
                ),
                {
                    "tenant_id": fields["tenant_id"],
                    "workspace_id": fields["workspace_id"],
                    "parent_id": row["id"],
                    "definition_yaml": fields["definition_yaml"],
                    "created_by": fields.get("created_by", "user"),
                },
            )
            return row

    async def list_metrics(
        self, tenant_id: str, workspace_id: uuid.UUID, *, dataset_id: uuid.UUID | None = None
    ) -> list[dict[str, Any]]:
        """Return all metrics for a workspace, optionally filtered by dataset."""
        params: dict[str, Any] = {"tenant_id": tenant_id, "workspace_id": workspace_id}
        extra = ""
        if dataset_id is not None:
            extra = "AND dataset_id = :dataset_id"
            params["dataset_id"] = dataset_id
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT id, tenant_id, workspace_id, dataset_id, name, label,
                           description, definition_yaml, compiled_sql_template,
                           metric_type, status, current_version, created_at, updated_at
                    FROM flyquery_semantic_metrics
                    WHERE tenant_id = :tenant_id AND workspace_id = :workspace_id {extra}
                    ORDER BY name
                    """
                ),
                params,
            )
            return [dict(r) for r in result.mappings().all()]

    async def get_metric(self, metric_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single metric by primary key."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, dataset_id, name, label,
                           description, definition_yaml, compiled_sql_template,
                           metric_type, status, current_version, created_at, updated_at
                    FROM flyquery_semantic_metrics WHERE id = :id
                    """
                ),
                {"id": metric_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update_metric(self, metric_id: uuid.UUID, **fields: Any) -> dict[str, Any]:
        """Sparse-update a metric, bump version, record history."""
        async with self._factory() as s, s.begin():
            # Fetch current version
            cur = await s.execute(
                sa.text(
                    "SELECT current_version, tenant_id, workspace_id, definition_yaml "
                    "FROM flyquery_semantic_metrics WHERE id = :id"
                ),
                {"id": metric_id},
            )
            cur_row = cur.mappings().one()
            new_version = cur_row["current_version"] + 1

            if not fields:
                return dict(cur_row)

            sets = ", ".join(f"{k} = :{k}" for k in fields)
            result = await s.execute(
                sa.text(
                    f"""
                    UPDATE flyquery_semantic_metrics
                    SET {sets}, current_version = :new_version, updated_at = now()
                    WHERE id = :id
                    RETURNING id, tenant_id, workspace_id, dataset_id, name, label,
                              description, definition_yaml, compiled_sql_template,
                              metric_type, status, current_version, created_at, updated_at
                    """
                ),
                {"id": metric_id, "new_version": new_version, **fields},
            )
            updated = dict(result.mappings().one())
            # Append history
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_semantic_versions
                        (tenant_id, workspace_id, kind, parent_id, version,
                         definition_yaml, compiled_sql_template, created_by)
                    VALUES
                        (:tenant_id, :workspace_id, 'metric', :parent_id, :version,
                         :definition_yaml, NULL, :created_by)
                    """
                ),
                {
                    "tenant_id": updated["tenant_id"],
                    "workspace_id": updated["workspace_id"],
                    "parent_id": metric_id,
                    "version": new_version,
                    "definition_yaml": fields.get("definition_yaml", cur_row["definition_yaml"]),
                    "created_by": fields.get("created_by", "user"),
                },
            )
            return updated

    async def publish_metric(self, metric_id: uuid.UUID, compiled_sql: str) -> dict[str, Any]:
        """Set status=PUBLISHED and persist the compiled SQL template."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_semantic_metrics
                    SET status = 'PUBLISHED',
                        compiled_sql_template = :compiled_sql,
                        updated_at = now()
                    WHERE id = :id
                    RETURNING id, tenant_id, workspace_id, dataset_id, name, label,
                              description, definition_yaml, compiled_sql_template,
                              metric_type, status, current_version, created_at, updated_at
                    """
                ),
                {"id": metric_id, "compiled_sql": compiled_sql},
            )
            return dict(result.mappings().one())

    async def retire_metric(self, metric_id: uuid.UUID) -> dict[str, Any]:
        """Set status=RETIRED."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_semantic_metrics
                    SET status = 'RETIRED', updated_at = now()
                    WHERE id = :id
                    RETURNING id, tenant_id, workspace_id, dataset_id, name, label,
                              description, definition_yaml, compiled_sql_template,
                              metric_type, status, current_version, created_at, updated_at
                    """
                ),
                {"id": metric_id},
            )
            return dict(result.mappings().one())

    # ------------------------------------------------------------------
    # Version history
    # ------------------------------------------------------------------

    async def list_history(self, metric_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return all version history rows for a metric, oldest first."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, kind, parent_id, version,
                           definition_yaml, compiled_sql_template, created_by, created_at
                    FROM flyquery_semantic_versions
                    WHERE kind = 'metric' AND parent_id = :parent_id
                    ORDER BY version
                    """
                ),
                {"parent_id": metric_id},
            )
            return [dict(r) for r in result.mappings().all()]
