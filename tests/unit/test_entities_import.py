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

"""All entity modules import + the Base.metadata enumerates the tables."""

from __future__ import annotations


def test_lifecycle_entities_register_on_base_metadata() -> None:
    from flyquery.models.entities import Base

    table_names = set(Base.metadata.tables.keys())
    assert {"flyquery_workspaces", "flyquery_datasets", "flyquery_files", "flyquery_tables"} <= table_names
