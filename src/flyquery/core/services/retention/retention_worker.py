# Copyright 2026 Firefly Software Solutions Inc
"""RetentionWorker -- periodic TTL sweep + stuck-job reaper.

Mirrors the flyradar pattern (``flyradar.core.services.workers.retention_worker``):
a single periodic loop that owns all of:

1. **Stuck-RUNNING ingest job reaper.** A crashed worker leaves the
   job in RUNNING with no path back to PENDING (the atomic claim in
   :meth:`IngestWorker._mark_running` requires PENDING). Every sweep
   we reset jobs whose ``started_at`` is older than
   ``processing_lease_s`` and republish them onto the bus.
2. **Orphan-PENDING reaper.** A publish that crashed after the DB
   insert leaves the row in PENDING with no event on the bus. We
   republish PENDING jobs older than ``orphan_queued_grace_s``. The
   worker's atomic claim deduplicates if the original event DID
   arrive after all.
3. **TTL deletes.** Hard-delete ``flyquery_ingest_events``,
   ``flyquery_audit_events``, and ``flyquery_cost_events`` rows older
   than the per-table retention window. ``0`` disables a window.
4. **Dataset purge tombstone.** Hard-delete dataset rows whose
   status has been ``PURGING`` for longer than
   ``dataset_purge_tombstone_days``. The object-store walk already
   ran at purge time; this collapses the SQL row.

The worker is **single-process-safe** -- two RetentionWorker
processes running concurrently is fine. Each operation is idempotent
(``DELETE WHERE ...`` and ``UPDATE WHERE status='RUNNING'``) and the
republish path is deduped at the bus by the atomic PENDING claim.

The worker is **not EDA-driven** -- it polls on a fixed interval
(``retention_scan_interval_s``) so it doesn't need a publisher
subscription. The ``run_forever()`` loop is cooperatively cancellable
via an ``asyncio.Event``.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from pyfly.container import service as service_bean

from flyquery.config import FlyquerySettings
from flyquery.core.eda.ingest_publisher import IngestPublisher, IngestRequestedEvent
from flyquery.core.services.datasets.dataset_repository import DatasetRepository
from flyquery.core.services.ingest_jobs.ingest_job_repository import IngestJobRepository
from flyquery.core.services.ops.audit_event_repository import AuditEventRepository
from flyquery.core.services.ops.cost_event_repository import CostEventRepository

logger = logging.getLogger(__name__)


@service_bean
class RetentionWorker:
    """Periodic background loop with TTL + stuck-recovery duties.

    See module docstring for the full set of concerns.

    The constructor takes one repo per table the sweep touches plus
    the ``IngestPublisher`` (for republish). All deps are pyfly
    ``@repository`` / ``@service`` beans so DI wires the worker at
    boot without extra plumbing.

    Two entry points:

    * :meth:`run_once` -- one full sweep. Public so the CLI and
      tests can run a single pass without spinning the loop.
    * :meth:`run_forever` -- sleep / sweep loop until
      :meth:`request_stop` is called (called by the CLI on
      SIGINT / SIGTERM).
    """

    def __init__(
        self,
        ingest_job_repository: IngestJobRepository,
        audit_event_repository: AuditEventRepository,
        cost_event_repository: CostEventRepository,
        dataset_repository: DatasetRepository,
        ingest_publisher: IngestPublisher,
        settings: FlyquerySettings,
    ) -> None:
        self._jobs = ingest_job_repository
        self._audit = audit_event_repository
        self._cost = cost_event_repository
        self._datasets = dataset_repository
        self._publisher = ingest_publisher
        self._settings = settings
        self._shutdown = asyncio.Event()

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    async def run_once(self) -> dict[str, int]:
        """One full sweep. Returns ``{concern_name: rows_affected}``.

        Stays declarative -- every step is its own helper, every step
        catches its own exceptions. The sweep never aborts halfway
        because step N raised; the rest of the steps still run.
        """
        now = datetime.now(UTC)
        stats: dict[str, int] = {
            "stuck_running_reaped": 0,
            "orphan_pending_republished": 0,
            "ingest_events_deleted": 0,
            "audit_events_deleted": 0,
            "cost_events_deleted": 0,
            "datasets_purged": 0,
        }

        for concern, fn in (
            ("stuck_running_reaped", self._reap_stuck_running),
            ("orphan_pending_republished", self._republish_orphan_pending),
            ("ingest_events_deleted", self._delete_ingest_events),
            ("audit_events_deleted", self._delete_audit_events),
            ("cost_events_deleted", self._delete_cost_events),
            ("datasets_purged", self._delete_purged_datasets),
        ):
            try:
                stats[concern] = await fn(now)
            except Exception:  # noqa: BLE001 -- never crash the sweep on one concern
                logger.exception("retention_sweep_step_failed concern=%s", concern)

        if any(stats.values()):
            logger.info(
                "retention_sweep_completed "
                "stuck_reaped=%d orphan_pending=%d ingest_events=%d "
                "audit_events=%d cost_events=%d datasets_purged=%d",
                stats["stuck_running_reaped"],
                stats["orphan_pending_republished"],
                stats["ingest_events_deleted"],
                stats["audit_events_deleted"],
                stats["cost_events_deleted"],
                stats["datasets_purged"],
            )
        return stats

    async def run_forever(self) -> None:
        """Sweep / sleep loop until ``request_stop()`` is called."""
        interval_s = max(60, int(self._settings.retention_scan_interval_s))
        logger.info("retention_worker_started interval_s=%d", interval_s)
        while not self._shutdown.is_set():
            try:
                await self.run_once()
            except Exception:  # noqa: BLE001 -- never let a transient blip kill the loop
                logger.exception("retention_sweep_failed")
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._shutdown.wait(), timeout=interval_s)
        logger.info("retention_worker_stopped")

    def request_stop(self) -> None:
        """Signal the sweep loop to exit at the next sleep boundary."""
        self._shutdown.set()

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------

    async def _reap_stuck_running(self, now: datetime) -> int:
        """Reset stuck RUNNING ingest jobs back to PENDING + republish them.

        Listing the candidate ids first lets us republish exactly the
        rows we reset (avoiding a republish for jobs another reaper /
        a healthy worker already finished between the list and the
        update).
        """
        lease_s = max(0, int(self._settings.processing_lease_s))
        if lease_s <= 0:
            return 0
        cutoff = now - timedelta(seconds=lease_s)
        stuck_ids = await self._jobs.list_stuck_running_ids(older_than=cutoff, limit=200)
        if not stuck_ids:
            return 0
        reset_count = await self._jobs.reap_stuck_running(older_than=cutoff)
        if reset_count == 0:
            return 0
        logger.warning(
            "retention_stuck_running_reaped count=%d lease_s=%d ids=%s",
            reset_count,
            lease_s,
            [str(i) for i in stuck_ids[:10]],
        )
        await self._republish_ids(stuck_ids, source="stuck_reap")
        return reset_count

    async def _republish_orphan_pending(self, now: datetime) -> int:
        """Republish PENDING ingest jobs older than ``orphan_queued_grace_s``."""
        grace_s = max(0, int(self._settings.orphan_queued_grace_s))
        if grace_s <= 0:
            return 0
        cutoff = now - timedelta(seconds=grace_s)
        orphan_ids = await self._jobs.list_orphaned_pending_ids(older_than=cutoff, limit=200)
        if not orphan_ids:
            return 0
        logger.warning(
            "retention_orphan_pending_republish count=%d grace_s=%d ids=%s",
            len(orphan_ids),
            grace_s,
            [str(i) for i in orphan_ids[:10]],
        )
        republished = await self._republish_ids(orphan_ids, source="orphan_republish")
        return republished

    async def _republish_ids(self, ids: list[Any], *, source: str) -> int:
        """Best-effort republish of N ingest job ids onto the EDA bus.

        Per-id try/except so one bus blip doesn't drop the rest.
        """
        n = 0
        for job_id in ids:
            try:
                await self._publisher.publish_ingest_requested(
                    IngestRequestedEvent(ingest_job_id=job_id),
                    ingest_topic=self._settings.ingest_topic,
                )
                n += 1
            except Exception:  # noqa: BLE001
                logger.exception(
                    "retention_republish_failed source=%s job_id=%s",
                    source,
                    job_id,
                )
        return n

    async def _delete_ingest_events(self, now: datetime) -> int:
        days = int(self._settings.retention_ingest_events_days)
        if days <= 0:
            return 0
        return await self._jobs.delete_events_older_than(
            cutoff=now - timedelta(days=days),
        )

    async def _delete_audit_events(self, now: datetime) -> int:
        days = int(self._settings.retention_audit_events_days)
        if days <= 0:
            return 0
        return await self._audit.delete_older_than(
            cutoff=now - timedelta(days=days),
        )

    async def _delete_cost_events(self, now: datetime) -> int:
        days = int(self._settings.retention_cost_events_days)
        if days <= 0:
            return 0
        return await self._cost.delete_older_than(
            cutoff=now - timedelta(days=days),
        )

    async def _delete_purged_datasets(self, now: datetime) -> int:
        days = int(self._settings.dataset_purge_tombstone_days)
        if days <= 0:
            return 0
        return await self._datasets.delete_purged_older_than(
            cutoff=now - timedelta(days=days),
        )


__all__ = ["RetentionWorker"]
