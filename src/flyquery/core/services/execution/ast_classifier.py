# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        # sqlglot.parse() is typed to yield its internal ``Expr`` alias, which
        # pyright does not unify with the public ``Expression`` base below.
        kind = self._kind(stmt)  # pyright: ignore[reportArgumentType]

        # Collect table refs — skip anonymous subquery aliases AND
        # CTE-defined names. sqlglot represents a reference to a CTE
        # (``FROM base`` where ``WITH base AS (...)``) as an ``exp.Table``
        # node, so without this filter the CTE alias leaks into
        # ``table_refs``; the downstream bad-tables guard then flags it
        # as a non-existent table and the (otherwise valid) query is
        # rejected — see QueryService bad-tables set-difference.
        cte_names = {cte.alias_or_name for cte in stmt.find_all(sqlglot.expressions.CTE) if cte.alias_or_name}
        tables = tuple(
            sorted(
                {
                    t.name
                    for t in stmt.find_all(sqlglot.expressions.Table)
                    if t.name and t.name not in cte_names
                }
            )
        )
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
        # ``Expression`` is the public base class but sqlglot omits it from
        # ``expressions.__all__``, so pyright flags it as a private import.
        stmt: sqlglot.expressions.Expression,  # pyright: ignore[reportPrivateImportUsage]
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
