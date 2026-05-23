# Copyright 2026 Firefly Software Solutions Inc
"""MetricFlow YAML schema validator.

Validates a subset of the MetricFlow YAML format used by flyquery's
semantic layer. Raises ``MetricYamlError`` with field and line context
on validation failure.
"""

from __future__ import annotations

from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError


class JoinSpec(BaseModel):
    """A single join specification: from_col → to_col."""

    from_: str = Field(alias="from")
    to: str

    model_config = {"populate_by_name": True}


class MetricYaml(BaseModel):
    """Validated shape of a flyquery semantic-layer metric YAML."""

    name: str = Field(min_length=1, max_length=256)
    label: str | None = None
    description: str | None = None
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"] = "SIMPLE"
    agg: Literal["sum", "count", "avg", "min", "max"]
    expr: str = Field(min_length=1)
    joins: list[JoinSpec] = Field(default_factory=list)
    group_by: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)


class MetricYamlError(ValueError):
    """Raised when metric YAML validation fails.

    Attributes:
        field: name of the failing field (or None for top-level parse errors)
        detail: human-readable description of what went wrong
    """

    def __init__(self, detail: str, *, field: str | None = None) -> None:
        self.field = field
        self.detail = detail
        super().__init__(f"MetricYamlError({field!r}): {detail}")


def validate_metric_yaml(yaml_str: str) -> MetricYaml:
    """Parse and validate a metric YAML string.

    :param yaml_str: raw YAML content as a string
    :return: a validated ``MetricYaml`` instance
    :raises MetricYamlError: on parse error or schema violation
    """
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as exc:
        raise MetricYamlError(str(exc)) from exc

    if not isinstance(data, dict):
        raise MetricYamlError("YAML root must be a mapping")

    try:
        return MetricYaml.model_validate(data)
    except ValidationError as exc:
        errors = exc.errors()
        first = errors[0]
        field = ".".join(str(p) for p in first["loc"]) if first["loc"] else None
        raise MetricYamlError(first["msg"], field=field) from exc
