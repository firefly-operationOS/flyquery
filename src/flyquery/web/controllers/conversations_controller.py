# Copyright 2026 Firefly Software Solutions Inc
"""Conversations REST controller.

``/api/v1/conversations`` — CRUD + turn dispatch for drill-down conversations.

Path conventions:
* ``POST /api/v1/conversations``           -- create (201)
* ``GET  /api/v1/conversations``           -- list (newest first)
* ``GET  /api/v1/conversations/{id}``      -- fetch with turns
* ``POST /api/v1/conversations/{id}/turn`` -- ask next NL question (drill-down)
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import Body, PathVar, Valid, get_mapping, post_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from flyquery.config import FlyquerySettings
from flyquery.core.agents.critic_agent import build_critic_agent
from flyquery.core.agents.explainer_agent import build_explainer_agent
from flyquery.core.agents.generation_agent import build_generation_agent
from flyquery.core.agents.grounding_agent import build_grounding_agent
from flyquery.core.services.examples.auto_learner import AutoLearner
from flyquery.core.services.examples.examples_service import ExamplesService
from flyquery.core.services.execution.ast_classifier import AstClassifier
from flyquery.core.services.execution.duckdb_executor import DuckDBExecutor
from flyquery.core.services.execution.scope_guard import ScopeGuard
from flyquery.core.services.execution.table_resolver import TableResolver
from flyquery.core.services.query.conversation_service import ConversationService
from flyquery.core.services.query.query_repository import QueryRepository
from flyquery.core.services.query.query_service import QueryService
from flyquery.core.services.query.result_uploader import ResultUploader
from flyquery.core.services.retrieval.embedder import OpenAiEmbedder
from flyquery.core.services.retrieval.hybrid_retriever import HybridRetriever
from flyquery.core.services.retrieval.reranker import build_reranker
from flyquery.core.services.retrieval.search_index import SearchIndex
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.interfaces.conversations import (
    ConversationCreate,
    ConversationRead,
    ConversationTurnRequest,
    TurnRead,
)
from flyquery.interfaces.query import AnswerResponse
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request
from flyquery.web.conventions.deps import _parse_workspace_id as _pw

_DEFAULT_SCOPES: set[str] = {"flyquery.query:read"}


def _parse_workspace_id(s: str) -> uuid.UUID:
    """Parse workspace ID string to UUID, re-using the internal helper."""
    from flyquery.web.conventions import InvalidRequest

    try:
        return uuid.UUID(str(s))
    except (ValueError, AttributeError) as exc:
        raise InvalidRequest(f"workspace_id {s!r} is not a valid UUID") from exc


@rest_controller
@request_mapping("/api/v1/conversations")
class ConversationsController:
    """REST adapter for conversation CRUD and per-turn query dispatch.

    The ``POST /turn`` route internally delegates to a freshly-built
    ``QueryService`` (same pattern as ``QueryController``) so the full
    Grounding → Generation → Exec → Critic → Explainer loop runs with
    drill-down context loaded from the conversation.

    :param settings: application settings
    :param session: async session factory
    :param object_store: blob store for result Parquet
    :param query_repository: repository for flyquery_queries
    :param conversation_service: service over flyquery_conversations
    :param examples_service: needed by AutoLearner
    :param embedder: OpenAI embedder for retrieval
    """

    def __init__(
        self,
        settings: FlyquerySettings,
        session: async_sessionmaker[AsyncSession],
        object_store: ObjectStore,
        query_repository: QueryRepository,
        conversation_service: ConversationService,
        examples_service: ExamplesService,
        embedder: OpenAiEmbedder,
    ) -> None:
        self._settings = settings
        self._session_factory = session
        self._object_store = object_store
        self._query_repo = query_repository
        self._conversation_service = conversation_service
        self._examples_service = examples_service
        self._embedder = embedder

        self._ast_classifier = AstClassifier()
        self._scope_guard = ScopeGuard()
        self._executor = DuckDBExecutor(settings)

    def _build_query_service(self, db_session: AsyncSession) -> QueryService:
        """Build a per-request QueryService with drill-down context support."""
        index = SearchIndex(db_session)
        retriever = HybridRetriever(
            index=index,
            embedder=self._embedder,
            rrf_k=self._settings.rrf_k,
        )
        reranker = build_reranker(self._settings)
        table_resolver = TableResolver(session=db_session, settings=self._settings)
        uploader = ResultUploader(
            object_store=self._object_store,
            query_repo=self._query_repo,
            settings=self._settings,
        )
        auto_learner = AutoLearner(examples_service=self._examples_service)

        return QueryService(
            retriever=retriever,
            reranker=reranker,
            grounding_agent=build_grounding_agent(self._settings),
            generation_agent=build_generation_agent(self._settings),
            critic_agent=build_critic_agent(self._settings),
            explainer_agent=build_explainer_agent(self._settings),
            ast_classifier=self._ast_classifier,
            scope_guard=self._scope_guard,
            table_resolver=table_resolver,
            executor=self._executor,
            query_repo=self._query_repo,
            settings=self._settings,
            result_uploader=uploader,
            auto_learner=auto_learner,
            conversation_service=self._conversation_service,
        )

    # ------------------------------------------------------------------
    # POST /api/v1/conversations  (create)
    # ------------------------------------------------------------------

    @post_mapping("", status_code=201)
    async def create(
        self,
        http_request: Request,
        body: Valid[Body[ConversationCreate]],
    ) -> ConversationRead:
        """Create a new conversation.

        :param http_request: Starlette request (tenant context headers)
        :param body: optional title
        :return: the new ConversationRead (no turns yet)
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)
        row = await self._conversation_service.create(
            ctx.tenant_id,
            workspace_id,
            title=body.title,
            actor=ctx.actor or "user",
        )
        return ConversationRead.model_validate({**row, "turns": []})

    # ------------------------------------------------------------------
    # GET /api/v1/conversations  (list)
    # ------------------------------------------------------------------

    @get_mapping("")
    async def list_conversations(self, http_request: Request) -> dict:
        """List conversations for the caller's workspace, newest first.

        :param http_request: Starlette request
        :return: ``{"items": [...]}``
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)
        rows = await self._conversation_service.list(ctx.tenant_id, workspace_id)
        return {
            "items": [
                ConversationRead.model_validate({**r, "turns": []}).model_dump(mode="json")
                for r in rows
            ]
        }

    # ------------------------------------------------------------------
    # GET /api/v1/conversations/{conversation_id}  (fetch with turns)
    # ------------------------------------------------------------------

    @get_mapping("/{conversation_id}")
    async def read(self, conversation_id: PathVar[uuid.UUID]) -> ConversationRead:
        """Fetch a conversation with all its turns.

        :param conversation_id: conversation UUID
        :return: ConversationRead including turns list
        :raises ResourceNotFound: when conversation does not exist
        """
        row = await self._conversation_service.get_with_turns(conversation_id)
        if row is None:
            raise ResourceNotFound(f"conversation {conversation_id!r} not found")
        turns = [TurnRead.model_validate(t) for t in row.get("turns", [])]
        return ConversationRead.model_validate({**row, "turns": [t.model_dump(mode="json") for t in turns]})

    # ------------------------------------------------------------------
    # POST /api/v1/conversations/{conversation_id}/turn  (drill-down)
    # ------------------------------------------------------------------

    @post_mapping("/{conversation_id}/turn")
    async def post_turn(
        self,
        http_request: Request,
        conversation_id: PathVar[uuid.UUID],
        body: Valid[Body[ConversationTurnRequest]],
    ) -> AnswerResponse:
        """Ask a follow-up question inside an existing conversation.

        Loads the prior turn's ``executed_sql + table_qnames + snapshot_pins``
        and passes them into the query pipeline as drill-down context.

        :param http_request: Starlette request
        :param conversation_id: conversation UUID
        :param body: dataset_id + question
        :return: AnswerResponse from the full pipeline
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        # Verify the conversation exists before paying pipeline cost.
        conv = await self._conversation_service.get_with_turns(conversation_id)
        if conv is None:
            raise ResourceNotFound(f"conversation {conversation_id!r} not found")

        async with self._session_factory() as db_session:
            svc = self._build_query_service(db_session)
            result = await svc.answer(
                tenant_id=ctx.tenant_id,
                workspace_id=workspace_id,
                dataset_id=body.dataset_id,
                question=body.question,
                scopes=_DEFAULT_SCOPES,
                conversation_id=conversation_id,
            )

        return AnswerResponse(
            query_id=result.query_id,
            sql=result.sql,
            execution_status=result.execution_status,
            preview=result.preview,
            row_count=result.row_count,
            truncated=result.truncated,
            elapsed_ms=result.elapsed_ms,
            chart_hint=result.chart_hint,
            explanation=result.explanation,
            clarification=result.clarification,
            grounded_summary=result.grounded_summary,
        )
