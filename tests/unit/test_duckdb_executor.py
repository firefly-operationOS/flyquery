# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for DuckDBExecutor and TableResolver.

DuckDB executor tests run synchronously (no async I/O needed for the
in-process DuckDB path). The async wrapper is tested via asyncio.
"""

from __future__ import annotations

import os
import tempfile

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from flyquery.core.services.execution.duckdb_executor import (
    DuckDBExecutor,
    ExecutionError,
    ExecutionResult,
)


class _Settings:
    duckdb_memory_limit = "256MB"
    default_row_cap = 100
    default_statement_timeout_ms = 5000


# ---------------------------------------------------------------------------
# Basic SELECT over an in-memory parquet
# ---------------------------------------------------------------------------


def _write_parquet(path: str, rows: list[dict]) -> None:
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)


@pytest.mark.asyncio
async def test_executor_basic_select():
    """Execute a simple SELECT against a single parquet-backed view."""
    executor = DuckDBExecutor(_Settings())

    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "orders.parquet")
        _write_parquet(
            parquet_path,
            [
                {"id": 1, "region": "North", "total": 100},
                {"id": 2, "region": "South", "total": 200},
                {"id": 3, "region": "North", "total": 300},
            ],
        )

        result = await executor.execute(
            "SELECT region, SUM(total) AS revenue FROM orders GROUP BY region ORDER BY region",
            {"orders": parquet_path},
        )

    assert isinstance(result, ExecutionResult)
    assert result.row_count == 2
    assert result.columns == ["region", "revenue"]
    rows_by_region = {r["region"]: r["revenue"] for r in result.rows}
    assert rows_by_region["North"] == 400
    assert rows_by_region["South"] == 200
    assert not result.truncated


@pytest.mark.asyncio
async def test_executor_row_cap_truncation():
    """When result exceeds row_cap, rows are truncated and truncated=True."""

    class TinyCapSettings:
        duckdb_memory_limit = "256MB"
        default_row_cap = 3
        default_statement_timeout_ms = 5000

    executor = DuckDBExecutor(TinyCapSettings())

    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "items.parquet")
        _write_parquet(
            parquet_path,
            [{"id": i, "v": i * 10} for i in range(10)],
        )

        result = await executor.execute(
            "SELECT * FROM items ORDER BY id",
            {"items": parquet_path},
        )

    assert isinstance(result, ExecutionResult)
    assert result.row_count == 3
    assert result.truncated is True


@pytest.mark.asyncio
async def test_executor_bad_sql_returns_error():
    """A SQL syntax error returns ExecutionError, not an exception."""
    executor = DuckDBExecutor(_Settings())

    result = await executor.execute(
        "SELECT * FROM nonexistent_table_xyz WHERE",
        {},
    )

    assert isinstance(result, ExecutionError)
    assert result.message


@pytest.mark.asyncio
async def test_executor_missing_table_returns_error():
    """Referencing a table not in attached_tables returns ExecutionError."""
    executor = DuckDBExecutor(_Settings())

    result = await executor.execute(
        "SELECT * FROM ghost_table",
        {},
    )

    assert isinstance(result, ExecutionError)


@pytest.mark.asyncio
async def test_executor_multi_table_join():
    """JOIN across two parquet-backed views produces correct results."""
    executor = DuckDBExecutor(_Settings())

    with tempfile.TemporaryDirectory() as tmpdir:
        orders_path = os.path.join(tmpdir, "orders.parquet")
        customers_path = os.path.join(tmpdir, "customers.parquet")

        _write_parquet(
            orders_path,
            [
                {"order_id": 1, "customer_id": 10, "amount": 50},
                {"order_id": 2, "customer_id": 20, "amount": 75},
            ],
        )
        _write_parquet(
            customers_path,
            [
                {"customer_id": 10, "name": "Alice"},
                {"customer_id": 20, "name": "Bob"},
            ],
        )

        result = await executor.execute(
            "SELECT c.name, o.amount FROM orders o JOIN customers c ON o.customer_id = c.customer_id ORDER BY c.name",
            {"orders": orders_path, "customers": customers_path},
        )

    assert isinstance(result, ExecutionResult)
    assert result.row_count == 2
    names = [r["name"] for r in result.rows]
    assert names == ["Alice", "Bob"]


@pytest.mark.asyncio
async def test_executor_empty_result():
    """An empty result set returns ExecutionResult with row_count=0."""
    executor = DuckDBExecutor(_Settings())

    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "empty.parquet")
        _write_parquet(parquet_path, [{"id": 1, "val": "x"}])

        result = await executor.execute(
            "SELECT * FROM empty WHERE 1=0",
            {"empty": parquet_path},
        )

    assert isinstance(result, ExecutionResult)
    assert result.row_count == 0
    assert result.rows == []
    assert not result.truncated
