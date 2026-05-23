# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_glossary_terms."""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_JSON_COLS = ("synonyms_json", "tags_json", "related_columns_json", "related_metrics_json")


def _dumps_json_cols(fields: dict[str, Any]) -> dict[str, Any]:
    out = dict(fields)
    for col in _JSON_COLS:
        if col in out and not isinstance(out[col], str):
            out[col] = json.dumps(out[col])
    return out


@repository
class GlossaryRepository:
    """Repository over ``flyquery_glossary_terms``.

    UQ constraint: (workspace_id, term) — enforced at DB level.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create(self, **fields: Any) -> dict[str, Any]:
        """Insert a new glossary term and return the full record."""
        fields = _dumps_json_cols(fields)
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_glossary_terms
                        (tenant_id, workspace_id, term, definition,
                         synonyms_json, tags_json, related_columns_json, related_metrics_json)
                    VALUES
                        (:tenant_id, :workspace_id, :term, :definition,
                         CAST(:synonyms_json AS jsonb), CAST(:tags_json AS jsonb),
                         CAST(:related_columns_json AS jsonb), CAST(:related_metrics_json AS jsonb))
                    RETURNING id, tenant_id, workspace_id, term, definition,
                              synonyms_json, tags_json, related_columns_json, related_metrics_json,
                              created_at, updated_at
                    """
                ),
                fields,
            )
            return dict(result.mappings().one())

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return glossary terms for a workspace, paginated."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, term, definition,
                           synonyms_json, tags_json, related_columns_json, related_metrics_json,
                           created_at, updated_at
                    FROM flyquery_glossary_terms
                    WHERE tenant_id = :tenant_id AND workspace_id = :workspace_id
                    ORDER BY term
                    LIMIT :lim OFFSET :off
                    """
                ),
                {"tenant_id": tenant_id, "workspace_id": workspace_id, "lim": limit, "off": offset},
            )
            return [dict(row) for row in result.mappings().all()]

    async def get(self, term_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single glossary term by primary key."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, term, definition,
                           synonyms_json, tags_json, related_columns_json, related_metrics_json,
                           created_at, updated_at
                    FROM flyquery_glossary_terms WHERE id = :id
                    """
                ),
                {"id": term_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update(self, term_id: uuid.UUID, **fields: Any) -> dict[str, Any]:
        """Sparse-update a glossary term and return the updated record."""
        if not fields:
            row = await self.get(term_id)
            assert row is not None
            return row
        fields = _dumps_json_cols(fields)
        sets = []
        for k in fields:
            if k in _JSON_COLS:
                sets.append(f"{k} = CAST(:{k} AS jsonb)")
            else:
                sets.append(f"{k} = :{k}")
        sets.append("updated_at = now()")
        set_clause = ", ".join(sets)
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    f"""
                    UPDATE flyquery_glossary_terms
                    SET {set_clause}
                    WHERE id = :id
                    RETURNING id, tenant_id, workspace_id, term, definition,
                              synonyms_json, tags_json, related_columns_json, related_metrics_json,
                              created_at, updated_at
                    """
                ),
                {"id": term_id, **fields},
            )
            return dict(result.mappings().one())

    async def delete(self, term_id: uuid.UUID) -> None:
        """Hard-delete a glossary term."""
        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text("DELETE FROM flyquery_glossary_terms WHERE id = :id"),
                {"id": term_id},
            )
