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

"""Unit tests for SemanticDimensionsService with an in-memory fake repository."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from flyquery.core.services.semantic.semantic_dimensions_service import (
    SemanticDimensionsService,
)
from flyquery.interfaces.semantic import SemanticDimensionCreate

TENANT = "ten-1"
WS = uuid.uuid4()
DS = uuid.uuid4()

CATEGORICAL = "dimension:\n  name: order_region\n  type: categorical\n  expr: orders.region\n"
TIME = "dimension:\n  name: order_day\n  type: time\n  expr: orders.dt\n  grain: day\n"


class FakeDimRepo:
    def __init__(self) -> None:
        self.store: dict[uuid.UUID, dict[str, Any]] = {}

    async def create_dimension(self, **f: Any) -> dict[str, Any]:
        row = {
            "id": uuid.uuid4(),
            "status": "DRAFT",
            "current_version": 1,
            "compiled_sql_template": None,
            **f,
        }
        self.store[row["id"]] = row
        return row

    async def get_dimension(self, did, *, tenant_id, workspace_id):  # noqa: ANN001
        return self.store.get(did)

    async def publish_dimension(self, did, compiled, *, tenant_id, workspace_id):  # noqa: ANN001
        self.store[did]["status"] = "PUBLISHED"
        self.store[did]["compiled_sql_template"] = compiled
        return self.store[did]

    async def retire_dimension(self, did, *, tenant_id, workspace_id):  # noqa: ANN001
        self.store[did]["status"] = "RETIRED"
        return self.store[did]


def _svc() -> SemanticDimensionsService:
    return SemanticDimensionsService(FakeDimRepo())


@pytest.mark.asyncio
async def test_create_categorical_dimension() -> None:
    svc = _svc()
    row = await svc.create(
        TENANT, WS, SemanticDimensionCreate(dataset_id=DS, name="order_region", definition_yaml=CATEGORICAL)
    )
    assert row["dimension_type"] == "categorical"
    assert row["status"] == "DRAFT"


@pytest.mark.asyncio
async def test_publish_categorical_dimension_stores_expr() -> None:
    svc = _svc()
    created = await svc.create(
        TENANT, WS, SemanticDimensionCreate(dataset_id=DS, name="order_region", definition_yaml=CATEGORICAL)
    )
    published = await svc.publish(TENANT, WS, created["id"])
    assert published["status"] == "PUBLISHED"
    assert published["compiled_sql_template"] == "orders.region"


@pytest.mark.asyncio
async def test_publish_time_dimension_applies_grain() -> None:
    svc = _svc()
    created = await svc.create(
        TENANT, WS, SemanticDimensionCreate(dataset_id=DS, name="order_day", definition_yaml=TIME)
    )
    published = await svc.publish(TENANT, WS, created["id"])
    assert published["compiled_sql_template"] == "DATE_TRUNC('day', orders.dt)"
