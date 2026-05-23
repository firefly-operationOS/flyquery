# Copyright 2026 Firefly Software Solutions Inc
"""AST classifier using sqlglot to classify SQL statements.

Parses SQL with the DuckDB dialect (``read="duckdb"``) and returns an
``AstClassification`` describing the statement type, table/column references,
and structural properties.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import sqlglot
import sqlglot.expressions  # noqa: F401 — ensures exp alias is populated on sqlglot module


@dataclass(frozen=True)
class AstClassification:
    """The result of classifying a SQL string via the AST."""

    classification: Literal["SELECT", "INSERT", "UPDATE", "DELETE", "DDL", "UNKNOWN"]
    single_statement: bool
    table_refs: tuple[str, ...]  # unqualified table names referenced in the statement
    column_refs: tuple[str, ...]  # column names referenced in the statement
    has_subquery: bool


class AstClassifier:
    """Classifies a SQL string using sqlglot with the DuckDB dialect."""

    def classify(self, sql: str) -> AstClassification:
        """Parse and classify ``sql``.

        :param sql: raw SQL string
        :return: :class:`AstClassification`; classification="UNKNOWN" on parse error
        """
        try:
            statements = sqlglot.parse(sql, read="duckdb")
        except Exception:  # noqa: BLE001
            return AstClassification(
                classification="UNKNOWN",
                single_statement=False,
                table_refs=(),
                column_refs=(),
                has_subquery=False,
            )

        # sqlglot.parse("") returns [None] for an empty/whitespace-only input
        non_null = [s for s in statements if s is not None]
        if not non_null:
            return AstClassification(
                classification="UNKNOWN",
                single_statement=False,
                table_refs=(),
                column_refs=(),
                has_subquery=False,
            )

        single = len(non_null) == 1
        stmt = non_null[0]
        kind = self._kind(stmt)

        # Collect table refs — skip anonymous subquery aliases
        tables = tuple(sorted({t.name for t in stmt.find_all(sqlglot.expressions.Table) if t.name}))
        columns = tuple(sorted({c.name for c in stmt.find_all(sqlglot.expressions.Column) if c.name}))
        has_subquery = bool(list(stmt.find_all(sqlglot.expressions.Subquery)))

        return AstClassification(
            classification=kind,
            single_statement=single,
            table_refs=tables,
            column_refs=columns,
            has_subquery=has_subquery,
        )

    @staticmethod
    def _kind(
        stmt: sqlglot.expressions.Expression,
    ) -> Literal["SELECT", "INSERT", "UPDATE", "DELETE", "DDL", "UNKNOWN"]:
        if isinstance(stmt, sqlglot.expressions.Select):
            return "SELECT"
        # ``UNION ALL`` / ``UNION`` / ``INTERSECT`` / ``EXCEPT`` are
        # also read-only set operations -- classify them as SELECT so
        # the scope guard treats them like a read and the queries
        # CHECK constraint (which only allows SELECT/INSERT/UPDATE/
        # DELETE/DDL) doesn't reject them with UNKNOWN.
        if isinstance(
            stmt,
            (sqlglot.expressions.Union, sqlglot.expressions.Intersect, sqlglot.expressions.Except),
        ):
            return "SELECT"
        if isinstance(stmt, sqlglot.expressions.Insert):
            return "INSERT"
        if isinstance(stmt, sqlglot.expressions.Update):
            return "UPDATE"
        if isinstance(stmt, sqlglot.expressions.Delete):
            return "DELETE"
        if isinstance(
            stmt, (sqlglot.expressions.Create, sqlglot.expressions.Drop, sqlglot.expressions.Alter)
        ):
            return "DDL"
        return "UNKNOWN"
