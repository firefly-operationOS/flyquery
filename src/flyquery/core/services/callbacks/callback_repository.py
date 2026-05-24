# Copyright 2026 Firefly Software Solutions Inc
"""Repository for flyquery_callback_outbox -- transactional webhook outbox.

The repo's invariants:

* ``enqueue_terminal`` and the job's status flip happen in the SAME
  AsyncSession (passed in by the IngestWorker) so the outbox row is
  durable iff the job is. No "lost" or "ghost" callbacks possible.
* ``claim_due_batch`` is the only path the CallbackWorker uses to
  pick rows: it filters on ``status='PENDING' AND next_attempt_at <= now()``,
  ``ORDER BY next_attempt_at``, ``FOR UPDATE SKIP LOCKED`` so multiple
  worker instances scale horizontally without colliding.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class CallbackOutboxRepository:
    """Async CRUD over the callback outbox."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def enqueue_terminal(
        self,
        *,
        session: AsyncSession,
        ingest_job_id: uuid.UUID,
        tenant_id: str,
        workspace_id: uuid.UUID,
        callback_url: str,
        callback_secret: str | None,
        callback_headers: dict[str, str],
        event_type: str,
        payload: dict[str, Any],
    ) -> uuid.UUID:
        """Append one outbox row using the caller's session.

        The CallerWorker is responsible for ``s.begin()`` / commit;
        we share its txn so the job's status flip and the outbox
        insert are atomic.
        """
        new_id = uuid.uuid4()
        await session.execute(
            sa.text(
                """
                INSERT INTO flyquery_callback_outbox
                    (id, ingest_job_id, tenant_id, workspace_id,
                     callback_url, callback_secret, callback_headers,
                     event_type, payload_json, status, attempts, next_attempt_at)
                VALUES
                    (:id, :job_id, :tenant, :ws,
                     :url, :secret, CAST(:headers AS jsonb),
                     :event, CAST(:payload AS jsonb), 'PENDING', 0, now())
                """
            ),
            {
                "id": new_id,
                "job_id": ingest_job_id,
                "tenant": tenant_id,
                "ws": workspace_id,
                "url": callback_url,
                "secret": callback_secret,
                "headers": json.dumps(callback_headers or {}),
                "event": event_type,
                "payload": json.dumps(payload, default=_json_default),
            },
        )
        return new_id

    async def claim_due_batch(
        self,
        *,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Atomically claim up to ``limit`` PENDING rows whose ``next_attempt_at <= now()``.

        Uses ``FOR UPDATE SKIP LOCKED`` so peer workers don't grab the
        same rows. The claim doesn't mutate ``status`` -- the worker
        marks each row ``DELIVERED`` / ``FAILED`` / ``DEAD`` after the
        HTTP call. The row stays ``PENDING`` while in flight; on worker
        crash the next sweep re-claims it.
        """
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    SELECT id, ingest_job_id, tenant_id, workspace_id,
                           callback_url, callback_secret, callback_headers,
                           event_type, payload_json, status, attempts,
                           last_attempt_at, last_status_code, last_error,
                           next_attempt_at, created_at, finished_at
                    FROM flyquery_callback_outbox
                    WHERE status = 'PENDING' AND next_attempt_at <= now()
                    ORDER BY next_attempt_at
                    LIMIT :limit
                    FOR UPDATE SKIP LOCKED
                    """
                ),
                {"limit": int(limit)},
            )
            return [_row_to_dict(r) for r in result.mappings().all()]

    async def mark_delivered(
        self,
        *,
        id_: uuid.UUID,
        status_code: int,
    ) -> None:
        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_callback_outbox
                    SET status = 'DELIVERED',
                        attempts = attempts + 1,
                        last_attempt_at = now(),
                        last_status_code = :code,
                        last_error = NULL,
                        finished_at = now()
                    WHERE id = :id
                    """
                ),
                {"id": id_, "code": int(status_code)},
            )

    async def mark_attempt_failure(
        self,
        *,
        id_: uuid.UUID,
        status_code: int | None,
        error: str,
        backoff_seconds: int,
        terminal: bool,
    ) -> None:
        """Increment attempts; flip to DEAD if ``terminal`` else schedule retry."""
        async with self._factory() as s, s.begin():
            if terminal:
                await s.execute(
                    sa.text(
                        """
                        UPDATE flyquery_callback_outbox
                        SET status = 'DEAD',
                            attempts = attempts + 1,
                            last_attempt_at = now(),
                            last_status_code = :code,
                            last_error = :err,
                            finished_at = now()
                        WHERE id = :id
                        """
                    ),
                    {"id": id_, "code": status_code, "err": error[:1000]},
                )
            else:
                await s.execute(
                    sa.text(
                        """
                        UPDATE flyquery_callback_outbox
                        SET attempts = attempts + 1,
                            last_attempt_at = now(),
                            last_status_code = :code,
                            last_error = :err,
                            next_attempt_at = now() + (:backoff || ' seconds')::interval
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": id_,
                        "code": status_code,
                        "err": error[:1000],
                        "backoff": int(backoff_seconds),
                    },
                )

    async def list_for_job(
        self,
        ingest_job_id: uuid.UUID,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        statuses: Sequence[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        conditions = [
            "ingest_job_id = :job_id",
            "tenant_id = :tenant",
            "workspace_id = :ws",
        ]
        params: dict[str, Any] = {
            "job_id": ingest_job_id,
            "tenant": tenant_id,
            "ws": workspace_id,
        }
        if statuses:
            placeholders = ", ".join(f":st_{i}" for i in range(len(statuses)))
            conditions.append(f"status IN ({placeholders})")
            for i, st in enumerate(statuses):
                params[f"st_{i}"] = st
        where = " AND ".join(conditions)

        async with self._factory() as s:
            total = (
                await s.execute(
                    sa.text(f"SELECT COUNT(*) FROM flyquery_callback_outbox WHERE {where}"),
                    params,
                )
            ).scalar_one()

            rows = await s.execute(
                sa.text(
                    f"""
                    SELECT id, ingest_job_id, tenant_id, workspace_id,
                           callback_url, callback_secret, callback_headers,
                           event_type, payload_json, status, attempts,
                           last_attempt_at, last_status_code, last_error,
                           next_attempt_at, created_at, finished_at
                    FROM flyquery_callback_outbox
                    WHERE {where}
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {**params, "limit": int(limit), "offset": int(offset)},
            )
            items = [_row_to_dict(r) for r in rows.mappings().all()]
            return items, int(total)


def _json_default(o: Any) -> Any:
    """Serialise UUID / datetime fields so json.dumps doesn't choke on the payload."""
    if isinstance(o, uuid.UUID):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"unserialisable type {type(o).__name__}")


def _row_to_dict(row: Any) -> dict[str, Any]:
    d = dict(row)
    for col in ("id", "ingest_job_id", "workspace_id"):
        v = d.get(col)
        if v is not None and not isinstance(v, uuid.UUID):
            d[col] = uuid.UUID(str(v))
    return d
