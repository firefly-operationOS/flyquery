# Copyright 2026 Firefly Software Solutions Inc
"""Billing service: cost rollup over flyquery_cost_events.

Aggregates the per-call cost ledger into period buckets (day / week /
month) so a single GET /api/v1/billing call returns a board-room-shape
``{total_cost_cents, breakdown[]}`` envelope without the caller paging
through every raw row.

Aggregation runs in Postgres via ``date_trunc(period, occurred_at)`` --
we never materialise a per-row preview in memory. The breakdown is
also split into ``ingest_cost_cents`` (rows where ``ingest_job_id`` is
non-null) vs ``query_cost_cents`` (rows where ``query_id`` is
non-null); rows with neither end up bucketed into ``other``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

import sqlalchemy as sa
from pyfly.container import service as service_bean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

Period = Literal["day", "week", "month"]


@service_bean
class BillingService:
    """Aggregation reader over ``flyquery_cost_events``.

    Wraps a session_factory directly rather than depending on
    :class:`CostEventRepository` because the rollup is one large
    GROUP BY query -- a dedicated method here is cheaper than
    composing repo calls.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def rollup(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        period: Period = "day",
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[Decimal, list[dict[str, Any]]]:
        """Aggregate cost into period buckets.

        Returns ``(total_cost_cents, breakdown)`` where each breakdown
        entry is ``{date, ingest_cost_cents, query_cost_cents, other_cost_cents}``.

        ``period`` controls the bucket granularity. Bounds default to
        the last 30 days when ``date_from`` is None.
        """
        if period not in ("day", "week", "month"):
            raise ValueError(f"unsupported period {period!r}; expected day | week | month")

        params: dict[str, Any] = {
            "tenant": tenant_id,
            "ws": workspace_id,
            "date_from": date_from,
            "date_to": date_to,
        }
        # period is a SQL literal but constrained above to a known
        # safe set -- inline it rather than binding (Postgres won't
        # accept a bind param inside date_trunc).
        sql = sa.text(
            f"""
            SELECT
                date_trunc('{period}', created_at) AS bucket,
                COALESCE(SUM(cost_cents) FILTER (WHERE ingest_job_id IS NOT NULL), 0) AS ingest,
                COALESCE(SUM(cost_cents) FILTER (WHERE query_id IS NOT NULL), 0) AS query,
                COALESCE(SUM(cost_cents) FILTER (
                    WHERE ingest_job_id IS NULL AND query_id IS NULL
                ), 0) AS other,
                COALESCE(SUM(cost_cents), 0) AS total
            FROM flyquery_cost_events
            WHERE tenant_id = :tenant
              AND workspace_id = :ws
              AND (CAST(:date_from AS timestamptz) IS NULL
                   OR created_at >= CAST(:date_from AS timestamptz))
              AND (CAST(:date_to AS timestamptz) IS NULL
                   OR created_at < CAST(:date_to AS timestamptz))
            GROUP BY bucket
            ORDER BY bucket
            """
        )

        async with self._factory() as s:
            result = await s.execute(sql, params)
            rows = list(result.mappings().all())

        breakdown: list[dict[str, Any]] = []
        total = Decimal("0")
        for r in rows:
            ingest = Decimal(r["ingest"] or 0)
            query = Decimal(r["query"] or 0)
            other = Decimal(r["other"] or 0)
            bucket_total = Decimal(r["total"] or 0)
            total += bucket_total
            breakdown.append(
                {
                    "date": r["bucket"],
                    "ingest_cost_cents": ingest,
                    "query_cost_cents": query,
                    "other_cost_cents": other,
                    "total_cost_cents": bucket_total,
                }
            )
        return total, breakdown
