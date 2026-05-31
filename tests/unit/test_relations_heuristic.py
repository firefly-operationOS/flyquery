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

"""Unit tests for relations stage heuristic helpers."""

from __future__ import annotations


class TestTypeGroup:
    def test_integer_numeric(self):
        from flyquery.core.services.ingestion.stages.relations import _type_group

        assert _type_group("INTEGER") == "numeric"
        assert _type_group("BIGINT") == "numeric"
        assert _type_group("DOUBLE") == "numeric"

    def test_varchar_text(self):
        from flyquery.core.services.ingestion.stages.relations import _type_group

        assert _type_group("VARCHAR") == "text"
        assert _type_group("TEXT") == "text"

    def test_date_temporal(self):
        from flyquery.core.services.ingestion.stages.relations import _type_group

        assert _type_group("DATE") == "temporal"
        assert _type_group("TIMESTAMP") == "temporal"

    def test_unknown_other(self):
        from flyquery.core.services.ingestion.stages.relations import _type_group

        assert _type_group("ARRAY") == "other"


class TestTypesCompatible:
    def test_numeric_numeric(self):
        from flyquery.core.services.ingestion.stages.relations import _types_compatible

        assert _types_compatible("INTEGER", "BIGINT")

    def test_text_text(self):
        from flyquery.core.services.ingestion.stages.relations import _types_compatible

        assert _types_compatible("VARCHAR", "TEXT")

    def test_numeric_text_incompatible(self):
        from flyquery.core.services.ingestion.stages.relations import _types_compatible

        assert not _types_compatible("INTEGER", "VARCHAR")

    def test_other_incompatible(self):
        from flyquery.core.services.ingestion.stages.relations import _types_compatible

        assert not _types_compatible("ARRAY", "INTEGER")


class TestNameSpecificity:
    def test_generic_id_low(self):
        from flyquery.core.services.ingestion.stages.relations import _name_specificity

        assert _name_specificity("id") < 0.5

    def test_customer_id_high(self):
        from flyquery.core.services.ingestion.stages.relations import _name_specificity

        assert _name_specificity("customer_id") >= 0.7

    def test_order_uuid_high(self):
        from flyquery.core.services.ingestion.stages.relations import _name_specificity

        assert _name_specificity("order_uuid") >= 0.7

    def test_ambiguous_medium(self):
        from flyquery.core.services.ingestion.stages.relations import _name_specificity

        score = _name_specificity("region")
        assert 0.4 <= score <= 0.8


class TestIsPkLike:
    def test_high_distinct_is_pk(self):
        from flyquery.core.services.ingestion.stages.relations import _is_pk_like

        col = {"profile_json": {"distinct_estimate": 950}}
        tbl = {"n_rows_actual": 1000}
        assert _is_pk_like(col, tbl)

    def test_low_distinct_not_pk(self):
        from flyquery.core.services.ingestion.stages.relations import _is_pk_like

        col = {"profile_json": {"distinct_estimate": 5}}
        tbl = {"n_rows_actual": 1000}
        assert not _is_pk_like(col, tbl)

    def test_no_profile_not_pk(self):
        from flyquery.core.services.ingestion.stages.relations import _is_pk_like

        col = {"profile_json": None}
        tbl = {"n_rows_actual": 1000}
        assert not _is_pk_like(col, tbl)


class TestRelationModuleImportable:
    def test_relation_proposer_agent_importable(self):
        from flyquery.core.agents.relation_proposer_agent import (
            ProposedRelation,
            ProposedRelations,
        )

        assert ProposedRelations is not None
        assert ProposedRelation is not None
