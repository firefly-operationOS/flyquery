# flyquery Plan 3 — Query Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the full natural-language Text-to-SQL pipeline on top of Plans 1+2: examples + glossary + semantic-layer CRUD, the 4-agent query pipeline (`Grounding → Generation → DuckDB Executor → Critic → Explainer`) with cross-encoder reranking on by default, AST firewall + scope gating, conversation memory with drill-down context, hybrid clarification SSE frame, auto-learning (first-shot OK runs auto-propose `flyquery_examples`), direct-SQL endpoint (`workspace.allow_direct_sql=true`), derived tables (`POST /tables:derive` + INSERT/UPDATE/DELETE), and agent-tier mirrors of every query endpoint. End-to-end demo: `POST /api/v1/query` with "show me total revenue by region" against the Northwind dataset produces a SELECT, executes it via DuckDB over the materialised Parquet, returns rows + chart hint, and a follow-up turn ("now for Q2 only") correctly drills down.

**Architecture:** All 4 query agents built via the lock-step `core/agents/builder.py:build_agent` factory (auto_register=False, structured `output_type`, no tools, fresh per call). The query path is `QueryService.answer()`: retrieve hits (BM25 over `content_tsv` + pgvector over `embedding` + RRF fusion) → cross-encoder reranks top-30 → top-10 → `GroundingAgent` produces `GroundedContext` (with `missing_info` + `confidence`) → if confidence is low, SSE emits a `clarification` frame alongside the answer → semantic-layer path (`MetricFlowCompiler` deterministic SQL) OR synthesis path (`GenerationAgent` produces N candidates) → AST classifier + scope/firewall check → DuckDB executor (in-process per-request, ATTACH the workspace's Parquet snapshots for referenced tables, statement_timeout + memory_limit + row_cap+1) → `CriticAgent` reruns on execution error up to MAX_REFINE_RETRIES → `ExplainerAgent` produces NL summary + chart hint. Result preview (≤128KiB JSON) lands on `flyquery_query_results.result_preview_json`; full result Parquet uploaded via `ObjectStore` with 24h presigned URL. Conversation memory carries `executed_sql + table_qnames + snapshot_pins` so drill-down turns reason about "filter to Q2" relative to the prior SQL. Auto-learning inserts a `quality=PROPOSED` `flyquery_examples` row on first-shot OK (not used in retrieval until operator approves).

**Tech Stack:** Plans 1+2 stack + `sqlglot` (already transitively present via DuckDB; explicit dep for AST classification) + `sentence-transformers` (behind `[ml-reranker]` extra) + OpenAI/Anthropic LLM clients via `fireflyframework-agentic`'s `FireflyAgent`. Embeddings model: `text-embedding-3-small` (lock-step with canon).

---

## File structure (delta over Plans 1+2)

```
flyquery/
├── src/flyquery/
│   ├── core/
│   │   ├── agents/
│   │   │   ├── builder.py                       # already exists (lock-step)
│   │   │   ├── describe_agent.py                # Plan 2
│   │   │   ├── relation_proposer_agent.py       # Plan 2
│   │   │   ├── rename_detection_agent.py        # Plan 2
│   │   │   ├── grounding_agent.py               # NEW (Task 11)
│   │   │   ├── generation_agent.py              # NEW (Task 12)
│   │   │   ├── critic_agent.py                  # NEW (Task 13)
│   │   │   └── explainer_agent.py               # NEW (Task 14)
│   │   ├── services/
│   │   │   ├── examples/                        # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── examples_repository.py
│   │   │   │   ├── examples_service.py
│   │   │   │   └── auto_learner.py              # PROPOSED on first-shot success
│   │   │   ├── glossary/                        # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── glossary_repository.py
│   │   │   │   └── glossary_service.py
│   │   │   ├── semantic/                        # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── semantic_repository.py
│   │   │   │   ├── semantic_service.py
│   │   │   │   ├── metricflow_compiler.py       # YAML → DuckDB SQL template
│   │   │   │   └── yaml_schema.py               # validation
│   │   │   ├── retrieval/                       # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── hybrid_retriever.py          # BM25 + pgvector + RRF
│   │   │   │   ├── reranker.py                  # cross-encoder (optional)
│   │   │   │   ├── embedder.py                  # OpenAI text-embedding-3-small wrapper
│   │   │   │   └── search_index.py              # query KB tables (read-only)
│   │   │   ├── execution/                       # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ast_classifier.py            # sqlglot + DuckDB parse + classify
│   │   │   │   ├── scope_guard.py               # ENforce token scopes ∩ AST classification
│   │   │   │   ├── duckdb_executor.py           # ATTACH + run + LIMIT enforcement
│   │   │   │   └── table_resolver.py            # qualified_name → table_id → parquet path
│   │   │   ├── query/                           # NEW package (orchestrator)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── query_service.py             # answer() — Grounding → Gen → Exec → Critic → Explainer
│   │   │   │   ├── query_repository.py          # flyquery_queries writes
│   │   │   │   ├── conversation_repository.py
│   │   │   │   ├── conversation_service.py
│   │   │   │   └── result_uploader.py           # preview + full Parquet upload via ObjectStore
│   │   │   └── derived/                         # NEW package
│   │   │       ├── __init__.py
│   │   │       └── derived_table_service.py     # CREATE TABLE AS SELECT materialisation
│   ├── interfaces/
│   │   ├── examples.py                          # NEW
│   │   ├── glossary.py                          # NEW
│   │   ├── semantic.py                          # NEW
│   │   ├── query.py                             # NEW: QueryRequest, AnswerResponse, ClarificationFrame
│   │   ├── conversations.py                     # NEW
│   │   └── sql_execute.py                       # NEW
│   ├── web/
│   │   ├── controllers/
│   │   │   ├── examples_controller.py           # NEW
│   │   │   ├── glossary_controller.py           # NEW
│   │   │   ├── semantic_metrics_controller.py   # NEW
│   │   │   ├── semantic_dimensions_controller.py # NEW
│   │   │   ├── query_controller.py              # NEW: /query, /query/stream, /query:explain, /query:validate
│   │   │   ├── conversations_controller.py      # NEW
│   │   │   ├── sql_execute_controller.py        # NEW: /sql:execute, /sql:execute/stream
│   │   │   ├── tables_derive_controller.py      # NEW: POST /tables:derive
│   │   │   └── agent/                           # NEW agent-tier mirrors
│   │   │       ├── query_controller.py
│   │   │       ├── examples_controller.py
│   │   │       └── sql_execute_controller.py
└── tests/
    ├── integration/
    │   ├── test_hybrid_retrieval.py             # BM25+pgvector+RRF
    │   ├── test_reranker.py
    │   ├── test_metricflow_compiler.py
    │   ├── test_grounding_agent.py
    │   ├── test_generation_agent.py
    │   ├── test_critic_agent.py
    │   ├── test_explainer_agent.py
    │   ├── test_ast_classifier.py
    │   ├── test_scope_guard.py
    │   ├── test_duckdb_executor.py
    │   ├── test_query_pipeline.py               # end-to-end /query
    │   ├── test_query_sse.py                    # SSE event sequence
    │   ├── test_clarification_frame.py
    │   ├── test_conversation_drilldown.py
    │   ├── test_auto_learning.py
    │   ├── test_sql_execute.py
    │   ├── test_tables_derive.py
    │   ├── test_agent_tier_query.py             # X-Agent-Token gated
    │   └── test_e2e_query_demo.py               # NL → result over Northwind
    └── unit/
        ├── test_examples_service.py
        ├── test_glossary_service.py
        ├── test_metricflow_yaml_schema.py
        ├── test_metricflow_compiler_unit.py
        ├── test_table_resolver.py
        ├── test_query_service.py
        └── test_auto_learner.py
```

---

## Phase A — Foundational query infrastructure (Tasks 1-7)

### Task 1: Examples DTOs + repository + service + auto-promotion hook

**Files:**
- Create: `src/flyquery/interfaces/examples.py`
- Create: `src/flyquery/core/services/examples/{__init__,examples_repository,examples_service,auto_learner}.py`
- Test: `tests/unit/test_examples_service.py`, `tests/unit/test_auto_learner.py`

- [ ] **Step 1: Write the failing service test**

```python
# tests/unit/test_examples_service.py
import pytest, uuid
from flyquery.core.services.examples.examples_service import ExamplesService
from flyquery.interfaces.examples import ExampleCreate


class FakeRepo:
    def __init__(self): self.rows = []
    async def create(self, **f): self.rows.append(f); return {**f, "id": uuid.uuid4()}
    async def list(self, tenant_id, workspace_id, **kwargs):
        return [r for r in self.rows if r["tenant_id"] == tenant_id and r["workspace_id"] == workspace_id]
    async def approve(self, id_): self.rows[0]["quality"] = "APPROVED"; return self.rows[0]
    async def reject(self, id_): self.rows[0]["quality"] = "REJECTED"; return self.rows[0]


@pytest.mark.asyncio
async def test_create_human_example_defaults():
    svc = ExamplesService(FakeRepo(), embedder=None)
    ws = uuid.uuid4()
    ex = await svc.create("ten-a", ws, ExampleCreate(
        question="how many orders by region",
        generated_sql="SELECT region, count(*) FROM orders GROUP BY 1",
    ))
    assert ex["source"] == "USER_CURATED"
    assert ex["quality"] == "PROPOSED"


@pytest.mark.asyncio
async def test_list_returns_only_approved_for_retrieval():
    svc = ExamplesService(FakeRepo(), embedder=None)
    ws = uuid.uuid4()
    await svc.create("ten-a", ws, ExampleCreate(
        question="q1", generated_sql="SELECT 1",
    ))
    # default list = no filter
    items = await svc.list("ten-a", ws)
    assert len(items) == 1
    # filter quality=APPROVED → empty
    items = await svc.list("ten-a", ws, quality="APPROVED")
    assert len(items) == 0
```

- [ ] **Step 2: Run → FAIL**

- [ ] **Step 3: Write DTOs `interfaces/examples.py`**

```python
# src/flyquery/interfaces/examples.py
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ExampleCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    question: str = Field(min_length=1, max_length=4096)
    generated_sql: str = Field(min_length=1)
    dataset_id: uuid.UUID | None = None
    citations_json: dict = Field(default_factory=dict)


class ExampleUpdate(BaseModel):
    question: str | None = None
    generated_sql: str | None = None


class ExampleRead(BaseModel):
    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID | None
    question: str
    generated_sql: str
    normalised_sql: str
    source: Literal["USER_CURATED", "AGENT_LEARNED"]
    quality: Literal["PROPOSED", "APPROVED", "REJECTED"]
    citations_json: dict
    created_at: datetime
    created_by: str
    last_used_at: datetime | None
    usage_count: int
```

- [ ] **Step 4: Write repository `examples_repository.py`**

Async SQLAlchemy repo with `create`/`list`/`get`/`approve`/`reject` against `flyquery_examples`. SQL stays raw `sa.text` like the other repos in this codebase. The `normalised_sql` column = `sqlglot.parse_one(generated_sql).sql(normalize=True)` — lower-cased, whitespace-normalised, used for retrieval similarity.

- [ ] **Step 5: Write service `examples_service.py`**

```python
class ExamplesService:
    def __init__(self, repo, embedder):
        self._repo = repo
        self._embedder = embedder  # may be None (no API key) — embeddings stay NULL

    async def create(self, tenant_id, workspace_id, body, *, source="USER_CURATED", quality="PROPOSED", actor="user"):
        normalised = _normalise_sql(body.generated_sql)
        embedding = await self._embedder.embed(body.question) if self._embedder else None
        return await self._repo.create(
            tenant_id=tenant_id, workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            question=body.question, generated_sql=body.generated_sql,
            normalised_sql=normalised, source=source, quality=quality,
            citations_json=body.citations_json, created_by=actor,
            embedding=embedding,
        )

    async def list(self, tenant_id, workspace_id, *, quality=None, dataset_id=None, limit=50):
        return await self._repo.list(tenant_id, workspace_id, quality=quality, dataset_id=dataset_id, limit=limit)

    async def approve(self, id_):
        return await self._repo.update_quality(id_, "APPROVED")

    async def reject(self, id_):
        return await self._repo.update_quality(id_, "REJECTED")
```

- [ ] **Step 6: Write auto-learner `auto_learner.py`**

```python
# src/flyquery/core/services/examples/auto_learner.py
"""Promote first-shot OK runs to AGENT_LEARNED, quality=PROPOSED."""

from __future__ import annotations
from flyquery.interfaces.examples import ExampleCreate


class AutoLearner:
    def __init__(self, examples_service):
        self._service = examples_service

    async def maybe_propose(self, *, tenant_id, workspace_id, dataset_id,
                            question, generated_sql, retries, pii_findings, query_id) -> None:
        """Insert flyquery_examples row when criteria pass."""
        if retries > 0:
            return
        if pii_findings:
            return
        await self._service.create(
            tenant_id, workspace_id,
            ExampleCreate(
                question=question, generated_sql=generated_sql,
                dataset_id=dataset_id,
                citations_json={"query_id": str(query_id)},
            ),
            source="AGENT_LEARNED", quality="PROPOSED", actor="agent",
        )
```

- [ ] **Step 7: Run unit tests → PASS**

- [ ] **Step 8: Commit**

```bash
git add src/flyquery/interfaces/examples.py \
        src/flyquery/core/services/examples/ \
        tests/unit/test_examples_service.py tests/unit/test_auto_learner.py
git commit -m "feat: ExamplesService + auto-learner (AGENT_LEARNED, PROPOSED)"
```

---

### Task 2: Examples REST controller

**Files:**
- Create: `src/flyquery/web/controllers/examples_controller.py`
- Test: `tests/integration/test_auto_learning.py`

- [ ] **Step 1: Write failing integration test**

```python
# tests/integration/test_auto_learning.py
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_examples_crud():
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "ten-a", "X-Workspace-Id": "ex"}
        r = await c.post("/api/v1/workspaces", json={"slug": "ex", "name": "Examples"}, headers=h)
        ws = r.json()["id"]
        h["X-Workspace-Id"] = ws

        r = await c.post("/api/v1/examples",
            json={"question": "total revenue", "generated_sql": "SELECT sum(total) FROM orders"},
            headers=h)
        assert r.status_code == 201
        ex_id = r.json()["id"]
        assert r.json()["source"] == "USER_CURATED"
        assert r.json()["quality"] == "PROPOSED"

        # Approve
        r = await c.post(f"/api/v1/examples/{ex_id}:approve", headers=h)
        assert r.status_code == 200
        assert r.json()["quality"] == "APPROVED"

        # Listing with quality filter
        r = await c.get("/api/v1/examples?quality=APPROVED", headers=h)
        assert len(r.json()["items"]) == 1
```

- [ ] **Step 2-4**: Implement controller (mirror workspaces_controller pattern). Routes:
  - `POST /api/v1/examples` (creates as USER_CURATED, PROPOSED)
  - `GET /api/v1/examples?quality=&dataset_id=`
  - `POST /api/v1/examples/{id}:approve`
  - `POST /api/v1/examples/{id}:reject`

- [ ] **Step 5: Commit** `feat: /api/v1/examples CRUD + :approve/:reject`

---

### Task 3: Glossary DTOs + repo + service + controller

**Files:**
- Create: `src/flyquery/interfaces/glossary.py`
- Create: `src/flyquery/core/services/glossary/`
- Create: `src/flyquery/web/controllers/glossary_controller.py`
- Test: `tests/unit/test_glossary_service.py`, `tests/integration/test_glossary_crud.py`

Glossary terms are workspace-scoped (not dataset-scoped). Fields per spec §5 `flyquery_glossary_terms`: `term`, `definition`, `synonyms_json: list[str]`, `tags_json: list[str]`, `related_columns_json: list[str]`, `related_metrics_json: list[str]`.

Routes:
- `POST /api/v1/glossary` (UQ: workspace_id + term)
- `GET /api/v1/glossary` (paginated)
- `PUT /api/v1/glossary/{id}`
- `DELETE /api/v1/glossary/{id}`

Commit: `feat: Glossary CRUD (workspace-scoped, term unique per workspace)`

---

### Task 4: Hybrid retriever (BM25 + pgvector + RRF) over the schema KB

**Files:**
- Create: `src/flyquery/core/services/retrieval/{__init__,hybrid_retriever,embedder,search_index}.py`
- Test: `tests/integration/test_hybrid_retrieval.py`

- [ ] **Step 1: Embedder (`embedder.py`)**

```python
# src/flyquery/core/services/retrieval/embedder.py
from __future__ import annotations
import os
from typing import Protocol


class Embedder(Protocol):
    async def embed(self, text: str) -> list[float] | None: ...
    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]: ...


class OpenAiEmbedder:
    """Wraps OpenAI's text-embedding-3-small. Returns None when no API key."""
    def __init__(self, model: str = "text-embedding-3-small", dim: int = 1536):
        self._model, self._dim = model, dim
        self._client = None
        if os.environ.get("OPENAI_API_KEY"):
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI()

    async def embed(self, text: str) -> list[float] | None:
        if not self._client:
            return None
        resp = await self._client.embeddings.create(model=self._model, input=text)
        return resp.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]:
        if not self._client or not texts:
            return [None] * len(texts)
        resp = await self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in resp.data]
```

- [ ] **Step 2: Search index (`search_index.py`)**

```python
# src/flyquery/core/services/retrieval/search_index.py
"""Read-only helpers for retrieving over flyquery_schema_objects + relations + examples + glossary + semantic_metrics."""
from __future__ import annotations
import uuid
import sqlalchemy as sa
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class Hit:
    source_kind: str   # "schema_object" | "example" | "metric" | "glossary"
    id: uuid.UUID
    text: str          # rendered for the reranker
    score: float
    metadata: dict     # qualified_name, table_id, etc.


class SearchIndex:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def bm25_schema_objects(self, query: str, dataset_id: uuid.UUID, limit: int = 30) -> list[Hit]:
        rows = await self._session.execute(sa.text("""
            SELECT id, qualified_name, description, data_type, table_id,
                   ts_rank(content_tsv, plainto_tsquery('english', :q)) AS score
            FROM flyquery_schema_objects o
            JOIN flyquery_tables t ON t.id = o.table_id
            WHERE t.dataset_id = :ds AND o.is_active = true
              AND content_tsv @@ plainto_tsquery('english', :q)
            ORDER BY score DESC
            LIMIT :lim
        """), {"q": query, "ds": dataset_id, "lim": limit})
        return [
            Hit(source_kind="schema_object", id=r.id,
                text=f"{r.qualified_name}: {r.data_type}\n{r.description or ''}",
                score=float(r.score),
                metadata={"qualified_name": r.qualified_name, "table_id": r.table_id})
            for r in rows.mappings()
        ]

    async def vector_schema_objects(self, query_embedding: list[float], dataset_id: uuid.UUID, limit: int = 30) -> list[Hit]:
        # Cosine distance via pgvector
        rows = await self._session.execute(sa.text("""
            SELECT id, qualified_name, description, data_type, table_id,
                   1 - (embedding <=> :emb::vector) AS score
            FROM flyquery_schema_objects o
            JOIN flyquery_tables t ON t.id = o.table_id
            WHERE t.dataset_id = :ds AND o.is_active = true AND embedding IS NOT NULL
            ORDER BY embedding <=> :emb::vector
            LIMIT :lim
        """), {"emb": str(query_embedding), "ds": dataset_id, "lim": limit})
        return [
            Hit(source_kind="schema_object", id=r.id,
                text=f"{r.qualified_name}: {r.data_type}\n{r.description or ''}",
                score=float(r.score),
                metadata={"qualified_name": r.qualified_name, "table_id": r.table_id})
            for r in rows.mappings()
        ]

    async def approved_examples(self, query: str, query_embedding: list[float] | None, workspace_id, dataset_id=None, limit: int = 10) -> list[Hit]: ...
    async def published_metrics(self, query: str, dataset_id, limit: int = 8) -> list[Hit]: ...
    async def glossary_hits(self, query: str, workspace_id, limit: int = 8) -> list[Hit]: ...
    async def approved_relations(self, dataset_id, threshold: float = 0.85) -> list[Hit]: ...
```

- [ ] **Step 3: Hybrid retriever (`hybrid_retriever.py`)** — Reciprocal Rank Fusion across BM25 + vector results:

```python
# src/flyquery/core/services/retrieval/hybrid_retriever.py
from __future__ import annotations
from collections import defaultdict
from flyquery.core.services.retrieval.search_index import Hit, SearchIndex
from flyquery.core.services.retrieval.embedder import Embedder


def _rrf(rankings: list[list[Hit]], k: int = 60) -> list[Hit]:
    scores: dict[tuple[str, str], float] = defaultdict(float)
    by_key: dict[tuple[str, str], Hit] = {}
    for rank in rankings:
        for i, h in enumerate(rank):
            key = (h.source_kind, str(h.id))
            scores[key] += 1.0 / (k + i + 1)
            by_key[key] = h
    fused = sorted(by_key.values(), key=lambda h: scores[(h.source_kind, str(h.id))], reverse=True)
    return fused


class HybridRetriever:
    def __init__(self, index: SearchIndex, embedder: Embedder, rrf_k: int = 60):
        self._index, self._embedder, self._rrf_k = index, embedder, rrf_k

    async def retrieve(self, query: str, *, dataset_id, workspace_id,
                       top_k_schema: int = 12, top_k_examples: int = 5, top_k_metrics: int = 8) -> list[Hit]:
        bm25_schema = await self._index.bm25_schema_objects(query, dataset_id, limit=top_k_schema * 3)
        query_embedding = await self._embedder.embed(query)
        if query_embedding is not None:
            vector_schema = await self._index.vector_schema_objects(query_embedding, dataset_id, limit=top_k_schema * 3)
        else:
            vector_schema = []
        examples = await self._index.approved_examples(query, query_embedding, workspace_id, dataset_id, limit=top_k_examples * 2)
        metrics = await self._index.published_metrics(query, dataset_id, limit=top_k_metrics * 2)
        glossary = await self._index.glossary_hits(query, workspace_id, limit=8)
        relations = await self._index.approved_relations(dataset_id)

        return {
            "schema_objects": _rrf([bm25_schema, vector_schema], k=self._rrf_k)[:top_k_schema],
            "examples": examples[:top_k_examples],
            "metrics": metrics[:top_k_metrics],
            "glossary": glossary,
            "relations": relations,
        }
```

- [ ] **Step 4: Integration test** with a seeded workspace + tables; assert BM25-only branch works when no embeddings are present; assert hybrid branch works when embeddings exist.

- [ ] **Step 5: Commit** `feat: hybrid retriever (BM25 + pgvector + RRF) over schema KB`

---

### Task 5: Cross-encoder reranker

**Files:**
- Create: `src/flyquery/core/services/retrieval/reranker.py`
- Test: `tests/integration/test_reranker.py`

```python
# src/flyquery/core/services/retrieval/reranker.py
from __future__ import annotations
from typing import Protocol
from flyquery.core.services.retrieval.search_index import Hit


class Reranker(Protocol):
    async def rerank(self, query: str, hits: list[Hit], top_n: int) -> list[Hit]: ...


class NoopReranker:
    async def rerank(self, query, hits, top_n):
        return hits[:top_n]


class CrossEncoderReranker:
    def __init__(self, model_name: str):
        # Lazy-import the heavy ml-reranker extra.
        from sentence_transformers import CrossEncoder
        self._model = CrossEncoder(model_name)

    async def rerank(self, query, hits, top_n):
        if not hits:
            return []
        pairs = [(query, h.text) for h in hits]
        scores = self._model.predict(pairs)
        order = sorted(range(len(hits)), key=lambda i: float(scores[i]), reverse=True)
        return [hits[i] for i in order[:top_n]]


def build_reranker(settings):
    if not settings.reranker_model:
        return NoopReranker()
    try:
        return CrossEncoderReranker(settings.reranker_model)
    except ImportError:
        return NoopReranker()
```

Integration test: feed 10 deliberately-ordered hits + a query, assert the model reorders the most-relevant first.

Commit: `feat: cross-encoder reranker (sentence-transformers; falls back to NoopReranker)`

---

### Task 6: Semantic-layer port + YAML schema + repository

**Files:**
- Create: `src/flyquery/core/services/semantic/{__init__,semantic_repository,semantic_service,yaml_schema}.py`
- Create: `src/flyquery/interfaces/semantic.py`
- Test: `tests/unit/test_metricflow_yaml_schema.py`

YAML schema (subset of MetricFlow):

```yaml
# Example metric YAML
name: revenue_by_region
label: "Revenue by Region"
description: "Total order revenue grouped by customer region"
metric_type: SIMPLE
agg: sum
expr: orders.total
filters: []
joins:
  - from: orders.customer_id
    to: customers.customer_id
group_by:
  - customers.region
```

- [ ] **Step 1: YAML schema validator** — `validate_metric_yaml(yaml_str) -> Metric` parses + validates; raises `MetricYamlError` with line + field.

- [ ] **Step 2: Repository** — CRUD over `flyquery_semantic_metrics` + `flyquery_semantic_versions` (history tracking).

- [ ] **Step 3: Service** — create, update, publish (status=PUBLISHED), retire, list_history.

- [ ] **Step 4: Unit test** the YAML validator with valid + invalid samples.

- [ ] **Step 5: Commit** `feat: semantic-layer YAML schema + repo + service (MetricFlow shape)`

---

### Task 7: MetricFlow compiler (YAML → DuckDB SQL template)

**Files:**
- Create: `src/flyquery/core/services/semantic/metricflow_compiler.py`
- Test: `tests/integration/test_metricflow_compiler.py`, `tests/unit/test_metricflow_compiler_unit.py`

Deterministic compilation:
- `agg: sum, expr: orders.total` → `SELECT SUM(orders.total) AS revenue_by_region FROM orders`
- Add joins: `JOIN customers ON orders.customer_id = customers.customer_id`
- Add group_by: `GROUP BY customers.region`
- Add filters: `WHERE` clause

```python
# src/flyquery/core/services/semantic/metricflow_compiler.py
class MetricFlowCompiler:
    @staticmethod
    def compile(metric_yaml: dict) -> str:
        select_expr = f"{metric_yaml['agg'].upper()}({metric_yaml['expr']}) AS {metric_yaml['name']}"
        select_clause = [select_expr]
        for gb in metric_yaml.get("group_by", []):
            select_clause.insert(0, gb)
        # Determine base table from first expr
        base_table = metric_yaml["expr"].split(".")[0]
        joins = " ".join(
            f"JOIN {_table_of(j['to'])} ON {j['from']} = {j['to']}"
            for j in metric_yaml.get("joins", [])
        )
        where = " AND ".join(metric_yaml.get("filters", []))
        group_by = ", ".join(metric_yaml.get("group_by", []))
        sql = f"SELECT {', '.join(select_clause)} FROM {base_table}"
        if joins:
            sql += f" {joins}"
        if where:
            sql += f" WHERE {where}"
        if group_by:
            sql += f" GROUP BY {group_by}"
        return sql


def _table_of(qualified: str) -> str:
    return qualified.split(".")[0]
```

Persist the compiled SQL on `flyquery_semantic_metrics.compiled_sql_template` on every `publish`.

Integration test: create a metric, publish, GET, verify `compiled_sql_template` is non-empty + valid via `sqlglot.parse_one`.

Commit: `feat: MetricFlowCompiler (YAML → DuckDB SQL; persisted on publish)`

---

## Phase B — Semantic-layer endpoints (Tasks 8-10)

### Task 8: Semantic metrics REST controller

`POST /api/v1/semantic/metrics`, `GET`, `GET/{id}`, `PUT/{id}`, `POST /{id}:publish`, `POST /{id}:retire`, `GET /{id}/history`.

Commit: `feat: /api/v1/semantic/metrics CRUD + :publish + :retire + history`

---

### Task 9: Semantic dimensions REST controller

Mirror metrics but on `flyquery_semantic_dimensions`. Same operations.

Commit: `feat: /api/v1/semantic/dimensions CRUD`

---

### Task 10: Glossary integration with retrieval

Verify `SearchIndex.glossary_hits` actually returns rows + the hybrid retriever passes them to the Grounding context. Extend `test_hybrid_retrieval.py` to seed a glossary term + assert it appears in the retrieved bundle.

Commit: `test: hybrid retrieval includes glossary terms`

---

## Phase C — Query pipeline agents (Tasks 11-15)

### Task 11: GroundingAgent

**File:** `src/flyquery/core/agents/grounding_agent.py`

```python
# src/flyquery/core/agents/grounding_agent.py
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from flyquery.core.agents.builder import build_agent


class GroundedTable(BaseModel):
    table_qualified_name: str
    relevance: float = Field(ge=0, le=1)


class GroundedColumn(BaseModel):
    column_qualified_name: str
    relevance: float = Field(ge=0, le=1)


class GroundedJoin(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship: Literal["inner", "left", "right", "outer"] = "inner"


class GroundedMetric(BaseModel):
    metric_name: str
    relevance: float = Field(ge=0, le=1)


class GroundedContext(BaseModel):
    path: Literal["SEMANTIC_LAYER", "SYNTHESIS", "HYBRID"]
    tables: list[GroundedTable]
    columns: list[GroundedColumn]
    joins: list[GroundedJoin] = Field(default_factory=list)
    metrics: list[GroundedMetric] = Field(default_factory=list)
    examples_used: list[str] = Field(default_factory=list)
    glossary_terms: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    missing_info: list[str] | None = None
    starting_point_sql: str | None = None   # from prior turn drill-down


_INSTRUCTIONS = """
You are a SQL grounding agent. You receive a natural-language question
plus retrieved schema metadata (tables, columns, samples, descriptions,
relations, examples, semantic metrics, glossary).

Your job: pick the MINIMAL set of tables + columns + joins to answer
the question. Output a GroundedContext with:
- path: SEMANTIC_LAYER if a published metric covers the question,
  SYNTHESIS otherwise (HYBRID if both contribute)
- tables, columns, joins (with reasoning)
- confidence ∈ [0, 1]
- missing_info: list of ambiguities the user should resolve, ONLY when
  confidence is below 0.55 — otherwise leave None

If the user is in a conversation and the prior turn provided a
starting_point_sql, treat it as the base SELECT and identify only
which deltas the new question requires.

Never invent tables or columns. Use only what's in the retrieved
metadata.
"""


def build_grounding_agent(settings):
    return build_agent(
        name="flyquery-grounding",
        model=settings.grounding_model,
        output_type=GroundedContext,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
```

Integration test: feed a fake retrieved bundle + question, assert agent returns a GroundedContext with `path` set + at least one table. Skip when no API key.

Commit: `feat: GroundingAgent (GroundedContext output_type)`

---

### Task 12: GenerationAgent

```python
# src/flyquery/core/agents/generation_agent.py
class GeneratedCandidate(BaseModel):
    sql: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)

class GeneratedCandidates(BaseModel):
    candidates: list[GeneratedCandidate]   # always N items


_INSTRUCTIONS = """
You are a SQL generation agent. You receive a GroundedContext
(tables, columns, joins, metrics) plus the NL question.

Generate exactly N candidate SQL queries against DuckDB, ordered by
confidence (highest first). Each candidate must:
- Use only the tables and columns from the grounded context
- Use the joins specified
- Be a SINGLE statement (no multi-statement; no DDL)
- Be a SELECT against ingested tables (no DML on UPLOADED tables)
- Prefer semantic-layer metrics over re-derived aggregations

Trust order: SEMANTIC_LAYER > UPLOADED_TABLE.

If the GroundedContext provides a starting_point_sql, your candidates
should be deltas (added WHERE clause, swapped column, etc.) — do not
rewrite from scratch unless necessary.

Output exactly the GeneratedCandidates structure.
"""
```

Commit: `feat: GenerationAgent (N candidates, single-statement, trust ordering)`

---

### Task 13: CriticAgent

```python
class RefinedSql(BaseModel):
    sql: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)


_INSTRUCTIONS = """
You are a SQL critic. You receive a candidate SQL that FAILED execution
(DuckDB error + error message) AND the GroundedContext.

Produce a corrected SQL. Common errors to fix:
- Misnamed columns/tables (the grounded context is authoritative)
- Wrong join conditions
- Missing GROUP BY
- Type-coercion issues (e.g. comparing TEXT to INTEGER)
- Aggregation in WHERE (move to HAVING)

Stay within the grounded context's table+column set. Do not introduce
new tables or columns.
"""
```

Commit: `feat: CriticAgent (RefinedSql; consumes execution error + grounded context)`

---

### Task 14: ExplainerAgent

```python
class ResultExplanation(BaseModel):
    summary: str            # 1-3 sentence NL answer
    chart_hint: Literal["line", "bar", "table", "pie", "none"]


_INSTRUCTIONS = """
You are a result explainer. You receive: the original question, the
executed SQL, the row count, and up to 50 rows of the result preview.

Output:
- summary: a 1-3 sentence direct answer to the question using the
  data (e.g. "Total revenue across all regions is $12,345. The
  Northeast region accounted for 42%.")
- chart_hint: pick the visualisation that best fits the result shape.
  - 1 row × 1 col → "none"
  - many rows × 2 cols (1 categorical + 1 numeric) → "bar" or "pie"
  - many rows × 2 cols (1 temporal + 1 numeric) → "line"
  - otherwise → "table"

Never invent numbers. Cite only what's in the result preview.
"""
```

Commit: `feat: ExplainerAgent (NL summary + chart hint)`

---

### Task 15: AST classifier + scope/firewall checker

**File:** `src/flyquery/core/services/execution/ast_classifier.py`

```python
# src/flyquery/core/services/execution/ast_classifier.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import sqlglot


@dataclass(frozen=True)
class AstClassification:
    classification: Literal["SELECT", "INSERT", "UPDATE", "DELETE", "DDL", "UNKNOWN"]
    single_statement: bool
    table_refs: tuple[str, ...]    # unqualified table names
    column_refs: tuple[str, ...]
    has_subquery: bool


class AstClassifier:
    def classify(self, sql: str) -> AstClassification:
        try:
            statements = sqlglot.parse(sql, read="duckdb")
        except Exception:
            return AstClassification(classification="UNKNOWN", single_statement=False, table_refs=(), column_refs=(), has_subquery=False)
        if not statements:
            return AstClassification(classification="UNKNOWN", single_statement=False, table_refs=(), column_refs=(), has_subquery=False)
        single = len(statements) == 1
        stmt = statements[0]
        kind = self._kind(stmt)
        tables = tuple(sorted({t.name for t in stmt.find_all(sqlglot.exp.Table)}))
        columns = tuple(sorted({c.name for c in stmt.find_all(sqlglot.exp.Column)}))
        return AstClassification(
            classification=kind, single_statement=single,
            table_refs=tables, column_refs=columns,
            has_subquery=any(stmt.find_all(sqlglot.exp.Subquery)),
        )

    @staticmethod
    def _kind(stmt):
        if isinstance(stmt, sqlglot.exp.Select):
            return "SELECT"
        if isinstance(stmt, sqlglot.exp.Insert):
            return "INSERT"
        if isinstance(stmt, sqlglot.exp.Update):
            return "UPDATE"
        if isinstance(stmt, sqlglot.exp.Delete):
            return "DELETE"
        if isinstance(stmt, (sqlglot.exp.Create, sqlglot.exp.Drop, sqlglot.exp.Alter)):
            return "DDL"
        return "UNKNOWN"
```

**File:** `src/flyquery/core/services/execution/scope_guard.py`

```python
# src/flyquery/core/services/execution/scope_guard.py
from __future__ import annotations
from flyquery.core.services.execution.ast_classifier import AstClassification


class ScopeGuardError(PermissionError):
    pass


class ScopeGuard:
    """Enforce: (scopes ∩ AST classification ∩ table.kind ∩ dataset allowlist)."""

    def check(self, *, classification: AstClassification, scopes: set[str],
              table_kinds_by_name: dict[str, str], dataset_allowlist: set[str] | None,
              dataset_of_table: dict[str, str]) -> None:
        # Single-statement only
        if not classification.single_statement:
            raise ScopeGuardError("multi-statement SQL not allowed")
        # DDL never allowed via /query (we own the engine)
        if classification.classification == "DDL":
            raise ScopeGuardError("DDL not allowed via /query")
        # Writes on UPLOADED tables forbidden
        if classification.classification in ("INSERT", "UPDATE", "DELETE"):
            for tbl in classification.table_refs:
                kind = table_kinds_by_name.get(tbl)
                if kind == "UPLOADED":
                    raise ScopeGuardError(f"DML on UPLOADED table {tbl!r} not allowed (use re-upload)")
                if kind != "DERIVED":
                    raise ScopeGuardError(f"DML on unknown table {tbl!r}")
            if "flyquery.derived:write" not in scopes:
                raise ScopeGuardError("missing flyquery.derived:write scope")
        else:
            # SELECT: just check scope
            if not (scopes & {"flyquery.query:read", "flyquery.sql:execute", "*"}):
                raise ScopeGuardError("missing flyquery.query:read scope")
        # Dataset allowlist
        if dataset_allowlist is not None:
            for tbl in classification.table_refs:
                ds = dataset_of_table.get(tbl)
                if ds and ds not in dataset_allowlist:
                    raise ScopeGuardError(f"table {tbl!r} (dataset {ds!r}) not in allowlist")
```

Unit + integration tests for classifier + guard. Test cases: SELECT (allowed), INSERT on UPLOADED (denied), DDL (denied), multi-statement (denied), out-of-allowlist (denied).

Commit: `feat: AST classifier + scope guard (sqlglot + table-kind enforcement)`

---

## Phase D — Query pipeline execution (Tasks 16-20)

### Task 16: DuckDB executor

**File:** `src/flyquery/core/services/execution/duckdb_executor.py`

```python
# src/flyquery/core/services/execution/duckdb_executor.py
from __future__ import annotations
import asyncio
import duckdb
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    rows: list[dict]
    columns: list[str]
    row_count: int
    truncated: bool


@dataclass(frozen=True)
class ExecutionError:
    message: str
    sql_state: str | None = None


class DuckDBExecutor:
    def __init__(self, settings):
        self._memory_limit = settings.duckdb_memory_limit
        self._statement_timeout_ms = settings.default_statement_timeout_ms
        self._row_cap = settings.default_row_cap

    async def execute(self, sql: str, attached_tables: dict[str, str]) -> ExecutionResult | ExecutionError:
        return await asyncio.to_thread(self._sync, sql, attached_tables)

    def _sync(self, sql: str, attached_tables: dict[str, str]):
        conn = duckdb.connect(":memory:")
        try:
            conn.execute(f"SET memory_limit='{self._memory_limit}'")
            conn.execute(f"SET threads=2")
            # ATTACH each parquet under its unqualified table name.
            for name, parquet_path in attached_tables.items():
                conn.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{parquet_path}')")
            # Run with LIMIT row_cap+1 to detect overflow.
            wrapped = f"SELECT * FROM ({sql.rstrip(';')}) AS q LIMIT {self._row_cap + 1}"
            cursor = conn.execute(wrapped)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            truncated = len(rows) > self._row_cap
            if truncated:
                rows = rows[:self._row_cap]
            return ExecutionResult(
                rows=[dict(zip(cols, r)) for r in rows],
                columns=cols,
                row_count=len(rows),
                truncated=truncated,
            )
        except Exception as exc:
            return ExecutionError(message=str(exc))
        finally:
            conn.close()
```

**File:** `src/flyquery/core/services/execution/table_resolver.py`

Translates AST `table_refs` (unqualified names like "orders") to (table_id, parquet_object_key) for the current snapshot. Used to build the ATTACH map.

```python
class TableResolver:
    def __init__(self, session):
        self._session = session

    async def resolve(self, dataset_id, table_names: list[str], object_store_base: str) -> dict[str, str]:
        rows = await self._session.execute(sa.text("""
            SELECT t.name, ss.parquet_object_key
            FROM flyquery_tables t
            JOIN flyquery_schema_snapshots ss ON ss.id = t.current_snapshot_id
            WHERE t.dataset_id = :ds AND t.name = ANY(:names) AND t.is_active = true
        """), {"ds": dataset_id, "names": table_names})
        return {r.name: f"{object_store_base}/{r.parquet_object_key}" for r in rows.mappings()}
```

Commit: `feat: DuckDBExecutor (ATTACH parquet, memory_limit, row_cap+1 overflow detect)`

---

### Task 17: QueryService orchestrator

**File:** `src/flyquery/core/services/query/query_service.py`

Pulls the whole pipeline together:

```python
class QueryService:
    def __init__(self, retriever, reranker, embedder,
                 grounding_agent, generation_agent, critic_agent, explainer_agent,
                 ast_classifier, scope_guard, table_resolver, executor,
                 query_repo, settings, object_store, result_uploader, auto_learner):
        ...

    async def answer(self, *, tenant_id, workspace_id, dataset_id,
                     question, scopes, dataset_allowlist=None, conversation_id=None) -> AnswerResult:
        # 1. Retrieve hits over schema KB
        bundle = await self._retriever.retrieve(question, dataset_id=dataset_id, workspace_id=workspace_id)
        reranked = await self._reranker.rerank(question, bundle["schema_objects"], top_n=self._settings.top_k_schema)
        bundle["schema_objects"] = reranked

        # 2. Conversation memory (drill-down)
        starting_point_sql, prior_table_qnames, prior_snapshot_pins = await self._load_drilldown(conversation_id)

        # 3. Ground
        grounded = await self._grounding_agent.run({"question": question, "bundle": bundle,
                                                     "starting_point_sql": starting_point_sql})

        # 4. Generate (semantic-layer fast path OR synthesis)
        if grounded.path == "SEMANTIC_LAYER" and grounded.metrics:
            candidates = [await self._metric_to_candidate(grounded.metrics[0])]
        else:
            gen_out = await self._generation_agent.run({"grounded": grounded, "question": question,
                                                         "starting_point_sql": starting_point_sql})
            candidates = gen_out.candidates

        chosen = candidates[0]

        # 5. AST classify + scope guard
        ast = self._ast_classifier.classify(chosen.sql)
        table_kinds = await self._table_kinds(ast.table_refs, dataset_id)
        dataset_of_table = await self._dataset_of_tables(ast.table_refs, dataset_id)
        self._scope_guard.check(classification=ast, scopes=scopes, table_kinds_by_name=table_kinds,
                                dataset_allowlist=dataset_allowlist, dataset_of_table=dataset_of_table)

        # 6. Execute (with critic loop)
        attached = await self._table_resolver.resolve(dataset_id, list(ast.table_refs), self._settings.object_store_base)
        result = await self._executor.execute(chosen.sql, attached)
        retries = 0
        while isinstance(result, ExecutionError) and retries < self._settings.max_refine_retries:
            refined = await self._critic_agent.run({
                "sql": chosen.sql, "error": result.message,
                "grounded": grounded, "question": question,
            })
            ast = self._ast_classifier.classify(refined.sql)
            self._scope_guard.check(...)
            attached = await self._table_resolver.resolve(...)
            result = await self._executor.execute(refined.sql, attached)
            chosen = refined
            retries += 1
        execution_status = "OK" if isinstance(result, ExecutionResult) and retries == 0 else \
                           "REFINED_OK" if isinstance(result, ExecutionResult) else "FAILED"

        # 7. Explain
        explanation = await self._explainer_agent.run({...}) if isinstance(result, ExecutionResult) else None

        # 8. Persist + upload + auto-learn
        query_id = await self._query_repo.create_query(...)
        if isinstance(result, ExecutionResult):
            await self._result_uploader.upload(query_id, result)
            if execution_status == "OK" and not pii_findings:
                await self._auto_learner.maybe_propose(...)

        return AnswerResult(
            query_id=query_id,
            sql=chosen.sql,
            execution_status=execution_status,
            preview=result.rows[:10] if isinstance(result, ExecutionResult) else None,
            row_count=result.row_count if isinstance(result, ExecutionResult) else None,
            elapsed_ms=...,
            grounded_summary=...,
            clarification=ClarificationFrame(...) if grounded.confidence < settings.grounding_min_confidence and grounded.missing_info else None,
            chart_hint=explanation.chart_hint if explanation else None,
            explanation=explanation.summary if explanation else None,
        )
```

Unit test `test_query_service.py` with mocked agents. Integration test only when API keys are set (mark `@pytest.mark.llm`).

Commit: `feat: QueryService orchestrator (Grounding → Gen → AST → Exec → Critic → Explainer)`

---

### Task 18: Query result uploader

**File:** `src/flyquery/core/services/query/result_uploader.py`

```python
class ResultUploader:
    def __init__(self, object_store, query_repo, settings):
        ...

    async def upload(self, query_id, result):
        preview = result.rows[:self._preview_row_count_limit]
        preview_json = json.dumps(preview)[:self._settings.result_preview_max_bytes]
        # Full Parquet upload via pyarrow + ObjectStore.put
        table = pa.Table.from_pylist(result.rows)
        buf = io.BytesIO()
        pq.write_table(table, buf, compression="snappy")
        key = f"flyquery/{tenant}/{workspace}/{dataset}/results/{query_id}.parquet"
        await self._object_store.put(key, buf.getvalue(), content_type="application/x-parquet")
        await self._query_repo.update_result(query_id, preview_json=preview, result_object_key=key, byte_size=len(buf.getvalue()))
```

Commit: `feat: query result uploader (preview JSON + full Parquet via ObjectStore)`

---

### Task 19: POST /api/v1/query + /query:explain + /query:validate

**File:** `src/flyquery/web/controllers/query_controller.py`

Routes:
- `POST /api/v1/query` — sync, drains the SSE pipeline internally
- `POST /api/v1/query:explain` — runs Grounding + Generation but stops before AST/exec; returns generated SQL
- `POST /api/v1/query:validate` — Grounding + Generation + AST + scope-check; returns AstClassification + scope errors

Integration tests gated by `@pytest.mark.llm` when no API keys.

Commit: `feat: POST /api/v1/query + :explain + :validate (sync user-tier)`

---

### Task 20: POST /api/v1/query/stream (SSE)

Server-sent events emitting `schema_linked → sql_generated → executed → explained → final` (+ optional `clarification` frame when grounding confidence is low + `missing_info` non-empty).

```python
@request_mapping(method="POST", path="/query/stream")
async def stream(self, body: Valid[Body[QueryRequest]]) -> StreamingResponse:
    return StreamingResponse(self._stream_events(body), media_type="text/event-stream")

async def _stream_events(self, body):
    async def gen():
        # Yield each stage as it completes
        bundle = await self._retriever.retrieve(...)
        yield self._sse("schema_linked", {...})
        ...
        if grounded.confidence < threshold and grounded.missing_info:
            yield self._sse("clarification", {"questions": grounded.missing_info, "reasons": [...]})
        ...
        yield self._sse("final", answer_response.model_dump())
    return gen()

@staticmethod
def _sse(event, payload):
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"
```

Commit: `feat: POST /api/v1/query/stream SSE (schema_linked → sql_generated → executed → explained → final + clarification)`

---

## Phase E — Conversation memory + drill-down + auto-learning (Tasks 21-23)

### Task 21: Conversation repository + service

CRUD over `flyquery_conversations` + `flyquery_conversation_turns` (existing tables from Plan 1 migration 0004).

Routes:
- `POST /api/v1/conversations` (creates a conversation)
- `GET /api/v1/conversations` (list)
- `GET /api/v1/conversations/{id}` (with turns)
- `POST /api/v1/conversations/{id}/turn` (asks the next NL question; carries drill-down context automatically)

Commit: `feat: Conversation + ConversationTurn CRUD`

---

### Task 22: Drill-down context wiring

The `POST /conversations/{id}/turn` controller calls `QueryService.answer(..., conversation_id=id)`. The service:
1. Loads the prior turn's `executed_sql + table_qnames + snapshot_pins`
2. Passes `starting_point_sql` into both Grounding and Generation agents
3. Persists the new turn

Integration test `test_conversation_drilldown.py`:
1. Upload Northwind
2. Create conversation
3. POST turn 1: "show me total revenue by region" → SELECT region, sum(total) → returns rows
4. POST turn 2: "now for Q2 only" → the new SQL adds `WHERE ordered_at >= '2026-04-01' AND ordered_at < '2026-07-01'`
5. Assert turn 2's `executed_sql` contains the WHERE clause + maintains the GROUP BY from turn 1

(LLM-gated test — mark `@pytest.mark.llm`.)

Commit: `feat: drill-down conversation context (prior SQL + table_qnames + snapshot_pins)`

---

### Task 23: Auto-learning hook

Wire `AutoLearner` into `QueryService.answer()`: after a successful run with `retries=0` AND no PII findings AND `clarification` not emitted, insert a `flyquery_examples` row (source=AGENT_LEARNED, quality=PROPOSED, embedding=computed).

Integration test (no LLM needed): mock the QueryService to short-circuit a "successful run" and assert an examples row landed with the right fields.

Commit: `feat: auto-learning hook (PROPOSED examples on first-shot success + no PII)`

---

## Phase F — Direct SQL + derived tables + agent-tier mirrors (Tasks 24-27)

### Task 24: POST /api/v1/sql:execute (direct SQL behind workspace flag)

**File:** `src/flyquery/web/controllers/sql_execute_controller.py`

Skip the agent pipeline; go straight to AST classifier + scope guard + executor. Workspace must have `allow_direct_sql=true`.

```python
@request_mapping(method="POST", path="/sql:execute")
async def execute(self, body: Valid[Body[SqlExecuteRequest]]) -> SqlExecuteResponse:
    workspace = await self._workspaces.get(workspace_id)
    if not workspace["allow_direct_sql"]:
        raise PermissionError("workspace.allow_direct_sql=false")
    ast = self._ast_classifier.classify(body.sql)
    self._scope_guard.check(...)
    attached = await self._table_resolver.resolve(body.dataset_id, list(ast.table_refs), ...)
    result = await self._executor.execute(body.sql, attached)
    # Same preview + Parquet upload pattern as /query
    ...
```

`POST /sql:execute/stream` mirrors `/query/stream` shape but with simpler event sequence (`ast_classified → executed → final`).

Integration test: enable flag, post SELECT, assert 200 + result. Without flag → 403.

Commit: `feat: POST /sql:execute + /sql:execute/stream (gated by workspace.allow_direct_sql)`

---

### Task 25: POST /api/v1/tables:derive

**File:** `src/flyquery/web/controllers/tables_derive_controller.py` + `src/flyquery/core/services/derived/derived_table_service.py`

Body: `{dataset_id, name, sql}` — runs the SELECT via DuckDB; if successful, writes the result as a new Parquet under `flyquery/{tenant}/{ws}/{ds}/derived/{derived_table_id}/v1.parquet`; inserts `flyquery_tables` row (kind=DERIVED, source_file_id=NULL, current_snapshot_id=new), `flyquery_schema_snapshots` row (READY), `flyquery_schema_objects` rows for table + columns. Returns the new table_id.

Integration test: derive `revenue_by_region` from `orders + customers` join. Verify GET /api/v1/datasets/{id}/tables shows the new DERIVED table.

Commit: `feat: POST /tables:derive (CREATE TABLE FROM QUERY; new DERIVED table_id + snapshot)`

---

### Task 26: INSERT/UPDATE/DELETE on derived tables

The scope guard from Task 15 already permits DML on DERIVED tables when the token has `flyquery.derived:write`. The executor needs to handle these as actual mutations: open a DuckDB connection in read-write mode for the derived table's Parquet (DuckDB doesn't mutate Parquet in place; we need to rewrite the file).

For v0: DML on derived tables = read existing Parquet → apply mutation in DuckDB → write new Parquet → bump `current_snapshot_id`. This is essentially an atomic snapshot-style mutation. Document this in `docs/`.

Integration test: derive a table, INSERT 3 rows via `/sql:execute`, SELECT * — confirm 3 new rows visible.

Commit: `feat: DML on DERIVED tables (read-modify-write Parquet + snapshot bump)`

---

### Task 27: Agent-tier mirrors

Create agent-tier controllers under `src/flyquery/web/controllers/agent/` for:
- `query_controller.py` → `/api/v1/agent/query`, `/agent/query/stream`, `/agent/query:explain`, `/agent/query:validate` (scope: `flyquery.query:read`)
- `sql_execute_controller.py` → `/agent/sql:execute`, `/agent/sql:execute/stream` (scope: `flyquery.sql:execute` + workspace flag)
- `examples_controller.py` → POST `/agent/examples` (scope: `flyquery.examples:author`), GET `/agent/examples` (scope: `flyquery.examples:read`)

Each controller delegates to the same service as the user-tier counterpart but uses `require_agent_token(scopes=[...])` for auth (Plan 1's lock-step pattern).

Integration test: mint a token with `flyquery.query:read`, POST to `/api/v1/agent/query`, assert 200; without scope, assert 403.

Commit: `feat: agent-tier mirrors (/agent/query/*, /agent/sql:execute, /agent/examples)`

---

## Phase G — End-to-end query demo (Task 28)

### Task 28: e2e demo + QUICKSTART update

**File:** `tests/integration/test_e2e_query_demo.py`

The crowning integration test. Builds on the Plan 2 Northwind demo:

```python
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.llm  # requires Anthropic + OpenAI API keys
async def test_query_pipeline_over_northwind():
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # ... upload the 4 Northwind fixtures (orders.csv, customers.csv, products.xlsx, nested_inventory.json)
        # ... run async DESCRIBE_PASS + RELATION_PASS jobs to populate descriptions + relations
        # ... approve at least one heuristic customer_id↔customer_id relation

        # ASK
        r = await c.post("/api/v1/query", json={
            "dataset_id": ds_id,
            "question": "what is total revenue by region?",
        }, headers=h)
        assert r.status_code == 200
        body = r.json()
        assert body["execution_status"] in ("OK", "REFINED_OK")
        assert "region" in body["sql"].lower()
        assert body["row_count"] > 0

        # DRILL-DOWN
        r = await c.post("/api/v1/conversations", json={}, headers=h)
        conv_id = r.json()["id"]
        # Turn 1
        r = await c.post(f"/api/v1/conversations/{conv_id}/turn",
            json={"dataset_id": ds_id, "question": "show me total revenue by region"}, headers=h)
        sql1 = r.json()["sql"]
        # Turn 2 (drill-down)
        r = await c.post(f"/api/v1/conversations/{conv_id}/turn",
            json={"dataset_id": ds_id, "question": "now for orders in May 2026 only"}, headers=h)
        sql2 = r.json()["sql"]
        assert "2026" in sql2 or "may" in sql2.lower()
        # The 2nd SQL builds on the 1st (still groups by region)
        assert "region" in sql2.lower() and "group by" in sql2.lower()

        # SSE on /query/stream
        async with c.stream("POST", "/api/v1/query/stream",
            json={"dataset_id": ds_id, "question": "how many products per category?"},
            headers=h) as resp:
            events = []
            async for line in resp.aiter_lines():
                if line.startswith("event:"):
                    events.append(line.split(": ", 1)[1])
                    if "final" in events: break
        assert events[0] == "schema_linked"
        assert "sql_generated" in events
        assert "executed" in events
        assert "explained" in events
        assert events[-1] == "final"
```

Also runs without the `llm` mark in a `light` mode — mocking the agents to canned responses — to verify the wiring without API keys.

Then update `QUICKSTART.md` with a "Asking questions" section showing the curl recipes.

Commit: `test: e2e query pipeline over Northwind (NL → SELECT → result + drill-down + SSE)` + `docs: QUICKSTART asking-questions section`

---

## Spec coverage self-check

| Spec §15 step | Plan 3 task(s) |
|---|---|
| 16. Examples + glossary CRUD + AGENT_LEARNED auto-promotion | 1, 2, 3, 10, 23 |
| 17. Semantic layer (MetricFlow YAML, compiler) | 6, 7, 8, 9 |
| 18. Multi-agent query pipeline | 11, 12, 13, 14, 15, 16, 17, 18 |
| 19. Clarification + drill-down conversation | 20, 21, 22 |
| 20. SSE on /query/* + agent-tier | 19, 20, 27 |
| 21. /sql:execute behind workspace flag | 24 |
| 22. /tables:derive + DML on derived | 25, 26 |

Every spec step is covered. Task 28 is the demoable cut.

## After Plan 3

Plan 4 (`2026-05-22-flyquery-04-packaging.md`) builds the Python + Java SDKs from the OpenAPI spec, writes the full `docs/` set (architecture, api-reference, ingestion, file-formats, semantic-layer, security, deployment, payload-reference), and lands the canon-matching CI workflows. Plan 4 is the smallest plan (~10 tasks).
