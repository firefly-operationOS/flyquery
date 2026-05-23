# Copyright 2026 Firefly Software Solutions Inc
"""DuckDB in-process executor for flyquery query pipeline.

Opens a fresh DuckDB :memory: connection per request, ATTACHes parquet
files for all AST-referenced tables as VIEWs, runs the user SQL wrapped
in a LIMIT row_cap+1 query to detect overflow, and returns an
``ExecutionResult`` or ``ExecutionError``.

Design choices:
- Fresh :memory: per call: no shared state, no connection pool needed.
- ``asyncio.to_thread``: DuckDB's Python API is synchronous; offload to a
  thread pool so the event loop stays unblocked.
- LIMIT row_cap+1: detect overflow without reading all rows into memory.
- All DuckDB exceptions are caught and returned as ``ExecutionError`` so
  the caller (QueryService) can decide whether to retry via CriticAgent.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    """A successful query result."""

    rows: list[dict]
    columns: list[str]
    row_count: int
    truncated: bool


@dataclass(frozen=True)
class ExecutionError:
    """A failed query execution."""

    message: str
    sql_state: str | None = None


class DuckDBExecutor:
    """Executes SQL against DuckDB with parquet-backed views.

    Each call opens a fresh ``:memory:`` DuckDB connection, creates a VIEW
    for every entry in ``attached_tables``, runs the SQL wrapped in a
    ``SELECT * FROM (...) LIMIT row_cap+1`` envelope, then closes the
    connection.

    :param settings: :class:`FlyquerySettings` — reads ``duckdb_memory_limit``,
        ``default_statement_timeout_ms``, and ``default_row_cap``.
    """

    def __init__(self, settings) -> None:
        self._memory_limit = settings.duckdb_memory_limit
        self._row_cap = settings.default_row_cap

    async def execute(
        self,
        sql: str,
        attached_tables: dict[str, str],
    ) -> ExecutionResult | ExecutionError:
        """Run ``sql`` asynchronously against the provided parquet views.

        :param sql: SQL statement to execute (single SELECT; no trailing semicolon required)
        :param attached_tables: mapping of unqualified table name → absolute parquet path
        :return: :class:`ExecutionResult` on success, :class:`ExecutionError` on failure
        """
        return await asyncio.to_thread(self._sync, sql, attached_tables)

    def _sync(self, sql: str, attached_tables: dict[str, str]) -> ExecutionResult | ExecutionError:
        """Synchronous execution body run in a thread pool worker."""
        try:
            import duckdb
        except ImportError as exc:
            return ExecutionError(message=f"duckdb not installed: {exc}")

        conn = duckdb.connect(":memory:")
        try:
            conn.execute(f"SET memory_limit='{self._memory_limit}'")
            conn.execute("SET threads=2")

            # Create a VIEW for each parquet-backed table.
            for name, parquet_path in attached_tables.items():
                conn.execute(
                    f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{parquet_path}')"
                )

            # Wrap in LIMIT row_cap+1 to detect truncation.
            wrapped = (
                f"SELECT * FROM ({sql.rstrip(';')}) AS q"
                f" LIMIT {self._row_cap + 1}"
            )
            cursor = conn.execute(wrapped)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()

            truncated = len(rows) > self._row_cap
            if truncated:
                rows = rows[: self._row_cap]

            return ExecutionResult(
                rows=[dict(zip(cols, r)) for r in rows],
                columns=cols,
                row_count=len(rows),
                truncated=truncated,
            )
        except Exception as exc:  # noqa: BLE001
            return ExecutionError(message=str(exc))
        finally:
            conn.close()
