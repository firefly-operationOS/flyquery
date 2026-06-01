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

"""Unit tests for semantic-layer domain errors."""

from __future__ import annotations

from flyquery.core.services.semantic.errors import MetricYamlError, SemanticCompileError


def test_semantic_compile_error_carries_field_and_code() -> None:
    e = SemanticCompileError("bad agg", field="agg")
    assert e.field == "agg"
    assert e.code == "semantic_compile_error"
    assert isinstance(e, ValueError)


def test_metric_yaml_error_is_semantic_compile_error() -> None:
    assert issubclass(MetricYamlError, SemanticCompileError)
    e = MetricYamlError("missing name", field="name")
    assert e.code == "semantic_compile_error"
    assert e.field == "name"
