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

"""Unit tests for SemanticService with in-memory fake repositories."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from flyquery.core.services.semantic.errors import SemanticCompileError
from flyquery.core.services.semantic.semantic_service import SemanticService
from flyquery.interfaces.semantic import SemanticMetricCreate, SemanticMetricUpdate

TENANT = "ten-1"
WS = uuid.uuid4()
DS = uuid.uuid4()

SIMPLE = """
metric:
  name: total_revenue
  type: simple
  type_params:
    measure: {name: amt, agg: sum, expr: orders.amount}
    filter: "orders.status = 'OK'"
  meta: {owner: finance}
"""

INJECTION = """
metric:
  name: bad
  type: simple
  type_params:
    measure: {name: a, agg: sum, expr: orders.amt}
    filter: "id IN (SELECT secret FROM other)"
"""


class FakeMetricRepo:
    def __init__(self) -> None:
        self.store: dict[uuid.UUID, dict[str, Any]] = {}

    async def create_metric(self, **f: Any) -> dict[str, Any]:
        row = {
            "id": uuid.uuid4(),
            "status": "DRAFT",
            "current_version": 1,
            "compiled_sql_template": None,
            **f,
        }
        self.store[row["id"]] = row
        return row

    async def get_metric(self, mid, *, tenant_id, workspace_id):  # noqa: ANN001
        return self.store.get(mid)

    async def get_by_name(self, name, dataset_id, *, tenant_id, workspace_id):  # noqa: ANN001
        for r in self.store.values():
            if r["name"] == name and r["status"] == "PUBLISHED":
                return r
        return None

    async def update_metric(self, mid, *, tenant_id, workspace_id, **f: Any):  # noqa: ANN001
        self.store[mid].update(f)
        self.store[mid]["current_version"] += 1
        return self.store[mid]

    async def publish_metric(self, mid, compiled, *, tenant_id, workspace_id):  # noqa: ANN001
        self.store[mid]["status"] = "PUBLISHED"
        self.store[mid]["compiled_sql_template"] = compiled
        return self.store[mid]

    async def retire_metric(self, mid, *, tenant_id, workspace_id):  # noqa: ANN001
        self.store[mid]["status"] = "RETIRED"
        return self.store[mid]

    async def list_metrics(self, t, w, *, dataset_id=None, status=None):  # noqa: ANN001
        return [r for r in self.store.values() if status is None or r["status"] == status]

    async def list_history(self, mid, *, tenant_id, workspace_id):  # noqa: ANN001
        return []


class FakeDimRepo:
    async def get_by_name(self, name, dataset_id, *, tenant_id, workspace_id):  # noqa: ANN001
        return None


def _svc() -> SemanticService:
    return SemanticService(FakeMetricRepo(), FakeDimRepo())


def _create_body(yaml_str: str = SIMPLE, name: str = "total_revenue") -> SemanticMetricCreate:
    return SemanticMetricCreate(dataset_id=DS, name=name, definition_yaml=yaml_str)


@pytest.mark.asyncio
async def test_create_derives_type_and_meta() -> None:
    svc = _svc()
    row = await svc.create(TENANT, WS, _create_body())
    assert row["status"] == "DRAFT"
    assert row["metric_type"] == "SIMPLE"
    assert row["metadata_json"] == {"owner": "finance"}


@pytest.mark.asyncio
async def test_publish_compiles_and_sets_template() -> None:
    svc = _svc()
    created = await svc.create(TENANT, WS, _create_body())
    published = await svc.publish(TENANT, WS, created["id"])
    assert published["status"] == "PUBLISHED"
    assert "SUM(orders.amount) AS total_revenue" in published["compiled_sql_template"]
    assert "{extra_filter_clause}" in published["compiled_sql_template"]


@pytest.mark.asyncio
async def test_publish_rejects_injection_filter() -> None:
    svc = _svc()
    created = await svc.create(TENANT, WS, _create_body(INJECTION, name="bad"))
    with pytest.raises(SemanticCompileError):
        await svc.publish(TENANT, WS, created["id"])


@pytest.mark.asyncio
async def test_update_published_recompiles() -> None:
    svc = _svc()
    created = await svc.create(TENANT, WS, _create_body())
    await svc.publish(TENANT, WS, created["id"])
    new_yaml = SIMPLE.replace("agg: sum", "agg: count")
    updated = await svc.update(
        TENANT, WS, created["id"], SemanticMetricUpdate(definition_yaml=new_yaml)
    )
    assert updated["status"] == "PUBLISHED"
    assert "COUNT(orders.amount) AS total_revenue" in updated["compiled_sql_template"]
    assert updated["current_version"] == 2


@pytest.mark.asyncio
async def test_retire_flips_status() -> None:
    svc = _svc()
    created = await svc.create(TENANT, WS, _create_body())
    retired = await svc.retire(TENANT, WS, created["id"])
    assert retired["status"] == "RETIRED"


@pytest.mark.asyncio
async def test_publish_missing_metric_raises() -> None:
    svc = _svc()
    with pytest.raises(KeyError):
        await svc.publish(TENANT, WS, uuid.uuid4())
