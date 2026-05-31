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

"""flyquery agent-token scope catalog (spec §7.3).

Lock-step note: canon + radar each maintain their own catalog. The
``agent_token_service`` (lock-step from canon) consumes a callable
``validate_scopes`` per service. This module is the flyquery-specific
binding.
"""

from __future__ import annotations

from typing import Final


class InvalidScopeError(ValueError):
    """Raised when a token mint or check sees an unknown scope."""


ALL_SCOPES: Final[tuple[str, ...]] = (
    "flyquery.datasets:read",
    "flyquery.datasets:write",
    "flyquery.files:upload",
    "flyquery.files:read",
    "flyquery.schema:read",
    "flyquery.schema:annotate",
    "flyquery.relations:read",
    "flyquery.relations:write",
    "flyquery.semantic:read",
    "flyquery.semantic:author",
    "flyquery.examples:read",
    "flyquery.examples:author",
    "flyquery.query:read",
    "flyquery.derived:write",
    "flyquery.sql:execute",
    "flyquery.conversations:read",
    "flyquery.conversations:write",
    "flyquery.ingest:read",
    "flyquery.ingest:run",
    "flyquery.lineage:read",
    "flyquery.audit:read",
    "flyquery.billing:read",
    "*",  # operator-only wildcard
)


def is_valid_scope(scope: str) -> bool:
    return scope in ALL_SCOPES


def validate_scopes(scopes: list[str]) -> None:
    """Raise :class:`InvalidScopeError` on the first unknown scope."""
    for s in scopes:
        if not is_valid_scope(s):
            raise InvalidScopeError(f"unknown scope: {s!r}")
