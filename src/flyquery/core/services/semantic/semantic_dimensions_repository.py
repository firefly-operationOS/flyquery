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

"""Async SQLAlchemy repository for flyquery_semantic_dimensions + versions.

Mirrors :class:`SemanticRepository`: tenant + workspace scoped, version rows
capture the compiled expression, and publish records the compiled SQL on the
current version row.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_COLUMNS = """id, tenant_id, workspace_id, dataset_id, name, label,
              description, definition_yaml, compiled_sql_template,
              dimension_type, status, current_version, metadata_json,
              created_at, updated_at"""


def _as_json(value: Any) -> str:
    return json.dumps(value if value is not None else {})


@repository
class SemanticDimensionsRepository:
    """Repository over ``flyquery_semantic_dimensions`` + ``flyquery_semantic_versions``."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create_dimension(self, **fields: Any) -> dict[str, Any]:
        """Insert a new dimension in DRAFT status (version 1) and return it."""
        fields.setdefault("metadata_json", {})
        fields.setdefault("dimension_type", "categorical")
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    f"""
                    INSERT INTO flyquery_semantic_dimensions
                        (tenant_id, workspace_id, dataset_id, name, label,
                         description, definition_yaml, dimension_type, status,
                         current_version, metadata_json)
                    VALUES
                        (:tenant_id, :workspace_id, :dataset_id, :name, :label,
                         :description, :definition_yaml, :dimension_type, 'DRAFT',
                         1, CAST(:metadata_json AS jsonb))
                    RETURNING {_COLUMNS}
                    """
                ),
                {**fields, "metadata_json": _as_json(fields["metadata_json"])},
            )
            row = dict(result.mappings().one())
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_semantic_versions
                        (tenant_id, workspace_id, kind, parent_id, version,
                         definition_yaml, compiled_sql_template, created_by)
                    VALUES
                        (:tenant_id, :workspace_id, 'dimension', :parent_id, 1,
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

    async def list_dimensions(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        dataset_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return dimensions for a workspace (optionally filtered by dataset/status)."""
        params: dict[str, Any] = {"tenant_id": tenant_id, "workspace_id": workspace_id}
        extra = ""
        if dataset_id is not None:
            extra += " AND dataset_id = :dataset_id"
            params["dataset_id"] = dataset_id
        if status is not None:
            extra += " AND status = :status"
            params["status"] = status
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT {_COLUMNS}
                    FROM flyquery_semantic_dimensions
                    WHERE tenant_id = :tenant_id AND workspace_id = :workspace_id {extra}
                    ORDER BY name
                    """
                ),
                params,
            )
            return [dict(r) for r in result.mappings().all()]

    async def get_dimension(
        self, dimension_id: uuid.UUID, *, tenant_id: str, workspace_id: uuid.UUID
    ) -> dict[str, Any] | None:
        """Fetch a single dimension by id, scoped to tenant + workspace."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT {_COLUMNS}
                    FROM flyquery_semantic_dimensions
                    WHERE id = :id AND tenant_id = :tenant_id AND workspace_id = :workspace_id
                    """
                ),
                {"id": dimension_id, "tenant_id": tenant_id, "workspace_id": workspace_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def get_by_name(
        self,
        name: str,
        dataset_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """Fetch a PUBLISHED dimension by (name, dataset) for group-by resolution."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT {_COLUMNS}
                    FROM flyquery_semantic_dimensions
                    WHERE name = :name AND dataset_id = :dataset_id
                      AND tenant_id = :tenant_id AND workspace_id = :workspace_id
                      AND status = 'PUBLISHED'
                    """
                ),
                {
                    "name": name,
                    "dataset_id": dataset_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                },
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update_dimension(
        self, dimension_id: uuid.UUID, *, tenant_id: str, workspace_id: uuid.UUID, **fields: Any
    ) -> dict[str, Any]:
        """Sparse-update a dimension, bump version, record history."""
        if "metadata_json" in fields:
            fields["metadata_json"] = _as_json(fields["metadata_json"])
        async with self._factory() as s, s.begin():
            cur = await s.execute(
                sa.text(
                    "SELECT current_version, definition_yaml "
                    "FROM flyquery_semantic_dimensions "
                    "WHERE id = :id AND tenant_id = :tenant_id AND workspace_id = :workspace_id"
                ),
                {"id": dimension_id, "tenant_id": tenant_id, "workspace_id": workspace_id},
            )
            cur_row = cur.mappings().one()
            new_version = cur_row["current_version"] + 1

            if not fields:
                got = await self.get_dimension(
                    dimension_id, tenant_id=tenant_id, workspace_id=workspace_id
                )
                assert got is not None
                return got

            set_cols = ", ".join(
                f"{k} = CAST(:{k} AS jsonb)" if k == "metadata_json" else f"{k} = :{k}"
                for k in fields
            )
            result = await s.execute(
                sa.text(
                    f"""
                    UPDATE flyquery_semantic_dimensions
                    SET {set_cols}, current_version = :new_version, updated_at = now()
                    WHERE id = :id AND tenant_id = :tenant_id AND workspace_id = :workspace_id
                    RETURNING {_COLUMNS}
                    """
                ),
                {
                    "id": dimension_id,
                    "new_version": new_version,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    **fields,
                },
            )
            updated = dict(result.mappings().one())
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_semantic_versions
                        (tenant_id, workspace_id, kind, parent_id, version,
                         definition_yaml, compiled_sql_template, created_by)
                    VALUES
                        (:tenant_id, :workspace_id, 'dimension', :parent_id, :version,
                         :definition_yaml, :compiled_sql_template, :created_by)
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "parent_id": dimension_id,
                    "version": new_version,
                    "definition_yaml": fields.get("definition_yaml", cur_row["definition_yaml"]),
                    "compiled_sql_template": fields.get("compiled_sql_template"),
                    "created_by": fields.get("created_by", "user"),
                },
            )
            return updated

    async def publish_dimension(
        self, dimension_id: uuid.UUID, compiled_sql: str, *, tenant_id: str, workspace_id: uuid.UUID
    ) -> dict[str, Any]:
        """Publish a dimension: persist compiled expr on the row AND its current version."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    f"""
                    UPDATE flyquery_semantic_dimensions
                    SET status = 'PUBLISHED',
                        compiled_sql_template = :compiled_sql,
                        updated_at = now()
                    WHERE id = :id AND tenant_id = :tenant_id AND workspace_id = :workspace_id
                    RETURNING {_COLUMNS}
                    """
                ),
                {
                    "id": dimension_id,
                    "compiled_sql": compiled_sql,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                },
            )
            row = dict(result.mappings().one())
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_semantic_versions
                    SET compiled_sql_template = :compiled_sql
                    WHERE kind = 'dimension' AND parent_id = :id AND version = :version
                    """
                ),
                {"compiled_sql": compiled_sql, "id": dimension_id, "version": row["current_version"]},
            )
            return row

    async def retire_dimension(
        self, dimension_id: uuid.UUID, *, tenant_id: str, workspace_id: uuid.UUID
    ) -> dict[str, Any]:
        """Set status=RETIRED, scoped to tenant + workspace."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    f"""
                    UPDATE flyquery_semantic_dimensions
                    SET status = 'RETIRED', updated_at = now()
                    WHERE id = :id AND tenant_id = :tenant_id AND workspace_id = :workspace_id
                    RETURNING {_COLUMNS}
                    """
                ),
                {"id": dimension_id, "tenant_id": tenant_id, "workspace_id": workspace_id},
            )
            return dict(result.mappings().one())

    async def list_history(
        self, dimension_id: uuid.UUID, *, tenant_id: str, workspace_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """Return all version history rows for a dimension, oldest first."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, kind, parent_id, version,
                           definition_yaml, compiled_sql_template, created_by, created_at
                    FROM flyquery_semantic_versions
                    WHERE kind = 'dimension' AND parent_id = :parent_id
                      AND tenant_id = :tenant_id AND workspace_id = :workspace_id
                    ORDER BY version
                    """
                ),
                {"parent_id": dimension_id, "tenant_id": tenant_id, "workspace_id": workspace_id},
            )
            return [dict(r) for r in result.mappings().all()]
