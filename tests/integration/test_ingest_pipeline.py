# Copyright 2026 Firefly Software Solutions Inc
"""Integration test for the synchronous ingestion pipeline (stages 1-3 + 9-10).

Verifies the 10-stage pipeline end-to-end at the service level (no HTTP layer),
which is faster and more precise than the full controller round-trip test.
"""

from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_pipeline_csv(started_app) -> None:  # noqa: ANN001
    """Upload a CSV via IngestService and verify DB state."""
    # --- Grab DI beans from the running container ---
    from flyquery.core.services.ingestion.ingest_service import IngestService
    from flyquery.main import _pyfly

    svc = _pyfly.context.get_bean(IngestService)
    assert svc is not None

    # We need a real tenant + workspace + dataset
    from flyquery.core.services.datasets.dataset_service import DatasetService
    from flyquery.core.services.workspaces.workspace_service import WorkspaceService
    from flyquery.interfaces.datasets import DatasetCreate
    from flyquery.interfaces.workspaces import WorkspaceCreate

    ws_svc = _pyfly.context.get_bean(WorkspaceService)
    ds_svc = _pyfly.context.get_bean(DatasetService)

    tenant_id = f"tenant-pipe-{uuid.uuid4().hex[:8]}"
    ws = await ws_svc.create(
        tenant_id, WorkspaceCreate(slug=f"pipe-{uuid.uuid4().hex[:6]}", name="Pipeline Test")
    )
    ws_id = ws["id"]

    ds = await ds_svc.create(tenant_id, ws_id, DatasetCreate(name="pipeline-test"))
    ds_id = ds["id"]

    csv_bytes = b"id,name,score\n1,Alice,9.5\n2,Bob,8.2\n3,Carol,7.8\n"

    result = await svc.ingest_upload(
        tenant_id=tenant_id,
        workspace_id=ws_id,
        dataset_id=ds_id,
        filename="scores.csv",
        file_bytes=csv_bytes,
        actor="test-actor",
        dataset_name=ds["name"],
    )

    assert result.file_id
    assert len(result.tables) == 1
    tbl = result.tables[0]
    assert tbl.n_columns == 3
    assert tbl.name == "scores"

    # Verify DB: snapshot is READY

    session_factory = _pyfly.context.get_bean(async_sessionmaker)
    async with session_factory() as s:
        # Snapshot
        r = await s.execute(
            sa.text("SELECT status FROM flyquery_schema_snapshots WHERE id = :sid"),
            {"sid": uuid.UUID(tbl.snapshot_id)},
        )
        snap = r.mappings().one()
        assert snap["status"] == "READY"

        # Table has current_snapshot_id set
        r = await s.execute(
            sa.text("SELECT current_snapshot_id FROM flyquery_tables WHERE id = :tid"),
            {"tid": uuid.UUID(tbl.table_id)},
        )
        tbl_row = r.mappings().one()
        assert str(tbl_row["current_snapshot_id"]) == tbl.snapshot_id

        # Schema objects: 1 TABLE + 3 COLUMN
        r = await s.execute(
            sa.text(
                "SELECT kind, count(*) as cnt FROM flyquery_schema_objects "
                "WHERE snapshot_id = :sid GROUP BY kind ORDER BY kind"
            ),
            {"sid": uuid.UUID(tbl.snapshot_id)},
        )
        obj_counts = {row["kind"]: row["cnt"] for row in r.mappings().all()}
        assert obj_counts.get("TABLE") == 1
        assert obj_counts.get("COLUMN") == 3

        # content_tsv should be set on at least the TABLE object
        r = await s.execute(
            sa.text(
                "SELECT count(*) as cnt FROM flyquery_schema_objects "
                "WHERE snapshot_id = :sid AND content_tsv IS NOT NULL"
            ),
            {"sid": uuid.UUID(tbl.snapshot_id)},
        )
        tsv_count = r.scalar_one()
        assert tsv_count > 0

        # Embedding count depends on the configured provider:
        # * ``null`` (CI default with no remote provider) -> 0
        # * ``ollama`` without the model pre-pulled       -> 0
        # * ``openai`` / ``cohere`` / ... with API key set -> > 0
        # The pipeline must NOT fail when the provider is unavailable;
        # only the content_tsv assertion above is load-bearing.
        r = await s.execute(
            sa.text(
                "SELECT count(*) as cnt FROM flyquery_schema_objects "
                "WHERE snapshot_id = :sid AND embedding IS NOT NULL"
            ),
            {"sid": uuid.UUID(tbl.snapshot_id)},
        )
        emb_count = r.scalar_one()
        assert emb_count >= 0  # any value is acceptable; embedding is best-effort
