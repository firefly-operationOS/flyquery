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


# ----------------------------------------------------------------------
# Prompt rendering helpers
# ----------------------------------------------------------------------
# Each pipeline agent (Grounding / Generation / Critic / Explainer) is
# a ``FireflyAgent`` -- pydantic-ai's ``Agent.run`` expects a single
# string ``user_prompt``. We render the structured bundle (schema KB
# retrieval hits, examples, glossary, relations, semantic metrics, the
# prior turn's drill-down SQL, etc.) into a markdown-shaped prompt the
# model can reason over.


def _render_grounding_prompt(
    *,
    question: str,
    bundle: dict,
    starting_point_sql: str | None,
) -> str:
    """Pack the retrieved schema KB into a Claude-readable grounding prompt."""

    out: list[str] = []
    out.append("# User question")
    out.append(question.strip())
    out.append("")

    if starting_point_sql:
        out.append("# Prior turn (drill-down starting point)")
        out.append("```sql")
        out.append(starting_point_sql.strip())
        out.append("```")
        out.append("")

    schema_hits = bundle.get("schema_objects", []) or []
    if schema_hits:
        out.append(f"# Retrieved schema objects (top {len(schema_hits)})")
        out.append(
            "Each entry is a table or column from the workspace knowledge base. "
            "Use ONLY these tables/columns in the grounded context — never invent "
            "names. Column names that look like dates (e.g. `2024-12-31`) are "
            "legitimate column names in dashboard-style XLSX uploads."
        )
        for h in schema_hits[:30]:
            md = getattr(h, "metadata", None) or {}
            qn = md.get("qualified_name") or md.get("table_qualified_name") or "?"
            text = getattr(h, "text", "") or ""
            text = text.replace("\n", " ").strip()
            if len(text) > 240:
                text = text[:237] + "…"
            out.append(f"- `{qn}` :: {text}")
        out.append("")

    examples = bundle.get("examples", []) or []
    if examples:
        out.append(f"# Approved Q→SQL examples ({len(examples)})")
        for h in examples[:5]:
            md = getattr(h, "metadata", None) or {}
            q = md.get("question", "")
            sql = md.get("sql", "")
            out.append(f"- Q: {q}\n  SQL: `{sql}`")
        out.append("")

    metrics = bundle.get("metrics", []) or []
    if metrics:
        out.append(f"# Published semantic metrics ({len(metrics)})")
        for h in metrics[:5]:
            md = getattr(h, "metadata", None) or {}
            out.append(f"- `{md.get('name')}` -- {md.get('description', '')}")
        out.append("")

    glossary = bundle.get("glossary", []) or []
    if glossary:
        out.append(f"# Glossary terms ({len(glossary)})")
        for h in glossary[:10]:
            md = getattr(h, "metadata", None) or {}
            out.append(f"- **{md.get('term')}**: {md.get('definition', '')}")
        out.append("")

    relations = bundle.get("relations", []) or []
    if relations:
        out.append(f"# Approved relations / join hints ({len(relations)})")
        for h in relations[:10]:
            md = getattr(h, "metadata", None) or {}
            out.append(
                f"- {md.get('from_table')}.{md.get('from_column')} "
                f"→ {md.get('to_table')}.{md.get('to_column')} "
                f"(confidence={md.get('confidence')})"
            )
        out.append("")

    out.append("# Task")
    out.append(
        "Produce the GroundedContext for this question. Pick the MINIMAL set of "
        "tables, columns, and joins. If a published metric covers the question, "
        "set path=SEMANTIC_LAYER. Otherwise path=SYNTHESIS. Set confidence ∈ [0,1] "
        "and only populate `missing_info` when confidence is below 0.55."
    )
    return "\n".join(out)


def _render_generation_prompt(
    question: str,
    grounded: Any,
    starting_point_sql: str | None,
) -> str:
    """Pack the grounded context into a SQL-generation prompt."""

    out: list[str] = []
    out.append("# User question")
    out.append(question.strip())
    out.append("")

    if starting_point_sql:
        out.append("# Prior turn SQL (build a delta on top of this when possible)")
        out.append("```sql")
        out.append(starting_point_sql.strip())
        out.append("```")
        out.append("")

    g_path = getattr(grounded, "path", None)
    g_tables = getattr(grounded, "tables", []) or []
    g_columns = getattr(grounded, "columns", []) or []
    g_joins = getattr(grounded, "joins", []) or []

    out.append(f"# Grounded context (path = {g_path})")
    if g_tables:
        out.append("## Tables in scope")
        for t in g_tables:
            out.append(f"- `{getattr(t, 'table_qualified_name', t)}`")
        out.append("")
    if g_columns:
        out.append("## Columns in scope")
        for c in g_columns:
            out.append(f"- `{getattr(c, 'column_qualified_name', c)}`")
        out.append("")
    if g_joins:
        out.append("## Approved joins")
        for j in g_joins:
            out.append(
                f"- `{getattr(j, 'from_table', '')}.{getattr(j, 'from_column', '')}` "
                f"= `{getattr(j, 'to_table', '')}.{getattr(j, 'to_column', '')}` "
                f"({getattr(j, 'relationship', 'inner')} join)"
            )
        out.append("")

    out.append("# Task")
    out.append(
        "Generate up to N candidate DuckDB SQL queries that answer the question, "
        "ordered by confidence (highest first). Each candidate must:\n"
        "- Use only the tables and columns listed above. "
        "Reference each table by its **unqualified name** (the last segment of the "
        "qualified name shown above), e.g. write `FROM IVI_MALAGA_SL__Activos` "
        "rather than `FROM orbis_companies.IVI_MALAGA_SL__Activos`.\n"
        "- Quote any column name that isn't a plain identifier (e.g. date-shaped "
        "names like `2024-12-31` must be `\"2024-12-31\"`).\n"
        "- Be a SINGLE statement (no multi-statement; no DDL).\n"
        "- Be a SELECT (DuckDB-flavored)."
    )
    return "\n".join(out)


def _render_critic_prompt(
    *,
    question: str,
    failing_sql: str,
    error_message: str,
    grounded: Any,
) -> str:
    out: list[str] = []
    out.append("# User question")
    out.append(question.strip())
    out.append("")
    out.append("# Failing SQL")
    out.append("```sql")
    out.append(failing_sql.strip())
    out.append("```")
    out.append("")
    out.append("# DuckDB execution error")
    out.append(error_message.strip())
    out.append("")
    g_tables = getattr(grounded, "tables", []) or []
    g_columns = getattr(grounded, "columns", []) or []
    if g_tables or g_columns:
        out.append("# Grounded scope (do not invent tables/columns outside this set)")
        for t in g_tables:
            out.append(f"- table: `{getattr(t, 'table_qualified_name', t)}`")
        for c in g_columns:
            out.append(f"- column: `{getattr(c, 'column_qualified_name', c)}`")
        out.append("")
    out.append("# Task")
    out.append(
        "Return a corrected SQL that resolves the execution error. Output a "
        "RefinedSql with a brief reasoning + a confidence in [0,1]. Stay inside "
        "the grounded scope. Use unqualified table names (last segment only) and "
        "quote any non-identifier column names like `\"2024-12-31\"`."
    )
    return "\n".join(out)


def _render_explainer_prompt(
    *,
    question: str,
    executed_sql: str,
    row_count: int,
    preview_rows: list[dict],
) -> str:
    out: list[str] = []
    out.append("# User question")
    out.append(question.strip())
    out.append("")
    out.append("# Executed SQL")
    out.append("```sql")
    out.append(executed_sql.strip())
    out.append("```")
    out.append("")
    out.append(f"# Result")
    out.append(f"row_count: {row_count}")
    if preview_rows:
        out.append("rows (first {}):".format(min(len(preview_rows), 50)))
        for row in preview_rows[:50]:
            out.append(f"- {row}")
    out.append("")
    out.append("# Task")
    out.append(
        "Produce a ResultExplanation with a 1-3 sentence NL summary that directly "
        "answers the question using the rows above, and a chart_hint picked from "
        "{line, bar, table, pie, none}. Never invent numbers -- cite only what is "
        "in the preview."
    )
    return "\n".join(out)


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
    :param conversation_service: ConversationService (optional — Phase E drill-down)
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
        conversation_service=None,
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
        self._conversation_service = conversation_service

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
        # 2b. Load drill-down context from prior turn (Phase E)
        # ------------------------------------------------------------------
        starting_point_sql: str | None = None
        prior_table_qnames: list[str] = []
        prior_snapshot_pins: dict[str, str] = {}

        if conversation_id is not None and self._conversation_service is not None:
            prior_turn = await self._conversation_service.last_turn(conversation_id)
            if prior_turn is not None:
                starting_point_sql = prior_turn.get("executed_sql")
                prior_table_qnames = prior_turn.get("table_qnames_json") or []
                prior_snapshot_pins = prior_turn.get("snapshot_pins_json") or {}

        bundle["starting_point_sql"] = starting_point_sql
        bundle["prior_table_qnames"] = prior_table_qnames

        # ------------------------------------------------------------------
        # 3. Grounding — pydantic-ai's Agent.run expects a STRING prompt,
        # so we render the retrieval bundle into a markdown-ish doc that
        # Claude can reason over.
        # ------------------------------------------------------------------
        grounding_prompt = _render_grounding_prompt(
            question=question,
            bundle=bundle,
            starting_point_sql=starting_point_sql,
        )
        grounded_run = await self._grounding_agent.run(grounding_prompt)
        # pydantic-ai's AgentRunResult wraps the structured response on .output
        grounded = getattr(grounded_run, "output", grounded_run)

        # ------------------------------------------------------------------
        # 4. SQL generation (semantic-layer fast path OR synthesis)
        # ------------------------------------------------------------------
        chosen_sql: str
        candidates_json: list = []

        if grounded.path == "SEMANTIC_LAYER" and grounded.metrics:
            # Try to get compiled SQL from the semantic repo
            compiled = await self._compiled_metric_sql(grounded.metrics[0].metric_name, dataset_id)
            if compiled:
                chosen_sql = compiled
                candidates_json = [
                    {"sql": compiled, "reasoning": "semantic-layer compiled", "confidence": 1.0}
                ]
            else:
                # Fall through to synthesis if no compiled SQL found
                gen_prompt = _render_generation_prompt(question, grounded, starting_point_sql)
                gen_run = await self._generation_agent.run(gen_prompt)
                gen_out = getattr(gen_run, "output", gen_run)
                candidates_json = [c.model_dump() for c in gen_out.candidates]
                chosen_sql = gen_out.candidates[0].sql
        else:
            gen_prompt = _render_generation_prompt(question, grounded, starting_point_sql)
            gen_run = await self._generation_agent.run(gen_prompt)
            gen_out = getattr(gen_run, "output", gen_run)
            candidates_json = [c.model_dump() for c in gen_out.candidates]
            chosen_sql = gen_out.candidates[0].sql

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
            critic_prompt = _render_critic_prompt(
                question=question,
                failing_sql=chosen_sql,
                error_message=result.message,
                grounded=grounded,
            )
            refined_run = await self._critic_agent.run(critic_prompt)
            refined = getattr(refined_run, "output", refined_run)
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
            explainer_prompt = _render_explainer_prompt(
                question=question,
                executed_sql=chosen_sql,
                row_count=result.row_count,
                preview_rows=result.rows[:50],
            )
            explanation_run = await self._explainer_agent.run(explainer_prompt)
            explanation_obj = getattr(explanation_run, "output", explanation_run)

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
        # 12. Auto-learn (only on first-shot OK + no PII + no clarification)
        # ------------------------------------------------------------------
        if execution_status == "OK" and isinstance(result, ExecutionResult) and not clarification_emitted:
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

        # ------------------------------------------------------------------
        # 13. Persist conversation turn (Phase E drill-down)
        # ------------------------------------------------------------------
        if (
            conversation_id is not None
            and self._conversation_service is not None
            and execution_status in ("OK", "REFINED_OK")
        ):
            await self._conversation_service.append_turn(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                question=question,
                executed_sql=chosen_sql,
                summary=explanation_obj.summary if explanation_obj else None,
                table_qnames_json=list(ast.table_refs),
                snapshot_pins_json=prior_snapshot_pins,
                elapsed_ms=elapsed,
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

        Uses the session injected into the TableResolver. Both QueryService
        and TableResolver receive the same request-scoped AsyncSession from
        the controller; the session is guaranteed live for the full request.
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

        if grounded.confidence < self._settings.grounding_min_confidence and grounded.missing_info:
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
