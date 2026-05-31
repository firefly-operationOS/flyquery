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

"""SQLAlchemy declarative Base + entity exports."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single declarative base for every flyquery_* table."""


# Force eager import so alembic env.py's target_metadata sees every table.
from flyquery.models.entities.dataset import Dataset  # noqa: F401,E402
from flyquery.models.entities.examples import Example  # noqa: F401,E402
from flyquery.models.entities.file import File  # noqa: F401,E402
from flyquery.models.entities.ops import (  # noqa: F401,E402
    AgentToken,
    AuditEvent,
    CostEvent,
    IngestEvent,
    IngestJob,
)
from flyquery.models.entities.queries import (  # noqa: F401,E402
    Conversation,
    ConversationTurn,
    Query,
    QueryResult,
)
from flyquery.models.entities.schema import (  # noqa: F401,E402
    Relation,
    SchemaChange,
    SchemaObject,
    SchemaSnapshot,
)
from flyquery.models.entities.semantic import (  # noqa: F401,E402
    GlossaryTerm,
    SemanticDimension,
    SemanticMetric,
    SemanticVersion,
)
from flyquery.models.entities.table import Table  # noqa: F401,E402
from flyquery.models.entities.workspace import Workspace  # noqa: F401,E402

__all__ = [
    "Base",
    "Workspace",
    "Dataset",
    "File",
    "Table",
    "SchemaSnapshot",
    "SchemaChange",
    "SchemaObject",
    "Relation",
    "SemanticMetric",
    "SemanticDimension",
    "SemanticVersion",
    "GlossaryTerm",
    "Example",
    "Query",
    "QueryResult",
    "Conversation",
    "ConversationTurn",
    "AgentToken",
    "AuditEvent",
    "CostEvent",
    "IngestJob",
    "IngestEvent",
]
