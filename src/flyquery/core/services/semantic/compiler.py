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

"""SemanticCompiler: ``MetricDefinition`` -> DuckDB SQL template (+ runtime bind).

Compilation is deterministic: the same definition always produces the same
template. The template carries two runtime substitution slots that
:meth:`SemanticCompiler.bind` fills at query time:

* ``{extra_filter_clause}`` -- an extra ``AND <predicate>`` appended to WHERE
* ``{group_by_append}``     -- extra ``, <column>`` entries appended to GROUP BY

Table resolution: a measure ``expr`` may be a qualified ``table.column`` (the
table is taken from the prefix) or a bare column, in which case an injected
``resolve_table(column, dataset_id)`` callback resolves the owning table from
the schema knowledge base. ``group_by`` entries that name a published
dimension are resolved via ``resolve_dimension(name, dataset_id)``.
"""

from __future__ import annotations

from collections.abc import Callable

from flyquery.core.services.semantic.yaml_schema import MeasureSpec, MetricDefinition

EXTRA_FILTER_SLOT = "{extra_filter_clause}"
GROUP_BY_SLOT = "{group_by_append}"

ResolveTable = Callable[..., str]
ResolveDimension = Callable[..., str]


def _table_of(expr: str, resolve_table: ResolveTable | None, dataset_id: object) -> str:
    """Resolve the base table for a measure expression."""
    if "." in expr:
        return expr.split(".")[0]
    if resolve_table is not None:
        return resolve_table(expr, dataset_id)
    return expr


def _agg_sql(measure: MeasureSpec) -> str:
    """Render an aggregate expression (``COUNT(DISTINCT ...)`` for count_distinct)."""
    column = measure.expr or measure.name
    if measure.agg == "count_distinct":
        return f"COUNT(DISTINCT {column})"
    return f"{measure.agg.upper()}({column})"


class SemanticCompiler:
    """Compiles a validated :class:`MetricDefinition` to a DuckDB SQL template."""

    @staticmethod
    def compile(  # noqa: A003 - matches the documented public name
        metric: MetricDefinition,
        *,
        resolve_table: ResolveTable | None = None,
        resolve_dimension: ResolveDimension | None = None,
        dataset_id: object = None,
    ) -> str:
        """Compile a metric definition to a DuckDB SELECT template with runtime slots."""
        group_by = [
            (resolve_dimension(col, dataset_id) if (resolve_dimension and "." not in col) else col)
            for col in metric.group_by
        ]

        if metric.type in ("simple", "cumulative"):
            measure = metric.type_params.measure
            table = _table_of(measure.expr or measure.name, resolve_table, dataset_id)
            if metric.type == "cumulative":
                tp = metric.type_params
                bucket = f"DATE_TRUNC('{tp.grain}', {tp.time_column})"
                select = f"{bucket} AS bucket, {_agg_sql(measure)} AS {metric.name}"
                return (
                    f"SELECT {select} FROM {table} WHERE 1=1 {EXTRA_FILTER_SLOT} "
                    f"GROUP BY {bucket} {GROUP_BY_SLOT} ORDER BY bucket"
                )
            select_parts = [*group_by, f"{_agg_sql(measure)} AS {metric.name}"]
            where = metric.type_params.filter
            where_sql = f"{where} {EXTRA_FILTER_SLOT}" if where else f"1=1 {EXTRA_FILTER_SLOT}"
            sql = f"SELECT {', '.join(select_parts)} FROM {table} WHERE {where_sql}"
            sql += f" GROUP BY {', '.join(group_by)} {GROUP_BY_SLOT}" if group_by else f" {GROUP_BY_SLOT}"
            return sql

        if metric.type == "ratio":
            num = metric.type_params.numerator
            den = metric.type_params.denominator
            table = _table_of(num.expr or num.name, resolve_table, dataset_id)
            ratio = f"CAST({_agg_sql(num)} AS DOUBLE) / NULLIF({_agg_sql(den)}, 0)"
            select_parts = [*group_by, f"{ratio} AS {metric.name}"]
            sql = f"SELECT {', '.join(select_parts)} FROM {table} WHERE 1=1 {EXTRA_FILTER_SLOT}"
            sql += f" GROUP BY {', '.join(group_by)} {GROUP_BY_SLOT}" if group_by else f" {GROUP_BY_SLOT}"
            return sql

        # derived: arithmetic over previously-defined metric expressions.
        expr = metric.type_params.expr
        return f"SELECT ({expr}) AS {metric.name} {EXTRA_FILTER_SLOT} {GROUP_BY_SLOT}"

    @staticmethod
    def bind(
        template: str,
        *,
        extra_filter: str | None = None,
        group_by_append: list[str] | None = None,
    ) -> str:
        """Substitute runtime slots and return the final, whitespace-normalised SQL."""
        extra = f"AND {extra_filter}" if extra_filter else ""
        gba = (", " + ", ".join(group_by_append)) if group_by_append else ""
        out = template.replace(EXTRA_FILTER_SLOT, extra).replace(GROUP_BY_SLOT, gba)
        return " ".join(out.split())


# Back-compat alias for existing imports.
MetricFlowCompiler = SemanticCompiler
