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

"""Publish-time SQL firewall for compiled semantic templates.

Compiled metric/dimension SQL is built from author-supplied YAML fragments
(filters, expressions, group-by columns). Before a template is persisted as
``compiled_sql_template`` it must pass this firewall, which enforces the
guarantees documented in ``docs/semantic-layer.md`` section 7:

1. The template parses (DuckDB dialect) to exactly one statement.
2. That statement is a single ``SELECT`` (no DDL / commands / multi-statement).
3. No subqueries.
4. Every *arbitrary* (anonymous) function call is on an allowlist -- this is
   what blocks DuckDB file-reading / exfiltration functions such as
   ``read_csv_auto`` / ``read_parquet`` / ``pg_read_file``.

Standard SQL builtins (SUM, CAST, COALESCE, DATE_TRUNC, ...) parse to typed
sqlglot nodes and are inherently safe; only un-typed ``Anonymous`` calls are
treated as a threat surface and checked against the allowlist.
"""

from __future__ import annotations

import sqlglot
from sqlglot import exp

from flyquery.core.services.semantic.compiler import EXTRA_FILTER_SLOT, GROUP_BY_SLOT
from flyquery.core.services.semantic.errors import SemanticCompileError

#: Allowlisted function names (uppercase). Typed builtins are always allowed;
#: this set additionally permits these names when they appear as anonymous calls.
ALLOWED_FUNCS: frozenset[str] = frozenset(
    {
        "SUM",
        "COUNT",
        "AVG",
        "MIN",
        "MAX",
        "COALESCE",
        "NULLIF",
        "CAST",
        "DATE_TRUNC",
        "DATETRUNC",
        "EXTRACT",
        "LOWER",
        "UPPER",
        "ABS",
        "ROUND",
        "FLOOR",
        "CEIL",
        "CEILING",
        "GREATEST",
        "LEAST",
        "LENGTH",
        "TRIM",
    }
)

_FORBIDDEN_NODES = (
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Command,
)


def _strip_slots(template: str) -> str:
    return template.replace(EXTRA_FILTER_SLOT, "").replace(GROUP_BY_SLOT, "")


def assert_safe_template(template: str) -> None:
    """Validate a compiled SQL template; raise :class:`SemanticCompileError` if unsafe."""
    sql = _strip_slots(template)
    try:
        statements = [s for s in sqlglot.parse(sql, read="duckdb") if s is not None]
    except Exception as exc:  # noqa: BLE001 - any parse failure is a compile error
        raise SemanticCompileError(f"compiled SQL is unparseable: {exc}") from exc

    if len(statements) != 1:
        raise SemanticCompileError("compiled SQL must be a single statement")

    root = statements[0]
    if not isinstance(root, exp.Select):
        raise SemanticCompileError("compiled SQL must be a single SELECT statement")

    if len(list(root.find_all(exp.Select))) > 1:
        raise SemanticCompileError("subqueries are not allowed in compiled SQL")

    for node in root.walk():
        if isinstance(node, _FORBIDDEN_NODES):
            raise SemanticCompileError("DDL and commands are not allowed in compiled SQL")
        if isinstance(node, exp.Anonymous):
            name = (node.name or "").upper()
            if name not in ALLOWED_FUNCS:
                raise SemanticCompileError(f"function not allowed: {name}", field="filter")
