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

"""DTO alias behaviour for glossary + semantic versions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timezone

from flyquery.interfaces.glossary import GlossaryTermCreate
from flyquery.interfaces.semantic import SemanticVersionRead


def test_glossary_create_accepts_documented_keys() -> None:
    dto = GlossaryTermCreate.model_validate(
        {
            "term": "ARR",
            "definition": "Annual Recurring Revenue.",
            "synonyms": ["annual recurring revenue"],
            "related_metrics": ["total_mrr"],
        }
    )
    assert dto.synonyms_json == ["annual recurring revenue"]
    assert dto.related_metrics_json == ["total_mrr"]


def test_glossary_create_still_accepts_internal_keys() -> None:
    dto = GlossaryTermCreate.model_validate({"term": "x", "definition": "d", "related_metrics_json": ["m"]})
    assert dto.related_metrics_json == ["m"]


def test_version_read_maps_columns_to_documented_names() -> None:
    row = {
        "id": uuid.uuid4(),
        "tenant_id": "t",
        "workspace_id": uuid.uuid4(),
        "kind": "metric",
        "parent_id": uuid.uuid4(),
        "version": 3,
        "definition_yaml": "metric: {}",
        "compiled_sql_template": "SELECT 1",
        "created_by": "alice@acme.com",
        "created_at": datetime.now(UTC),
    }
    dto = SemanticVersionRead.model_validate(row)
    assert dto.version_number == 3
    assert dto.metric_id == row["parent_id"]
