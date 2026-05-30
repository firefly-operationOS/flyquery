# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_cost_events."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, cast

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class CostEventRepository:
    """Append-only LLM cost ledger writer + reader.

    One row per LLM-bearing operation (Grounding, Generation, Critic,
    Explainer, Describe, Column-name proposer, etc.). The service layer
    is the only writer; the read side powers ``GET /api/v1/cost-events``
    + the future ``GET /api/v1/billing`` rollup endpoint.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def insert(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        actor: str,
        operation: str,
        model: str | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_cents: Decimal | float | int = 0,
        ingest_job_id: uuid.UUID | None = None,
        query_id: uuid.UUID | None = None,
        correlation_id: str | None = None,
    ) -> uuid.UUID:
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_cost_events
                        (tenant_id, workspace_id, actor, model, operation,
                         input_tokens, output_tokens, cost_cents,
                         ingest_job_id, query_id, correlation_id)
                    VALUES
                        (:tenant_id, :workspace_id, :actor, :model, :operation,
                         :input_tokens, :output_tokens, :cost_cents,
                         :ingest_job_id, :query_id, :correlation_id)
                    RETURNING id
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "actor": actor,
                    "model": model,
                    "operation": operation,
                    "input_tokens": int(input_tokens),
                    "output_tokens": int(output_tokens),
                    "cost_cents": Decimal(str(cost_cents)),
                    "ingest_job_id": ingest_job_id,
                    "query_id": query_id,
                    "correlation_id": correlation_id,
                },
            )
            return result.scalar_one()

    async def list_filtered(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        actor: str | None = None,
        model: str | None = None,
        operation: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "actor": actor,
            "model": model,
            "operation": operation,
            "date_from": date_from,
            "date_to": date_to,
            "limit": int(limit),
            "offset": int(offset),
        }
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT *, COUNT(*) OVER () AS _total
                    FROM flyquery_cost_events
                    WHERE tenant_id = :tenant_id
                      AND workspace_id = :workspace_id
                      AND (CAST(:actor AS text) IS NULL OR actor = CAST(:actor AS text))
                      AND (CAST(:model AS text) IS NULL OR model = CAST(:model AS text))
                      AND (CAST(:operation AS text) IS NULL
                           OR operation = CAST(:operation AS text))
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
        if not rows:
            return [], await self._count_filtered(params)
        total = int(rows[0].pop("_total"))
        for r in rows[1:]:
            r.pop("_total", None)
        return rows, total

    async def delete_older_than(self, *, cutoff: datetime) -> int:
        """Hard-delete cost rows older than ``cutoff`` (retention sweep)."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text("DELETE FROM flyquery_cost_events WHERE created_at < :cutoff"),
                {"cutoff": cutoff},
            )
            return int(cast(sa.CursorResult[Any], result).rowcount or 0)

    async def _count_filtered(self, params: dict[str, Any]) -> int:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT COUNT(*) AS n
                    FROM flyquery_cost_events
                    WHERE tenant_id = :tenant_id
                      AND workspace_id = :workspace_id
                      AND (CAST(:actor AS text) IS NULL OR actor = CAST(:actor AS text))
                      AND (CAST(:model AS text) IS NULL OR model = CAST(:model AS text))
                      AND (CAST(:operation AS text) IS NULL
                           OR operation = CAST(:operation AS text))
                      AND (CAST(:date_from AS timestamptz) IS NULL
                           OR created_at >= CAST(:date_from AS timestamptz))
                      AND (CAST(:date_to AS timestamptz) IS NULL
                           OR created_at < CAST(:date_to AS timestamptz))
                    """
                ),
                params,
            )
            return int(result.scalar_one())
