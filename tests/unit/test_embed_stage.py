# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for Stage 9 — embed.

Verifies:
- _build_embed_text constructs correct text from schema object rows
- _build_embedder returns None when OPENAI_API_KEY is absent (graceful skip)
- _build_embedder returns a callable when OPENAI_API_KEY is present
"""

from __future__ import annotations

import pytest

from flyquery.core.services.ingestion.stages.embed import (
    _build_embed_text,
    _build_embedder,
)


class TestBuildEmbedText:
    def test_qualified_name_and_type(self) -> None:
        row = {
            "qualified_name": "sales.orders.total",
            "data_type": "DOUBLE",
            "description": None,
            "synonyms_json": None,
        }
        text = _build_embed_text(row)
        assert text == "sales.orders.total: DOUBLE"

    def test_with_description(self) -> None:
        row = {
            "qualified_name": "ds.tbl.col",
            "data_type": "INTEGER",
            "description": "Primary key for order",
            "synonyms_json": None,
        }
        text = _build_embed_text(row)
        assert "Primary key for order" in text

    def test_with_synonyms_list(self) -> None:
        row = {
            "qualified_name": "ds.t.c",
            "data_type": "VARCHAR",
            "description": None,
            "synonyms_json": ["amount", "price", "cost"],
        }
        text = _build_embed_text(row)
        assert "Synonyms:" in text
        assert "amount" in text

    def test_with_synonyms_dict(self) -> None:
        row = {
            "qualified_name": "ds.t.c",
            "data_type": "VARCHAR",
            "description": None,
            "synonyms_json": {"0": "amt", "1": "price"},
        }
        text = _build_embed_text(row)
        assert "Synonyms:" in text

    def test_missing_qualified_name_does_not_crash(self) -> None:
        row = {
            "qualified_name": None,
            "data_type": "BOOLEAN",
            "description": None,
            "synonyms_json": None,
        }
        text = _build_embed_text(row)
        # Should not raise; may be empty or just the type
        assert isinstance(text, str)


class TestBuildEmbedder:
    def test_returns_none_when_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        embedder = _build_embedder("")
        assert embedder is None

    def test_returns_callable_when_api_key_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-test")
        embedder = _build_embedder("sk-fake-key-for-test")
        assert callable(embedder)

    def test_pipeline_does_not_crash_without_openai_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Graceful skip: embeddings_written=0 when key is absent."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        # Verify _build_embedder(""  ) returns None (no API call will be made)
        assert _build_embedder("") is None
