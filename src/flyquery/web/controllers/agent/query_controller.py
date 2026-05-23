# Copyright 2026 Firefly Software Solutions Inc
"""Agent-tier query pipeline controller.

``/api/v1/agent/query`` — same pipeline as the user-tier ``/api/v1/query``
but requires a valid ``X-Agent-Token`` with ``flyquery.query:read`` scope.

Delegates to the same :class:`QueryService` as the user-tier controller.
Auth difference: verifies ``X-Agent-Token`` instead of a JWT bearer.

Path conventions:
* ``POST /api/v1/agent/query``          -- full sync pipeline
* ``POST /api/v1/agent/query:explain``  -- Grounding + Generation only
* ``POST /api/v1/agent/query:validate`` -- Grounding + Generation + AST + ScopeGuard
* ``POST /api/v1/agent/query/stream``   -- SSE event stream
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import Body, Valid, post_mapping, request_mapping
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import StreamingResponse

from flyquery.config import FlyquerySettings
from flyquery.core.agents.critic_agent import build_critic_agent
from flyquery.core.agents.explainer_agent import build_explainer_agent
from flyquery.core.agents.generation_agent import build_generation_agent
from flyquery.core.agents.grounding_agent import build_grounding_agent
from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.core.services.examples.auto_learner import AutoLearner
from flyquery.core.services.examples.examples_service import ExamplesService
from flyquery.core.services.execution.ast_classifier import AstClassifier
from flyquery.core.services.execution.duckdb_executor import DuckDBExecutor
from flyquery.core.services.execution.scope_guard import ScopeGuard, ScopeGuardError
from flyquery.core.services.execution.table_resolver import TableResolver
from flyquery.core.services.query.conversation_service import ConversationService
from flyquery.core.services.query.query_repository import QueryRepository
from flyquery.core.services.query.query_service import QueryService
from flyquery.core.services.query.result_uploader import ResultUploader
from flyquery.core.services.retrieval.embedder import Embedder
from flyquery.core.services.retrieval.hybrid_retriever import HybridRetriever
from flyquery.core.services.retrieval.reranker import build_reranker
from flyquery.core.services.retrieval.search_index import SearchIndex
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.interfaces.query import (
    AnswerResponse,
    ClarificationFrame,
    ExplainResponse,
    QueryRequest,
    ValidateResponse,
)
from flyquery.web.conventions import (
    HEADER_AGENT_TOKEN,
    FireflyHTTPException,
    InvalidRequest,
    tenant_context_from_request,
)

_SCOPE_QUERY_READ = "flyquery.query:read"


class MissingAgentToken(FireflyHTTPException):
    status = 401
    code = "missing_agent_token"
    title = "Missing X-Agent-Token header"


def _parse_workspace_id(s: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(s))
    except (ValueError, AttributeError) as exc:
        raise InvalidRequest(f"workspace_id {s!r} is not a valid UUID") from exc


@rest_controller
@request_mapping("/api/v1/agent")
class AgentQueryController:
    """Agent-tier mirror of :class:`QueryController`.

    Requires ``X-Agent-Token`` with ``flyquery.query:read`` scope for every
    route. Delegates to the same ``QueryService`` pipeline.

    :param settings: application settings
    :param session: async session factory
    :param object_store: blob store for result Parquet
    :param query_repository: repository for flyquery_queries
    :param conversation_service: for drill-down context
    :param examples_service: needed by AutoLearner
    :param embedder: OpenAI embedder for retrieval
    :param agent_token_service: used to verify scope on every request
    """

    def __init__(
        self,
        settings: FlyquerySettings,
        session: async_sessionmaker[AsyncSession],
        object_store: ObjectStore,
        query_repository: QueryRepository,
        conversation_service: ConversationService,
        examples_service: ExamplesService,
        embedder: Embedder,
        agent_token_service: AgentTokenService,
    ) -> None:
        self._settings = settings
        self._session_factory = session
        self._object_store = object_store
        self._query_repo = query_repository
        self._conversation_service = conversation_service
        self._examples_service = examples_service
        self._embedder = embedder
        self._token_service = agent_token_service

        self._ast_classifier = AstClassifier()
        self._scope_guard = ScopeGuard()
        self._executor = DuckDBExecutor(settings)

    async def _verify(self, http_request: Request) -> None:
        """Verify X-Agent-Token with flyquery.query:read scope.

        :raises MissingAgentToken: when header is absent
        :raises 403: when token does not carry the required scope
        """
        token = http_request.headers.get(HEADER_AGENT_TOKEN)
        if not token:
            raise MissingAgentToken("X-Agent-Token header is required for /api/v1/agent/* routes.")
        ctx = tenant_context_from_request(http_request)
        await self._token_service.verify(
            token,
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.workspace_id,
            scope=_SCOPE_QUERY_READ,
        )

    def _build_service(self, db_session: AsyncSession) -> QueryService:
        """Build a per-request QueryService with the shared embedder/agents."""
        index = SearchIndex(db_session)
        retriever = HybridRetriever(index=index, embedder=self._embedder, rrf_k=self._settings.rrf_k)
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
    # POST /api/v1/agent/query
    # ------------------------------------------------------------------

    @post_mapping("/query")
    async def query(
        self,
        http_request: Request,
        body: Valid[Body[QueryRequest]],
    ) -> AnswerResponse:
        """Run the full NL → SQL → result pipeline (agent-tier).

        :param http_request: Starlette request (provides tenant context + agent token)
        :param body: validated QueryRequest
        :return: AnswerResponse
        """
        await self._verify(http_request)
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        async with self._session_factory() as db_session:
            svc = self._build_service(db_session)
            result = await svc.answer(
                tenant_id=ctx.tenant_id,
                workspace_id=workspace_id,
                dataset_id=body.dataset_id,
                question=body.question,
                scopes={_SCOPE_QUERY_READ},
                conversation_id=body.conversation_id,
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

    # ------------------------------------------------------------------
    # POST /api/v1/agent/query:explain
    # ------------------------------------------------------------------

    @post_mapping("/query:explain")
    async def explain(
        self,
        http_request: Request,
        body: Valid[Body[QueryRequest]],
    ) -> ExplainResponse:
        """Run Grounding + Generation only (agent-tier).

        :param http_request: Starlette request
        :param body: validated QueryRequest
        :return: ExplainResponse with candidate SQL and reasoning
        """
        await self._verify(http_request)
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        async with self._session_factory() as db_session:
            index = SearchIndex(db_session)
            retriever = HybridRetriever(index=index, embedder=self._embedder, rrf_k=self._settings.rrf_k)
            reranker = build_reranker(self._settings)

            bundle = await retriever.retrieve(
                body.question,
                dataset_id=body.dataset_id,
                workspace_id=workspace_id,
                top_k_schema=self._settings.top_k_schema * 3,
            )
            schema_hits = bundle.get("schema_objects", [])
            reranked = await reranker.rerank(body.question, schema_hits, top_n=self._settings.top_k_schema)
            bundle["schema_objects"] = reranked

            grounding_agent = build_grounding_agent(self._settings)
            grounded = await grounding_agent.run(
                {"question": body.question, "bundle": bundle, "starting_point_sql": None}
            )

            generation_agent = build_generation_agent(self._settings)
            gen_out = await generation_agent.run(
                {"grounded": grounded, "question": body.question, "starting_point_sql": None}
            )
            candidate = gen_out.candidates[0]

        clarification: ClarificationFrame | None = None
        if grounded.confidence < self._settings.grounding_min_confidence and grounded.missing_info:
            clarification = ClarificationFrame(questions=grounded.missing_info, reasons=[])

        return ExplainResponse(
            sql=candidate.sql,
            reasoning=candidate.reasoning,
            confidence=candidate.confidence,
            grounded_summary={
                "path": grounded.path,
                "confidence": grounded.confidence,
                "table_count": len(grounded.tables),
            },
            clarification=clarification,
        )

    # ------------------------------------------------------------------
    # POST /api/v1/agent/query:validate
    # ------------------------------------------------------------------

    @post_mapping("/query:validate")
    async def validate(
        self,
        http_request: Request,
        body: Valid[Body[QueryRequest]],
    ) -> ValidateResponse:
        """Run Grounding + Generation + AST + ScopeGuard (agent-tier).

        :param http_request: Starlette request
        :param body: validated QueryRequest
        :return: ValidateResponse
        """
        await self._verify(http_request)
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        async with self._session_factory() as db_session:
            index = SearchIndex(db_session)
            retriever = HybridRetriever(index=index, embedder=self._embedder, rrf_k=self._settings.rrf_k)
            reranker = build_reranker(self._settings)

            bundle = await retriever.retrieve(
                body.question,
                dataset_id=body.dataset_id,
                workspace_id=workspace_id,
                top_k_schema=self._settings.top_k_schema * 3,
            )
            schema_hits = bundle.get("schema_objects", [])
            reranked = await reranker.rerank(body.question, schema_hits, top_n=self._settings.top_k_schema)
            bundle["schema_objects"] = reranked

            grounding_agent = build_grounding_agent(self._settings)
            grounded = await grounding_agent.run(
                {"question": body.question, "bundle": bundle, "starting_point_sql": None}
            )

            generation_agent = build_generation_agent(self._settings)
            gen_out = await generation_agent.run(
                {"grounded": grounded, "question": body.question, "starting_point_sql": None}
            )
            chosen_sql = gen_out.candidates[0].sql

        ast = self._ast_classifier.classify(chosen_sql)
        scope_error: str | None = None
        try:
            self._scope_guard.check(
                classification=ast,
                scopes={_SCOPE_QUERY_READ},
                table_kinds_by_name={},
                dataset_allowlist=None,
                dataset_of_table={},
            )
        except ScopeGuardError as exc:
            scope_error = str(exc)

        clarification: ClarificationFrame | None = None
        if grounded.confidence < self._settings.grounding_min_confidence and grounded.missing_info:
            clarification = ClarificationFrame(questions=grounded.missing_info, reasons=[])

        return ValidateResponse(
            sql=chosen_sql,
            ast_classification=ast.classification,
            table_refs=list(ast.table_refs),
            single_statement=ast.single_statement,
            scope_error=scope_error,
            clarification=clarification,
        )

    # ------------------------------------------------------------------
    # POST /api/v1/agent/query/stream
    # ------------------------------------------------------------------

    @post_mapping("/query/stream")
    async def stream(
        self,
        http_request: Request,
        body: Valid[Body[QueryRequest]],
    ) -> StreamingResponse:
        """Run the pipeline as SSE stream (agent-tier).

        :param http_request: Starlette request
        :param body: validated QueryRequest
        :return: StreamingResponse with text/event-stream
        """
        await self._verify(http_request)
        # Delegate to the user-tier QueryController's stream implementation
        # by importing and calling it inline (re-uses all SSE logic).
        from flyquery.web.controllers.query_controller import QueryController

        user_ctrl = QueryController(
            settings=self._settings,
            session=self._session_factory,
            object_store=self._object_store,
            query_repository=self._query_repo,
            examples_service=self._examples_service,
            embedder=self._embedder,
        )
        ctx = tenant_context_from_request(http_request)
        workspace_id = _parse_workspace_id(ctx.workspace_id)

        return StreamingResponse(
            user_ctrl._stream_events(
                tenant_id=ctx.tenant_id,
                workspace_id=workspace_id,
                request=body,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
