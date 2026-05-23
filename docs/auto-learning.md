# flyquery — Auto-Learning

## Table of Contents

1. [Overview](#1-overview)
2. [The PROPOSED → APPROVED example cycle](#2-the-proposed--approved-example-cycle)
3. [When auto-learner fires](#3-when-auto-learner-fires)
4. [What auto-learner skips](#4-what-auto-learner-skips)
5. [Operator approval flow](#5-operator-approval-flow)
6. [How APPROVED examples enter retrieval](#6-how-approved-examples-enter-retrieval)
7. [Example data model](#7-example-data-model)
8. [Tuning and configuration](#8-tuning-and-configuration)
9. [v1+ roadmap](#9-v1-roadmap)

---

## 1. Overview

flyquery implements a Vanna-style few-shot retrieval system. The
`flyquery_examples` table stores `(question, SQL)` pairs that the
GroundingAgent uses during hybrid retrieval to anchor SQL generation to
previously successful patterns.

Examples can come from two sources:

| Source | Quality | Enters retrieval? |
|--------|---------|-----------------|
| `USER_CURATED` | Always `APPROVED` | Immediately |
| `AGENT_LEARNED` | `PROPOSED` (pending approval) | Only after operator approves |

The auto-learning mechanism automatically inserts `AGENT_LEARNED / PROPOSED`
examples from successful query runs. This builds a workspace-specific library
of `(question, SQL)` pairs over time without manual curation overhead.

---

## 2. The PROPOSED → APPROVED example cycle

```
Query executes successfully (no retries, no PII, no clarification)
        │
        ▼
Auto-learner inserts flyquery_examples:
  source = AGENT_LEARNED
  quality = PROPOSED
  embedding = <vector(1536) of question>
  citation = {executed_query_id: "<query_id>"}
  NOT in retrieval pool yet

        │ (asynchronously, via operator review)
        ▼
Operator sees PROPOSED examples:
  GET /api/v1/examples?source=AGENT_LEARNED&quality=PROPOSED

        │
        ├── POST /examples/{id}:approve
        │         │
        │         ▼
        │   quality = APPROVED
        │   → enters retrieval pool
        │   → used in future GroundingAgent context
        │
        └── POST /examples/{id}:reject
                  │
                  ▼
            quality = REJECTED
            → never used again
            (retained for audit)
```

PROPOSED examples remain invisible to the retrieval pipeline. They only affect
future queries after explicit operator approval.

---

## 3. When auto-learner fires

The auto-learner fires at the end of `QueryService.answer()` when ALL of the
following conditions are true:

| Condition | Check |
|-----------|-------|
| Execution succeeded | `execution_status == OK` |
| No retries | `retries == 0` |
| No PII findings | `len(pii_findings_json) == 0` |
| No clarification emitted | `clarification_emitted == False` |
| No existing example for this (question, normalised_sql) pair | Dedup check on `normalised_sql` |

The dedup check prevents the same canonical SQL from flooding the example
store if users ask the same question repeatedly with minor phrasing variations.

Normalised SQL is the output of `sqlglot.parse_one(sql).sql(dialect="duckdb")`
— a canonical representation that strips whitespace differences and
consistent alias variations.

---

## 4. What auto-learner skips

### Retries > 0

SQL that required the CriticAgent to repair it may have been fragile; adding
it as a future few-shot example risks reinforcing the wrong pattern. Only
first-shot successes are auto-learned.

### PII findings

Queries that touched PII columns (as recorded in `pii_findings_json`) are not
auto-learned. The example store is accessible to the retrieval pipeline, which
runs in a broader scope than the originating query; PII-laden SQL should not
propagate.

### Clarification emitted

A clarification frame means the GroundingAgent was uncertain about the schema.
The resulting SQL may be a best-guess with unknown correctness. Not suitable
as a future anchor.

### Conversation drill-down turns

Turns with `starting_point_sql` (drill-down in a conversation) are NOT
auto-learned. The generated SQL depends on the prior turn's context; stripped
of that context, the SQL would produce wrong results for the same question
asked standalone.

### Rejected or failed executions

`execution_status=FAILED` and `execution_status=REJECTED_BY_FIREWALL` are
never auto-learned.

---

## 5. Operator approval flow

### Listing PROPOSED examples

```
GET /api/v1/examples?source=AGENT_LEARNED&quality=PROPOSED
→ [{
    "example_id": "ex_01",
    "question": "Total revenue by region",
    "generated_sql": "SELECT region, SUM(amount) ...",
    "normalised_sql": "SELECT region, SUM(amount) ...",
    "citations": {"executed_query_id": "q_01"},
    "created_at": "2026-05-23T10:00:00Z",
    "dataset_id": "ds_01",
    "usage_count": 0
  }, ...]
```

### Approving

```
POST /api/v1/examples/{id}:approve
→ {"example_id": "ex_01", "quality": "APPROVED"}
```

After approval, the example's embedding is indexed in pgvector and becomes
available for the next query run.

### Rejecting

```
POST /api/v1/examples/{id}:reject
→ {"example_id": "ex_01", "quality": "REJECTED"}
```

Rejected examples are retained in the database for audit but are excluded from
all future retrieval.

### Agent-tier

```
POST /api/v1/agent/examples/{id}:approve   scope: flyquery.examples:author
POST /api/v1/agent/examples/{id}:reject    scope: flyquery.examples:author
```

This allows an automated curator agent (in a future v1 scenario) to
bulk-approve high-confidence examples.

---

## 6. How APPROVED examples enter retrieval

The hybrid retrieval step (before GroundingAgent) queries
`flyquery_examples` with `quality=APPROVED` using:

1. **pgvector similarity** — cosine distance between the question embedding
   and the example question embeddings. Top-`FLYQUERY_TOP_K_EXAMPLES=5`
   candidates retrieved.

2. **BM25** — `content_tsv` over question text. Fused with pgvector results
   via RRF (Reciprocal Rank Fusion, k=`FLYQUERY_RRF_K=60`).

3. **Cross-encoder reranker** — the combined schema + examples pool is
   reranked by the cross-encoder before being passed to GroundingAgent.

The GroundingAgent prompt includes the top examples as few-shot context:

```
APPROVED EXAMPLES (use these as patterns, do not copy verbatim):
1. Question: "Total revenue by region"
   SQL: SELECT region, SUM(amount) AS total_revenue FROM ds.orders GROUP BY region
2. ...
```

### Dataset scoping

Examples can be scoped to a specific `dataset_id` (for dataset-specific
patterns) or workspace-wide (`dataset_id=null`). During retrieval, workspace-
wide examples are always included; dataset-scoped examples are included only
when the query targets that dataset.

---

## 7. Example data model

```
flyquery_examples
  id (uuid), tenant_id, workspace_id
  dataset_id (uuid|null)        -- null = workspace-wide
  question (text)               -- original question text
  generated_sql (text)          -- the executed SQL
  normalised_sql (text)         -- sqlglot-normalised; used for dedup
  source (USER_CURATED | AGENT_LEARNED)
  quality (PROPOSED | APPROVED | REJECTED)
  embedding (vector(1536))      -- question embedding
  citations_json (jsonb)        -- {executed_query_id?: uuid}
  created_at, created_by
  last_used_at, usage_count     -- tracked when example used in retrieval
```

`usage_count` and `last_used_at` are updated each time an example appears in
a GroundingAgent context. This data feeds the `GET /api/v1/stats` response
(top examples by usage frequency).

---

## 8. Tuning and configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `FLYQUERY_TOP_K_EXAMPLES` | `5` | Max examples passed to GroundingAgent per query |
| `FLYQUERY_RRF_K` | `60` | RRF fusion constant (higher = smoother blend) |
| `FLYQUERY_RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder model for reranking |
| `FLYQUERY_RERANKER_TOP_N` | `30` | Candidates fed to cross-encoder before top-10 selection |

### Too many PROPOSED examples accumulating?

If operators are not reviewing proposals fast enough, the example store grows
with unvetted SQL. Options:
- Disable auto-learn entirely by setting `FLYQUERY_AUTOLEARN_ENABLED=false`.
- Set up a review workflow: `GET /examples?quality=PROPOSED&order=created_at_asc`
  daily and batch-approve/reject.
- Use the agent surface to build an automated reviewer in v1.

---

## 9. v1+ roadmap

The current auto-learning is a conservative "observe first, human approves"
model. v1 planned extensions:

- **Automated curator** — an agent that evaluates PROPOSED examples against
  a held-out validation set of known-good queries and bulk-approves those that
  pass.
- **Confidence-gated auto-approve** — examples from queries with high
  GroundingAgent `confidence` (>0.95) and zero retries auto-promoted to
  APPROVED without human review.
- **Feedback loop from result** — if a user explicitly marks an answer as
  incorrect (via a future UI), the associated example is rejected and
  `usage_count` is decremented.
- **Cross-workspace example sharing** — workspace-wide example library visible
  to all workspaces in a tenant (opt-in, operator-controlled).
