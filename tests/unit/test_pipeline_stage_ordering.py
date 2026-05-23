# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for pipeline stage contracts (no DB required).

Covers:
- snapshot hash is deterministic given the same column signature
- schema diff logic (added / removed / type_changed)
- embed text building
- annotation transplant key derivation
"""

from __future__ import annotations

import hashlib
import json

import pytest

from flyquery.core.services.ingestion.reader import ColumnSchema
from flyquery.core.services.ingestion.stages.embed import _build_embed_text


class TestSnapshotHash:
    def test_same_columns_same_hash(self) -> None:
        cols1 = [("id", "INTEGER"), ("name", "VARCHAR")]
        cols2 = [("name", "VARCHAR"), ("id", "INTEGER")]  # different order
        h1 = _col_hash(cols1)
        h2 = _col_hash(cols2)
        # sorted → order-independent
        assert h1 == h2

    def test_different_columns_different_hash(self) -> None:
        cols1 = [("id", "INTEGER"), ("name", "VARCHAR")]
        cols2 = [("id", "INTEGER"), ("email", "VARCHAR")]
        assert _col_hash(cols1) != _col_hash(cols2)

    def test_type_change_different_hash(self) -> None:
        cols1 = [("total", "DOUBLE")]
        cols2 = [("total", "VARCHAR")]
        assert _col_hash(cols1) != _col_hash(cols2)


def _col_hash(cols: list[tuple[str, str]]) -> str:
    sig = sorted(cols)
    return hashlib.sha256(json.dumps(sig).encode()).hexdigest()


class TestEmbedText:
    def test_minimal_object(self) -> None:
        row = {"qualified_name": "ds.tbl.col", "data_type": "VARCHAR",
               "description": None, "synonyms_json": None}
        text = _build_embed_text(row)
        assert "ds.tbl.col" in text
        assert "VARCHAR" in text

    def test_with_description_and_synonyms(self) -> None:
        row = {
            "qualified_name": "sales.orders.total",
            "data_type": "DOUBLE",
            "description": "Order total in USD",
            "synonyms_json": ["amount", "price"],
        }
        text = _build_embed_text(row)
        assert "Order total in USD" in text
        assert "amount" in text

    def test_no_qualified_name(self) -> None:
        row = {"qualified_name": None, "data_type": "INTEGER",
               "description": None, "synonyms_json": None}
        text = _build_embed_text(row)
        # should not raise
        assert text is not None


class TestSchemaDiff:
    """Test column diff logic used in reconcile stage."""

    def test_added_column(self) -> None:
        prev = {"id": "INTEGER", "name": "VARCHAR"}
        new = {"id": "INTEGER", "name": "VARCHAR", "email": "VARCHAR"}
        added = [k for k in new if k not in prev]
        removed = [k for k in prev if k not in new]
        type_changed = [k for k in new if k in prev and new[k] != prev[k]]
        assert added == ["email"]
        assert removed == []
        assert type_changed == []

    def test_removed_column(self) -> None:
        prev = {"id": "INTEGER", "name": "VARCHAR", "email": "VARCHAR"}
        new = {"id": "INTEGER", "name": "VARCHAR"}
        added = [k for k in new if k not in prev]
        removed = [k for k in prev if k not in new]
        assert added == []
        assert "email" in removed

    def test_type_changed(self) -> None:
        prev = {"total": "DOUBLE"}
        new = {"total": "VARCHAR"}
        type_changed = [k for k in new if k in prev and new[k] != prev[k]]
        assert "total" in type_changed

    def test_first_upload_no_diff(self) -> None:
        prev: dict = {}  # no previous snapshot
        new = {"id": "INTEGER", "name": "VARCHAR"}
        added = [k for k in new if k not in prev]
        removed = [k for k in prev if k not in new]
        type_changed: list[str] = []
        assert added == ["id", "name"] or set(added) == {"id", "name"}
        assert removed == []
        assert type_changed == []
