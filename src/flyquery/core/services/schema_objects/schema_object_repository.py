# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_schema_objects.

Owns every read + write against ``flyquery_schema_objects``. The
controller (``schema_objects_controller``) holds only the HTTP
serialisation surface; all SQL lives here.

The update path locks the row with ``FOR UPDATE`` to avoid lost-writes
under concurrent human + agent annotation: humans and the
``describe`` / ``pii_tag`` ingestion stages can both write to the same
row, and the ``description_source`` / ``pii_source`` columns must
reflect the last *human* override even when an LLM pass arrives a
moment later.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_JSON_COLUMNS = frozenset({"governance_json", "synonyms_json"})


@repository
class SchemaObjectRepository:
    """Repository over ``flyquery_schema_objects``."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def get(
        self,
        object_id: uuid.UUID,
        *,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """Fetch a single schema object by id within a tenant.

        Tenant filter is required so RLS is honoured even from
        BYPASSRLS roles (the ingestion worker can be that role).
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_schema_objects WHERE id = :oid AND tenant_id = :tenant"),
                {"oid": object_id, "tenant": tenant_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def update(
        self,
        object_id: uuid.UUID,
        *,
        tenant_id: str,
        fields: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Sparse-update a schema object inside a SELECT-FOR-UPDATE transaction.

        ``fields`` is a dict of column-name -> value pairs already
        decided by the service layer (e.g. the service decides that
        ``description_source = 'HUMAN'`` when the caller set
        ``description``). JSON-shaped columns are serialised with
        ``json.dumps`` and cast to ``jsonb`` in SQL.

        Returns the updated row or ``None`` if the row doesn't exist
        for this tenant (so the controller can map to 404).
        """
        now = datetime.now(UTC)
        fields = {**fields, "last_changed_at": now}

        # Materialise JSON columns once.
        for key in _JSON_COLUMNS & fields.keys():
            value = fields[key]
            if isinstance(value, (dict, list)):
                fields[key] = json.dumps(value)

        async with self._factory() as s, s.begin():
            # Lock the row so we don't race with an in-flight describe / pii_tag
            # write inside the ingestion worker.
            locked = await s.execute(
                sa.text(
                    "SELECT id FROM flyquery_schema_objects "
                    "WHERE id = :oid AND tenant_id = :tenant "
                    "FOR UPDATE"
                ),
                {"oid": object_id, "tenant": tenant_id},
            )
            if locked.first() is None:
                return None

            # Only emit a real UPDATE if there's something to set
            # beyond the bookkeeping last_changed_at -- otherwise we'd
            # touch the row for no caller-visible reason.
            payload_fields = {k: v for k, v in fields.items() if k != "last_changed_at"}
            if payload_fields:
                set_clauses = ", ".join(
                    f"{k} = CAST(:{k} AS jsonb)" if k in _JSON_COLUMNS else f"{k} = :{k}" for k in fields
                )
                await s.execute(
                    sa.text(f"UPDATE flyquery_schema_objects SET {set_clauses} WHERE id = :oid"),
                    {**fields, "oid": object_id},
                )

            # Re-read the row in the same transaction so the controller
            # sees the post-update snapshot.
            result = await s.execute(
                sa.text("SELECT * FROM flyquery_schema_objects WHERE id = :oid AND tenant_id = :tenant"),
                {"oid": object_id, "tenant": tenant_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None
