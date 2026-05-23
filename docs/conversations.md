# flyquery — Conversations

## Table of Contents

1. [Overview](#1-overview)
2. [Drill-down semantics](#2-drill-down-semantics)
3. [Conversation data model](#3-conversation-data-model)
4. [API surface](#4-api-surface)
5. [Token budget and limits](#5-token-budget-and-limits)
6. [Snapshot pinning across turns](#6-snapshot-pinning-across-turns)
7. [Auto-learn and conversations](#7-auto-learn-and-conversations)
8. [Examples](#8-examples)

---

## 1. Overview

flyquery supports multi-turn conversation sessions on top of the query
pipeline. Each conversation maintains a thread of
`(question, executed_sql, summary, table_qnames, snapshot_pins)` tuples
that carry forward as context for subsequent questions.

This enables two distinct patterns:

- **Drill-down** — narrowing or extending a prior result with follow-up
  questions ("now for Q2 only", "show me just the top 5").
- **Context accumulation** — building up a complex analysis across turns
  without re-specifying which tables or metrics are in scope.

The conversation model mirrors `flycanon`'s
`canon_conversations`/`canon_conversation_turns` shape. The key extension
for flyquery is **snapshot pinning**: each turn records the exact Parquet
snapshot that answered it, so historical queries remain reproducible even
after a re-upload changes the underlying data.

---

## 2. Drill-down semantics

### How prior context is forwarded

When `conversation_id` is provided to `POST /conversations/{id}/turn` (or
`POST /query` with a `conversation_id` field), the `QueryService` resolves
the prior turns from `flyquery_conversation_turns` and feeds them to the
pipeline:

1. **GroundingAgent** receives `message_history` (pydantic-ai format) with
   the last N turns' `(question, summary)` pairs. This lets it understand
   the user's analytical intent without being re-told what tables are
   relevant.

2. **GenerationAgent** receives `starting_point`:
   ```python
   {
     "executed_sql": "<prior turn's executed SQL>",
     "table_qnames": ["ds.orders", "ds.customers"],
     "snapshot_pins": {"t_01": "snap_02", "t_02": "snap_01"}
   }
   ```
   The Generation agent is instructed to write a **delta** (added WHERE
   clause, swapped column, changed aggregation) rather than rewriting
   from scratch.

### NL→delta-SQL examples

**Turn 1:**
```
Question: "Show me total revenue by region"
Generated SQL:
  SELECT region, SUM(amount) AS total_revenue
  FROM ds.orders
  GROUP BY region
  ORDER BY total_revenue DESC
```

**Turn 2 (drill-down):**
```
Question: "Now for Q2 only"
Starting point SQL: <turn 1>
Generated SQL (delta):
  SELECT region, SUM(amount) AS total_revenue
  FROM ds.orders
  WHERE order_date BETWEEN '2026-04-01' AND '2026-06-30'
  GROUP BY region
  ORDER BY total_revenue DESC
```

**Turn 3 (further drill-down):**
```
Question: "Show me the top 3 customers in the Northeast for Q2"
Starting point SQL: <turn 2>
Generated SQL (delta):
  SELECT customer_name, SUM(amount) AS total_revenue
  FROM ds.orders
  JOIN ds.customers ON orders.customer_id = customers.id
  WHERE order_date BETWEEN '2026-04-01' AND '2026-06-30'
    AND region = 'Northeast'
  GROUP BY customer_name
  ORDER BY total_revenue DESC
  LIMIT 3
```

### When context is NOT forwarded

Context is not forwarded if:
- The question starts with explicit table references that differ from the
  conversation's accumulated `table_qnames` — the Grounding agent starts
  fresh.
- The `starting_point_sql` is stale (the table snapshot was re-uploaded
  between turns; stale snapshots are detected via
  `flyquery_tables.current_snapshot_id` vs `snapshot_pins`).
- The conversation has expired (past `created_at + FLYQUERY_CONV_TTL_DAYS`).

---

## 3. Conversation data model

```
flyquery_conversations
  id (uuid), tenant_id, workspace_id
  dataset_id (uuid|null)            -- null = cross-dataset conversation
  summary (text|null)               -- rolling summary; fed into Grounding system-instructions
  title (text|null)                 -- user-supplied or auto-generated
  turn_count (int)
  created_at, updated_at, expires_at

flyquery_conversation_turns
  id (uuid), tenant_id, workspace_id
  conversation_id (FK)
  turn_index (int)                  -- 0-based, monotonic
  question (text)
  executed_sql (text|null)          -- null if query failed
  summary (text|null)               -- ExplainerAgent output for this turn
  table_qnames_json (jsonb)         -- ["ds.orders", "ds.customers"]
  snapshot_pins_json (jsonb)        -- {table_id: snapshot_id}
  citations_json (jsonb|null)       -- {query_id: ...}
  no_answer (bool)                  -- true if execution_status != OK
  elapsed_ms (int)
  model (text)                      -- model used (grounding model)
  created_at
  UNIQUE (conversation_id, turn_index)
```

The `summary` on `flyquery_conversations` is a rolling aggregate computed
from the last few turns' summaries. It fits in the system-instructions
token budget and gives the Grounding agent efficient context without
sending the full turn history.

---

## 4. API surface

### Create a conversation

```
POST /api/v1/conversations
{
  "dataset_id": "ds_01",    -- optional; scopes the conversation to a dataset
  "title": "Q2 revenue analysis"
}
→ {"conversation_id": "conv_01", "created_at": "..."}
```

### Post a turn

```
POST /api/v1/conversations/{conversation_id}/turn
{
  "question": "Show me total revenue by region"
}
→ AnswerResponse {
    "answer": "Total Q2 revenue is $4.2M. ...",
    "executed_sql": "SELECT region, SUM(amount) ...",
    "chart_hint": "bar",
    "row_count": 4,
    "result_url": "https://...presigned...",
    "snapshot_pins": {"t_01": "snap_02"},
    "turn_id": "turn_01",
    "query_id": "q_01"
  }
```

Turn posts use the same underlying pipeline as `POST /query` — the only
difference is that `conversation_id` triggers prior-context loading.

### Retrieve conversation history

```
GET /api/v1/conversations
GET /api/v1/conversations/{id}
  → {conversation_id, title, summary, turn_count, ...}
```

> **Note:** Per-turn pagination (`GET /conversations/{id}/turns`) and an SSE
> turn endpoint are v1+ additions. The current API exposes conversation
> metadata (including `turn_count`) but not the individual turn list.
> Agent-tier conversation endpoints are also v1+.

---

## 5. Token budget and limits

| Limit | Default | Config key |
|-------|---------|-----------|
| Prior turns sent to agents | Last 5 turns | `FLYQUERY_CONV_HISTORY_TURNS` |
| Rolling summary max length | 500 tokens | `FLYQUERY_CONV_SUMMARY_MAX_TOKENS` |
| Conversation TTL | 90 days | `FLYQUERY_CONV_TTL_DAYS` |
| Max turns per conversation | Unbounded in v0 | — |

The rolling summary is re-generated by the ExplainerAgent on each turn when
`turn_count % FLYQUERY_CONV_SUMMARY_INTERVAL == 0` (default every 5 turns).
Between regens, new turn summaries are appended to the rolling text.

Token budget pressure: the Grounding agent prompt budget is
`FLYQUERY_AGENT_MAX_OUTPUT_TOKENS` (default 8192). Prior turn history + schema
metadata together must fit within the model's context window. flyquery
truncates history (oldest first) if the combined token estimate would exceed
the model's context limit.

---

## 6. Snapshot pinning across turns

Each conversation turn records `snapshot_pins_json`: a `{table_id: snapshot_id}`
map of which Parquet snapshot answered the question.

**Why this matters:**

If a dataset is re-uploaded between turn 1 and turn 2, the active snapshot
changes. Without pinning, "show me Q2 for the top 5 customers" (turn 2)
might execute against different data than "total revenue by region" (turn 1),
making the drill-down comparison meaningless.

**Pinning behaviour:**

- The GenerationAgent's `starting_point.snapshot_pins` locks the Parquet
  snapshots for tables seen in prior turns.
- New tables introduced in the current turn use `current_snapshot_id`.
- If a pinned snapshot is no longer available (e.g., workspace retention
  purged it), the turn fails with `error_code=SNAPSHOT_EXPIRED` and the
  conversation requires a reset.

**Resetting pins:**

Start a new conversation. There is no in-place pin reset; a fresh
`POST /conversations` clears all accumulated context.

---

## 7. Auto-learn and conversations

The auto-learn mechanism (inserting `AGENT_LEARNED, quality=PROPOSED` examples
after a successful first-shot query) does NOT fire for conversation turns where
`retries > 0` or `clarification_emitted = true`. Drill-down SQL that depends
on prior context is also excluded, because the `starting_point_sql` would make
the example non-reusable for standalone questions.

Only clean, standalone-query turns (no prior conversation context, no retries,
no clarification) are eligible for auto-learn insertion.

---

## 8. Examples

### Drill-down session (curl)

```bash
# Create a conversation
CONV=$(curl -s -X POST http://localhost:8520/api/v1/conversations \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "ds_01", "title": "Revenue drill-down"}' | jq -r .conversation_id)

# Turn 1: broad question
curl -s -X POST http://localhost:8520/api/v1/conversations/$CONV/turn \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" \
  -H "Content-Type: application/json" \
  -d '{"question": "Total revenue by region"}'

# Turn 2: drill down without restating context
curl -s -X POST http://localhost:8520/api/v1/conversations/$CONV/turn \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" \
  -H "Content-Type: application/json" \
  -d '{"question": "Now for Q2 only"}'

# Turn 3: further drill down
curl -s -X POST http://localhost:8520/api/v1/conversations/$CONV/turn \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 3 customers in the Northeast"}'
```

### Python SDK

```python
from flyquery_sdk import FlyqueryClient
import asyncio

async def drill_down():
    client = FlyqueryClient(
        base_url="http://localhost:8520",
        tenant_id="acme",
        workspace_id="analytics",
    )
    conv = await client.conversations.create(dataset_id="ds_01")
    
    r1 = await client.conversations.turn(conv.conversation_id,
                                          question="Total revenue by region")
    print(r1.answer)
    
    r2 = await client.conversations.turn(conv.conversation_id,
                                          question="Now for Q2 only")
    print(r2.answer)

asyncio.run(drill_down())
```
