# Copyright 2026 Firefly Software Solutions Inc
"""IngestService — synchronous orchestrator for Stages 1-3 + 9-10.

Wired as a pyfly @service bean. Injected into the FilesController.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from pyfly.container import service as service_bean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.config import FlyquerySettings
from flyquery.core.eda.ingest_publisher import IngestPublisher
from flyquery.core.services.ingestion.stages.describe import run_describe
from flyquery.core.services.ingestion.stages.embed import run_embed
from flyquery.core.services.ingestion.stages.parse import run_parse
from flyquery.core.services.ingestion.stages.profile import run_profile
from flyquery.core.services.ingestion.stages.publish import run_publish
from flyquery.core.services.ingestion.stages.receive import run_receive
from flyquery.core.services.ingestion.stages.reconcile import run_reconcile
from flyquery.core.services.ingestion.stages.sample import run_sample
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.workspaces.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)


@dataclass
class IngestedTable:
    table_id: str
    name: str
    n_columns: int
    n_rows_estimate: int
    snapshot_id: str


@dataclass
class IngestResult:
    file_id: str
    tables: list[IngestedTable]


@service_bean
class IngestService:
    """Orchestrates synchronous upload ingestion (Stages 1-3 + 9-10)."""

    def __init__(
        self,
        settings: FlyquerySettings,
        object_store: ObjectStore,
        workspace_service: WorkspaceService,
        session: async_sessionmaker[AsyncSession],
    ) -> None:
        self._settings = settings
        self._object_store = object_store
        self._workspace_service = workspace_service
        self._session_factory = session
        self._publisher = IngestPublisher()
        # Cap concurrent per-section LLM calls (describe + column naming).
        # A 60-section dashboard XLSX runs ~120 LLM calls; serialising
        # them takes ~4 min, firing all at once trips Anthropic's per-key
        # rate limit. ``settings.ingest_section_concurrency`` defaults to 8.
        self._stage_semaphore = asyncio.Semaphore(getattr(settings, "ingest_section_concurrency", 8))

    async def ingest_upload(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        filename: str,
        file_bytes: bytes,
        actor: str,
        dataset_name: str = "dataset",
        workspace_locale: str | None = None,
    ) -> IngestResult:
        """Run stages 1-3 + 9-10 synchronously for a new file upload.

        Returns the created file_id + list of tables created.
        """
        locale = workspace_locale or self._settings.default_locale

        # --- Load workspace for storage quota check ---
        ws = await self._workspace_service.get(workspace_id)
        storage_used = ws["storage_used_bytes"] if ws else 0

        # --- Stage 1: receive ---
        recv = await run_receive(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            filename=filename,
            file_bytes=file_bytes,
            actor=actor,
            object_store=self._object_store,
            session_factory=self._session_factory,
            settings=self._settings,
            workspace_storage_used_bytes=storage_used,
        )

        # Track storage usage
        await self._workspace_service.track_storage(workspace_id, recv.size_bytes)

        # --- Stage 2: parse ---
        parsed_tables = await run_parse(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            file_id=recv.file_id,
            local_temp_path=recv.local_temp_path,
            file_format=recv.file_format,
            compression=recv.compression,
            object_store=self._object_store,
            session_factory=self._session_factory,
            settings=self._settings,
            existing_table_id=None,
            dataset_name=dataset_name,
            workspace_locale=locale,
            original_filename=filename,
        )

        # --- Stages 3, 4, 5, 7, 9, 10 per table ---
        # Stages 6 (relations), 8 (pii_tag) intentionally deferred to
        # the async worker; they're not on the critical path for the
        # first NL query against the table.
        #
        # Sections are processed in parallel via asyncio.gather, capped
        # by ``self._stage_semaphore``. The cap exists to keep concurrent
        # LLM calls under the provider's rate limit -- describe + column
        # naming both hit the LLM provider, and a 60-section XLSX can
        # otherwise spam 120 concurrent requests against Anthropic.
        ingested = await asyncio.gather(
            *[
                self._process_section(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset_id,
                    actor=actor,
                    parsed=pt,
                )
                for pt in parsed_tables
            ]
        )
        ingested = [t for t in ingested if t is not None]

        logger.info(
            "ingest_upload complete file_id=%s tables=%d",
            recv.file_id,
            len(ingested),
        )
        return IngestResult(file_id=str(recv.file_id), tables=ingested)

    async def _process_section(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        actor: str,
        parsed: Any,  # ParsedTable
    ) -> IngestedTable | None:
        """Run reconcile -> sample -> profile -> describe -> embed -> publish.

        Bracketed by ``self._stage_semaphore`` to cap concurrent LLM
        calls; everything inside the bracket is happy to run in parallel
        with other sections (each section owns its own snapshot id and
        its own Parquet local path, so DuckDB / sample / profile don't
        contend).
        """
        async with self._stage_semaphore:
            rec = await run_reconcile(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                parsed=parsed,
                actor=actor,
                triggered_by="USER",
                session_factory=self._session_factory,
            )

            local_parquet = parsed.local_parquet_path or parsed.parquet_key

            # --- Stage 4: sample ---
            # Reads the local Parquet directly so DuckDB resolves the
            # path natively. Failures are logged and skipped -- the
            # describe stage still works without samples (column name
            # + data type alone).
            try:
                await run_sample(
                    tenant_id=tenant_id,
                    snapshot_id=rec.snapshot_id,
                    parquet_key=local_parquet,
                    session_factory=self._session_factory,
                    settings=self._settings,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("stage=sample snapshot=%s skipped err=%s", rec.snapshot_id, exc)

            # --- Stage 5: profile (small-table stats) ---
            try:
                await run_profile(
                    tenant_id=tenant_id,
                    snapshot_id=rec.snapshot_id,
                    parquet_key=local_parquet,
                    n_rows_actual=rec.n_rows_actual,
                    session_factory=self._session_factory,
                    settings=self._settings,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("stage=profile snapshot=%s skipped err=%s", rec.snapshot_id, exc)

            # --- Stage 7: describe (AI column descriptions + synonyms) ---
            # CRITICAL for grounding: without descriptions the Grounding
            # agent can't match user questions to actual tables/columns
            # and falls back to hallucinated names. Skipped silently
            # if no LLM key is configured -- ingestion still succeeds.
            try:
                await run_describe(
                    tenant_id=tenant_id,
                    snapshot_id=rec.snapshot_id,
                    session_factory=self._session_factory,
                    settings=self._settings,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("stage=describe snapshot=%s skipped err=%s", rec.snapshot_id, exc)

            # --- Stage 9: embed ---
            # Runs AFTER describe so embeddings include the AI-generated
            # description + synonyms in the corpus, not just the bare
            # column name.
            await run_embed(
                tenant_id=tenant_id,
                snapshot_id=rec.snapshot_id,
                session_factory=self._session_factory,
                settings=self._settings,
            )

            await run_publish(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                table_id=parsed.table_id,
                snapshot_id=rec.snapshot_id,
                n_columns=rec.n_columns,
                n_rows_actual=rec.n_rows_actual,
                publisher=self._publisher,
                session_factory=self._session_factory,
            )

            # Clean up the local Parquet now that every downstream stage
            # is finished with it. Keeping these around for a 60-section
            # XLSX wastes ~50MB of /tmp.
            if parsed.local_parquet_path:
                try:
                    from pathlib import Path

                    Path(parsed.local_parquet_path).unlink(missing_ok=True)
                except OSError:  # noqa: BLE001
                    pass

            return IngestedTable(
                table_id=str(parsed.table_id),
                name=parsed.name,
                n_columns=rec.n_columns,
                n_rows_estimate=rec.n_rows_actual,
                snapshot_id=str(rec.snapshot_id),
            )

    async def ingest_reupload(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        table_id: uuid.UUID,
        filename: str,
        file_bytes: bytes,
        actor: str,
        dataset_name: str = "dataset",
        workspace_locale: str | None = None,
    ) -> IngestResult:
        """Run stages 1-3 + 9-10 for re-uploading into an existing table slot."""
        locale = workspace_locale or self._settings.default_locale

        ws = await self._workspace_service.get(workspace_id)
        storage_used = ws["storage_used_bytes"] if ws else 0

        # Stage 1
        recv = await run_receive(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            filename=filename,
            file_bytes=file_bytes,
            actor=actor,
            object_store=self._object_store,
            session_factory=self._session_factory,
            settings=self._settings,
            workspace_storage_used_bytes=storage_used,
        )

        await self._workspace_service.track_storage(workspace_id, recv.size_bytes)

        # Stage 2 (re-upload into existing slot)
        parsed_tables = await run_parse(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            file_id=recv.file_id,
            local_temp_path=recv.local_temp_path,
            file_format=recv.file_format,
            compression=recv.compression,
            object_store=self._object_store,
            session_factory=self._session_factory,
            settings=self._settings,
            existing_table_id=table_id,
            dataset_name=dataset_name,
            workspace_locale=locale,
            original_filename=filename,
        )

        # Same parallel fan-out as the fresh-upload path.
        ingested_raw = await asyncio.gather(
            *[
                self._process_section(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset_id,
                    actor=actor,
                    parsed=pt,
                )
                for pt in parsed_tables
            ]
        )
        ingested = [t for t in ingested_raw if t is not None]

        return IngestResult(file_id=str(recv.file_id), tables=ingested)
