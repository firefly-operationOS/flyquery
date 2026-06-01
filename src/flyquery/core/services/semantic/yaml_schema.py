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

"""Nested MetricFlow YAML schema validators.

Validates the MetricFlow-compatible metric and dimension definition
formats documented in ``docs/semantic-layer.md``. Metrics are nested
under a ``metric:`` root; dimensions under a ``dimension:`` root.

Raises :class:`MetricYamlError` (a :class:`SemanticCompileError`) with
field context on validation failure.
"""

from __future__ import annotations

import re
from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from flyquery.core.services.semantic.errors import MetricYamlError

# Re-exported for callers that catch the alias by name.
__all__ = [
    "Agg",
    "DimensionDefinition",
    "MeasureSpec",
    "MetricDefinition",
    "MetricRef",
    "MetricType",
    "MetricTypeParams",
    "MetricYamlError",
    "validate_dimension_yaml",
    "validate_metric_yaml",
]

_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

Agg = Literal["sum", "count", "count_distinct", "avg", "min", "max"]
MetricType = Literal["simple", "ratio", "derived", "cumulative"]
DimensionType = Literal["categorical", "time"]


class MeasureSpec(BaseModel):
    """A single aggregated measure (column + aggregation)."""

    name: str
    agg: Agg
    expr: str | None = None


class MetricRef(BaseModel):
    """A reference to another metric (used by derived metrics)."""

    name: str


class MetricTypeParams(BaseModel):
    """Type-specific parameters; which fields apply depends on metric type."""

    measure: MeasureSpec | None = None
    filter: str | None = None
    numerator: MeasureSpec | None = None
    denominator: MeasureSpec | None = None
    expr: str | None = None
    metrics: list[MetricRef] = Field(default_factory=list)
    window: int | None = None
    grain: str | None = None
    time_column: str | None = None


class MetricDefinition(BaseModel):
    """Validated shape of a flyquery semantic-layer metric (``metric:`` root)."""

    name: str = Field(min_length=1, max_length=256)
    label: str | None = None
    description: str | None = None
    type: MetricType = "simple"
    type_params: MetricTypeParams
    group_by: list[str] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> MetricDefinition:
        if not _NAME_RE.match(self.name):
            raise ValueError("name must be alphanumeric + underscore only")
        tp = self.type_params
        if self.type == "simple" and tp.measure is None:
            raise ValueError("simple metric requires type_params.measure")
        if self.type == "ratio" and (tp.numerator is None or tp.denominator is None):
            raise ValueError("ratio metric requires type_params.numerator and denominator")
        if self.type == "derived" and (not tp.expr or not tp.metrics):
            raise ValueError("derived metric requires type_params.expr and metrics")
        if self.type == "cumulative" and (
            tp.measure is None or tp.window is None or not tp.grain or not tp.time_column
        ):
            raise ValueError(
                "cumulative metric requires type_params.measure, window, grain, time_column"
            )
        return self


class DimensionDefinition(BaseModel):
    """Validated shape of a flyquery semantic-layer dimension (``dimension:`` root)."""

    name: str = Field(min_length=1, max_length=256)
    label: str | None = None
    description: str | None = None
    type: DimensionType
    expr: str = Field(min_length=1)
    grain: str | None = None

    @model_validator(mode="after")
    def _check(self) -> DimensionDefinition:
        if not _NAME_RE.match(self.name):
            raise ValueError("name must be alphanumeric + underscore only")
        if self.type == "time" and not self.grain:
            raise ValueError("time dimension requires a grain")
        return self


def _first_error(exc: ValidationError) -> MetricYamlError:
    err = exc.errors()[0]
    loc = ".".join(str(p) for p in err["loc"]) if err["loc"] else None
    return MetricYamlError(err["msg"], field=loc)


def validate_metric_yaml(yaml_str: str) -> MetricDefinition:
    """Parse and validate a metric YAML string (``metric:`` root).

    :param yaml_str: raw YAML content
    :return: a validated :class:`MetricDefinition`
    :raises MetricYamlError: on parse error or schema violation
    """
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as exc:
        raise MetricYamlError(str(exc)) from exc
    if not isinstance(data, dict) or "metric" not in data:
        raise MetricYamlError("YAML root must contain a 'metric' mapping")
    try:
        return MetricDefinition.model_validate(data["metric"])
    except ValidationError as exc:
        raise _first_error(exc) from exc


def validate_dimension_yaml(yaml_str: str) -> DimensionDefinition:
    """Parse and validate a dimension YAML string (``dimension:`` root).

    :param yaml_str: raw YAML content
    :return: a validated :class:`DimensionDefinition`
    :raises MetricYamlError: on parse error or schema violation
    """
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as exc:
        raise MetricYamlError(str(exc)) from exc
    if not isinstance(data, dict) or "dimension" not in data:
        raise MetricYamlError("YAML root must contain a 'dimension' mapping")
    try:
        return DimensionDefinition.model_validate(data["dimension"])
    except ValidationError as exc:
        raise _first_error(exc) from exc
