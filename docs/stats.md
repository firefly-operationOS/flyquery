# flyquery — Stats

## Table of Contents

1. [Overview](#1-overview)
2. [GET /api/v1/stats response schema](#2-get-apiv1stats-response-schema)
3. [Fields reference](#3-fields-reference)
4. [Access and scoping](#4-access-and-scoping)
5. [Using stats for dashboards](#5-using-stats-for-dashboards)

---

## 1. Overview

`GET /api/v1/stats` returns a one-shot workspace inventory snapshot. It
aggregates:

- Storage utilisation (bytes used vs workspace cap).
- Query activity (total counts, recent history, top questions).
- Dataset and table inventory.
- Schema knowledge base size.
- Top tables by query frequency.

The endpoint is read-only and cached with a short TTL (default 60 seconds)
to avoid hammering Postgres on dashboard polling.

---

## 2. GET /api/v1/stats response schema

```
GET /api/v1/stats
X-Tenant-Id: acme
X-Workspace-Id: analytics
```

```json
{
  "workspace_id": "analytics",
  "tenant_id": "acme",
  "as_of": "2026-05-23T10:00:00Z",

  "storage": {
    "used_bytes": 524288000,
    "cap_bytes": 214748364800,
    "used_pct": 0.24,
    "object_store_breakdown": {
      "files_bytes": 209715200,
      "tables_bytes": 262144000,
      "results_bytes": 52428800
    }
  },

  "datasets": {
    "total": 5,
    "active": 4,
    "archived": 1
  },

  "tables": {
    "total": 23,
    "uploaded": 20,
    "derived": 3,
    "with_ready_snapshot": 22,
    "with_null_embeddings": 0
  },

  "schema_objects": {
    "total_columns": 284,
    "described": 271,
    "pii_tagged": 18,
    "pii_tagged_active": 4
  },

  "queries": {
    "total_all_time": 1402,
    "last_30_days": 312,
    "last_7_days": 89,
    "last_24_hours": 14,
    "semantic_layer_path_pct": 0.12,
    "avg_latency_ms_last_7_days": 2840,
    "p95_latency_ms_last_7_days": 6200,
    "success_rate_last_7_days": 0.94,
    "avg_retries_last_7_days": 0.08
  },

  "top_questions": [
    {
      "question": "Total revenue by region",
      "count": 42,
      "last_asked_at": "2026-05-23T09:45:00Z"
    },
    ...
  ],

  "top_tables": [
    {
      "table_id": "t_01",
      "qualified_name": "ds_sales.orders",
      "query_count_last_30_days": 128
    },
    ...
  ],

  "examples": {
    "total_approved": 34,
    "total_proposed": 12,
    "total_rejected": 3
  },

  "relations": {
    "total_approved": 8,
    "total_proposed": 15,
    "heuristic_proposed": 12,
    "agent_proposed": 3
  }
}
```

---

## 3. Fields reference

### storage

| Field | Type | Notes |
|-------|------|-------|
| `used_bytes` | int | Current workspace storage (from `flyquery_workspaces.storage_used_bytes`; denormalised) |
| `cap_bytes` | int | `FLYQUERY_MAX_WORKSPACE_GB` × 1024³ |
| `used_pct` | float | `used_bytes / cap_bytes` |
| `object_store_breakdown.files_bytes` | int | Original upload blobs |
| `object_store_breakdown.tables_bytes` | int | Parquet snapshots for all tables |
| `object_store_breakdown.results_bytes` | int | Query results (within TTL) |

### datasets

Active = `status=ACTIVE`; archived = `status=ARCHIVED`.

### tables

- `with_ready_snapshot` — tables where `current_snapshot_id IS NOT NULL`
  (queryable).
- `with_null_embeddings` — schema objects with `embedding IS NULL AND is_active=true`;
  should be 0 after ingestion completes. Non-zero indicates a stuck embed stage.

### schema_objects

- `described` — columns with non-null `description`.
- `pii_tagged` — columns with `pii_tag != 'NONE'` (including inactive).
- `pii_tagged_active` — PII-tagged columns with `is_active=true` AND
  `policy=reject` (i.e., currently blocking queries).

### queries

- `semantic_layer_path_pct` — fraction of queries that used the
  `SEMANTIC_LAYER` path (deterministic MetricFlow compilation; cheaper).
- `avg_retries_last_7_days` — average `retries` per query; higher values
  indicate the Grounding / Generation quality needs attention.

### top_questions

The 10 most-asked questions in the last 30 days (normalised by similarity;
minor phrasing variations are grouped). Useful for identifying candidates
for semantic-layer metrics.

### top_tables

The 10 tables most frequently referenced in query `snapshot_pins_json` over
the last 30 days.

---

## 4. Access and scoping

The endpoint is scoped to the workspace in `X-Workspace-Id`. A caller cannot
read stats for a different workspace without switching headers.

Scope required: none for user-tier (any authenticated user in the workspace
can read stats). For agent-tier:
```
GET /api/v1/agent/stats    (no scope restriction; all agent tokens can read)
```

Cache TTL: 60 seconds. The `as_of` field reflects when the snapshot was
computed.

---

## 5. Using stats for dashboards

### Workspace overview widget

```python
stats = await client.stats.get()
print(f"Storage: {stats.storage.used_pct:.1%} of cap")
print(f"Tables: {stats.tables.total} ({stats.tables.with_ready_snapshot} queryable)")
print(f"Queries today: {stats.queries.last_24_hours}")
print(f"Success rate (7d): {stats.queries.success_rate_last_7_days:.0%}")
```

### PII attention needed

```python
if stats.schema_objects.pii_tagged_active > 0:
    print(f"WARNING: {stats.schema_objects.pii_tagged_active} columns blocked by PII (policy=reject)")
    # Surface to operator: GET /api/v1/schema-objects?pii_tag_set=true&is_active=false
```

### Embedding health alert

```python
if stats.tables.with_null_embeddings > 0:
    print(f"ALERT: {stats.tables.with_null_embeddings} tables have null embeddings")
    print("Run: POST /api/v1/ingest-jobs {job_kind: 'REPARSE', ...} to fix")
```

### Top-question → semantic-metric candidates

If the same question appears in `top_questions` with count > 20, consider
creating a MetricFlow metric for it:

```python
for q in stats.top_questions:
    if q.count > 20:
        print(f"Metric candidate: '{q.question}' (asked {q.count}× in 30d)")
        # POST /api/v1/semantic/metrics with the compiled SQL
```
