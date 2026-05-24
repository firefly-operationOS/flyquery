# Copyright 2026 Firefly Software Solutions Inc
"""Audit event service: structured business-event ledger.

Used by mutating handlers (create / update / delete / approve / ...) to
record what happened, who did it, and against which resource. Reads
are exposed via ``GET /api/v1/audit-events`` for compliance + support.

Design notes
------------
* **Best-effort writes.** A failed audit insert must never break the
  caller's business operation. :meth:`record` swallows + logs every
  exception. The repository owns the SQL; the service owns the
  swallow-and-log policy.
* **Per-request correlation_id.** Callers should pass the value of
  ``X-Correlation-Id`` (or the server-minted UUID echoed back) so a
  single user request can be traced across audit + cost ledgers and
  structured logs.
* **No publish to the EDA bus** yet -- the OpenAPI tour talks about a
  ``flyquery.audit`` topic but no consumer exists. Added a TODO marker
  so a future EDA wiring lands in one place.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.ops.audit_event_repository import AuditEventRepository

logger = logging.getLogger(__name__)


@service_bean
class AuditEventService:
    """Writer + paginated reader for ``flyquery_audit_events``."""

    def __init__(self, repository: AuditEventRepository) -> None:
        self._repo = repository

    async def record(
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
    ) -> None:
        """Best-effort audit record. Never raises -- failures log only.

        Use snake_case event types (``dataset.created``,
        ``agent_token.minted``, ``query.executed``,
        ``schema_object.described``). Resource kind matches the
        canonical resource name (``dataset``, ``agent_token``, ``query``).
        """
        try:
            await self._repo.insert(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                actor=actor,
                event_type=event_type,
                resource_kind=resource_kind,
                resource_id=resource_id,
                correlation_id=correlation_id,
                payload=payload,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "audit insert failed event_type=%s resource_kind=%s err=%s",
                event_type,
                resource_kind,
                exc,
            )

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
        """Filtered + paginated read. Returns ``(rows, total_unpaginated)``."""
        limit = max(1, min(1000, int(limit)))
        offset = max(0, int(offset))
        return await self._repo.list_filtered(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            event_type=event_type,
            actor=actor,
            resource_kind=resource_kind,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
