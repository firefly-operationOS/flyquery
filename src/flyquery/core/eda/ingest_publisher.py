# Copyright 2026 Firefly Software Solutions Inc
"""EDA publisher for flyquery ingestion events.

Phase C: real implementation using pyfly's EventPublisher bean.
Publishes `IngestRequested {ingest_job_id}` to FLYQUERY_INGEST_TOPIC
and `flyquery.schema.updated` after a snapshot is committed.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# Topic-level event type identifiers (align with flycanon's pattern)
INGEST_REQUESTED_EVENT = "IngestRequested"

# Sentinel: when the EDA bus is unavailable the publisher falls back to
# in-memory mode (used by tests and single-process deployments).
_MISSING = object()


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
    triggered_at: datetime = field(default_factory=lambda: datetime.now(UTC))

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


@dataclass
class IngestRequestedEvent:
    """Published to FLYQUERY_INGEST_TOPIC to trigger async worker."""

    ingest_job_id: uuid.UUID

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingest_job_id": str(self.ingest_job_id),
        }


class IngestPublisher:
    """EDA publisher for flyquery ingestion events.

    Constructor-injected with pyfly's ``EventPublisher`` bean (Phase C).
    Falls back to in-memory mode when ``event_publisher`` is ``None``
    (test isolation, single-process deployments).

    The interface is intentionally thin: two publish methods mirror the
    two event types the ingestion pipeline emits.
    """

    def __init__(self, event_publisher: Any = None) -> None:
        self._publisher = event_publisher
        # In-memory fallback storage (test assertions + single-process mode)
        self._published: list[dict[str, Any]] = []

    async def publish_ingest_requested(
        self,
        event: IngestRequestedEvent,
        *,
        ingest_topic: str = "flyquery.ingest",
        correlation_id: str | None = None,
    ) -> None:
        """Publish an IngestRequested event to the ingest topic.

        Triggers the IngestWorker to pick up the job. Best-effort:
        publish failures are logged and swallowed so the synchronous
        upload path is not interrupted by a transient EDA outage.
        """
        payload = event.to_dict()
        self._published.append({"event_type": INGEST_REQUESTED_EVENT, **payload})
        if self._publisher is not None:
            try:
                await self._publisher.publish(
                    destination=ingest_topic,
                    event_type=INGEST_REQUESTED_EVENT,
                    payload=payload,
                    headers={"correlation-id": correlation_id} if correlation_id else None,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "IngestRequested publish failed ingest_job_id=%s: %s",
                    event.ingest_job_id,
                    exc,
                )
        else:
            logger.info(
                "flyquery.ingest IngestRequested (in-memory) ingest_job_id=%s",
                event.ingest_job_id,
            )

    async def publish_schema_updated(self, event: SchemaUpdatedEvent) -> None:
        """Publish a flyquery.schema.updated event.

        Best-effort: publish failures are logged and swallowed.
        """
        payload = event.to_dict()
        self._published.append(payload)
        if self._publisher is not None:
            try:
                await self._publisher.publish(
                    destination="flyquery.schema",
                    event_type="flyquery.schema.updated",
                    payload=payload,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "flyquery.schema.updated publish failed table_id=%s: %s",
                    event.table_id,
                    exc,
                )
        else:
            logger.info(
                "flyquery.schema.updated published (in-memory) table_id=%s snapshot_id=%s",
                event.table_id,
                event.snapshot_id,
            )

    @property
    def published_events(self) -> list[dict[str, Any]]:
        """Exposed for test assertions only."""
        return list(self._published)
