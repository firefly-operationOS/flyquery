# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for SemanticCompiler + SemanticService (publish path)."""

from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

SIMPLE_METRIC_YAML = """
metric:
  name: revenue_by_region
  label: Revenue by Region
  description: Total order revenue by region
  type: simple
  type_params:
    measure: {name: total, agg: sum, expr: orders.total}
    filter: "orders.status = 'COMPLETED'"
  group_by:
    - orders.region
  meta:
    owner: finance
"""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_publish_sets_compiled_sql(started_app: None) -> None:  # noqa: ARG001
    """Create → publish a metric; verify compiled_sql_template is set and parseable."""
    import os

    import sqlglot

    from flyquery.core.services.semantic.semantic_dimensions_repository import (
        SemanticDimensionsRepository,
    )
    from flyquery.core.services.semantic.semantic_repository import SemanticRepository
    from flyquery.core.services.semantic.semantic_service import SemanticService
    from flyquery.interfaces.semantic import SemanticMetricCreate

    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"].replace("+psycopg", "+asyncpg")
    db_url = os.environ["FLYQUERY_DATABASE_URL"]
    seed_engine = create_async_engine(admin_url)
    engine = create_async_engine(db_url)
    seed_factory = async_sessionmaker(seed_engine, expire_on_commit=False)
    async_sessionmaker(engine, expire_on_commit=False)

    tenant = "ten-sem"
    ws_id = uuid.uuid4()
    ds_id = uuid.uuid4()

    # Seed workspace + dataset (admin role bypasses RLS for setup)
    async with seed_factory() as s, s.begin():
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
    await seed_engine.dispose()

    # SemanticRepository uses its factory for all writes; use admin factory to
    # bypass RLS in tests (mirrors how the HTTP layer sets tenant GUCs before inserts).
    admin_factory2 = async_sessionmaker(create_async_engine(admin_url), expire_on_commit=False)
    repo = SemanticRepository(admin_factory2)
    dim_repo = SemanticDimensionsRepository(admin_factory2)
    svc = SemanticService(repo, dim_repo)

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
    assert metric["metric_type"] == "SIMPLE"
    assert metric["metadata_json"] == {"owner": "finance"}

    # Publish
    published = await svc.publish(tenant, ws_id, metric["id"])
    assert published["status"] == "PUBLISHED"
    sql = published["compiled_sql_template"]
    assert sql and "SUM(orders.total) AS revenue_by_region" in sql

    # Must be parseable by sqlglot (slots stripped first)
    bound = sql.replace("{extra_filter_clause}", "").replace("{group_by_append}", "")
    assert sqlglot.parse_one(bound, read="duckdb") is not None

    # Published metric is resolvable by name for the query fast-path.
    by_name = await repo.get_by_name(
        "revenue_by_region", ds_id, tenant_id=tenant, workspace_id=ws_id
    )
    assert by_name is not None and by_name["compiled_sql_template"] == sql

    # History records the compiled SQL on the published version (no longer NULL).
    history = await svc.list_history(tenant, ws_id, metric["id"])
    assert len(history) >= 1
    assert history[-1]["compiled_sql_template"] == sql

    await engine.dispose()
