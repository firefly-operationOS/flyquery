# Copyright 2026 Firefly Software Solutions Inc
"""IngestService — synchronous orchestrator for Stages 1-3 + 9-10.

Wired as a pyfly @service bean. Injected into the FilesController.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any

from pyfly.container import service as service_bean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.config import FlyquerySettings
from flyquery.core.eda.ingest_publisher import IngestPublisher
from flyquery.core.services.ingestion.stages.embed import run_embed
from flyquery.core.services.ingestion.stages.parse import run_parse
from flyquery.core.services.ingestion.stages.publish import run_publish
from flyquery.core.services.ingestion.stages.receive import run_receive
from flyquery.core.services.ingestion.stages.reconcile import run_reconcile
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

        # --- Stages 3, 9, 10 per table ---
        ingested: list[IngestedTable] = []
        for pt in parsed_tables:
            rec = await run_reconcile(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                parsed=pt,
                actor=actor,
                triggered_by="USER",
                session_factory=self._session_factory,
            )

            await run_embed(
                tenant_id=tenant_id,
                snapshot_id=rec.snapshot_id,
                session_factory=self._session_factory,
            )

            await run_publish(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                table_id=pt.table_id,
                snapshot_id=rec.snapshot_id,
                n_columns=rec.n_columns,
                n_rows_actual=rec.n_rows_actual,
                publisher=self._publisher,
                session_factory=self._session_factory,
            )

            ingested.append(
                IngestedTable(
                    table_id=str(pt.table_id),
                    name=pt.name,
                    n_columns=rec.n_columns,
                    n_rows_estimate=rec.n_rows_actual,
                    snapshot_id=str(rec.snapshot_id),
                )
            )

        logger.info(
            "ingest_upload complete file_id=%s tables=%d",
            recv.file_id,
            len(ingested),
        )
        return IngestResult(file_id=str(recv.file_id), tables=ingested)

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

        ingested: list[IngestedTable] = []
        for pt in parsed_tables:
            rec = await run_reconcile(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                parsed=pt,
                actor=actor,
                triggered_by="USER",
                session_factory=self._session_factory,
            )

            await run_embed(
                tenant_id=tenant_id,
                snapshot_id=rec.snapshot_id,
                session_factory=self._session_factory,
            )

            await run_publish(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                table_id=pt.table_id,
                snapshot_id=rec.snapshot_id,
                n_columns=rec.n_columns,
                n_rows_actual=rec.n_rows_actual,
                publisher=self._publisher,
                session_factory=self._session_factory,
            )

            ingested.append(
                IngestedTable(
                    table_id=str(pt.table_id),
                    name=pt.name,
                    n_columns=rec.n_columns,
                    n_rows_estimate=rec.n_rows_actual,
                    snapshot_id=str(rec.snapshot_id),
                )
            )

        return IngestResult(file_id=str(recv.file_id), tables=ingested)
