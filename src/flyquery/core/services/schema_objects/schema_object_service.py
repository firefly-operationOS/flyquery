# Copyright 2026 Firefly Software Solutions Inc
"""Schema object service: applies the source-tagging policy on update.

The schema object table tracks a ``description_source`` and
``pii_source`` column with values like ``HUMAN`` / ``LLM`` / ``HEURISTIC``.
Whenever a human explicitly sets ``description`` or ``pii_tag`` through
``PUT /schema-objects/{id}`` we must flip the corresponding ``_source``
to ``HUMAN`` so a later LLM pass doesn't silently overwrite the
operator's curation. The service is the single owner of this rule, so
the ingestion stages can call the same path when they need to.
"""

from __future__ import annotations

import uuid
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.schema_objects.schema_object_repository import (
    SchemaObjectRepository,
)
from flyquery.interfaces.files import SchemaObjectUpdate


@service_bean
class SchemaObjectService:
    """Domain operations for ``flyquery_schema_objects``."""

    def __init__(self, schema_object_repository: SchemaObjectRepository) -> None:
        # Parameter renamed from ``repository`` to match the snake-cased
        # bean name so pyfly's name-first resolver finds the bean before
        # falling back to bare construction (which would crash because
        # the repository's own constructor takes a session_factory).
        self._repo = schema_object_repository

    async def get(
        self,
        object_id: uuid.UUID,
        *,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        return await self._repo.get(object_id, tenant_id=tenant_id)

    async def update(
        self,
        object_id: uuid.UUID,
        *,
        tenant_id: str,
        body: SchemaObjectUpdate,
    ) -> dict[str, Any] | None:
        """Apply the human-source-tagging policy and persist the update.

        Returns the post-update row or ``None`` if the object doesn't
        exist for this tenant (the controller maps that to 404).
        """
        fields: dict[str, Any] = {}
        if body.description is not None:
            fields["description"] = body.description
            fields["description_source"] = "HUMAN"
        if body.pii_tag is not None:
            fields["pii_tag"] = body.pii_tag
            fields["pii_source"] = "HUMAN"
        if body.business_owner is not None:
            fields["business_owner"] = body.business_owner
        if body.governance_json is not None:
            fields["governance_json"] = body.governance_json
        if body.synonyms_json is not None:
            fields["synonyms_json"] = body.synonyms_json
        return await self._repo.update(
            object_id,
            tenant_id=tenant_id,
            fields=fields,
        )
