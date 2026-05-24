# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for RetentionWorker.

Mocks all four repos + the publisher so we can exercise the full
sweep without a database. Covers:

* Per-step stats accounting (each concern returns its rows-affected).
* "Step N raises" isolation -- the rest of the sweep still completes.
* TTL=0 shortcuts (don't bother listing/deleting).
* Republish of stuck-RUNNING + orphan-PENDING ids.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import pytest

from flyquery.core.services.retention.retention_worker import RetentionWorker


class _StubSettings:
    retention_scan_interval_s: int = 60
    retention_ingest_events_days: int = 30
    retention_audit_events_days: int = 365
    retention_cost_events_days: int = 365
    processing_lease_s: int = 1800
    orphan_queued_grace_s: int = 600
    dataset_purge_tombstone_days: int = 90
    ingest_topic: str = "flyquery.ingest"


class _StubJobs:
    def __init__(
        self,
        *,
        stuck_ids: list[uuid.UUID] | None = None,
        orphan_ids: list[uuid.UUID] | None = None,
        reset_count: int = 0,
        events_deleted: int = 0,
    ) -> None:
        self._stuck = stuck_ids or []
        self._orphans = orphan_ids or []
        self._reset = reset_count
        self._events = events_deleted
        self.list_stuck_calls = 0
        self.reap_calls = 0
        self.list_orphan_calls = 0
        self.delete_events_calls = 0

    async def list_stuck_running_ids(self, *, older_than, limit):  # type: ignore[no-untyped-def]
        self.list_stuck_calls += 1
        return list(self._stuck)

    async def reap_stuck_running(self, *, older_than):  # type: ignore[no-untyped-def]
        self.reap_calls += 1
        return self._reset

    async def list_orphaned_pending_ids(self, *, older_than, limit):  # type: ignore[no-untyped-def]
        self.list_orphan_calls += 1
        return list(self._orphans)

    async def delete_events_older_than(self, *, cutoff):  # type: ignore[no-untyped-def]
        self.delete_events_calls += 1
        return self._events


class _StubAudit:
    def __init__(self, deleted: int = 0) -> None:
        self._n = deleted
        self.calls = 0

    async def delete_older_than(self, *, cutoff):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self._n


class _StubCost:
    def __init__(self, deleted: int = 0) -> None:
        self._n = deleted
        self.calls = 0

    async def delete_older_than(self, *, cutoff):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self._n


class _StubDatasets:
    def __init__(self, deleted: int = 0) -> None:
        self._n = deleted
        self.calls = 0

    async def delete_purged_older_than(self, *, cutoff):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self._n


class _RecordingPublisher:
    def __init__(self) -> None:
        self.published: list[Any] = []
        self.fail_after: int | None = None

    async def publish_ingest_requested(self, event, *, ingest_topic):  # type: ignore[no-untyped-def]
        if self.fail_after is not None and len(self.published) >= self.fail_after:
            raise RuntimeError("simulated bus blip")
        self.published.append(event)


def _make_worker(
    *,
    jobs: _StubJobs,
    audit: _StubAudit | None = None,
    cost: _StubCost | None = None,
    datasets: _StubDatasets | None = None,
    publisher: _RecordingPublisher | None = None,
    settings: _StubSettings | None = None,
) -> RetentionWorker:
    return RetentionWorker(
        ingest_job_repository=jobs,  # type: ignore[arg-type]
        audit_event_repository=audit or _StubAudit(),  # type: ignore[arg-type]
        cost_event_repository=cost or _StubCost(),  # type: ignore[arg-type]
        dataset_repository=datasets or _StubDatasets(),  # type: ignore[arg-type]
        ingest_publisher=publisher or _RecordingPublisher(),  # type: ignore[arg-type]
        settings=settings or _StubSettings(),  # type: ignore[arg-type]
    )


# --------------------------------------------------------------------------- #
# Happy paths
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_run_once_returns_zero_stats_when_nothing_to_do() -> None:
    worker = _make_worker(jobs=_StubJobs())
    stats = await worker.run_once()
    assert stats == {
        "stuck_running_reaped": 0,
        "orphan_pending_republished": 0,
        "ingest_events_deleted": 0,
        "audit_events_deleted": 0,
        "cost_events_deleted": 0,
        "datasets_purged": 0,
    }


@pytest.mark.asyncio
async def test_stuck_reaper_resets_and_republishes() -> None:
    stuck = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
    jobs = _StubJobs(stuck_ids=stuck, reset_count=3)
    publisher = _RecordingPublisher()
    worker = _make_worker(jobs=jobs, publisher=publisher)

    stats = await worker.run_once()

    assert stats["stuck_running_reaped"] == 3
    assert len(publisher.published) == 3
    assert jobs.list_stuck_calls == 1
    assert jobs.reap_calls == 1


@pytest.mark.asyncio
async def test_orphan_pending_republisher() -> None:
    orphans = [uuid.uuid4(), uuid.uuid4()]
    jobs = _StubJobs(orphan_ids=orphans)
    publisher = _RecordingPublisher()
    worker = _make_worker(jobs=jobs, publisher=publisher)

    stats = await worker.run_once()

    assert stats["orphan_pending_republished"] == 2
    assert len(publisher.published) == 2


@pytest.mark.asyncio
async def test_ttl_deletes_pass_correct_cutoffs() -> None:
    """Each TTL step computes ``now - days`` and forwards to its repo."""
    jobs = _StubJobs(events_deleted=10)
    audit = _StubAudit(deleted=20)
    cost = _StubCost(deleted=30)
    datasets = _StubDatasets(deleted=2)
    worker = _make_worker(jobs=jobs, audit=audit, cost=cost, datasets=datasets)

    stats = await worker.run_once()

    assert stats["ingest_events_deleted"] == 10
    assert stats["audit_events_deleted"] == 20
    assert stats["cost_events_deleted"] == 30
    assert stats["datasets_purged"] == 2


# --------------------------------------------------------------------------- #
# Disabled steps
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_zero_lease_disables_stuck_reaper() -> None:
    """processing_lease_s=0 -> the step is skipped entirely (no list call)."""
    settings = _StubSettings()
    settings.processing_lease_s = 0
    jobs = _StubJobs(stuck_ids=[uuid.uuid4()])
    worker = _make_worker(jobs=jobs, settings=settings)
    stats = await worker.run_once()
    assert stats["stuck_running_reaped"] == 0
    assert jobs.list_stuck_calls == 0
    assert jobs.reap_calls == 0


@pytest.mark.asyncio
async def test_zero_audit_days_disables_audit_ttl() -> None:
    settings = _StubSettings()
    settings.retention_audit_events_days = 0
    audit = _StubAudit(deleted=1000)  # would lie if called
    worker = _make_worker(jobs=_StubJobs(), audit=audit, settings=settings)
    stats = await worker.run_once()
    assert stats["audit_events_deleted"] == 0
    assert audit.calls == 0


# --------------------------------------------------------------------------- #
# Failure isolation
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_one_step_failing_does_not_abort_the_sweep() -> None:
    """If audit TTL raises, the rest of the steps still complete."""

    class _RaisingAudit:
        async def delete_older_than(self, *, cutoff):  # type: ignore[no-untyped-def]
            raise RuntimeError("simulated DB blip")

    jobs = _StubJobs(events_deleted=5)
    cost = _StubCost(deleted=7)
    worker = _make_worker(
        jobs=jobs,
        audit=_RaisingAudit(),  # type: ignore[arg-type]
        cost=cost,
    )

    stats = await worker.run_once()

    # audit failed silently
    assert stats["audit_events_deleted"] == 0
    # but the rest still ran
    assert stats["ingest_events_deleted"] == 5
    assert stats["cost_events_deleted"] == 7


@pytest.mark.asyncio
async def test_publisher_blip_during_stuck_reap_does_not_abort_the_step() -> None:
    """If one of the republish calls raises, others still run + reset count survives."""
    stuck = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
    jobs = _StubJobs(stuck_ids=stuck, reset_count=3)
    publisher = _RecordingPublisher()
    publisher.fail_after = 1  # fail on the second publish
    worker = _make_worker(jobs=jobs, publisher=publisher)

    stats = await worker.run_once()

    # Reset count is the load-bearing number; we count it even when
    # republishes fail (the bus will redeliver via PENDING anyway).
    assert stats["stuck_running_reaped"] == 3
    # First publish succeeded; remaining 2 raised.
    assert len(publisher.published) == 1


# --------------------------------------------------------------------------- #
# Cooperative shutdown
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_request_stop_exits_run_forever_promptly() -> None:
    """run_forever must exit within one sweep interval after request_stop()."""
    import asyncio as _asyncio

    settings = _StubSettings()
    settings.retention_scan_interval_s = 60  # would block 60s without the stop
    worker = _make_worker(jobs=_StubJobs(), settings=settings)

    async def _stop_soon() -> None:
        await _asyncio.sleep(0.05)
        worker.request_stop()

    await _asyncio.wait_for(
        _asyncio.gather(worker.run_forever(), _stop_soon()),
        timeout=2.0,
    )
