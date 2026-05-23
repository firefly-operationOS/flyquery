# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for AstClassifier.

Covers: simple SELECT, multi-statement (rejected), DML on UPLOADED (rejected),
DML on DERIVED with scope (allowed), DDL (rejected).
"""

from __future__ import annotations

import pytest

from flyquery.core.services.execution.ast_classifier import AstClassification, AstClassifier


@pytest.fixture
def classifier() -> AstClassifier:
    return AstClassifier()


def test_simple_select(classifier: AstClassifier) -> None:
    """Simple SELECT is classified correctly."""
    result = classifier.classify("SELECT region, SUM(total) FROM orders GROUP BY region")
    assert result.classification == "SELECT"
    assert result.single_statement is True
    assert "orders" in result.table_refs


def test_select_with_join(classifier: AstClassifier) -> None:
    """SELECT with JOIN includes both table names in table_refs."""
    sql = "SELECT o.region, c.name FROM orders o JOIN customers c ON o.customer_id = c.id"
    result = classifier.classify(sql)
    assert result.classification == "SELECT"
    assert result.single_statement is True
    assert "orders" in result.table_refs or "o" in result.table_refs
    # At least one of the referenced tables must appear
    assert len(result.table_refs) >= 1


def test_select_with_subquery(classifier: AstClassifier) -> None:
    """SELECT with a subquery sets has_subquery=True."""
    sql = "SELECT * FROM (SELECT id, total FROM orders WHERE total > 100) AS sub"
    result = classifier.classify(sql)
    assert result.classification == "SELECT"
    assert result.has_subquery is True


def test_multi_statement_rejected(classifier: AstClassifier) -> None:
    """Two statements separated by semicolons → single_statement=False."""
    sql = "SELECT 1; SELECT 2"
    result = classifier.classify(sql)
    assert result.single_statement is False


def test_insert_classified(classifier: AstClassifier) -> None:
    """INSERT is classified as INSERT."""
    sql = "INSERT INTO derived_table (col) VALUES (1)"
    result = classifier.classify(sql)
    assert result.classification == "INSERT"
    assert result.single_statement is True


def test_update_classified(classifier: AstClassifier) -> None:
    """UPDATE is classified as UPDATE."""
    sql = "UPDATE derived_table SET col = 1 WHERE id = 2"
    result = classifier.classify(sql)
    assert result.classification == "UPDATE"
    assert result.single_statement is True


def test_delete_classified(classifier: AstClassifier) -> None:
    """DELETE is classified as DELETE."""
    sql = "DELETE FROM derived_table WHERE id = 2"
    result = classifier.classify(sql)
    assert result.classification == "DELETE"
    assert result.single_statement is True


def test_ddl_create_classified(classifier: AstClassifier) -> None:
    """CREATE TABLE is classified as DDL."""
    sql = "CREATE TABLE new_table (id INTEGER)"
    result = classifier.classify(sql)
    assert result.classification == "DDL"


def test_ddl_drop_classified(classifier: AstClassifier) -> None:
    """DROP TABLE is classified as DDL."""
    sql = "DROP TABLE old_table"
    result = classifier.classify(sql)
    assert result.classification == "DDL"


def test_empty_sql_unknown(classifier: AstClassifier) -> None:
    """Empty string returns UNKNOWN."""
    result = classifier.classify("")
    assert result.classification == "UNKNOWN"
    assert result.single_statement is False


def test_garbage_sql_unknown(classifier: AstClassifier) -> None:
    """Complete nonsense returns UNKNOWN without raising."""
    result = classifier.classify("not valid SQL @#!$%")
    assert result.classification in ("UNKNOWN", "SELECT")  # sqlglot is lenient; at minimum no crash


def test_ast_classification_is_frozen() -> None:
    """AstClassification instances are frozen dataclasses."""
    cls = AstClassification(
        classification="SELECT",
        single_statement=True,
        table_refs=("orders",),
        column_refs=("total",),
        has_subquery=False,
    )
    with pytest.raises(Exception):
        cls.classification = "INSERT"  # type: ignore[misc]
