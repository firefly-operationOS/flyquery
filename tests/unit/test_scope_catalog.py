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

import pytest

from flyquery.core.services.auth.scope_catalog import (
    ALL_SCOPES,
    InvalidScopeError,
    validate_scopes,
)


def test_catalog_includes_every_spec_scope() -> None:
    expected = {
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
        "*",
    }
    assert expected <= set(ALL_SCOPES)


def test_validate_rejects_unknown_scope() -> None:
    with pytest.raises(InvalidScopeError):
        validate_scopes(["flyquery.query:bogus"])


def test_validate_accepts_known() -> None:
    validate_scopes(["flyquery.query:read", "flyquery.files:upload"])
