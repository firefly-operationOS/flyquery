# Copyright 2026 Firefly Software Solutions Inc
"""SQLAlchemy declarative Base + entity exports."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single declarative base for every flyquery_* table."""


# Force eager import so alembic env.py's target_metadata sees every table.
from flyquery.models.entities.workspace import Workspace  # noqa: F401,E402
from flyquery.models.entities.dataset import Dataset  # noqa: F401,E402
from flyquery.models.entities.file import File  # noqa: F401,E402
from flyquery.models.entities.table import Table  # noqa: F401,E402
from flyquery.models.entities.schema import SchemaSnapshot, SchemaChange, SchemaObject, Relation  # noqa: F401,E402
from flyquery.models.entities.semantic import SemanticMetric, SemanticDimension, SemanticVersion, GlossaryTerm  # noqa: F401,E402
from flyquery.models.entities.examples import Example  # noqa: F401,E402
from flyquery.models.entities.queries import Query, QueryResult, Conversation, ConversationTurn  # noqa: F401,E402

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
]
