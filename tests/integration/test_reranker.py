# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for reranker module (deterministic, no LLM needed)."""

from __future__ import annotations

import uuid

import pytest

from flyquery.core.services.retrieval.reranker import NoopReranker, build_reranker
from flyquery.core.services.retrieval.search_index import Hit


def _make_hits(n: int) -> list[Hit]:
    return [
        Hit(
            source_kind="schema_object",
            id=uuid.uuid4(),
            text=f"hit {i}",
            score=float(n - i),
            metadata={},
        )
        for i in range(n)
    ]


@pytest.mark.asyncio
async def test_noop_reranker_truncates() -> None:
    reranker = NoopReranker()
    hits = _make_hits(10)
    result = await reranker.rerank("revenue", hits, top_n=5)
    assert len(result) == 5
    assert result == hits[:5]


@pytest.mark.asyncio
async def test_noop_reranker_handles_empty() -> None:
    reranker = NoopReranker()
    result = await reranker.rerank("revenue", [], top_n=5)
    assert result == []


@pytest.mark.asyncio
async def test_build_reranker_returns_noop_when_no_model() -> None:
    class FakeSettings:
        reranker_model = ""

    r = build_reranker(FakeSettings())
    assert isinstance(r, NoopReranker)


@pytest.mark.asyncio
async def test_build_reranker_falls_back_on_bad_model() -> None:
    class FakeSettings:
        reranker_model = "nonexistent/model-that-does-not-exist"

    r = build_reranker(FakeSettings())
    # Should fall back silently to Noop when sentence-transformers isn't installed
    # or the model can't be loaded.
    assert isinstance(r, NoopReranker)


@pytest.mark.asyncio
async def test_noop_reranker_does_not_change_order() -> None:
    reranker = NoopReranker()
    hits = _make_hits(4)
    original_ids = [h.id for h in hits]
    result = await reranker.rerank("test", hits, top_n=4)
    assert [h.id for h in result] == original_ids
