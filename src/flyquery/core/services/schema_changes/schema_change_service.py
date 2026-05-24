# Copyright 2026 Firefly Software Solutions Inc
"""Schema change service: confirm a RENAMED_CANDIDATE -> RENAMED."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.schema_changes.schema_change_repository import (
    SchemaChangeRepository,
)


class SchemaChangeNotFound(Exception):
    """Raised by the service when the change row doesn't exist for the tenant."""


class SchemaChangeWrongState(Exception):
    """Raised when the change row exists but isn't in RENAMED_CANDIDATE."""


@dataclass
class ConfirmedChange:
    """Service-layer result of a successful confirm."""

    row: dict[str, Any]
    approved_by: str
    approved_at: datetime


@service_bean
class SchemaChangeService:
    """Domain operations for ``flyquery_schema_changes``."""

    def __init__(self, repository: SchemaChangeRepository) -> None:
        self._repo = repository

    async def confirm(
        self,
        change_id: uuid.UUID,
        *,
        tenant_id: str,
        approved_by: str,
    ) -> ConfirmedChange:
        """Confirm a rename candidate. Raises typed exceptions on failure
        so the controller can map them to 404 / 422 respectively.
        """
        approved_at = datetime.now(UTC)
        row, err = await self._repo.confirm_transaction(
            change_id,
            tenant_id=tenant_id,
            approved_by=approved_by,
            approved_at=approved_at,
        )
        if err == "not_found":
            raise SchemaChangeNotFound(f"schema change {change_id!r} not found")
        if err == "wrong_state":
            current = (row or {}).get("change", "UNKNOWN")
            raise SchemaChangeWrongState(
                f"change {change_id!r} has status {current!r}; only RENAMED_CANDIDATE rows can be confirmed"
            )
        assert row is not None
        return ConfirmedChange(row=row, approved_by=approved_by, approved_at=approved_at)
