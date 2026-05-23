# Copyright 2026 Firefly Software Solutions Inc
"""EDA publisher for flyquery ingestion events.

Phase B: records events in-memory (TODO Phase C: wire to real EDA bus).
Publishes `flyquery.schema.updated` after a snapshot is committed.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SchemaUpdatedEvent:
    """Published to `flyquery.schema.updated` after atomic READY swap."""

    tenant_id: str
    workspace_id: str
    dataset_id: str
    table_id: str
    snapshot_id: str
    n_columns: int
    n_rows_actual: int | None
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "flyquery.schema.updated",
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "dataset_id": self.dataset_id,
            "table_id": self.table_id,
            "snapshot_id": self.snapshot_id,
            "n_columns": self.n_columns,
            "n_rows_actual": self.n_rows_actual,
            "triggered_at": self.triggered_at.isoformat(),
        }


class IngestPublisher:
    """Stub publisher — logs events + stores them for test inspection.

    TODO (Phase C): replace the in-memory store with a real EDA bus call
    using pyfly's EDA bean.  The interface is intentionally thin so the
    wire-up is mechanical.
    """

    def __init__(self) -> None:
        self._published: list[dict[str, Any]] = []

    async def publish_schema_updated(self, event: SchemaUpdatedEvent) -> None:
        payload = event.to_dict()
        self._published.append(payload)
        logger.info(
            "flyquery.schema.updated published (stub) table_id=%s snapshot_id=%s",
            event.table_id,
            event.snapshot_id,
        )

    @property
    def published_events(self) -> list[dict[str, Any]]:
        """Exposed for test assertions only."""
        return list(self._published)
