# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_audit_events."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class AuditEventRepository:
    """Append-only ledger writer + filtered reader for ``flyquery_audit_events``.

    Writes are fire-and-forget from a correctness standpoint -- a failed
    audit insert must NEVER break the business operation it accompanies.
    The service wraps every call in a best-effort try/except and logs at
    WARNING. This matches the pattern used by IngestEventRepository.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def insert(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        actor: str,
        event_type: str,
        resource_kind: str,
        resource_id: str | None = None,
        correlation_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> uuid.UUID:
        payload_json = json.dumps(payload or {})
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_audit_events
                        (tenant_id, workspace_id, actor, event_type, resource_kind,
                         resource_id, correlation_id, payload_json)
                    VALUES
                        (:tenant_id, :workspace_id, :actor, :event_type, :resource_kind,
                         :resource_id, :correlation_id, CAST(:payload_json AS jsonb))
                    RETURNING id
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "actor": actor,
                    "event_type": event_type,
                    "resource_kind": resource_kind,
                    "resource_id": resource_id,
                    "correlation_id": correlation_id,
                    "payload_json": payload_json,
                },
            )
            return result.scalar_one()

    async def list_filtered(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        event_type: str | None = None,
        actor: str | None = None,
        resource_kind: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Paginated + filtered audit-event read. Returns ``(rows, total)``."""
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "event_type": event_type,
            "actor": actor,
            "resource_kind": resource_kind,
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
                    FROM flyquery_audit_events
                    WHERE tenant_id = :tenant_id
                      AND workspace_id = :workspace_id
                      AND (CAST(:event_type AS text) IS NULL OR event_type = CAST(:event_type AS text))
                      AND (CAST(:actor AS text) IS NULL OR actor = CAST(:actor AS text))
                      AND (CAST(:resource_kind AS text) IS NULL
                           OR resource_kind = CAST(:resource_kind AS text))
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
        """Hard-delete audit rows older than ``cutoff`` (retention sweep)."""
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text("DELETE FROM flyquery_audit_events WHERE created_at < :cutoff"),
                {"cutoff": cutoff},
            )
            return int(result.rowcount or 0)

    async def _count_filtered(self, params: dict[str, Any]) -> int:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT COUNT(*) AS n
                    FROM flyquery_audit_events
                    WHERE tenant_id = :tenant_id
                      AND workspace_id = :workspace_id
                      AND (CAST(:event_type AS text) IS NULL OR event_type = CAST(:event_type AS text))
                      AND (CAST(:actor AS text) IS NULL OR actor = CAST(:actor AS text))
                      AND (CAST(:resource_kind AS text) IS NULL
                           OR resource_kind = CAST(:resource_kind AS text))
                      AND (CAST(:date_from AS timestamptz) IS NULL
                           OR created_at >= CAST(:date_from AS timestamptz))
                      AND (CAST(:date_to AS timestamptz) IS NULL
                           OR created_at < CAST(:date_to AS timestamptz))
                    """
                ),
                params,
            )
            return int(result.scalar_one())
