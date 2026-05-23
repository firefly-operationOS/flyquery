# Copyright 2026 Firefly Software Solutions Inc
"""Stage 10 — publish: atomic snapshot READY swap + EDA event.

Single transaction:
1. UPDATE flyquery_schema_snapshots SET status='READY'
2. UPDATE flyquery_tables SET current_snapshot_id + updated_at
3. Publish flyquery.schema.updated via IngestPublisher (stub in Phase B)
"""

from __future__ import annotations

import logging
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.eda.ingest_publisher import IngestPublisher, SchemaUpdatedEvent

logger = logging.getLogger(__name__)


async def run_publish(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    table_id: uuid.UUID,
    snapshot_id: uuid.UUID,
    n_columns: int,
    n_rows_actual: int,
    publisher: IngestPublisher,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Execute Stage 10: atomic READY swap + EDA publish."""
    # --- Atomic transaction: flip snapshot + table ---
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                "UPDATE flyquery_schema_snapshots SET status = 'READY' "
                "WHERE id = :sid AND tenant_id = :tenant"
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        await s.execute(
            sa.text(
                "UPDATE flyquery_tables "
                "SET current_snapshot_id = :sid, updated_at = now() "
                "WHERE id = :tid AND tenant_id = :tenant"
            ),
            {"sid": snapshot_id, "tid": table_id, "tenant": tenant_id},
        )

    # --- EDA publish ---
    event = SchemaUpdatedEvent(
        tenant_id=tenant_id,
        workspace_id=str(workspace_id),
        dataset_id=str(dataset_id),
        table_id=str(table_id),
        snapshot_id=str(snapshot_id),
        n_columns=n_columns,
        n_rows_actual=n_rows_actual,
    )
    await publisher.publish_schema_updated(event)

    logger.info(
        "stage=publish snapshot_id=%s table_id=%s status=READY",
        snapshot_id,
        table_id,
    )
