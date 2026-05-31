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

"""Unit tests for ExamplesService."""

from __future__ import annotations

import uuid

import pytest

from flyquery.core.services.examples.examples_service import ExamplesService
from flyquery.interfaces.examples import ExampleCreate


class FakeRepo:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    async def create(self, **fields: object) -> dict:
        row = {**fields, "id": uuid.uuid4()}
        self.rows.append(row)
        return row

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        quality: str | None = None,
        dataset_id: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[dict]:
        result = [r for r in self.rows if r["tenant_id"] == tenant_id and r["workspace_id"] == workspace_id]
        if quality is not None:
            result = [r for r in result if r.get("quality") == quality]
        if dataset_id is not None:
            result = [r for r in result if r.get("dataset_id") == dataset_id]
        return result[:limit]

    async def get(self, example_id: uuid.UUID) -> dict | None:
        for r in self.rows:
            if r.get("id") == example_id:
                return r
        return None

    async def update_quality(self, example_id: uuid.UUID, quality: str) -> dict:
        for r in self.rows:
            if r.get("id") == example_id:
                r["quality"] = quality
                return r
        raise KeyError(f"example {example_id} not found")


@pytest.mark.asyncio
async def test_create_human_example_defaults() -> None:
    svc = ExamplesService(FakeRepo(), embedder=None)
    ws = uuid.uuid4()
    ex = await svc.create(
        "ten-a",
        ws,
        ExampleCreate(
            question="how many orders by region",
            generated_sql="SELECT region, count(*) FROM orders GROUP BY 1",
        ),
    )
    assert ex["source"] == "USER_CURATED"
    assert ex["quality"] == "PROPOSED"
    assert ex["created_by"] == "user"


@pytest.mark.asyncio
async def test_create_normalises_sql() -> None:
    svc = ExamplesService(FakeRepo(), embedder=None)
    ws = uuid.uuid4()
    ex = await svc.create(
        "ten-a",
        ws,
        ExampleCreate(
            question="count",
            generated_sql="SELECT   COUNT(*)   FROM   orders",
        ),
    )
    # normalised_sql must be non-empty and collapsed (no multiple spaces)
    assert ex["normalised_sql"]
    assert "  " not in ex["normalised_sql"]  # whitespace collapsed
    assert "orders" in ex["normalised_sql"].lower()


@pytest.mark.asyncio
async def test_list_returns_only_approved_for_retrieval() -> None:
    repo = FakeRepo()
    svc = ExamplesService(repo, embedder=None)
    ws = uuid.uuid4()
    ex = await svc.create(
        "ten-a",
        ws,
        ExampleCreate(question="q1", generated_sql="SELECT 1"),
    )
    # Default list — no quality filter — returns 1
    items = await svc.list("ten-a", ws)
    assert len(items) == 1

    # Filter quality=APPROVED → empty because ex is still PROPOSED
    items_approved = await svc.list("ten-a", ws, quality="APPROVED")
    assert len(items_approved) == 0

    # After approve, filter returns the row
    await svc.approve(ex["id"])
    items_approved = await svc.list("ten-a", ws, quality="APPROVED")
    assert len(items_approved) == 1


@pytest.mark.asyncio
async def test_create_agent_learned_overrides_defaults() -> None:
    svc = ExamplesService(FakeRepo(), embedder=None)
    ws = uuid.uuid4()
    ex = await svc.create(
        "ten-a",
        ws,
        ExampleCreate(question="q", generated_sql="SELECT 1"),
        source="AGENT_LEARNED",
        quality="PROPOSED",
        actor="agent",
    )
    assert ex["source"] == "AGENT_LEARNED"
    assert ex["created_by"] == "agent"


@pytest.mark.asyncio
async def test_reject_sets_quality() -> None:
    svc = ExamplesService(FakeRepo(), embedder=None)
    ws = uuid.uuid4()
    ex = await svc.create(
        "ten-a",
        ws,
        ExampleCreate(question="q", generated_sql="SELECT 1"),
    )
    rejected = await svc.reject(ex["id"])
    assert rejected["quality"] == "REJECTED"
