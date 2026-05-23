# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for IngestPublisher (Phase C: real EDA publisher with in-memory fallback)."""

from __future__ import annotations

import uuid

import pytest

from flyquery.core.eda.ingest_publisher import (
    INGEST_REQUESTED_EVENT,
    IngestPublisher,
    IngestRequestedEvent,
    SchemaUpdatedEvent,
)


@pytest.mark.asyncio
async def test_publish_ingest_requested_records_event() -> None:
    pub = IngestPublisher()
    job_id = uuid.uuid4()
    event = IngestRequestedEvent(ingest_job_id=job_id)
    await pub.publish_ingest_requested(event, ingest_topic="flyquery.ingest")
    assert len(pub.published_events) == 1
    recorded = pub.published_events[0]
    assert recorded["event_type"] == INGEST_REQUESTED_EVENT
    assert recorded["ingest_job_id"] == str(job_id)


@pytest.mark.asyncio
async def test_publish_schema_updated_records_event() -> None:
    pub = IngestPublisher()
    event = SchemaUpdatedEvent(
        tenant_id="t1",
        workspace_id=str(uuid.uuid4()),
        dataset_id=str(uuid.uuid4()),
        table_id=str(uuid.uuid4()),
        snapshot_id=str(uuid.uuid4()),
        n_columns=5,
        n_rows_actual=100,
    )
    await pub.publish_schema_updated(event)
    assert len(pub.published_events) == 1
    recorded = pub.published_events[0]
    assert recorded["event_type"] == "flyquery.schema.updated"
    assert recorded["n_columns"] == 5
    assert recorded["n_rows_actual"] == 100


@pytest.mark.asyncio
async def test_publish_multiple_events() -> None:
    pub = IngestPublisher()
    for i in range(3):
        await pub.publish_schema_updated(
            SchemaUpdatedEvent(
                tenant_id="t1",
                workspace_id=str(uuid.uuid4()),
                dataset_id=str(uuid.uuid4()),
                table_id=str(uuid.uuid4()),
                snapshot_id=str(uuid.uuid4()),
                n_columns=i + 1,
                n_rows_actual=10,
            )
        )
    assert len(pub.published_events) == 3


def test_schema_updated_event_to_dict() -> None:
    event = SchemaUpdatedEvent(
        tenant_id="ten",
        workspace_id="ws-1",
        dataset_id="ds-1",
        table_id="tbl-1",
        snapshot_id="snap-1",
        n_columns=3,
        n_rows_actual=50,
    )
    d = event.to_dict()
    assert d["event_type"] == "flyquery.schema.updated"
    assert "triggered_at" in d
    assert d["n_columns"] == 3


@pytest.mark.asyncio
async def test_publish_ingest_requested_with_real_eda_fallback(monkeypatch) -> None:
    """EDA bus errors are swallowed; in-memory record still lands."""

    class BrokenPublisher:
        async def publish(self, **_kwargs):
            raise RuntimeError("bus down")

    pub = IngestPublisher(event_publisher=BrokenPublisher())
    job_id = uuid.uuid4()
    # Should not raise even though the EDA bus is broken
    await pub.publish_ingest_requested(
        IngestRequestedEvent(ingest_job_id=job_id),
        ingest_topic="flyquery.ingest",
    )
    # In-memory fallback record exists
    assert len(pub.published_events) == 1


def test_ingest_requested_event_to_dict() -> None:
    job_id = uuid.uuid4()
    event = IngestRequestedEvent(ingest_job_id=job_id)
    d = event.to_dict()
    assert d["ingest_job_id"] == str(job_id)
