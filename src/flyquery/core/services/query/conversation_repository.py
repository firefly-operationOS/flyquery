# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_conversations and flyquery_conversation_turns."""

from __future__ import annotations

import json
import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class ConversationRepository:
    """Repository over ``flyquery_conversations`` and ``flyquery_conversation_turns``.

    :param session: ``async_sessionmaker`` injected by pyfly's DI container.
    """

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def create_conversation(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        title: str | None,
        actor: str,
    ) -> dict[str, Any]:
        """Insert a new conversation row and return the full record.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param title: optional human-readable title
        :param actor: actor who created the conversation
        :return: dict with all conversation columns
        """
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text("""
                    INSERT INTO flyquery_conversations
                        (tenant_id, workspace_id, title, actor)
                    VALUES
                        (:tenant_id, :workspace_id, :title, :actor)
                    RETURNING id, tenant_id, workspace_id, title, summary,
                              actor, model, metadata_json, created_at, updated_at
                """),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "title": title,
                    "actor": actor,
                },
            )
            row = result.mappings().one()
            return dict(row)

    async def list_conversations(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return conversations for a workspace, newest first.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param limit: max rows to return
        :return: list of conversation dicts
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text("""
                    SELECT id, tenant_id, workspace_id, title, summary,
                           actor, model, metadata_json, created_at, updated_at
                    FROM flyquery_conversations
                    WHERE tenant_id = :tenant_id AND workspace_id = :workspace_id
                    ORDER BY updated_at DESC
                    LIMIT :lim
                """),
                {"tenant_id": tenant_id, "workspace_id": workspace_id, "lim": limit},
            )
            return [dict(row) for row in result.mappings().all()]

    async def get_conversation(self, conversation_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single conversation by primary key.

        :param conversation_id: conversation UUID
        :return: conversation dict or None if not found
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text("""
                    SELECT id, tenant_id, workspace_id, title, summary,
                           actor, model, metadata_json, created_at, updated_at
                    FROM flyquery_conversations WHERE id = :id
                """),
                {"id": conversation_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def get_turns(self, conversation_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return all turns for a conversation, ordered by turn_index.

        :param conversation_id: conversation UUID
        :return: list of turn dicts
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text("""
                    SELECT id, tenant_id, workspace_id, conversation_id, turn_index,
                           question, executed_sql, summary,
                           table_qnames_json, snapshot_pins_json, citations_json,
                           no_answer, elapsed_ms, model, created_at
                    FROM flyquery_conversation_turns
                    WHERE conversation_id = :conv_id
                    ORDER BY turn_index ASC
                """),
                {"conv_id": conversation_id},
            )
            return [dict(row) for row in result.mappings().all()]

    async def get_last_turn(self, conversation_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch the most recent turn for a conversation.

        :param conversation_id: conversation UUID
        :return: turn dict or None if the conversation has no turns yet
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text("""
                    SELECT id, tenant_id, workspace_id, conversation_id, turn_index,
                           question, executed_sql, summary,
                           table_qnames_json, snapshot_pins_json, citations_json,
                           no_answer, elapsed_ms, model, created_at
                    FROM flyquery_conversation_turns
                    WHERE conversation_id = :conv_id
                    ORDER BY turn_index DESC
                    LIMIT 1
                """),
                {"conv_id": conversation_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None

    async def append_turn(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        conversation_id: uuid.UUID,
        question: str,
        executed_sql: str | None,
        summary: str | None,
        table_qnames_json: list[str],
        snapshot_pins_json: dict[str, str],
        elapsed_ms: int | None = None,
    ) -> dict[str, Any]:
        """Append a new turn to an existing conversation.

        The turn_index is derived from the current MAX(turn_index) + 1 in the
        same conversation, serialised inside the same transaction.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param conversation_id: parent conversation UUID
        :param question: NL question for this turn
        :param executed_sql: SQL that was run (None on failure)
        :param summary: NL explanation of the result (None on failure)
        :param table_qnames_json: qualified table names referenced by the SQL
        :param snapshot_pins_json: {table_id: snapshot_id} mapping for reproducibility
        :param elapsed_ms: execution time in milliseconds
        :return: the newly inserted turn dict
        """
        async with self._factory() as s, s.begin():
            # Derive the next turn_index atomically.
            idx_result = await s.execute(
                sa.text("""
                    SELECT COALESCE(MAX(turn_index), -1) + 1
                    FROM flyquery_conversation_turns
                    WHERE conversation_id = :conv_id
                """),
                {"conv_id": conversation_id},
            )
            next_index: int = idx_result.scalar_one()

            result = await s.execute(
                sa.text("""
                    INSERT INTO flyquery_conversation_turns
                        (tenant_id, workspace_id, conversation_id, turn_index,
                         question, executed_sql, summary,
                         table_qnames_json, snapshot_pins_json, elapsed_ms)
                    VALUES
                        (:tenant_id, :workspace_id, :conversation_id, :turn_index,
                         :question, :executed_sql, :summary,
                         CAST(:table_qnames AS jsonb), CAST(:snapshot_pins AS jsonb),
                         :elapsed_ms)
                    RETURNING id, tenant_id, workspace_id, conversation_id, turn_index,
                              question, executed_sql, summary,
                              table_qnames_json, snapshot_pins_json, citations_json,
                              no_answer, elapsed_ms, model, created_at
                """),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "conversation_id": conversation_id,
                    "turn_index": next_index,
                    "question": question,
                    "executed_sql": executed_sql,
                    "summary": summary,
                    "table_qnames": json.dumps(table_qnames_json),
                    "snapshot_pins": json.dumps(snapshot_pins_json),
                    "elapsed_ms": elapsed_ms,
                },
            )
            turn = dict(result.mappings().one())

            # Touch updated_at on the parent conversation.
            await s.execute(
                sa.text(
                    "UPDATE flyquery_conversations SET updated_at = now() WHERE id = :id"
                ),
                {"id": conversation_id},
            )
            return turn
