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

"""Unit tests for ScopeGuard.

Covers: missing scope (rejected), wildcard scope (allowed), dataset allowlist
(rejected when out), DML on UPLOADED (rejected), DML on DERIVED with scope
(allowed), DDL (rejected), multi-statement (rejected).
"""

from __future__ import annotations

import pytest

from flyquery.core.services.execution.ast_classifier import AstClassification
from flyquery.core.services.execution.scope_guard import ScopeGuard, ScopeGuardError


@pytest.fixture
def guard() -> ScopeGuard:
    return ScopeGuard()


def _select_cls(tables: tuple[str, ...] = ("orders",)) -> AstClassification:
    return AstClassification(
        classification="SELECT",
        single_statement=True,
        table_refs=tables,
        column_refs=(),
        has_subquery=False,
    )


def _dml_cls(
    kind: str = "INSERT",
    tables: tuple[str, ...] = ("derived_table",),
) -> AstClassification:
    return AstClassification(
        classification=kind,
        single_statement=True,
        table_refs=tables,
        column_refs=(),
        has_subquery=False,
    )


def _ddl_cls() -> AstClassification:
    return AstClassification(
        classification="DDL",
        single_statement=True,
        table_refs=(),
        column_refs=(),
        has_subquery=False,
    )


def _multi_cls() -> AstClassification:
    return AstClassification(
        classification="SELECT",
        single_statement=False,
        table_refs=(),
        column_refs=(),
        has_subquery=False,
    )


# ---------------------------------------------------------------------------
# SELECT tests
# ---------------------------------------------------------------------------


def test_select_with_read_scope_allowed(guard: ScopeGuard) -> None:
    """SELECT passes when caller has flyquery.query:read."""
    guard.check(
        classification=_select_cls(),
        scopes={"flyquery.query:read"},
        table_kinds_by_name={"orders": "UPLOADED"},
        dataset_allowlist=None,
        dataset_of_table={},
    )  # must not raise


def test_select_with_execute_scope_allowed(guard: ScopeGuard) -> None:
    """SELECT passes when caller has flyquery.sql:execute."""
    guard.check(
        classification=_select_cls(),
        scopes={"flyquery.sql:execute"},
        table_kinds_by_name={"orders": "UPLOADED"},
        dataset_allowlist=None,
        dataset_of_table={},
    )  # must not raise


def test_select_with_wildcard_scope_allowed(guard: ScopeGuard) -> None:
    """SELECT passes when caller has wildcard * scope."""
    guard.check(
        classification=_select_cls(),
        scopes={"*"},
        table_kinds_by_name={"orders": "UPLOADED"},
        dataset_allowlist=None,
        dataset_of_table={},
    )  # must not raise


def test_select_missing_scope_rejected(guard: ScopeGuard) -> None:
    """SELECT is rejected when caller has no relevant scope."""
    with pytest.raises(ScopeGuardError, match="missing flyquery.query:read scope"):
        guard.check(
            classification=_select_cls(),
            scopes={"flyquery.examples:read"},
            table_kinds_by_name={"orders": "UPLOADED"},
            dataset_allowlist=None,
            dataset_of_table={},
        )


# ---------------------------------------------------------------------------
# Dataset allowlist tests
# ---------------------------------------------------------------------------


def test_select_within_allowlist_allowed(guard: ScopeGuard) -> None:
    """Table whose dataset is in the allowlist passes."""
    guard.check(
        classification=_select_cls(("orders",)),
        scopes={"flyquery.query:read"},
        table_kinds_by_name={"orders": "UPLOADED"},
        dataset_allowlist={"ds-northwind"},
        dataset_of_table={"orders": "ds-northwind"},
    )  # must not raise


def test_select_outside_allowlist_rejected(guard: ScopeGuard) -> None:
    """Table whose dataset is NOT in the allowlist is rejected."""
    with pytest.raises(ScopeGuardError, match="not in the caller's dataset allowlist"):
        guard.check(
            classification=_select_cls(("orders",)),
            scopes={"flyquery.query:read"},
            table_kinds_by_name={"orders": "UPLOADED"},
            dataset_allowlist={"ds-other"},
            dataset_of_table={"orders": "ds-northwind"},
        )


def test_select_no_allowlist_allows_anything(guard: ScopeGuard) -> None:
    """None allowlist means no restriction."""
    guard.check(
        classification=_select_cls(("orders",)),
        scopes={"flyquery.query:read"},
        table_kinds_by_name={"orders": "UPLOADED"},
        dataset_allowlist=None,
        dataset_of_table={"orders": "any-dataset"},
    )  # must not raise


# ---------------------------------------------------------------------------
# DDL / multi-statement
# ---------------------------------------------------------------------------


def test_ddl_always_rejected(guard: ScopeGuard) -> None:
    """DDL is rejected regardless of scope."""
    with pytest.raises(ScopeGuardError, match="DDL not allowed"):
        guard.check(
            classification=_ddl_cls(),
            scopes={"*"},
            table_kinds_by_name={},
            dataset_allowlist=None,
            dataset_of_table={},
        )


def test_multi_statement_rejected(guard: ScopeGuard) -> None:
    """Multi-statement SQL is always rejected."""
    with pytest.raises(ScopeGuardError, match="multi-statement"):
        guard.check(
            classification=_multi_cls(),
            scopes={"*"},
            table_kinds_by_name={},
            dataset_allowlist=None,
            dataset_of_table={},
        )


# ---------------------------------------------------------------------------
# DML tests
# ---------------------------------------------------------------------------


def test_dml_on_uploaded_table_rejected(guard: ScopeGuard) -> None:
    """DML on UPLOADED table is always rejected."""
    with pytest.raises(ScopeGuardError, match="DML on UPLOADED table"):
        guard.check(
            classification=_dml_cls("INSERT", ("orders",)),
            scopes={"flyquery.derived:write"},
            table_kinds_by_name={"orders": "UPLOADED"},
            dataset_allowlist=None,
            dataset_of_table={},
        )


def test_dml_on_derived_with_scope_allowed(guard: ScopeGuard) -> None:
    """DML on DERIVED table with flyquery.derived:write scope is allowed."""
    guard.check(
        classification=_dml_cls("INSERT", ("derived_table",)),
        scopes={"flyquery.derived:write"},
        table_kinds_by_name={"derived_table": "DERIVED"},
        dataset_allowlist=None,
        dataset_of_table={},
    )  # must not raise


def test_dml_on_derived_without_scope_rejected(guard: ScopeGuard) -> None:
    """DML on DERIVED table without write scope is rejected."""
    with pytest.raises(ScopeGuardError, match="missing flyquery.derived:write scope"):
        guard.check(
            classification=_dml_cls("UPDATE", ("derived_table",)),
            scopes={"flyquery.query:read"},
            table_kinds_by_name={"derived_table": "DERIVED"},
            dataset_allowlist=None,
            dataset_of_table={},
        )


def test_dml_on_unknown_table_rejected(guard: ScopeGuard) -> None:
    """DML on a table with no known kind is rejected."""
    with pytest.raises(ScopeGuardError, match="DML on unknown table"):
        guard.check(
            classification=_dml_cls("DELETE", ("mystery_table",)),
            scopes={"flyquery.derived:write"},
            table_kinds_by_name={},  # no entry for mystery_table
            dataset_allowlist=None,
            dataset_of_table={},
        )
