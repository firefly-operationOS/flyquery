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

"""Unit tests for the nested MetricFlow YAML schema validators."""

from __future__ import annotations

import pytest

from flyquery.core.services.semantic.errors import MetricYamlError
from flyquery.core.services.semantic.yaml_schema import (
    MetricDefinition,
    validate_dimension_yaml,
    validate_metric_yaml,
)

SIMPLE = """
metric:
  name: total_revenue
  label: Total Revenue
  type: simple
  type_params:
    measure: {name: order_amount, agg: sum, expr: orders.order_amount}
    filter: "orders.order_status = 'COMPLETED'"
  group_by: [orders.region]
  meta: {owner: finance}
"""

RATIO = """
metric:
  name: win_rate
  type: ratio
  type_params:
    numerator: {name: won, agg: count, expr: deals.id}
    denominator: {name: total, agg: count, expr: deals.id}
"""

DERIVED = """
metric:
  name: gross_margin
  type: derived
  type_params:
    expr: "(total_revenue - cogs) / total_revenue"
    metrics: [{name: total_revenue}, {name: cogs}]
"""

CUMULATIVE = """
metric:
  name: mtd_revenue
  type: cumulative
  type_params:
    measure: {name: order_amount, agg: sum, expr: orders.order_amount}
    window: 30
    grain: day
    time_column: orders.order_date
"""


def test_simple_parses() -> None:
    m = validate_metric_yaml(SIMPLE)
    assert isinstance(m, MetricDefinition)
    assert m.name == "total_revenue"
    assert m.type == "simple"
    assert m.type_params.measure.agg == "sum"
    assert m.group_by == ["orders.region"]
    assert m.meta == {"owner": "finance"}


def test_count_distinct_accepted() -> None:
    y = (
        "metric:\n  name: c\n  type: simple\n  type_params:\n"
        "    measure: {name: id, agg: count_distinct, expr: orders.id}\n"
    )
    assert validate_metric_yaml(y).type_params.measure.agg == "count_distinct"


def test_ratio_requires_numerator_and_denominator() -> None:
    assert validate_metric_yaml(RATIO).type == "ratio"
    bad = (
        "metric:\n  name: r\n  type: ratio\n  type_params:\n"
        "    numerator: {name: a, agg: count, expr: t.id}\n"
    )
    with pytest.raises(MetricYamlError):
        validate_metric_yaml(bad)


def test_derived_and_cumulative_parse() -> None:
    assert validate_metric_yaml(DERIVED).type == "derived"
    assert validate_metric_yaml(CUMULATIVE).type_params.window == 30


def test_bad_name_rejected() -> None:
    bad = (
        "metric:\n  name: 'bad; name'\n  type: simple\n  type_params:\n"
        "    measure: {name: x, agg: sum, expr: t.c}\n"
    )
    with pytest.raises(MetricYamlError):
        validate_metric_yaml(bad)


def test_missing_metric_root_rejected() -> None:
    with pytest.raises(MetricYamlError):
        validate_metric_yaml("name: x\nagg: sum\n")


def test_invalid_agg_rejected() -> None:
    bad = (
        "metric:\n  name: x\n  type: simple\n  type_params:\n"
        "    measure: {name: x, agg: median, expr: t.c}\n"
    )
    with pytest.raises(MetricYamlError):
        validate_metric_yaml(bad)


def test_simple_requires_measure() -> None:
    bad = "metric:\n  name: x\n  type: simple\n  type_params: {}\n"
    with pytest.raises(MetricYamlError):
        validate_metric_yaml(bad)


def test_malformed_yaml_rejected() -> None:
    with pytest.raises(MetricYamlError):
        validate_metric_yaml("metric: [\nbroken yaml")


# --- dimensions ------------------------------------------------------------


def test_categorical_dimension_parses() -> None:
    d = validate_dimension_yaml(
        "dimension:\n  name: order_region\n  type: categorical\n  expr: region\n"
    )
    assert d.name == "order_region"
    assert d.type == "categorical"
    assert d.expr == "region"


def test_time_dimension_requires_grain() -> None:
    ok = validate_dimension_yaml(
        "dimension:\n  name: order_day\n  type: time\n  expr: order_date\n  grain: day\n"
    )
    assert ok.grain == "day"
    with pytest.raises(MetricYamlError):
        validate_dimension_yaml(
            "dimension:\n  name: order_day\n  type: time\n  expr: order_date\n"
        )


def test_missing_dimension_root_rejected() -> None:
    with pytest.raises(MetricYamlError):
        validate_dimension_yaml("name: x\ntype: categorical\nexpr: region\n")
