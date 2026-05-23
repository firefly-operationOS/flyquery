# Copyright 2026 Firefly Software Solutions Inc
"""Glossary wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GlossaryTermCreate(BaseModel):
    """Payload for creating a new glossary term."""

    model_config = ConfigDict(populate_by_name=True)

    term: str = Field(min_length=1, max_length=512)
    definition: str = Field(min_length=1)
    synonyms_json: list[str] = Field(default_factory=list)
    tags_json: list[str] = Field(default_factory=list)
    related_columns_json: list[str] = Field(default_factory=list)
    related_metrics_json: list[str] = Field(default_factory=list)


class GlossaryTermUpdate(BaseModel):
    """Sparse-update payload for an existing glossary term."""

    definition: str | None = None
    synonyms_json: list[str] | None = None
    tags_json: list[str] | None = None
    related_columns_json: list[str] | None = None
    related_metrics_json: list[str] | None = None


class GlossaryTermRead(BaseModel):
    """Full read representation of a flyquery_glossary_terms row."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    term: str
    definition: str
    synonyms_json: list[str]
    tags_json: list[str]
    related_columns_json: list[str]
    related_metrics_json: list[str]
    created_at: datetime
    updated_at: datetime
