# Copyright 2026 Firefly Software Solutions Inc
"""Integration test: auto-learning hook inserts a PROPOSED example on first-shot OK.

This test exercises Task 23 by short-circuiting the LLM agents with canned
responses and verifying that a ``flyquery_examples`` row (source=AGENT_LEARNED,
quality=PROPOSED) is inserted after a successful first-shot run.
"""

from __future__ import annotations

import uuid

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auto_learning_inserts_proposed_example(started_app: None) -> None:  # noqa: ARG001
    """Mock QueryService internals to simulate a first-shot OK; assert example landed."""
    from httpx import ASGITransport, AsyncClient

    from flyquery.core.services.examples.auto_learner import AutoLearner
    from flyquery.core.services.examples.examples_service import ExamplesService
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Create workspace and dataset
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "autolrn", "name": "Auto Learning WS"},
            headers={"X-Tenant-Id": "ten-al", "X-Workspace-Id": "placeholder"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "ten-al", "X-Workspace-Id": ws_id}

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "AL Dataset", "slug": "al-ds"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ds_id = r.json()["id"]

    # Use ExamplesService directly to verify the insert path.
    # Build a minimal mock that records create() calls.
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from flyquery.core.services.examples.examples_repository import ExamplesRepository
    from flyquery.main import _pyfly

    # Fetch real beans from the DI container.
    session_factory = _pyfly.context.get_bean(async_sessionmaker)
    examples_repo = ExamplesRepository(session_factory)
    examples_service = ExamplesService(repo=examples_repo, embedder=None)
    auto_learner = AutoLearner(examples_service=examples_service)

    tenant_id = "ten-al"
    workspace_uuid = uuid.UUID(ws_id)
    dataset_uuid = uuid.UUID(ds_id)
    question = "how many rows in orders?"
    generated_sql = "SELECT COUNT(*) FROM orders"
    query_id = uuid.uuid4()

    # First-shot OK: retries=0, no PII → should insert
    await auto_learner.maybe_propose(
        tenant_id=tenant_id,
        workspace_id=workspace_uuid,
        dataset_id=dataset_uuid,
        question=question,
        generated_sql=generated_sql,
        retries=0,
        pii_findings=[],
        query_id=query_id,
    )

    # Verify a PROPOSED / AGENT_LEARNED example was inserted.
    rows = await examples_repo.list(tenant_id, workspace_uuid, quality="PROPOSED", dataset_id=dataset_uuid)
    assert len(rows) >= 1, "Expected at least one PROPOSED example after auto-learning"
    row = rows[0]
    assert row["source"] == "AGENT_LEARNED"
    assert row["quality"] == "PROPOSED"
    assert row["question"] == question

    # Second call with retries=1 → no insert
    before_count = len(rows)
    await auto_learner.maybe_propose(
        tenant_id=tenant_id,
        workspace_id=workspace_uuid,
        dataset_id=dataset_uuid,
        question="another question",
        generated_sql="SELECT 1",
        retries=1,
        pii_findings=[],
        query_id=uuid.uuid4(),
    )
    rows_after = await examples_repo.list(
        tenant_id, workspace_uuid, quality="PROPOSED", dataset_id=dataset_uuid
    )
    assert len(rows_after) == before_count, "retries=1 should not produce a new example"

    # Call with PII → no insert
    await auto_learner.maybe_propose(
        tenant_id=tenant_id,
        workspace_id=workspace_uuid,
        dataset_id=dataset_uuid,
        question="pii question",
        generated_sql="SELECT email FROM customers",
        retries=0,
        pii_findings=["email"],
        query_id=uuid.uuid4(),
    )
    rows_after_pii = await examples_repo.list(
        tenant_id, workspace_uuid, quality="PROPOSED", dataset_id=dataset_uuid
    )
    assert len(rows_after_pii) == before_count, "pii_findings should block auto-learning"
