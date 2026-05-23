# Copyright 2026 Firefly Software Solutions Inc
"""Conversation wire DTOs (Pydantic v2).

Defines the request/response shapes for the /conversations endpoints.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Request body for POST /api/v1/conversations."""

    model_config = ConfigDict(populate_by_name=True)

    title: str | None = Field(default=None, max_length=500)


class ConversationTurnRequest(BaseModel):
    """Request body for POST /api/v1/conversations/{id}/turn."""

    model_config = ConfigDict(populate_by_name=True)

    dataset_id: uuid.UUID
    question: str = Field(min_length=1, max_length=4096)


class TurnRead(BaseModel):
    """Single conversation turn."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    conversation_id: uuid.UUID
    turn_index: int
    question: str
    executed_sql: str | None
    summary: str | None
    table_qnames_json: list[str] = Field(default_factory=list)
    snapshot_pins_json: dict[str, Any] = Field(default_factory=dict)
    no_answer: bool
    elapsed_ms: int | None
    created_at: datetime


class ConversationRead(BaseModel):
    """A conversation, optionally with its turns."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    title: str | None
    summary: str | None
    actor: str
    created_at: datetime
    updated_at: datetime
    turns: list[TurnRead] = Field(default_factory=list)
