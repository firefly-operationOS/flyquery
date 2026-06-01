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

"""Unit tests for SemanticCompiler (compile + bind)."""

from __future__ import annotations

from flyquery.core.services.semantic.compiler import MetricFlowCompiler, SemanticCompiler
from flyquery.core.services.semantic.yaml_schema import validate_metric_yaml


def _compile(yaml_str: str, **kwargs: object) -> str:
    return SemanticCompiler.compile(validate_metric_yaml(yaml_str), **kwargs)


def test_back_compat_alias() -> None:
    assert MetricFlowCompiler is SemanticCompiler


def test_simple_sum_with_slots() -> None:
    sql = _compile(
        "metric:\n  name: total_revenue\n  type: simple\n  type_params:\n"
        "    measure: {name: amt, agg: sum, expr: orders.amount}\n"
        "    filter: \"orders.status = 'OK'\"\n  group_by: [orders.region]\n"
    )
    assert "SUM(orders.amount) AS total_revenue" in sql
    assert "FROM orders" in sql
    assert "WHERE orders.status = 'OK'" in sql
    assert "{extra_filter_clause}" in sql
    assert "{group_by_append}" in sql
    assert "GROUP BY orders.region" in sql


def test_simple_no_group_by_still_has_slot() -> None:
    sql = _compile(
        "metric:\n  name: c\n  type: simple\n  type_params:\n"
        "    measure: {name: id, agg: count, expr: orders.id}\n"
    )
    assert "COUNT(orders.id) AS c" in sql
    assert "{group_by_append}" in sql
    assert "GROUP BY" not in sql


def test_count_distinct() -> None:
    sql = _compile(
        "metric:\n  name: c\n  type: simple\n  type_params:\n"
        "    measure: {name: id, agg: count_distinct, expr: orders.id}\n"
    )
    assert "COUNT(DISTINCT orders.id) AS c" in sql


def test_ratio() -> None:
    sql = _compile(
        "metric:\n  name: win_rate\n  type: ratio\n  type_params:\n"
        "    numerator: {name: w, agg: count, expr: deals.id}\n"
        "    denominator: {name: t, agg: count, expr: deals.id}\n"
    )
    assert "NULLIF(" in sql
    assert "AS win_rate" in sql
    assert "FROM deals" in sql


def test_cumulative() -> None:
    sql = _compile(
        "metric:\n  name: mtd\n  type: cumulative\n  type_params:\n"
        "    measure: {name: a, agg: sum, expr: orders.amt}\n"
        "    window: 30\n    grain: day\n    time_column: orders.dt\n"
    )
    assert "DATE_TRUNC('day', orders.dt)" in sql
    assert "ORDER BY bucket" in sql


def test_derived() -> None:
    sql = _compile(
        "metric:\n  name: gm\n  type: derived\n  type_params:\n"
        '    expr: "(rev - cogs) / rev"\n    metrics: [{name: rev}, {name: cogs}]\n'
    )
    assert "((rev - cogs) / rev) AS gm" in sql


def test_resolve_table_for_bare_column() -> None:
    sql = _compile(
        "metric:\n  name: oc\n  type: simple\n  type_params:\n"
        "    measure: {name: id, agg: count, expr: order_id}\n",
        resolve_table=lambda col, ds=None: "orders",
    )
    assert "FROM orders" in sql
    assert "FROM order_id" not in sql


def test_resolve_dimension_in_group_by() -> None:
    sql = _compile(
        "metric:\n  name: r\n  type: simple\n  type_params:\n"
        "    measure: {name: amt, agg: sum, expr: orders.amt}\n  group_by: [order_day]\n",
        resolve_dimension=lambda name, ds=None: "DATE_TRUNC('day', orders.dt)",
    )
    assert "DATE_TRUNC('day', orders.dt)" in sql


def test_bind_substitutes_slots() -> None:
    tmpl = "SELECT x AS m FROM t WHERE 1=1 {extra_filter_clause} GROUP BY x {group_by_append}"
    out = SemanticCompiler.bind(tmpl, extra_filter="dt >= '2026-01-01'", group_by_append=["region"])
    assert "AND dt >= '2026-01-01'" in out
    assert ", region" in out
    assert "{extra_filter_clause}" not in out
    assert "{group_by_append}" not in out


def test_bind_empty_slots() -> None:
    tmpl = "SELECT x AS m FROM t WHERE 1=1 {extra_filter_clause} GROUP BY x {group_by_append}"
    out = SemanticCompiler.bind(tmpl)
    assert "{" not in out
    assert out == "SELECT x AS m FROM t WHERE 1=1 GROUP BY x"
