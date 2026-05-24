# Copyright 2026 Firefly Software Solutions Inc
"""Relation service: list/approve/reject for proposed FK-style relations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.relations.relation_repository import RelationRepository


@service_bean
class RelationService:
    """Domain operations for ``flyquery_relations``."""

    def __init__(self, relation_repository: RelationRepository) -> None:
        # Parameter renamed from ``repository`` to match snake-cased bean name.
        self._repo = relation_repository

    async def list_for_dataset(
        self,
        dataset_id: uuid.UUID,
        *,
        tenant_id: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._repo.list_for_dataset(dataset_id, tenant_id=tenant_id, status=status)

    async def approve(
        self,
        relation_id: uuid.UUID,
        *,
        tenant_id: str,
        approved_by: str,
    ) -> dict[str, Any] | None:
        return await self._repo.approve(
            relation_id,
            tenant_id=tenant_id,
            approved_by=approved_by,
            approved_at=datetime.now(UTC),
        )

    async def reject(
        self,
        relation_id: uuid.UUID,
        *,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        return await self._repo.reject(
            relation_id,
            tenant_id=tenant_id,
            updated_at=datetime.now(UTC),
        )
