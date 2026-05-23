# Copyright 2026 Firefly Software Solutions Inc
"""QueryService orchestrator — the complete NL → SQL → result pipeline.

Execution order
---------------
1.  Retrieve schema KB hits (BM25 + pgvector via HybridRetriever)
2.  Rerank top-K schema objects via the cross-encoder reranker
3.  Run GroundingAgent → GroundedContext
4.  Semantic-layer fast-path (SEMANTIC_LAYER + metrics) → compile SQL via MetricFlowCompiler
    OR synthesis path → run GenerationAgent → take candidates[0]
5.  AST classify the chosen SQL (sqlglot)
6.  ScopeGuard.check() — table-kind + dataset allowlist + scope enforcement
7.  Resolve parquet paths for AST table_refs (TableResolver)
8.  DuckDBExecutor.execute() — execute with LIMIT row_cap+1
9.  CriticAgent loop: on ExecutionError, retry up to max_refine_retries times
10. ExplainerAgent — NL summary + chart hint
11. Persist flyquery_queries row via QueryRepository
12. Upload result Parquet + upsert flyquery_query_results via ResultUploader
13. AutoLearner.maybe_propose() — first-shot OK + no PII → insert PROPOSED example
14. Return AnswerResult
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from flyquery.core.services.execution.ast_classifier import AstClassifier
from flyquery.core.services.execution.duckdb_executor import ExecutionError, ExecutionResult
from flyquery.core.services.execution.scope_guard import ScopeGuard, ScopeGuardError


@dataclass
class AnswerResult:
    """Full result from QueryService.answer()."""

    query_id: uuid.UUID
    sql: str | None
    execution_status: Literal["OK", "REFINED_OK", "FAILED", "REJECTED_BY_FIREWALL"] | None
    preview: list[dict] | None
    row_count: int | None
    truncated: bool
    elapsed_ms: int | None
    chart_hint: str | None
    explanation: str | None
    clarification: Any  # ClarificationFrame or None
    grounded_summary: dict | None
    snapshot_pins: dict[str, str] = field(default_factory=dict)


class QueryService:
    """Orchestrates the Grounding → Generation → AST → Exec → Critic → Explainer loop.

    All agents are injected (built by ``build_*_agent`` factories) so they
    can be replaced with canned fakes in unit tests without touching LLM APIs.

    :param retriever: HybridRetriever
    :param reranker: cross-encoder reranker (NoopReranker when unavailable)
    :param grounding_agent: FireflyAgent[GroundedContext]
    :param generation_agent: FireflyAgent[GeneratedCandidates]
    :param critic_agent: FireflyAgent[RefinedSql]
    :param explainer_agent: FireflyAgent[ResultExplanation]
    :param ast_classifier: AstClassifier
    :param scope_guard: ScopeGuard
    :param table_resolver: TableResolver
    :param executor: DuckDBExecutor
    :param query_repo: QueryRepository
    :param settings: FlyquerySettings
    :param result_uploader: ResultUploader
    :param auto_learner: AutoLearner
    :param metric_compiler: MetricFlowCompiler (optional — used for SEMANTIC_LAYER path)
    :param semantic_repo: SemanticRepository (optional — fetches compiled SQL)
    """

    def __init__(
        self,
        retriever,
        reranker,
        grounding_agent,
        generation_agent,
        critic_agent,
        explainer_agent,
        ast_classifier: AstClassifier,
        scope_guard: ScopeGuard,
        table_resolver,
        executor,
        query_repo,
        settings,
        result_uploader,
        auto_learner,
        metric_compiler=None,
        semantic_repo=None,
    ) -> None:
        self._retriever = retriever
        self._reranker = reranker
        self._grounding_agent = grounding_agent
        self._generation_agent = generation_agent
        self._critic_agent = critic_agent
        self._explainer_agent = explainer_agent
        self._ast_classifier = ast_classifier
        self._scope_guard = scope_guard
        self._table_resolver = table_resolver
        self._executor = executor
        self._query_repo = query_repo
        self._settings = settings
        self._result_uploader = result_uploader
        self._auto_learner = auto_learner
        self._metric_compiler = metric_compiler
        self._semantic_repo = semantic_repo

    async def answer(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        question: str,
        scopes: set[str],
        dataset_allowlist: set[str] | None = None,
        conversation_id: uuid.UUID | None = None,
    ) -> AnswerResult:
        """Run the full NL → SQL → result pipeline.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param dataset_id: dataset to query
        :param question: natural-language question
        :param scopes: caller's token scopes (used by ScopeGuard)
        :param dataset_allowlist: optional set of allowed dataset IDs (None = unrestricted)
        :param conversation_id: optional conversation for drill-down context (Phase E)
        :return: :class:`AnswerResult`
        """
        start_ms = time.monotonic_ns() // 1_000_000

        # ------------------------------------------------------------------
        # 1. Hybrid retrieval
        # ------------------------------------------------------------------
        bundle = await self._retriever.retrieve(
            question,
            dataset_id=dataset_id,
            workspace_id=workspace_id,
            top_k_schema=self._settings.top_k_schema * 3,
            top_k_examples=self._settings.top_k_examples,
            top_k_metrics=self._settings.top_k_metrics,
        )

        # ------------------------------------------------------------------
        # 2. Rerank top-30 schema hits → top-K
        # ------------------------------------------------------------------
        schema_hits = bundle.get("schema_objects", [])
        top_k = self._settings.top_k_schema
        reranked = await self._reranker.rerank(question, schema_hits, top_n=top_k)
        bundle["schema_objects"] = reranked

        # ------------------------------------------------------------------
        # 3. Grounding
        # ------------------------------------------------------------------
        grounded = await self._grounding_agent.run(
            {
                "question": question,
                "bundle": bundle,
                "starting_point_sql": None,  # Phase E fills this from conversation history
            }
        )

        # ------------------------------------------------------------------
        # 4. SQL generation (semantic-layer fast path OR synthesis)
        # ------------------------------------------------------------------
        chosen_sql: str
        chosen_reasoning: str | None = None
        candidates_json: list = []

        if grounded.path == "SEMANTIC_LAYER" and grounded.metrics:
            # Try to get compiled SQL from the semantic repo
            compiled = await self._compiled_metric_sql(grounded.metrics[0].metric_name, dataset_id)
            if compiled:
                chosen_sql = compiled
                candidates_json = [{"sql": compiled, "reasoning": "semantic-layer compiled", "confidence": 1.0}]
            else:
                # Fall through to synthesis if no compiled SQL found
                gen_out = await self._generation_agent.run(
                    {"grounded": grounded, "question": question, "starting_point_sql": None}
                )
                candidates_json = [c.model_dump() for c in gen_out.candidates]
                chosen_sql = gen_out.candidates[0].sql
                chosen_reasoning = gen_out.candidates[0].reasoning
        else:
            gen_out = await self._generation_agent.run(
                {"grounded": grounded, "question": question, "starting_point_sql": None}
            )
            candidates_json = [c.model_dump() for c in gen_out.candidates]
            chosen_sql = gen_out.candidates[0].sql
            chosen_reasoning = gen_out.candidates[0].reasoning

        # ------------------------------------------------------------------
        # 5. AST classify + scope guard
        # ------------------------------------------------------------------
        ast = self._ast_classifier.classify(chosen_sql)
        table_kinds = await self._table_kinds_by_name(list(ast.table_refs), dataset_id)
        dataset_of_table = await self._dataset_of_tables(list(ast.table_refs), dataset_id)

        try:
            self._scope_guard.check(
                classification=ast,
                scopes=scopes,
                table_kinds_by_name=table_kinds,
                dataset_allowlist=dataset_allowlist,
                dataset_of_table=dataset_of_table,
            )
        except ScopeGuardError as exc:
            elapsed = (time.monotonic_ns() // 1_000_000) - start_ms
            query_id = await self._query_repo.create_query(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                question=question,
                semantic_path_taken=grounded.path,
                candidates_json=candidates_json,
                chosen_candidate_index=0,
                executed_sql=chosen_sql,
                ast_classification=ast.classification,
                execution_status="REJECTED_BY_FIREWALL",
                retries=0,
                row_count=None,
                elapsed_ms=elapsed,
                clarification_emitted=False,
                clarification_json=None,
                pii_findings_json=None,
                error_json={"scope_error": str(exc)},
            )
            return AnswerResult(
                query_id=query_id,
                sql=chosen_sql,
                execution_status="REJECTED_BY_FIREWALL",
                preview=None,
                row_count=None,
                truncated=False,
                elapsed_ms=elapsed,
                chart_hint=None,
                explanation=None,
                clarification=self._clarification(grounded),
                grounded_summary=self._grounded_summary(grounded),
            )

        # ------------------------------------------------------------------
        # 6. Resolve parquet paths + execute (with critic loop)
        # ------------------------------------------------------------------
        attached = await self._table_resolver.resolve(
            dataset_id,
            list(ast.table_refs),
        )
        result = await self._executor.execute(chosen_sql, attached)
        retries = 0

        while isinstance(result, ExecutionError) and retries < self._settings.max_refine_retries:
            refined = await self._critic_agent.run(
                {
                    "sql": chosen_sql,
                    "error": result.message,
                    "grounded": grounded,
                    "question": question,
                }
            )
            chosen_sql = refined.sql
            ast = self._ast_classifier.classify(chosen_sql)
            table_kinds = await self._table_kinds_by_name(list(ast.table_refs), dataset_id)
            dataset_of_table = await self._dataset_of_tables(list(ast.table_refs), dataset_id)
            try:
                self._scope_guard.check(
                    classification=ast,
                    scopes=scopes,
                    table_kinds_by_name=table_kinds,
                    dataset_allowlist=dataset_allowlist,
                    dataset_of_table=dataset_of_table,
                )
            except ScopeGuardError:
                break
            attached = await self._table_resolver.resolve(dataset_id, list(ast.table_refs))
            result = await self._executor.execute(chosen_sql, attached)
            retries += 1

        # ------------------------------------------------------------------
        # 7. Determine execution status
        # ------------------------------------------------------------------
        if isinstance(result, ExecutionResult) and retries == 0:
            execution_status: str = "OK"
        elif isinstance(result, ExecutionResult):
            execution_status = "REFINED_OK"
        else:
            execution_status = "FAILED"

        # ------------------------------------------------------------------
        # 8. Explain
        # ------------------------------------------------------------------
        explanation_obj = None
        if isinstance(result, ExecutionResult):
            explanation_obj = await self._explainer_agent.run(
                {
                    "question": question,
                    "sql": chosen_sql,
                    "row_count": result.row_count,
                    "preview_rows": result.rows[:50],
                }
            )

        # ------------------------------------------------------------------
        # 9. Clarification frame (emitted alongside answer when confidence is low)
        # ------------------------------------------------------------------
        clarification = self._clarification(grounded)
        clarification_emitted = clarification is not None

        # ------------------------------------------------------------------
        # 10. Persist query row
        # ------------------------------------------------------------------
        elapsed = (time.monotonic_ns() // 1_000_000) - start_ms
        error_json: dict | None = None
        if isinstance(result, ExecutionError):
            error_json = {"message": result.message}

        query_id = await self._query_repo.create_query(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            question=question,
            semantic_path_taken=grounded.path,
            candidates_json=candidates_json,
            chosen_candidate_index=0,
            executed_sql=chosen_sql,
            ast_classification=ast.classification,
            execution_status=execution_status,
            retries=retries,
            row_count=result.row_count if isinstance(result, ExecutionResult) else None,
            elapsed_ms=elapsed,
            clarification_emitted=clarification_emitted,
            clarification_json=clarification.model_dump() if clarification else None,
            pii_findings_json=None,  # PII scanning in result is Phase F
            error_json=error_json,
            model_grounding=self._settings.grounding_model,
            model_generation=self._settings.generation_model,
            model_critic=self._settings.critic_model if retries > 0 else None,
            model_explainer=self._settings.explainer_model if explanation_obj else None,
        )

        # ------------------------------------------------------------------
        # 11. Upload result
        # ------------------------------------------------------------------
        if isinstance(result, ExecutionResult):
            await self._result_uploader.upload(
                query_id=query_id,
                result=result,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
            )

        # ------------------------------------------------------------------
        # 12. Auto-learn
        # ------------------------------------------------------------------
        if execution_status == "OK" and isinstance(result, ExecutionResult):
            await self._auto_learner.maybe_propose(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                question=question,
                generated_sql=chosen_sql,
                retries=retries,
                pii_findings=[],
                query_id=query_id,
            )

        return AnswerResult(
            query_id=query_id,
            sql=chosen_sql,
            execution_status=execution_status,  # type: ignore[arg-type]
            preview=result.rows[:10] if isinstance(result, ExecutionResult) else None,
            row_count=result.row_count if isinstance(result, ExecutionResult) else None,
            truncated=result.truncated if isinstance(result, ExecutionResult) else False,
            elapsed_ms=elapsed,
            chart_hint=explanation_obj.chart_hint if explanation_obj else None,
            explanation=explanation_obj.summary if explanation_obj else None,
            clarification=clarification,
            grounded_summary=self._grounded_summary(grounded),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _table_kinds_by_name(
        self,
        table_names: list[str],
        dataset_id: uuid.UUID,
    ) -> dict[str, str]:
        """Return {name: kind} for the given table names in the dataset.

        Uses the session injected into the TableResolver so we don't need
        a separate session factory on the QueryService.
        """
        if not table_names:
            return {}
        import sqlalchemy as sa

        session = self._table_resolver._session
        rows = await session.execute(
            sa.text("""
                SELECT name, kind FROM flyquery_tables
                WHERE dataset_id = :ds AND name = ANY(:names) AND is_active = true
            """),
            {"ds": dataset_id, "names": list(table_names)},
        )
        return {r["name"]: r["kind"] for r in rows.mappings()}

    async def _dataset_of_tables(
        self,
        table_names: list[str],
        dataset_id: uuid.UUID,
    ) -> dict[str, str]:
        """Return {name: dataset_id_str} — all resolved tables share the same dataset."""
        return {name: str(dataset_id) for name in table_names}

    async def _compiled_metric_sql(
        self,
        metric_name: str,
        dataset_id: uuid.UUID,
    ) -> str | None:
        """Fetch the compiled SQL for a published metric, or None if unavailable."""
        if self._semantic_repo is None:
            return None
        try:
            row = await self._semantic_repo.get_by_name(metric_name, dataset_id)
            if row and row.get("status") == "PUBLISHED":
                return row.get("compiled_sql_template")
        except Exception:  # noqa: BLE001
            pass
        return None

    def _clarification(self, grounded) -> Any:
        """Build a ClarificationFrame if grounding confidence is low."""
        from flyquery.interfaces.query import ClarificationFrame

        if (
            grounded.confidence < self._settings.grounding_min_confidence
            and grounded.missing_info
        ):
            return ClarificationFrame(
                questions=grounded.missing_info,
                reasons=[],
            )
        return None

    def _grounded_summary(self, grounded) -> dict:
        """Convert GroundedContext to a summary dict for the response."""
        return {
            "path": grounded.path,
            "confidence": grounded.confidence,
            "table_count": len(grounded.tables),
            "missing_info": grounded.missing_info,
        }
