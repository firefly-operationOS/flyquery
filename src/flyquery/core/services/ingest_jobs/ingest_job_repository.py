# Copyright 2026 Firefly Software Solutions Inc
"""Repository for flyquery_ingest_jobs and flyquery_ingest_events."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Sequence

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class IngestJobRepository:
    """Thin async repository over flyquery_ingest_jobs + flyquery_ingest_events.

    All mutations are scoped by (tenant_id, workspace_id) to prevent
    cross-tenant access. Reads return plain dicts so callers don't take
    a transitive dependency on the ORM layer.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        table_id: uuid.UUID | None,
        file_id: uuid.UUID | None,
        job_kind: str,
        request_json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        import json

        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_ingest_jobs
                        (tenant_id, workspace_id, dataset_id, table_id, file_id,
                         job_kind, request_json, status)
                    VALUES
                        (:tenant, :ws, :dataset, :table_id, :file_id,
                         :kind, CAST(:req AS jsonb), 'PENDING')
                    RETURNING
                        id, tenant_id, workspace_id, dataset_id, table_id, file_id,
                        snapshot_id, job_kind, status, attempts,
                        request_json, result_json, cost_cents, elapsed_ms,
                        started_at, finished_at
                    """
                ),
                {
                    "tenant": tenant_id,
                    "ws": workspace_id,
                    "dataset": dataset_id,
                    "table_id": table_id,
                    "file_id": file_id,
                    "kind": job_kind,
                    "req": json.dumps(request_json or {}),
                },
            )
            row = result.mappings().first()
            return _row_to_dict(row)

    async def get(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, tenant_id, workspace_id, dataset_id, table_id, file_id,
                           snapshot_id, job_kind, status, attempts,
                           request_json, result_json, cost_cents, elapsed_ms,
                           started_at, finished_at
                    FROM flyquery_ingest_jobs
                    WHERE id = :id AND tenant_id = :tenant AND workspace_id = :ws
                    """
                ),
                {"id": job_id, "tenant": tenant_id, "ws": workspace_id},
            )
            row = result.mappings().first()
            return _row_to_dict(row) if row else None

    async def list_jobs(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        statuses: Sequence[str] | None = None,
        job_kinds: Sequence[str] | None = None,
        dataset_id: uuid.UUID | None = None,
        table_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Returns (items, total_count)."""
        # Build dynamic WHERE clauses
        conditions = ["tenant_id = :tenant", "workspace_id = :ws"]
        params: dict[str, Any] = {"tenant": tenant_id, "ws": workspace_id}

        if statuses:
            placeholders = ", ".join(f":status_{i}" for i in range(len(statuses)))
            conditions.append(f"status IN ({placeholders})")
            for i, s in enumerate(statuses):
                params[f"status_{i}"] = s

        if job_kinds:
            placeholders = ", ".join(f":kind_{i}" for i in range(len(job_kinds)))
            conditions.append(f"job_kind IN ({placeholders})")
            for i, k in enumerate(job_kinds):
                params[f"kind_{i}"] = k

        if dataset_id is not None:
            conditions.append("dataset_id = :dataset_id")
            params["dataset_id"] = dataset_id

        if table_id is not None:
            conditions.append("table_id = :table_id")
            params["table_id"] = table_id

        where = " AND ".join(conditions)

        async with self._factory() as s:
            total_result = await s.execute(
                sa.text(f"SELECT COUNT(*) FROM flyquery_ingest_jobs WHERE {where}"),
                params,
            )
            total = total_result.scalar_one()

            list_params = {**params, "limit": limit, "offset": offset}
            rows_result = await s.execute(
                sa.text(
                    f"""
                    SELECT id, tenant_id, workspace_id, dataset_id, table_id, file_id,
                           snapshot_id, job_kind, status, attempts,
                           request_json, result_json, cost_cents, elapsed_ms,
                           started_at, finished_at
                    FROM flyquery_ingest_jobs
                    WHERE {where}
                    ORDER BY started_at DESC NULLS LAST, id DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                list_params,
            )
            items = [_row_to_dict(r) for r in rows_result.mappings().all()]
            return items, total

    async def cancel(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """Flip status to CANCELLED (idempotent for already-terminal jobs).

        Returns the updated row, or None if not found.
        """
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_ingest_jobs
                    SET status = 'CANCELLED', finished_at = COALESCE(finished_at, now())
                    WHERE id = :id AND tenant_id = :tenant AND workspace_id = :ws
                      AND status NOT IN ('SUCCEEDED', 'FAILED')
                    RETURNING
                        id, tenant_id, workspace_id, dataset_id, table_id, file_id,
                        snapshot_id, job_kind, status, attempts,
                        request_json, result_json, cost_cents, elapsed_ms,
                        started_at, finished_at
                    """
                ),
                {"id": job_id, "tenant": tenant_id, "ws": workspace_id},
            )
            row = result.mappings().first()
            if row is not None:
                return _row_to_dict(row)
            # May already be terminal — still return the current row
            return await self.get(job_id, tenant_id=tenant_id, workspace_id=workspace_id)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    async def list_events(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        after_id: int | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Returns (events, total_count) ordered by id ascending."""
        async with self._factory() as s:
            base_cond = (
                "ingest_job_id = :job_id AND tenant_id = :tenant AND workspace_id = :ws"
            )
            params: dict[str, Any] = {"job_id": job_id, "tenant": tenant_id, "ws": workspace_id}

            extra = ""
            if after_id is not None:
                extra = " AND id > :after_id"
                params["after_id"] = after_id

            total_result = await s.execute(
                sa.text(f"SELECT COUNT(*) FROM flyquery_ingest_events WHERE {base_cond}{extra}"),
                params,
            )
            total = total_result.scalar_one()

            list_params = {**params, "limit": limit, "offset": offset}
            rows_result = await s.execute(
                sa.text(
                    f"""
                    SELECT id, ingest_job_id, stage, status, message, payload_json, created_at
                    FROM flyquery_ingest_events
                    WHERE {base_cond}{extra}
                    ORDER BY id ASC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                list_params,
            )
            items = [_event_row_to_dict(r) for r in rows_result.mappings().all()]
            return items, total

    async def list_events_since(
        self,
        job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        after_id: int,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Poll for new events since ``after_id`` (used by SSE stream loop)."""
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, ingest_job_id, stage, status, message, payload_json, created_at
                    FROM flyquery_ingest_events
                    WHERE ingest_job_id = :job_id
                      AND tenant_id = :tenant
                      AND workspace_id = :ws
                      AND id > :after_id
                    ORDER BY id ASC
                    LIMIT :limit
                    """
                ),
                {
                    "job_id": job_id,
                    "tenant": tenant_id,
                    "ws": workspace_id,
                    "after_id": after_id,
                    "limit": limit,
                },
            )
            return [_event_row_to_dict(r) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# Row → dict helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict[str, Any]:
    d = dict(row)
    # Ensure UUID columns are uuid.UUID objects not strings
    for col in ("id", "workspace_id", "dataset_id", "table_id", "file_id", "snapshot_id"):
        if col in d and d[col] is not None and not isinstance(d[col], uuid.UUID):
            d[col] = uuid.UUID(str(d[col]))
    return d


def _event_row_to_dict(row: Any) -> dict[str, Any]:
    d = dict(row)
    for col in ("ingest_job_id",):
        if col in d and d[col] is not None and not isinstance(d[col], uuid.UUID):
            d[col] = uuid.UUID(str(d[col]))
    return d
