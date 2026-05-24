# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_queries and flyquery_query_results.

Handles two tables:
- ``flyquery_queries``: one row per NL question — tracks the full pipeline
  run (SQL, status, timing, agent models, error, clarification).
- ``flyquery_query_results``: one row per query — the result preview JSON
  and optional full-parquet object key.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class QueryRepository:
    """Repository over ``flyquery_queries`` and ``flyquery_query_results``.

    :param session: ``async_sessionmaker`` injected by pyfly's DI container.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create_query(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID | None,
        question: str,
        semantic_path_taken: str | None,
        candidates_json: list,
        chosen_candidate_index: int | None,
        executed_sql: str | None,
        ast_classification: str | None,
        execution_status: str | None,
        retries: int,
        row_count: int | None,
        elapsed_ms: int | None,
        clarification_emitted: bool,
        clarification_json: dict | None,
        pii_findings_json: dict | None,
        error_json: dict | None,
        model_grounding: str | None = None,
        model_generation: str | None = None,
        model_critic: str | None = None,
        model_explainer: str | None = None,
    ) -> uuid.UUID:
        """Insert a new flyquery_queries row and return the generated id.

        :return: the UUID assigned to the new query row
        """
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text("""
                    INSERT INTO flyquery_queries (
                        tenant_id, workspace_id, dataset_id, question,
                        semantic_path_taken, candidates_json, chosen_candidate_index,
                        executed_sql, ast_classification, execution_status,
                        retries, row_count, elapsed_ms,
                        clarification_emitted, clarification_json,
                        pii_findings_json, error_json,
                        model_grounding, model_generation, model_critic, model_explainer,
                        finalised_at
                    ) VALUES (
                        :tenant_id, :workspace_id, :dataset_id, :question,
                        :semantic_path_taken,
                        CAST(:candidates_json AS jsonb),
                        :chosen_candidate_index,
                        :executed_sql, :ast_classification, :execution_status,
                        :retries, :row_count, :elapsed_ms,
                        :clarification_emitted,
                        CAST(:clarification_json AS jsonb),
                        CAST(:pii_findings_json AS jsonb),
                        CAST(:error_json AS jsonb),
                        :model_grounding, :model_generation, :model_critic, :model_explainer,
                        now()
                    )
                    RETURNING id
                """),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "dataset_id": dataset_id,
                    "question": question,
                    "semantic_path_taken": semantic_path_taken,
                    "candidates_json": json.dumps(candidates_json),
                    "chosen_candidate_index": chosen_candidate_index,
                    "executed_sql": executed_sql,
                    "ast_classification": ast_classification,
                    "execution_status": execution_status,
                    "retries": retries,
                    "row_count": row_count,
                    "elapsed_ms": elapsed_ms,
                    "clarification_emitted": clarification_emitted,
                    "clarification_json": json.dumps(clarification_json) if clarification_json else "null",
                    "pii_findings_json": json.dumps(pii_findings_json) if pii_findings_json else "null",
                    "error_json": json.dumps(error_json) if error_json else "null",
                    "model_grounding": model_grounding,
                    "model_generation": model_generation,
                    "model_critic": model_critic,
                    "model_explainer": model_explainer,
                },
            )
            row = result.mappings().one()
            return row["id"]

    async def get_query(
        self,
        query_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """Read a single query row scoped to ``(tenant, workspace)``.

        The full row is returned (every column from ``flyquery_queries``)
        so the controller can expose candidates, retries, model
        identifiers, error envelopes, and clarification frames in one
        round-trip.
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    "SELECT * FROM flyquery_queries "
                    "WHERE id = :id AND tenant_id = :tenant AND workspace_id = :ws"
                ),
                {"id": query_id, "tenant": tenant_id, "ws": workspace_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def list_queries(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID | None = None,
        execution_status: str | None = None,
        semantic_path_taken: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Paginated + filtered list. Returns ``(rows, total_unpaginated)``.

        Default ordering: newest first by ``created_at``. ``date_from``
        is inclusive, ``date_to`` is exclusive. ``limit`` clamped to
        [1, 200] -- queries carry heavy JSONB columns (candidates,
        clarification, pii_findings) so the page size cap is tighter
        than for cheap rows.
        """
        clamped_limit = max(1, min(200, int(limit)))
        clamped_offset = max(0, int(offset))
        params: dict[str, Any] = {
            "tenant": tenant_id,
            "ws": workspace_id,
            "ds_id": dataset_id,
            "execution_status": execution_status,
            "semantic_path_taken": semantic_path_taken,
            "date_from": date_from,
            "date_to": date_to,
            "limit": clamped_limit,
            "offset": clamped_offset,
        }
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT *, COUNT(*) OVER () AS _total
                    FROM flyquery_queries
                    WHERE tenant_id = :tenant
                      AND workspace_id = :ws
                      AND (CAST(:ds_id AS uuid) IS NULL OR dataset_id = CAST(:ds_id AS uuid))
                      AND (CAST(:execution_status AS text) IS NULL
                           OR execution_status = CAST(:execution_status AS text))
                      AND (CAST(:semantic_path_taken AS text) IS NULL
                           OR semantic_path_taken = CAST(:semantic_path_taken AS text))
                      AND (CAST(:date_from AS timestamptz) IS NULL
                           OR created_at >= CAST(:date_from AS timestamptz))
                      AND (CAST(:date_to AS timestamptz) IS NULL
                           OR created_at < CAST(:date_to AS timestamptz))
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                params,
            )
            rows = [dict(r) for r in result.mappings().all()]
        if rows:
            total = int(rows[0].pop("_total"))
            for r in rows[1:]:
                r.pop("_total", None)
            return rows, total
        return [], await self._count_queries(params)

    async def _count_queries(self, params: dict[str, Any]) -> int:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT COUNT(*) AS n
                    FROM flyquery_queries
                    WHERE tenant_id = :tenant
                      AND workspace_id = :ws
                      AND (CAST(:ds_id AS uuid) IS NULL OR dataset_id = CAST(:ds_id AS uuid))
                      AND (CAST(:execution_status AS text) IS NULL
                           OR execution_status = CAST(:execution_status AS text))
                      AND (CAST(:semantic_path_taken AS text) IS NULL
                           OR semantic_path_taken = CAST(:semantic_path_taken AS text))
                      AND (CAST(:date_from AS timestamptz) IS NULL
                           OR created_at >= CAST(:date_from AS timestamptz))
                      AND (CAST(:date_to AS timestamptz) IS NULL
                           OR created_at < CAST(:date_to AS timestamptz))
                    """
                ),
                params,
            )
            return int(result.scalar_one())

    async def get_result(
        self,
        query_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """Read the persisted result row for ``query_id``.

        Returns the full ``flyquery_query_results`` row including the
        preview JSON, object-store key (raw Parquet), byte size, and
        TTL. The controller is responsible for turning the
        ``result_object_key`` into a presigned URL.
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    "SELECT * FROM flyquery_query_results "
                    "WHERE query_id = :id AND tenant_id = :tenant "
                    "AND workspace_id = :ws"
                ),
                {"id": query_id, "tenant": tenant_id, "ws": workspace_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def upsert_result(
        self,
        *,
        query_id: uuid.UUID,
        tenant_id: str,
        workspace_id: uuid.UUID,
        result_preview_json: Any,
        result_object_key: str | None,
        result_byte_size: int | None,
        ttl_hours: int = 24,
    ) -> None:
        """Insert or update the query result row.

        :param query_id: the parent query UUID
        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param result_preview_json: serialisable preview (list of row dicts)
        :param result_object_key: object store key for the full parquet (may be None)
        :param result_byte_size: byte size of the full parquet (may be None)
        :param ttl_hours: result TTL in hours (default 24)
        """
        from datetime import timedelta

        expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)

        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text("""
                    INSERT INTO flyquery_query_results
                        (query_id, tenant_id, workspace_id, result_preview_json,
                         result_object_key, result_byte_size, ttl_expires_at)
                    VALUES
                        (:query_id, :tenant_id, :workspace_id,
                         CAST(:preview AS jsonb),
                         :result_object_key, :result_byte_size, :ttl_expires_at)
                    ON CONFLICT (query_id) DO UPDATE SET
                        result_preview_json = CAST(:preview AS jsonb),
                        result_object_key   = :result_object_key,
                        result_byte_size    = :result_byte_size,
                        ttl_expires_at      = :ttl_expires_at
                """),
                {
                    "query_id": query_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "preview": json.dumps(result_preview_json),
                    "result_object_key": result_object_key,
                    "result_byte_size": result_byte_size,
                    "ttl_expires_at": expires_at,
                },
            )
