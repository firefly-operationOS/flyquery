# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for GlossaryService."""

from __future__ import annotations

import uuid

import pytest

from flyquery.core.services.glossary.glossary_service import GlossaryService
from flyquery.interfaces.glossary import GlossaryTermCreate, GlossaryTermUpdate


class FakeGlossaryRepo:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    async def create(self, **fields: object) -> dict:
        row = {**fields, "id": uuid.uuid4(), "created_at": "2026-01-01", "updated_at": "2026-01-01"}
        self.rows.append(row)
        return row

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        result = [r for r in self.rows if r["tenant_id"] == tenant_id and r["workspace_id"] == workspace_id]
        return result[offset : offset + limit]

    async def get(self, term_id: uuid.UUID) -> dict | None:
        for r in self.rows:
            if r.get("id") == term_id:
                return r
        return None

    async def update(self, term_id: uuid.UUID, **fields: object) -> dict:
        for r in self.rows:
            if r.get("id") == term_id:
                r.update(fields)
                return r
        raise KeyError(f"term {term_id} not found")

    async def delete(self, term_id: uuid.UUID) -> None:
        self.rows = [r for r in self.rows if r.get("id") != term_id]


@pytest.mark.asyncio
async def test_create_glossary_term() -> None:
    svc = GlossaryService(FakeGlossaryRepo())
    ws = uuid.uuid4()
    row = await svc.create(
        "ten-a",
        ws,
        GlossaryTermCreate(term="revenue", definition="Total money from sales"),
    )
    assert row["term"] == "revenue"
    assert row["definition"] == "Total money from sales"
    assert row["synonyms_json"] == []


@pytest.mark.asyncio
async def test_list_returns_workspace_terms() -> None:
    svc = GlossaryService(FakeGlossaryRepo())
    ws = uuid.uuid4()
    other_ws = uuid.uuid4()
    await svc.create("ten-a", ws, GlossaryTermCreate(term="revenue", definition="Sales total"))
    await svc.create("ten-a", other_ws, GlossaryTermCreate(term="churn", definition="Lost customers"))

    items = await svc.list("ten-a", ws)
    assert len(items) == 1
    assert items[0]["term"] == "revenue"


@pytest.mark.asyncio
async def test_update_definition() -> None:
    repo = FakeGlossaryRepo()
    svc = GlossaryService(repo)
    ws = uuid.uuid4()
    row = await svc.create("ten-a", ws, GlossaryTermCreate(term="revenue", definition="Old def"))
    updated = await svc.update(row["id"], GlossaryTermUpdate(definition="New def"))
    assert updated["definition"] == "New def"


@pytest.mark.asyncio
async def test_delete_removes_term() -> None:
    repo = FakeGlossaryRepo()
    svc = GlossaryService(repo)
    ws = uuid.uuid4()
    row = await svc.create("ten-a", ws, GlossaryTermCreate(term="revenue", definition="Sales total"))
    await svc.delete(row["id"])
    items = await svc.list("ten-a", ws)
    assert len(items) == 0
