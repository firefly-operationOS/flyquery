# Copyright 2026 Firefly Software Solutions Inc
"""flyquery CLI entry point.

Four top-level commands:

* ``flyquery serve``                -- API server (Uvicorn).
* ``flyquery worker ingest``        -- IngestWorker (EDA-driven).
* ``flyquery worker retention``     -- RetentionWorker (periodic sweep).
* ``flyquery worker callback``      -- CallbackWorker (outbox drain).
* ``flyquery worker all``           -- single-process mode -- runs all
                                       workers in one event loop
                                       (dev / docker-compose convenience;
                                       NOT recommended for production).

In production each worker scales horizontally as N processes per
worker type. See ``docs/workers.md`` for the deployment topology.

SIGTERM + SIGINT are caught in the long-running commands and trigger
a cooperative shutdown -- the worker drains inflight tasks within
``ingest_shutdown_grace_s`` before exiting.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
import sys

import click


@click.group()
@click.version_option()
def main() -> None:
    """flyquery command-line interface."""


# --------------------------------------------------------------------------- #
# API server                                                                  #
# --------------------------------------------------------------------------- #


@main.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8520, show_default=True, type=int)
def serve(host: str, port: int) -> None:
    """Run the API server."""
    import uvicorn

    uvicorn.run("flyquery.main:app", host=host, port=port)


# --------------------------------------------------------------------------- #
# Workers                                                                     #
# --------------------------------------------------------------------------- #


@main.group()
def worker() -> None:
    """Run long-running background workers.

    Each subcommand spawns one process. Scale horizontally by
    running the same subcommand on multiple hosts -- the EDA bus
    and the atomic PENDING-> RUNNING claim in the ingest job repo
    make concurrent workers safe.
    """


@worker.command("ingest")
def worker_ingest() -> None:
    """IngestWorker -- consumes flyquery.ingest, runs the 10-stage pipeline.

    Scales horizontally as N processes (typical: 1 process per core,
    capped by your LLM provider's per-key RPM).
    """
    asyncio.run(_run_ingest_worker())


@worker.command("retention")
def worker_retention() -> None:
    """RetentionWorker -- periodic TTL sweep + stuck-job reaper.

    One process is enough for most deployments. Two processes is fine
    (the sweep is idempotent + atomic) but redundant.
    """
    asyncio.run(_run_retention_worker())


@worker.command("callback")
def worker_callback() -> None:
    """CallbackWorker -- drains flyquery_callback_outbox + delivers webhooks.

    Horizontally scalable: the outbox row claim uses ``FOR UPDATE SKIP
    LOCKED`` so N peers don't double-deliver. Typical deployment is
    1-2 processes per region.
    """
    asyncio.run(_run_callback_worker())


@worker.command("all")
def worker_all() -> None:
    """Run all workers (ingest + retention + callback) in one process.

    Dev / docker-compose only. Production should split into separate
    `flyquery worker {ingest|retention|callback}` processes so each
    scales + restarts independently.
    """
    asyncio.run(_run_all())


@main.command()
def version() -> None:
    """Print the package version."""
    from flyquery import __version__

    click.echo(__version__)


# --------------------------------------------------------------------------- #
# Internals                                                                   #
# --------------------------------------------------------------------------- #


async def _run_ingest_worker() -> None:
    """Bootstrap the DI context, resolve IngestWorker, run until SIGTERM."""
    from pyfly.core import PyFlyApplication

    from flyquery.app import FlyqueryApplication
    from flyquery.core.services.ingestion.workers import IngestWorker

    pyfly = PyFlyApplication(FlyqueryApplication)
    await pyfly.startup()
    try:
        ingest_worker: IngestWorker = pyfly.context.get_bean(IngestWorker)
        _install_signal_handlers(stop_fn=ingest_worker.stop)
        await ingest_worker.run_forever()
    finally:
        await pyfly.shutdown()


async def _run_retention_worker() -> None:
    """Bootstrap the DI context, resolve RetentionWorker, run until SIGTERM."""
    from pyfly.core import PyFlyApplication

    from flyquery.app import FlyqueryApplication
    from flyquery.core.services.retention.retention_worker import RetentionWorker

    pyfly = PyFlyApplication(FlyqueryApplication)
    await pyfly.startup()
    try:
        retention: RetentionWorker = pyfly.context.get_bean(RetentionWorker)
        _install_signal_handlers(stop_fn=retention.request_stop)
        await retention.run_forever()
    finally:
        await pyfly.shutdown()


async def _run_callback_worker() -> None:
    """Bootstrap the DI context, resolve CallbackWorker, run until SIGTERM."""
    from pyfly.core import PyFlyApplication

    from flyquery.app import FlyqueryApplication
    from flyquery.core.services.callbacks.callback_worker import CallbackWorker

    pyfly = PyFlyApplication(FlyqueryApplication)
    await pyfly.startup()
    try:
        callback: CallbackWorker = pyfly.context.get_bean(CallbackWorker)
        _install_signal_handlers(stop_fn=lambda: asyncio.create_task(callback.stop()))
        await callback.run_forever()
    finally:
        await pyfly.shutdown()


async def _run_all() -> None:
    """Run IngestWorker + RetentionWorker + CallbackWorker concurrently. Dev only."""
    from pyfly.core import PyFlyApplication

    from flyquery.app import FlyqueryApplication
    from flyquery.core.services.callbacks.callback_worker import CallbackWorker
    from flyquery.core.services.ingestion.workers import IngestWorker
    from flyquery.core.services.retention.retention_worker import RetentionWorker

    pyfly = PyFlyApplication(FlyqueryApplication)
    await pyfly.startup()
    try:
        ingest_worker: IngestWorker = pyfly.context.get_bean(IngestWorker)
        retention: RetentionWorker = pyfly.context.get_bean(RetentionWorker)
        callback: CallbackWorker = pyfly.context.get_bean(CallbackWorker)

        def _stop_all() -> None:
            ingest_worker.stop()
            retention.request_stop()
            asyncio.create_task(callback.stop())

        _install_signal_handlers(stop_fn=_stop_all)
        await asyncio.gather(
            ingest_worker.run_forever(),
            retention.run_forever(),
            callback.run_forever(),
            return_exceptions=True,
        )
    finally:
        await pyfly.shutdown()


def _install_signal_handlers(*, stop_fn) -> None:  # type: ignore[no-untyped-def]
    """Install SIGTERM + SIGINT handlers that call ``stop_fn``.

    No-op on platforms that don't support ``add_signal_handler``
    (Windows event loops); on those platforms a KeyboardInterrupt
    still propagates to the run loop.
    """
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop_fn)


if __name__ == "__main__":
    sys.exit(main())
