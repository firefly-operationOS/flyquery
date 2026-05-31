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

"""Async SQLAlchemy repository for flyquery_examples."""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class ExamplesRepository:
    """Repository over ``flyquery_examples``.

    Every operation owns its own session + transaction lifetime via
    the injected ``async_sessionmaker``.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create(self, **fields: Any) -> dict[str, Any]:
        """Insert a new examples row and return the full record."""
        if "citations_json" in fields and isinstance(fields["citations_json"], dict):
            fields = {**fields, "citations_json": json.dumps(fields["citations_json"])}
        embedding = fields.pop("embedding", None)
        async with self._factory() as s, s.begin():
            if embedding is not None:
                result = await s.execute(
                    sa.text(
                        """
                        INSERT INTO flyquery_examples
                            (tenant_id, workspace_id, dataset_id, question, generated_sql,
                             normalised_sql, source, quality, citations_json, created_by, embedding)
                        VALUES
                            (:tenant_id, :workspace_id, :dataset_id, :question, :generated_sql,
                             :normalised_sql, :source, :quality,
                             CAST(:citations_json AS jsonb), :created_by,
                             CAST(:embedding AS vector))
                        RETURNING id, tenant_id, workspace_id, dataset_id, question,
                                  generated_sql, normalised_sql, source, quality,
                                  citations_json, created_at, created_by, last_used_at, usage_count
                        """
                    ),
                    {**fields, "embedding": str(embedding)},
                )
            else:
                result = await s.execute(
                    sa.text(
                        """
                        INSERT INTO flyquery_examples
                            (tenant_id, workspace_id, dataset_id, question, generated_sql,
                             normalised_sql, source, quality, citations_json, created_by)
                        VALUES
                            (:tenant_id, :workspace_id, :dataset_id, :question, :generated_sql,
                             :normalised_sql, :source, :quality,
                             CAST(:citations_json AS jsonb), :created_by)
                        RETURNING id, tenant_id, workspace_id, dataset_id, question,
                                  generated_sql, normalised_sql, source, quality,
                                  citations_json, created_at, created_by, last_used_at, usage_count
                        """
                    ),
                    fields,
                )
            row = result.mappings().one()
            return dict(row)

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        quality: str | None = None,
        dataset_id: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return examples for a workspace, optionally filtered."""
        filters = ["tenant_id = :tenant_id", "workspace_id = :workspace_id"]
        params: dict[str, Any] = {"tenant_id": tenant_id, "workspace_id": workspace_id, "lim": limit}
        if quality is not None:
            filters.append("quality = :quality")
            params["quality"] = quality
        if dataset_id is not None:
            filters.append("dataset_id = :dataset_id")
            params["dataset_id"] = dataset_id
        where = " AND ".join(filters)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    f"""
                    SELECT id, tenant_id, workspace_id, dataset_id, question,
                           generated_sql, normalised_sql, source, quality,
                           citations_json, created_at, created_by, last_used_at, usage_count
                    FROM flyquery_examples
                    WHERE {where}
                    ORDER BY created_at DESC
                    LIMIT :lim
                    """
                ),
                params,
            )
            return [dict(row) for row in result.mappings().all()]

    async def get(self, example_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single example by primary key."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, dataset_id, question,
                           generated_sql, normalised_sql, source, quality,
                           citations_json, created_at, created_by, last_used_at, usage_count
                    FROM flyquery_examples WHERE id = :id
                    """
                ),
                {"id": example_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update_quality(self, example_id: uuid.UUID, quality: str) -> dict[str, Any]:
        """Set quality (APPROVED | REJECTED | PROPOSED) and return updated row."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_examples
                    SET quality = :quality
                    WHERE id = :id
                    RETURNING id, tenant_id, workspace_id, dataset_id, question,
                              generated_sql, normalised_sql, source, quality,
                              citations_json, created_at, created_by, last_used_at, usage_count
                    """
                ),
                {"id": example_id, "quality": quality},
            )
            return dict(result.mappings().one())
