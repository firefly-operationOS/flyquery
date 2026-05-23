# flyquery — Billing

## Table of Contents

1. [Overview](#1-overview)
2. [Per-query LLM cost](#2-per-query-llm-cost)
3. [Per-ingest LLM cost](#3-per-ingest-llm-cost)
4. [Storage cost](#4-storage-cost)
5. [flyquery_cost_events schema](#5-flyquery_cost_events-schema)
6. [Billing API](#6-billing-api)
7. [v0 observe-only model](#7-v0-observe-only-model)
8. [v1 enforcement roadmap](#8-v1-enforcement-roadmap)

---

## 1. Overview

flyquery records all LLM usage and associated cost estimates in
`flyquery_cost_events` (append-only, mirrors `canon_cost_events`).

In v0, cost tracking is **observe-only**: events are recorded but no hard
spending limits are enforced. An operator can read the cost data via
`GET /api/v1/billing` and set up external alerts.

v1 will add enforcement (per-workspace budget caps, rate-limit-rpm on LLM
calls, automatic degradation to cheaper models when approaching limits).

---

## 2. Per-query LLM cost

Every query run produces cost events for each agent invocation:

| Agent | When invoked | Typical cost |
|-------|-------------|-------------|
| `GroundingAgent` | Every query | 0.1–1 cent (claude-sonnet-4-6) |
| `GenerationAgent` | SYNTHESIS / HYBRID path | 0.2–2 cents (claude-sonnet-4-6 × N candidates) |
| `CriticAgent` | On execution error (up to 2×) | 0.1–0.5 cents per retry |
| `ExplainerAgent` | Every query | 0.02–0.1 cents (claude-haiku-4-5) |

**Total per simple query:** 0.4–3 cents.
**Total per complex multi-retry query:** 0.5–5 cents.

Cost varies with:
- Question complexity (affects prompt + output token counts).
- Number of schema objects in the Grounding context (large schemas = more tokens).
- Number of CriticAgent retries.
- `FLYQUERY_GENERATION_CANDIDATES` (3 = 3× generation token cost).

---

## 3. Per-ingest LLM cost

Ingestion agents contribute costs to the ingest job:

| Agent | Stage | Typical cost |
|-------|-------|-------------|
| `DescribeAgent` | 7 | 0.01–0.05 cents per column (claude-haiku-4-5) |
| `RelationProposerAgent` | 6 | 0.5–5 cents per dataset (claude-sonnet-4-6, cross-table) |
| `RenameDetectionAgent` | 3 | 0.01–0.1 cents per ambiguous rename (claude-haiku-4-5) |

**Budget cap:** `FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN=200` (default $2.00)
caps the DescribeAgent cost per PARSE_AND_INGEST run. Large schemas (1000+
columns) will require multiple DESCRIBE_PASS jobs.

**Full ingest cost breakdown for a 50-column CSV:**
- DescribeAgent (50 columns, 3 batches): ~$0.05
- RelationProposerAgent (one small dataset): ~$0.01–0.05
- Total: ~$0.06–0.10

---

## 4. Storage cost

flyquery does not directly bill for storage — storage cost accrues at the
object-storage provider level. The `flyquery_workspaces.storage_used_bytes`
field provides a denormalised cache of current workspace storage.

**Storage categories:**
- Original upload blobs (`files/`): retained per workspace retention policy.
- Parquet snapshots (`tables/v{n}.parquet`): one per re-upload per table;
  old snapshots retained until retention expires.
- Query results (`results/`): TTL = `FLYQUERY_RESULT_TTL_HOURS` (24 h default).

**Estimation for a 200 MB dataset (10 tables):**
- Original files: ~200 MB
- Parquet snapshots (1×): ~40–70 MB (3:1 compression typical)
- Query results (100/day × 200 KB avg): ~20 MB/day, swept after 24 h

Total Postgres storage per workspace with 1000 schema objects:
~100 MB (pgvector embeddings dominate at 1536 dims × 4 bytes × 1000 = 6 MB;
rest is metadata).

---

## 5. flyquery_cost_events schema

```
flyquery_cost_events
  id (uuid), tenant_id, workspace_id
  ingest_job_id (FK|null)       -- set for ingestion agent calls
  query_id (FK|null)            -- set for query pipeline agent calls
  agent_name (text)             -- "flyquery-grounding", "flyquery-describe", etc.
  model (text)                  -- "anthropic:claude-sonnet-4-6"
  input_tokens (int)
  output_tokens (int)
  cost_cents (numeric)          -- estimated cost; not a billing invoice
  elapsed_ms (int)
  created_at
```

`cost_cents` is an estimate computed from published per-token pricing at the
time of recording. Actual billing depends on your contract with the LLM
provider.

---

## 6. Billing API

### Cost rollup by workspace

```
GET /api/v1/billing
X-Tenant-Id: acme
X-Workspace-Id: analytics

→ {
    "period_start": "2026-05-01T00:00:00Z",
    "period_end": "2026-05-31T23:59:59Z",
    "total_cost_cents": 1245,
    "by_agent": {
      "flyquery-grounding": 420,
      "flyquery-generation": 560,
      "flyquery-critic": 80,
      "flyquery-explainer": 35,
      "flyquery-describe": 110,
      "flyquery-relation-proposer": 40
    },
    "by_day": [
      {"date": "2026-05-01", "cost_cents": 42},
      ...
    ]
  }
```

### Query parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `period_start` | 30 days ago | Start of the billing window |
| `period_end` | now | End of the billing window |
| `dataset_id` | (all) | Filter to a specific dataset |
| `agent_name` | (all) | Filter to a specific agent |

### Access control

Scope required: `flyquery.billing:read`. Agent-tier also supported:
```
GET /api/v1/agent/billing   scope: flyquery.billing:read
```

---

## 7. v0 observe-only model

In v0, `flyquery_cost_events` is populated but no enforcement runs:

- No per-workspace budget cap.
- No automatic degradation to cheaper models.
- No rate-limit-rpm on LLM calls (only on API requests via
  `agent_token.rate_limit_rpm`).

Operators can set up external cost alerts using the billing API:

```bash
# Simple alert: daily cost check (run via cron or monitoring pipeline)
COST=$(curl -s "http://flyquery:8520/api/v1/billing?period_start=$(date -d '-1 day' +%Y-%m-%dT%H:%M:%SZ)" \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" | jq .total_cost_cents)
if [ "$COST" -gt "10000" ]; then   # $100/day threshold
  echo "ALERT: flyquery daily cost exceeded $100 (actual: $(echo $COST/100 | bc) USD)"
fi
```

---

## 8. v1 enforcement roadmap

Planned for v1:

- **Per-workspace budget cap** (`workspace.monthly_budget_cents`): queries
  that would exceed the cap return `402 Payment Required` with a
  `BUDGET_EXCEEDED` error code.
- **Automatic model degradation**: when a workspace approaches its budget,
  substitute `claude-haiku-4-5` for `claude-sonnet-4-6` on
  Generation + Grounding.
- **Per-token rate limiting** on LLM API calls (separate from the request
  rate limit).
- **Cost forecast**: `GET /api/v1/billing/forecast` estimates end-of-month
  cost based on current daily rate.
