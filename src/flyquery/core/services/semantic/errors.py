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

"""Domain errors for the semantic layer.

These live in the core layer and carry no web dependency. The web layer
registers a handler that renders :class:`SemanticCompileError` as an
RFC 7807 ``400`` with ``code=semantic_compile_error``.
"""

from __future__ import annotations


class SemanticCompileError(ValueError):
    """Raised when a metric/dimension definition is invalid or unsafe.

    Attributes:
        field: the failing field path (or None for top-level parse errors)
        detail: human-readable description of what went wrong
        code: stable machine code surfaced over HTTP
    """

    code = "semantic_compile_error"

    def __init__(self, detail: str, *, field: str | None = None) -> None:
        self.field = field
        self.detail = detail
        super().__init__(f"SemanticCompileError({field!r}): {detail}")


class MetricYamlError(SemanticCompileError):
    """Back-compat alias for definition-validation failures.

    Existing call sites raise ``MetricYamlError``; it is a
    :class:`SemanticCompileError` so the same HTTP mapping applies.
    """
