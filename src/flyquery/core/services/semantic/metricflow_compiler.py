# Copyright 2026 Firefly Software Solutions Inc
"""MetricFlowCompiler: deterministic YAML dict → DuckDB SQL template.

Input is the parsed YAML dict (already validated by ``yaml_schema.py``).
Output is a single DuckDB-compatible SELECT statement.

No external dependencies — pure Python string manipulation.
"""

from __future__ import annotations


def _table_of(qualified: str) -> str:
    """Extract the table name from a qualified ``table.column`` reference."""
    return qualified.split(".")[0]


class MetricFlowCompiler:
    """Compiles a validated MetricFlow YAML dict to a DuckDB SQL string.

    The compiler handles:
    - Single-table aggregation (``agg``, ``expr``)
    - Explicit joins (``joins``)
    - Column projections in SELECT (``group_by``)
    - WHERE filters (``filters``)
    - GROUP BY clause (``group_by``)

    The compiled SQL is intended to be parameterised by the caller when
    table names are resolved at query time.
    """

    @staticmethod
    def compile(metric_yaml: dict) -> str:  # noqa: A003
        """Compile a metric YAML dict to a DuckDB SELECT statement.

        :param metric_yaml: validated metric definition (must contain at
            least ``name``, ``agg``, and ``expr``)
        :return: DuckDB-compatible SELECT statement
        """
        name = metric_yaml["name"]
        agg = metric_yaml["agg"].upper()
        expr = metric_yaml["expr"]
        group_by_cols: list[str] = list(metric_yaml.get("group_by", []))
        joins: list[dict] = list(metric_yaml.get("joins", []))
        filters: list[str] = list(metric_yaml.get("filters", []))

        # SELECT clause: group_by columns first, then the aggregation
        agg_alias = f"{agg}({expr}) AS {name}"
        select_parts = group_by_cols + [agg_alias] if group_by_cols else [agg_alias]
        select_clause = ", ".join(select_parts)

        # Base table: derived from the first component of the expr
        base_table = _table_of(expr)

        # JOIN clauses
        join_clauses = []
        for j in joins:
            from_col = j.get("from") or j.get("from_")
            to_col = j["to"]
            to_table = _table_of(to_col)
            join_clauses.append(f"JOIN {to_table} ON {from_col} = {to_col}")
        join_sql = " ".join(join_clauses)

        # WHERE clause
        where_sql = " AND ".join(filters)

        # GROUP BY clause
        group_by_sql = ", ".join(group_by_cols)

        # Assemble
        sql = f"SELECT {select_clause} FROM {base_table}"
        if join_sql:
            sql += f" {join_sql}"
        if where_sql:
            sql += f" WHERE {where_sql}"
        if group_by_sql:
            sql += f" GROUP BY {group_by_sql}"

        return sql
