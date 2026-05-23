# Copyright 2026 Firefly Software Solutions Inc
"""Schema objects controller.

GET /api/v1/schema-objects/{object_id}
PUT /api/v1/schema-objects/{object_id}
  -- update description (sets description_source='HUMAN'), pii_tag (pii_source='HUMAN'),
     business_owner, governance_json, synonyms_json
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from pyfly.container import rest_controller
from pyfly.web import Body, PathVar, Valid, get_mapping, put_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from flyquery.interfaces.files import SchemaObjectRead, SchemaObjectUpdate
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/schema-objects")
class SchemaObjectsController:
    """REST adapter for schema knowledge-base column/table objects."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    @get_mapping("/{object_id}")
    async def get_object(
        self,
        http_request: Request,
        object_id: PathVar[uuid.UUID],
    ) -> SchemaObjectRead:
        """Get a single schema object by ID."""
        ctx = tenant_context_from_request(http_request)
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT * FROM flyquery_schema_objects
                    WHERE id = :oid AND tenant_id = :tenant
                    """
                ),
                {"oid": object_id, "tenant": ctx.tenant_id},
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise ResourceNotFound(f"schema object {object_id!r} not found")
        return _row_to_read(dict(row))

    @put_mapping("/{object_id}", status_code=200)
    async def update_object(
        self,
        http_request: Request,
        object_id: PathVar[uuid.UUID],
        body: Valid[Body[SchemaObjectUpdate]],
    ) -> SchemaObjectRead:
        """Update human-set fields on a schema object.

        Sets description_source='HUMAN' when description is provided.
        Sets pii_source='HUMAN' when pii_tag is provided.
        """
        ctx = tenant_context_from_request(http_request)
        now = datetime.now(timezone.utc)

        async with self._factory() as s, s.begin():
            # Lock and load existing row
            result = await s.execute(
                sa.text(
                    """
                    SELECT * FROM flyquery_schema_objects
                    WHERE id = :oid AND tenant_id = :tenant
                    FOR UPDATE
                    """
                ),
                {"oid": object_id, "tenant": ctx.tenant_id},
            )
            row = result.mappings().one_or_none()
            if row is None:
                raise ResourceNotFound(f"schema object {object_id!r} not found")

            row = dict(row)

            # Build update fields
            updates: dict[str, object] = {"last_changed_at": now}
            if body.description is not None:
                updates["description"] = body.description
                updates["description_source"] = "HUMAN"
            if body.pii_tag is not None:
                updates["pii_tag"] = body.pii_tag
                updates["pii_source"] = "HUMAN"
            if body.business_owner is not None:
                updates["business_owner"] = body.business_owner
            if body.governance_json is not None:
                updates["governance_json"] = json.dumps(body.governance_json)
            if body.synonyms_json is not None:
                updates["synonyms_json"] = json.dumps(body.synonyms_json)

            if len(updates) > 1:  # more than just last_changed_at
                set_clauses = ", ".join(
                    f"{k} = :{k}" if k != "governance_json" and k != "synonyms_json"
                    else f"{k} = CAST(:{k} AS jsonb)"
                    for k in updates
                )
                await s.execute(
                    sa.text(
                        f"""
                        UPDATE flyquery_schema_objects
                        SET {set_clauses}
                        WHERE id = :oid
                        """
                    ),
                    {**updates, "oid": object_id},
                )

        # Return the updated row
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT * FROM flyquery_schema_objects
                    WHERE id = :oid AND tenant_id = :tenant
                    """
                ),
                {"oid": object_id, "tenant": ctx.tenant_id},
            )
            row = result.mappings().one_or_none()

        if row is None:
            raise ResourceNotFound(f"schema object {object_id!r} not found after update")
        return _row_to_read(dict(row))


def _row_to_read(row: dict) -> SchemaObjectRead:
    return SchemaObjectRead(
        id=row["id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        table_id=row["table_id"],
        snapshot_id=row["snapshot_id"],
        kind=row["kind"],
        qualified_name=row["qualified_name"],
        data_type=row.get("data_type"),
        is_nullable=row.get("is_nullable"),
        description=row.get("description"),
        description_source=row.get("description_source"),
        synonyms_json=row.get("synonyms_json"),
        pii_tag=row.get("pii_tag"),
        pii_source=row.get("pii_source"),
        business_owner=row.get("business_owner"),
        governance_json=row.get("governance_json"),
        is_active=row.get("is_active", True),
        created_at=row["created_at"],
        last_changed_at=row["last_changed_at"],
    )
