# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

from pyfly.container import service as service_bean
from pyfly.eda import EventPublisher

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


@service_bean
class IngestPublisher:
    """EDA publisher for flyquery ingestion events.

    Follows the flycanon ``AuditService`` / ``AsyncIngestService``
    pattern: ``@service`` decorated, takes the
    :class:`EventPublisher` bean as a typed-and-required constructor
    parameter. Pyfly DI resolves the bean by exact type -- a Union
    with ``None`` or a default value would make the resolver
    short-circuit and pass ``None``, dropping every publish into the
    in-memory branch silently (worker never sees the event).

    For tests that need an in-memory publisher, use
    :meth:`for_testing` which builds the instance with a no-op
    publisher rather than relying on a default parameter.
    """

    def __init__(self, event_publisher: EventPublisher) -> None:
        self._publisher = event_publisher
        # In-memory fallback storage (test assertions + single-process mode)
        self._published: list[dict[str, Any]] = []

    @classmethod
    def for_testing(cls) -> IngestPublisher:
        """Construct an instance whose publish calls are no-ops.

        Tests that just want to assert "publish was called with X"
        should use this -- it captures publishes into the
        ``_published`` list without going through a real EDA bus.
        """
        inst = cls.__new__(cls)
        inst._publisher = None  # type: ignore[assignment]
        inst._published = []
        return inst

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
