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

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from flyquery.core.services.execution.ast_classifier import AstClassifier
from flyquery.core.services.execution.duckdb_executor import ExecutionError, ExecutionResult
from flyquery.core.services.execution.scope_guard import ScopeGuard, ScopeGuardError
from flyquery.core.services.semantic.compiler import SemanticCompiler

logger = logging.getLogger(__name__)

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

    # 1. The "Complete dataset catalogue" lists EVERY table in the dataset.
    #    Ground-truth inventory the LLM must pick from; prevents
    #    hallucination of plausible-but-nonexistent tables like
    #    ``balance_sheet`` / ``income_statement``.
    inventory = bundle.get("schema_inventory", []) or []
    inv_tables = [h for h in inventory if (getattr(h, "metadata", {}) or {}).get("kind") == "TABLE"]
    if inv_tables:
        out.append(f"# Complete dataset catalogue ({len(inv_tables)} tables)")
        out.append(
            "These are the ONLY tables available. Use exactly these qualified "
            "names. Never invent table names like `balance_sheet`, "
            "`income_statement`, or `financials.*` -- if the user asks about "
            "assets, find the matching table below (it may be named in "
            "another language: Spanish `Activos` for English `Assets`, "
            "`Cuenta de Pérdidas y Ganancias` for `Profit & Loss`)."
        )
        for h in inv_tables:
            md = getattr(h, "metadata", None) or {}
            qn = md.get("qualified_name") or "?"
            text = getattr(h, "text", "") or ""
            text = text.replace("\n", " ").strip()
            if len(text) > 160:
                text = text[:157] + "…"
            out.append(f"- `{qn}` :: {text}")
        out.append("")

    # 2. The "Top-ranked columns" section -- only column-level hits
    #    from the hybrid retriever, ranked. Helps the LLM zero in on
    #    the right columns once it has picked a table.
    schema_hits = bundle.get("schema_objects", []) or []
    column_hits = [h for h in schema_hits if (getattr(h, "metadata", {}) or {}).get("kind") != "TABLE"]
    if column_hits:
        out.append(f"# Top-ranked column matches ({len(column_hits)})")
        out.append(
            "Most relevant column-level matches for this question, ranked by "
            "BM25 + vector retrieval. Prefer these when writing the SQL. "
            "Column names that look like dates (e.g. `2024-12-31`) are "
            "legitimate XLSX column names and must be quoted."
        )
        for h in column_hits[:200]:
            md = getattr(h, "metadata", None) or {}
            qn = md.get("qualified_name") or "?"
            text = getattr(h, "text", "") or ""
            text = text.replace("\n", " ").strip()
            if len(text) > 200:
                text = text[:197] + "…"
            out.append(f"- `{qn}` :: {text}")
        out.append("")

    # 2b. The "Column value catalogue" lists EVERY column with its real
    #     values (distinct set for low-cardinality columns; numeric
    #     range otherwise). This is the ground truth the agent must copy
    #     filter/CASE literals from -- it prevents guessing wrong
    #     literals (`Year IN (2023)` when the values are `FY23`), maps a
    #     question entity to the column whose values contain it
    #     (`DAPA` lives in a column's values, not a column name), and
    #     reveals tall/EAV layouts (P&L line items are VALUES of a single
    #     column) and scaled-duplicate measures (`FY` vs `FY (Real)`).
    inv_columns = [h for h in inventory if (getattr(h, "metadata", {}) or {}).get("kind") == "COLUMN"]
    cols_with_values = [h for h in inv_columns if (getattr(h, "metadata", {}) or {}).get("values")]
    if cols_with_values:
        out.append(f"# Column value catalogue ({len(cols_with_values)} columns)")
        out.append(
            "Real values per column. When the question names an entity (a brand, "
            "year, market, category, P&L line, team…) that is NOT a column name, "
            "find the column whose values contain it and filter THAT column. Copy "
            "filter/CASE literals VERBATIM from these values (values may be encoded, "
            "e.g. a year shown as `FY23`). If several columns share members, prefer "
            "the one whose values match the question most precisely."
        )
        for h in cols_with_values:
            md = getattr(h, "metadata", None) or {}
            qn = md.get("qualified_name") or "?"
            out.append(f"- `{qn}` :: {md.get('values')}")
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
            line = f"- **{md.get('term')}**: {md.get('definition', '')}"
            related = md.get("related_metrics") or []
            if related:
                # A glossary term that maps to a published metric is a strong
                # signal to take the SEMANTIC_LAYER path using that metric.
                line += f" (related metrics: {', '.join(related)})"
            out.append(line)
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
    *,
    schema_inventory: list[Any] | None = None,
) -> str:
    """Pack the grounded context into a SQL-generation prompt.

    The ``schema_inventory`` fallback is appended even when grounding
    returned a non-empty tables list -- the inventory acts as a
    safety net the generation agent can fall back on if it judges
    the grounded set incomplete (e.g. needs a join to a table the
    grounding agent missed). Without this fallback, generation
    hallucinates plausible-but-nonexistent tables like
    ``balance_sheet`` whenever grounding under-selects.
    """

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

    inv = schema_inventory or []
    inv_tables = [h for h in inv if (getattr(h, "metadata", {}) or {}).get("kind") == "TABLE"]
    # Map qualified_name -> value fingerprint so the generator copies
    # filter/CASE literals verbatim from real values rather than guessing.
    value_index: dict[str, str] = {}
    for h in inv:
        md = getattr(h, "metadata", None) or {}
        if md.get("kind") == "COLUMN" and md.get("values"):
            value_index[md.get("qualified_name")] = md.get("values")
    if inv_tables:
        out.append(f"# Complete dataset catalogue ({len(inv_tables)} tables)")
        out.append(
            "Every table in this dataset. The SQL you generate MUST reference "
            "tables from this list only -- never invent table names like "
            "`balance_sheet`, `income_statement`, or `financials.*`."
        )
        for h in inv_tables:
            md = getattr(h, "metadata", None) or {}
            qn = md.get("qualified_name") or "?"
            text = getattr(h, "text", "") or ""
            text = text.replace("\n", " ").strip()
            if len(text) > 160:
                text = text[:157] + "…"
            out.append(f"- `{qn}` :: {text}")
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
        out.append("## Columns in scope (with real values — copy literals verbatim)")
        for c in g_columns:
            cqn = getattr(c, "column_qualified_name", c)
            vals = value_index.get(cqn)
            out.append(f"- `{cqn}`" + (f" :: {vals}" if vals else ""))
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

    # Full column-value catalogue -- the grounding agent may under-select
    # columns, so expose every column's real values here too. This is the
    # source of truth for WHERE / CASE literals.
    if value_index:
        out.append(f"# Column value catalogue ({len(value_index)} columns)")
        out.append(
            "Real values per column. Copy filter/CASE literals VERBATIM from these. "
            "If the question names an entity that is not a column name, filter the "
            "column whose values contain it."
        )
        for qn, vals in value_index.items():
            out.append(f"- `{qn}` :: {vals}")
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
        'names like `2024-12-31` must be `"2024-12-31"`).\n'
        "- Copy every WHERE / CASE / IN literal VERBATIM from the column value "
        "catalogue above -- never invent or reformat a value (a year is `FY23`, "
        "not `2023`; a market may be `Brazil` or `44000BR Brazil` -- use exactly "
        "what is listed).\n"
        "- When the metric the user names is not a column but appears among a "
        "column's listed values, filter that column (tall/EAV layout): e.g. P&L "
        "line items like `Total Revenue` / `Manpower` are VALUES of a single "
        "category column, selected with `CASE WHEN \"<col>\" = 'Total Revenue' …`.\n"
        "- When two numeric columns are near-duplicates whose ranges differ by a "
        "constant factor (~10^k), they are the same measure at different scales -- "
        "prefer the larger-magnitude one for monetary sums.\n"
        "- Do NOT add a WHERE filter on a dimension the question did not ask to "
        "slice by -- aggregate across ALL of its values, and do NOT drop a row "
        "just because a category value's name contains 'total'/'all' (those are "
        "usually legitimate, often 'unallocated', buckets). Exclude a value only "
        "if you can confirm it is literally the sum of the other rows.\n"
        "- Return what is ASKED FOR: if the question asks for names, a list, "
        "'who', 'which', or 'dame los nombres/quiénes', SELECT the identifying "
        "column(s) (e.g. the name) and return the matching ROWS -- do NOT collapse "
        "to a COUNT. Use COUNT/aggregates only when a count or total is requested. "
        "If BOTH a count and the names are asked, return the names (the count is "
        "derivable from the row count).\n"
        "- HIERARCHY questions: when the question asks about a person's TEAM, "
        "direct reports, the people 'at their charge' / under them, their org, or "
        "movements in THEIR structure, it is a self-referencing hierarchy. A "
        "column marked 'HIERARCHY: holds entities/people from column X' holds each "
        "row's manager/owner. The person's team = the ROWS where such a column "
        "equals that person (filter it with case-insensitive LIKE '%name%'), NOT "
        "the person's own row. Try EVERY hierarchy column (a person may appear in "
        "more than one), and match names tolerantly (accents/spacing).\n"
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
    schema_inventory: list[Any] | None = None,
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

    # Full dataset catalogue -- the critic's most common failure mode
    # is rewriting one hallucinated table name into another (e.g.
    # ``balance_sheet`` -> ``financials.balance_sheet`` rather than
    # picking the real ``IVI_MALAGA_SL__Activos``). Showing every real
    # table by qualified_name + column fingerprint forces the critic
    # to pick from the catalogue.
    inv = schema_inventory or []
    inv_tables = [h for h in inv if (getattr(h, "metadata", {}) or {}).get("kind") == "TABLE"]
    if inv_tables:
        out.append(f"# Complete dataset catalogue ({len(inv_tables)} tables)")
        out.append(
            "ONLY these tables exist. If the failing SQL referenced anything "
            "else, that's the bug -- pick the right one from this list. Table "
            "names may be in any language (Spanish `Activos` = Assets, "
            "`Cuenta de Pérdidas y Ganancias` = Profit & Loss)."
        )
        for h in inv_tables:
            md = getattr(h, "metadata", None) or {}
            qn = md.get("qualified_name") or "?"
            text = getattr(h, "text", "") or ""
            text = text.replace("\n", " ").strip()
            if len(text) > 160:
                text = text[:157] + "…"
            out.append(f"- `{qn}` :: {text}")
        out.append("")

    g_tables = getattr(grounded, "tables", []) or []
    g_columns = getattr(grounded, "columns", []) or []
    if g_tables or g_columns:
        out.append("# Grounded scope (preferred tables / columns)")
        for t in g_tables:
            out.append(f"- table: `{getattr(t, 'table_qualified_name', t)}`")
        for c in g_columns:
            out.append(f"- column: `{getattr(c, 'column_qualified_name', c)}`")
        out.append("")
    out.append("# Task")
    out.append(
        "Return a corrected SQL that resolves the execution error. Output a "
        "RefinedSql with a brief reasoning + a confidence in [0,1]. Pick "
        "tables ONLY from the catalogue above. Use unqualified table names "
        "(last segment only) and quote any non-identifier column names like "
        '`"2024-12-31"`.'
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
    out.append("# Result")
    out.append(f"row_count: {row_count}")
    if preview_rows:
        out.append(f"rows (first {min(len(preview_rows), 50)}):")
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
            # Fetch + bind the published metric's compiled SQL. When found, the
            # bound SQL goes straight to the AST firewall + executor — the
            # GenerationAgent is NOT invoked — and the metric version is pinned
            # into the persisted query record for reproducibility.
            metric_name = grounded.metrics[0].metric_name
            compiled, metric_version = await self._compiled_metric_sql(
                metric_name,
                dataset_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                extra_filter=getattr(grounded.metrics[0], "extra_filter", None),
            )
            if compiled:
                chosen_sql = compiled
                candidates_json = [
                    {
                        "sql": compiled,
                        "reasoning": "semantic-layer compiled",
                        "confidence": 1.0,
                        "metric_name": metric_name,
                        "metric_version": metric_version,
                    }
                ]
            else:
                # Fall through to synthesis if no compiled SQL found
                gen_prompt = _render_generation_prompt(
                    question,
                    grounded,
                    starting_point_sql,
                    schema_inventory=bundle.get("schema_inventory"),
                )
                gen_run = await self._generation_agent.run(gen_prompt)
                gen_out = getattr(gen_run, "output", gen_run)
                candidates_json = [c.model_dump() for c in gen_out.candidates]
                chosen_sql = gen_out.candidates[0].sql
        else:
            gen_prompt = _render_generation_prompt(
                question,
                grounded,
                starting_point_sql,
                schema_inventory=bundle.get("schema_inventory"),
            )
            gen_run = await self._generation_agent.run(gen_prompt)
            gen_out = getattr(gen_run, "output", gen_run)
            candidates_json = [c.model_dump() for c in gen_out.candidates]
            # Don't blindly take the highest-confidence candidate: probe them
            # (DuckDB only, no extra LLM) and prefer one that passes the firewall
            # and returns non-empty, non-degenerate rows. Empty candidate list
            # degrades to "" (FAILED) instead of raising an IndexError.
            chosen_sql = await self._select_best_candidate(
                [c.sql for c in gen_out.candidates if c.sql],
                dataset_id=dataset_id,
                scopes=scopes,
                dataset_allowlist=dataset_allowlist,
                pins=prior_snapshot_pins,
            )

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
        # Pre-execution guard: detect SQL that references a table not in
        # the dataset. ``_table_kinds_by_name`` returns ONLY matching
        # rows -- a missing table simply has no key in the dict. So
        # the bad-tables check is set-difference against
        # ``ast.table_refs``, not a None-value sweep.
        #
        # The LLM occasionally hallucinates ``balance_sheet`` /
        # ``income_statement`` / ``financials.*`` despite the prompt
        # rules; rather than waiting for DuckDB to emit a generic
        # ``Catalog Error: Table does not exist``, we synthesise a
        # sharp ExecutionError that the existing critic loop picks
        # up. The critic prompt receives the full dataset catalogue
        # so the rewrite has the real table names in scope.
        ref_set = {t for t in ast.table_refs if t}
        bad_tables = sorted(ref_set - set(table_kinds.keys()))
        if bad_tables:
            real_tables = sorted(table_kinds.keys()) + [
                (getattr(h, "metadata", {}) or {}).get("qualified_name", "").rsplit(".", 1)[-1]
                for h in (bundle.get("schema_inventory") or [])
                if (getattr(h, "metadata", {}) or {}).get("kind") == "TABLE"
            ]
            real_tables = [t for t in dict.fromkeys(real_tables) if t]
            result: ExecutionResult | ExecutionError = ExecutionError(
                message=(
                    f"Table(s) {bad_tables!r} do not exist in this dataset. "
                    f"Pick ONLY from this catalogue (and translate as needed: "
                    f"Spanish `Activos` = Assets, `Cuenta de Pérdidas y Ganancias` "
                    f"= Profit & Loss): {real_tables[:80]!r}."
                )
            )
        else:
            attached = await self._table_resolver.resolve(
                dataset_id,
                list(ast.table_refs),
                pins=prior_snapshot_pins,
            )
            result = await self._executor.execute(chosen_sql, attached)
        retries = 0

        while isinstance(result, ExecutionError) and retries < self._settings.max_refine_retries:
            critic_prompt = _render_critic_prompt(
                question=question,
                failing_sql=chosen_sql,
                error_message=result.message,
                grounded=grounded,
                schema_inventory=bundle.get("schema_inventory"),
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
            # Re-apply the unknown-table guard on the refined SQL too --
            # otherwise the critic could hallucinate a different
            # non-existent table and DuckDB would catch it generically.
            ref_set = {t for t in ast.table_refs if t}
            bad_tables = sorted(ref_set - set(table_kinds.keys()))
            if bad_tables:
                real_tables = sorted(table_kinds.keys()) + [
                    (getattr(h, "metadata", {}) or {}).get("qualified_name", "").rsplit(".", 1)[-1]
                    for h in (bundle.get("schema_inventory") or [])
                    if (getattr(h, "metadata", {}) or {}).get("kind") == "TABLE"
                ]
                real_tables = [t for t in dict.fromkeys(real_tables) if t]
                result = ExecutionError(
                    message=(
                        f"Refined SQL still references missing table(s) "
                        f"{bad_tables!r}. The dataset only contains: "
                        f"{real_tables[:80]!r}."
                    )
                )
                retries += 1
                continue
            attached = await self._table_resolver.resolve(
                dataset_id, list(ast.table_refs), pins=prior_snapshot_pins
            )
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
        # A syntactically-valid query that returns 0 rows (or a single
        # all-NULL/zero aggregate) is suspicious: the usual cause is a
        # filter literal that doesn't match how the data is encoded. Rather
        # than report it as a confident empty answer, surface a clarification
        # and downgrade confidence so the caller knows to verify.
        suspicious_empty = isinstance(result, ExecutionResult) and self._is_suspicious_empty(result)
        if clarification is None and suspicious_empty:
            from flyquery.interfaces.query import ClarificationFrame

            clarification = ClarificationFrame(
                questions=[
                    "The query executed successfully but returned no matching data "
                    "(0 rows / empty result). The filter values may not match how the "
                    "data is encoded -- please verify the exact column values (e.g. "
                    "category labels or period format) or rephrase the question."
                ],
                reasons=[],
            )
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
        if (
            execution_status == "OK"
            and isinstance(result, ExecutionResult)
            and result.row_count > 0
            and not clarification_emitted
        ):
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
        # THIS turn's snapshot pins: the snapshot each resolved table was
        # answered against. Tables already pinned by an earlier turn keep
        # their pin (prior wins); newly-referenced tables pin to current.
        # Persisting THIS turn's pins (not the prior turn's) is what makes
        # drill-down reproducible across a mid-conversation re-ingest.
        this_turn_pins: dict[str, str] = {
            **(await self._table_resolver.current_snapshots(dataset_id, list(ast.table_refs))),
            **prior_snapshot_pins,
        }

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
                snapshot_pins_json=this_turn_pins,
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
            grounded_summary=self._grounded_summary(
                grounded, confidence_cap=0.4 if suspicious_empty else None
            ),
            snapshot_pins=this_turn_pins,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_suspicious_empty(result) -> bool:
        """True when an executed result is empty/degenerate enough to doubt.

        Catches the canonical wrong-literal symptom: a valid query that
        matched nothing (0 rows), or a single-row single-column aggregate
        whose only value is NULL / 0 / 0.0 (e.g. a SUM/CASE pivot where
        every branch missed).
        """
        if result.row_count == 0:
            return True
        rows = getattr(result, "rows", None) or []
        if result.row_count == 1 and len(rows) == 1 and isinstance(rows[0], dict) and len(rows[0]) == 1:
            (only_value,) = rows[0].values()
            return only_value is None or only_value == 0
        return False

    async def _select_best_candidate(
        self,
        candidate_sqls: list[str],
        *,
        dataset_id: uuid.UUID,
        scopes: set[str],
        dataset_allowlist: set[uuid.UUID] | None,
        pins: dict[str, str],
    ) -> str:
        """Pick the candidate SQL that best answers the question.

        Generation emits N candidates ranked by self-reported confidence, but
        the top one sometimes filters on the wrong column (or under-searches a
        set of hierarchy columns) and returns 0 rows while a lower-ranked
        candidate is correct. So we probe the candidates and prefer the first
        that (a) passes the firewall, (b) executes, and (c) returns non-empty,
        non-degenerate rows. This is DuckDB-only -- NO extra LLM calls -- and
        general: it just prefers a candidate that actually returns data.

        Falls back to the first candidate that executed at all, else the first
        candidate (so the existing scope/critic handling downstream is
        unchanged when nothing is clearly better).
        """
        if len(candidate_sqls) <= 1:
            return candidate_sqls[0] if candidate_sqls else ""

        first_executed: str | None = None
        for sql in candidate_sqls:
            ast = self._ast_classifier.classify(sql)
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
                continue  # unsafe candidate -- skip
            if sorted({t for t in ast.table_refs if t} - set(table_kinds.keys())):
                continue  # references a table not in the dataset -- skip
            attached = await self._table_resolver.resolve(dataset_id, list(ast.table_refs), pins=pins)
            result = await self._executor.execute(sql, attached)
            if isinstance(result, ExecutionResult):
                if not self._is_suspicious_empty(result):
                    return sql  # passes firewall + returns real rows -- best
                if first_executed is None:
                    first_executed = sql  # remember first successful-but-empty
        return first_executed or candidate_sqls[0]

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
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        extra_filter: str | None = None,
    ) -> tuple[str | None, int | None]:
        """Fetch + bind the compiled SQL for a PUBLISHED metric.

        Returns ``(bound_sql, current_version)`` so the version can be pinned
        in the query record, or ``(None, None)`` when no usable metric is found.

        ``extra_filter`` is the per-question slice the grounding agent derived
        (e.g. ``Market = 'Brazil' AND Year = 'FY24'``) to be appended to the
        metric's WHERE via the compiler's ``{extra_filter_clause}`` slot. It is
        an LLM-supplied predicate, so it is re-run through the publish-time
        firewall before binding; an unsafe filter is dropped (the metric still
        returns its unfiltered value) rather than executed.
        """
        if self._semantic_repo is None:
            return None, None
        try:
            row = await self._semantic_repo.get_by_name(
                metric_name, dataset_id, tenant_id=tenant_id, workspace_id=workspace_id
            )
        except (AttributeError, KeyError, TypeError) as exc:  # pragma: no cover - defensive
            logger.warning("semantic metric lookup failed for %r: %s", metric_name, exc)
            return None, None
        if not row or not row.get("compiled_sql_template"):
            return None, None

        safe_filter = self._firewall_extra_filter(row["compiled_sql_template"], extra_filter)
        bound = SemanticCompiler.bind(row["compiled_sql_template"], extra_filter=safe_filter)
        return bound, row.get("current_version")

    @staticmethod
    def _firewall_extra_filter(template: str, extra_filter: str | None) -> str | None:
        """Validate an LLM-supplied metric filter via the publish-time firewall.

        Returns the filter when the bound SQL passes ``assert_safe_template``,
        else ``None`` (filter dropped). Defensive: any firewall/parse failure
        also drops the filter rather than risking an unsafe predicate.
        """
        if not extra_filter:
            return None
        try:
            from flyquery.core.services.semantic.firewall import assert_safe_template

            probe = SemanticCompiler.bind(template, extra_filter=extra_filter)
            assert_safe_template(probe)
            return extra_filter
        except Exception as exc:  # noqa: BLE001 -- any failure → drop the filter
            logger.warning("dropping unsafe semantic extra_filter %r: %s", extra_filter, exc)
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

    def _grounded_summary(self, grounded, confidence_cap: float | None = None) -> dict:
        """Convert GroundedContext to a summary dict for the response.

        ``confidence_cap`` lets the caller lower the reported confidence when
        the executed result is suspicious (e.g. 0 rows from a wrong literal),
        so a confidently-wrong empty answer is not surfaced at high confidence.
        """
        confidence = grounded.confidence
        if confidence_cap is not None:
            confidence = min(confidence, confidence_cap)
        return {
            "path": grounded.path,
            "confidence": confidence,
            "table_count": len(grounded.tables),
            "missing_info": grounded.missing_info,
        }
