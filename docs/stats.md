# flyquery — Stats

## Table of Contents

1. [Overview](#1-overview)
2. [GET /api/v1/stats response schema](#2-get-apiv1stats-response-schema)
3. [Fields reference](#3-fields-reference)
4. [Access and scoping](#4-access-and-scoping)
5. [Using stats for dashboards](#5-using-stats-for-dashboards)

---

## 1. Overview

`GET /api/v1/stats` is **live as of 26.5.10** (see
[`stats_controller.py:32`](../src/flyquery/web/controllers/stats_controller.py)).
It returns a compact workspace summary in six fields, computed on demand
from a small set of `COUNT(*)` queries — operator traffic, no caching.

The current v1 shape is deliberately small. Per-table activity, top
questions, latency histograms, and `schema_objects` rollups remain on
the roadmap; they require additional indexes on `flyquery_queries` that
have not been added yet. See [api-reference.md § 5.12](api-reference.md#512-history-and-ops)
for the wire reference.

---

## 2. GET /api/v1/stats response schema

```bash
curl -sS http://localhost:8520/api/v1/stats \
  -H 'X-Tenant-Id: acme' \
  -H 'X-Workspace-Id: analytics'
```

```json
{
  "storage_used_bytes": 524288000,
  "dataset_count": 5,
  "table_count": 23,
  "query_count_last_30d": 312,
  "token_count_last_30d": 412380,
  "ingest_job_count_pending": 0
}
```

The shape is `WorkspaceStats` from
[`src/flyquery/interfaces/ops.py:90`](../src/flyquery/interfaces/ops.py).

---

## 3. Fields reference

| Field | Type | Notes |
|-------|------|-------|
| `storage_used_bytes` | int | Current workspace storage (from `flyquery_workspaces.storage_used_bytes`; denormalised cache, updated as files land + as datasets purge). |
| `dataset_count` | int | Count of `flyquery_datasets` rows for the workspace (any status). |
| `table_count` | int | Count of `flyquery_tables` rows for the workspace (UPLOADED + DERIVED). |
| `query_count_last_30d` | int | Count of `flyquery_queries` rows with `created_at >= now() - 30 days`. |
| `token_count_last_30d` | int | Sum of `input_tokens + output_tokens` in `flyquery_cost_events` for the same 30-day window. |
| `ingest_job_count_pending` | int | Count of `flyquery_ingest_jobs` with `status='PENDING'`. Use this + [`workers.md`](workers.md) to detect a stalled worker fleet — a non-zero, slowly-growing value when no ingests are accepted means the worker is down. |

---

## 4. Access and scoping

The endpoint is scoped to the workspace in `X-Workspace-Id`. A caller
cannot read stats for a different workspace without switching headers.

Scope required: `flyquery.billing:read` (shared with the billing
rollup; both are operator-tier reads).

---

## 5. Using stats for dashboards

### Workspace overview widget

```python
stats = await client.get("/api/v1/stats")
print(f"Storage: {stats['storage_used_bytes'] / (1024**3):.2f} GB")
print(f"Datasets: {stats['dataset_count']}")
print(f"Tables: {stats['table_count']}")
print(f"Queries (30d): {stats['query_count_last_30d']}")
print(f"Tokens (30d): {stats['token_count_last_30d']:,}")
print(f"Pending ingest jobs: {stats['ingest_job_count_pending']}")
```

### Ingest-fleet liveness alert

If `ingest_job_count_pending` keeps creeping up while `dataset_count`
grows in step, the IngestWorker fleet is likely down — every new upload
queues a job but nothing claims it. Cross-check with the worker logs
documented in [workers.md](workers.md) and the queue-depth metric
documented in [scale-and-performance.md § 6](scale-and-performance.md#6-observability-for-performance).

### Cost dashboards

For finer-grained cost dashboards (per-period split, per-agent
breakdown), use [`GET /api/v1/billing`](billing.md) — `stats` only
exposes the aggregate token volume so a single dashboard tile can fit.
