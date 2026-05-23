# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for the MetricFlow YAML schema validator."""

from __future__ import annotations

import pytest

from flyquery.core.services.semantic.yaml_schema import MetricYaml, MetricYamlError, validate_metric_yaml

VALID_YAML = """
name: revenue_by_region
label: "Revenue by Region"
description: "Total order revenue grouped by customer region"
metric_type: SIMPLE
agg: sum
expr: orders.total
filters: []
joins:
  - from: orders.customer_id
    to: customers.customer_id
group_by:
  - customers.region
"""

MINIMAL_VALID_YAML = """
name: order_count
agg: count
expr: orders.id
"""


def test_valid_full_yaml_parses() -> None:
    m = validate_metric_yaml(VALID_YAML)
    assert isinstance(m, MetricYaml)
    assert m.name == "revenue_by_region"
    assert m.agg == "sum"
    assert m.metric_type == "SIMPLE"
    assert len(m.joins) == 1
    assert m.joins[0].from_ == "orders.customer_id"
    assert m.joins[0].to == "customers.customer_id"
    assert m.group_by == ["customers.region"]


def test_minimal_valid_yaml_parses() -> None:
    m = validate_metric_yaml(MINIMAL_VALID_YAML)
    assert m.name == "order_count"
    assert m.agg == "count"
    assert m.joins == []
    assert m.group_by == []
    assert m.filters == []


def test_missing_required_name_raises() -> None:
    yaml_str = "agg: sum\nexpr: orders.total\n"
    with pytest.raises(MetricYamlError) as exc_info:
        validate_metric_yaml(yaml_str)
    assert exc_info.value.field == "name"


def test_missing_required_agg_raises() -> None:
    yaml_str = "name: x\nexpr: orders.total\n"
    with pytest.raises(MetricYamlError) as exc_info:
        validate_metric_yaml(yaml_str)
    assert exc_info.value.field == "agg"


def test_invalid_agg_value_raises() -> None:
    yaml_str = "name: x\nagg: median\nexpr: orders.total\n"
    with pytest.raises(MetricYamlError):
        validate_metric_yaml(yaml_str)


def test_invalid_metric_type_raises() -> None:
    yaml_str = "name: x\nagg: sum\nexpr: orders.total\nmetric_type: INVALID\n"
    with pytest.raises(MetricYamlError):
        validate_metric_yaml(yaml_str)


def test_malformed_yaml_raises() -> None:
    with pytest.raises(MetricYamlError):
        validate_metric_yaml("name: [\nbroken yaml")


def test_non_mapping_root_raises() -> None:
    with pytest.raises(MetricYamlError):
        validate_metric_yaml("- item1\n- item2\n")


def test_all_valid_agg_types_accepted() -> None:
    for agg in ("sum", "count", "avg", "min", "max"):
        m = validate_metric_yaml(f"name: x\nagg: {agg}\nexpr: t.col\n")
        assert m.agg == agg


def test_all_valid_metric_types_accepted() -> None:
    for mt in ("SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"):
        m = validate_metric_yaml(f"name: x\nagg: sum\nexpr: t.col\nmetric_type: {mt}\n")
        assert m.metric_type == mt
