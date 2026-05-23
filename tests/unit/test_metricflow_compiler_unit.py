# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for MetricFlowCompiler."""

from __future__ import annotations

from flyquery.core.services.semantic.metricflow_compiler import MetricFlowCompiler


def test_simple_count() -> None:
    sql = MetricFlowCompiler.compile({"name": "order_count", "agg": "count", "expr": "orders.id"})
    assert sql == "SELECT COUNT(orders.id) AS order_count FROM orders"


def test_simple_sum() -> None:
    sql = MetricFlowCompiler.compile({"name": "total_revenue", "agg": "sum", "expr": "orders.total"})
    assert sql == "SELECT SUM(orders.total) AS total_revenue FROM orders"


def test_with_group_by() -> None:
    sql = MetricFlowCompiler.compile(
        {
            "name": "revenue_by_region",
            "agg": "sum",
            "expr": "orders.total",
            "group_by": ["customers.region"],
        }
    )
    assert "customers.region" in sql
    assert "GROUP BY customers.region" in sql
    assert "SUM(orders.total) AS revenue_by_region" in sql


def test_with_join() -> None:
    sql = MetricFlowCompiler.compile(
        {
            "name": "revenue_by_region",
            "agg": "sum",
            "expr": "orders.total",
            "joins": [{"from": "orders.customer_id", "to": "customers.customer_id"}],
            "group_by": ["customers.region"],
        }
    )
    assert "JOIN customers ON orders.customer_id = customers.customer_id" in sql
    assert "FROM orders" in sql


def test_with_filter() -> None:
    sql = MetricFlowCompiler.compile(
        {
            "name": "active_orders",
            "agg": "count",
            "expr": "orders.id",
            "filters": ["orders.status = 'ACTIVE'"],
        }
    )
    assert "WHERE orders.status = 'ACTIVE'" in sql


def test_combined_join_filter_group() -> None:
    sql = MetricFlowCompiler.compile(
        {
            "name": "revenue_by_region",
            "agg": "sum",
            "expr": "orders.total",
            "joins": [{"from": "orders.customer_id", "to": "customers.customer_id"}],
            "filters": ["orders.year = 2026"],
            "group_by": ["customers.region"],
        }
    )
    assert "JOIN customers" in sql
    assert "WHERE orders.year = 2026" in sql
    assert "GROUP BY customers.region" in sql


def test_multiple_group_by_cols() -> None:
    sql = MetricFlowCompiler.compile(
        {
            "name": "revenue",
            "agg": "sum",
            "expr": "orders.total",
            "group_by": ["customers.region", "customers.country"],
        }
    )
    assert "GROUP BY customers.region, customers.country" in sql


def test_sql_is_parseable_by_sqlglot() -> None:
    """Compiled SQL must be parseable by sqlglot."""
    import sqlglot

    sql = MetricFlowCompiler.compile(
        {
            "name": "revenue_by_region",
            "agg": "sum",
            "expr": "orders.total",
            "joins": [{"from": "orders.customer_id", "to": "customers.customer_id"}],
            "group_by": ["customers.region"],
        }
    )
    parsed = sqlglot.parse_one(sql, read="duckdb")
    assert parsed is not None
