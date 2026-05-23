# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for MetricFlowCompiler + SemanticService (publish path)."""

from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


SIMPLE_METRIC_YAML = """
name: revenue_by_region
label: Revenue by Region
description: Total order revenue by region
metric_type: SIMPLE
agg: sum
expr: orders.total
joins:
  - from: orders.customer_id
    to: customers.customer_id
group_by:
  - customers.region
"""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_publish_sets_compiled_sql(started_app: None) -> None:  # noqa: ARG001
    """Create → publish a metric; verify compiled_sql_template is set and parseable."""
    import os

    import sqlglot

    from flyquery.core.services.semantic.semantic_repository import SemanticRepository
    from flyquery.core.services.semantic.semantic_service import SemanticService
    from flyquery.interfaces.semantic import SemanticMetricCreate

    db_url = os.environ["FLYQUERY_DATABASE_URL"]
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    tenant = "ten-sem"
    ws_id = uuid.uuid4()
    ds_id = uuid.uuid4()

    # Seed workspace + dataset
    async with factory() as s, s.begin():
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_workspaces (id, tenant_id, slug, name, status) "
                "VALUES (:id, :t, :slug, :name, 'ACTIVE')"
            ),
            {"id": ws_id, "t": tenant, "slug": f"smws-{ws_id}", "name": "Sem WS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_datasets (id, tenant_id, workspace_id, name, status, drift_policy) "
                "VALUES (:id, :t, :ws, :name, 'ACTIVE', 'WARN')"
            ),
            {"id": ds_id, "t": tenant, "ws": ws_id, "name": "Sem DS"},
        )

    repo = SemanticRepository(factory)
    svc = SemanticService(repo)

    # Create metric
    metric = await svc.create(
        tenant,
        ws_id,
        SemanticMetricCreate(
            dataset_id=ds_id,
            name="revenue_by_region",
            definition_yaml=SIMPLE_METRIC_YAML,
        ),
    )
    assert metric["status"] == "DRAFT"
    assert metric["compiled_sql_template"] is None

    # Publish
    published = await svc.publish(metric["id"])
    assert published["status"] == "PUBLISHED"
    assert published["compiled_sql_template"] is not None
    sql = published["compiled_sql_template"]
    assert len(sql) > 0

    # Must be parseable by sqlglot
    parsed = sqlglot.parse_one(sql, read="duckdb")
    assert parsed is not None

    # History should have at least 1 version
    history = await svc.list_history(metric["id"])
    assert len(history) >= 1

    await engine.dispose()
