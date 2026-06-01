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

"""Unit tests for the semantic publish-time SQL firewall."""

from __future__ import annotations

import pytest

from flyquery.core.services.semantic.compiler import SemanticCompiler
from flyquery.core.services.semantic.errors import SemanticCompileError
from flyquery.core.services.semantic.firewall import ALLOWED_FUNCS, assert_safe_template
from flyquery.core.services.semantic.yaml_schema import validate_metric_yaml


def test_clean_simple_passes() -> None:
    assert_safe_template("SELECT region, SUM(amount) AS m FROM orders WHERE s = 'x' GROUP BY region")


def test_allowed_funcs_constant_has_core_aggregates() -> None:
    assert {"SUM", "COUNT", "AVG", "MIN", "MAX", "COALESCE", "NULLIF", "DATE_TRUNC"} <= ALLOWED_FUNCS


@pytest.mark.parametrize(
    "yaml_str",
    [
        "metric:\n  name: a\n  type: simple\n  type_params:\n    measure: {name: x, agg: sum, expr: orders.amt}\n    filter: \"orders.s = 'OK'\"\n  group_by: [orders.region]\n",
        "metric:\n  name: b\n  type: ratio\n  type_params:\n    numerator: {name: w, agg: count, expr: deals.id}\n    denominator: {name: t, agg: count, expr: deals.id}\n",
        "metric:\n  name: c\n  type: cumulative\n  type_params:\n    measure: {name: a, agg: sum, expr: orders.amt}\n    window: 30\n    grain: day\n    time_column: orders.dt\n",
        "metric:\n  name: d\n  type: simple\n  type_params:\n    measure: {name: id, agg: count_distinct, expr: orders.id}\n",
    ],
)
def test_compiled_templates_pass_firewall(yaml_str: str) -> None:
    template = SemanticCompiler.compile(validate_metric_yaml(yaml_str))
    assert_safe_template(template)


def test_multi_statement_rejected() -> None:
    with pytest.raises(SemanticCompileError):
        assert_safe_template("SELECT 1 AS m FROM t; DROP TABLE t")


def test_ddl_rejected() -> None:
    with pytest.raises(SemanticCompileError):
        assert_safe_template("DROP TABLE t")


def test_subquery_rejected() -> None:
    with pytest.raises(SemanticCompileError):
        assert_safe_template("SELECT SUM(x) AS m FROM t WHERE id IN (SELECT id FROM secret_pii)")


def test_disallowed_function_rejected() -> None:
    with pytest.raises(SemanticCompileError):
        assert_safe_template("SELECT read_csv_auto('/etc/passwd') AS m FROM t")


def test_injection_filter_rejected_via_template() -> None:
    # A filter carrying a statement separator must not survive the firewall.
    with pytest.raises(SemanticCompileError):
        assert_safe_template("SELECT SUM(amount) AS m FROM orders WHERE 1=1; DROP TABLE orders")
