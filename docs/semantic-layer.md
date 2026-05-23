# flyquery — Semantic Layer

## Table of Contents

1. [Overview](#1-overview)
2. [Concepts](#2-concepts)
3. [Metric YAML schema](#3-metric-yaml-schema)
4. [Metric types](#4-metric-types)
5. [Dimensions and entities](#5-dimensions-and-entities)
6. [Glossary](#6-glossary)
7. [Compilation: YAML → DuckDB SQL](#7-compilation-yaml--duckdb-sql)
8. [Versioning and history](#8-versioning-and-history)
9. [Query integration](#9-query-integration)
10. [API quick-reference](#10-api-quick-reference)
11. [Configuration](#11-configuration)

---

## 1. Overview

flyquery's semantic layer sits between the raw schema knowledge base and
the query pipeline. Its purpose:

- Define business metrics in a stable, version-controlled YAML format
  (MetricFlow / OSI-compatible).
- Compile those metrics deterministically to DuckDB SQL templates.
- Make metrics available to the `GroundingAgent` as an alternative query path
  (`SEMANTIC_LAYER` path), bypassing free-form SQL generation when a metric
  covers the question.

The semantic layer gives operators confidence that sensitive business
definitions — revenue, churn, ARR — produce consistent SQL regardless of
which phrasing a user employs.

**v0 ships**: `SIMPLE` metric type (aggregate + expr + filter + group_by).
`RATIO`, `DERIVED`, and `CUMULATIVE` types are accepted in YAML and stored,
but execution is deferred to v1+. Attempting to query a non-SIMPLE published
metric falls through to the `SYNTHESIS` path with the metric definition
passed as few-shot context.

---

## 2. Concepts

| Concept | Table | Description |
|---------|-------|-------------|
| **Metric** | `flyquery_semantic_metrics` | A named, versioned business measure defined in YAML. Scoped per dataset. |
| **Dimension** | `flyquery_semantic_dimensions` | A named grouping attribute or entity. Referenced by metrics in `group_by`. |
| **Glossary term** | `flyquery_glossary_terms` | Workspace-scoped business vocabulary. Linked to metrics, columns, or standalone. |
| **Semantic version** | `flyquery_semantic_versions` | Immutable snapshot of a metric or dimension definition at a point in time. |

Metrics are **scoped per dataset** in v0. A future v1 workspace-level metric
(spanning multiple datasets with explicit join paths) is planned but not
shipped.

---

## 3. Metric YAML schema

Metrics are defined in the `definition_yaml` field. The schema is a subset
of [MetricFlow metric syntax](https://docs.getdbt.com/docs/build/metrics-overview):

```yaml
metric:
  name: total_revenue             # unique within the dataset
  label: Total Revenue            # human-readable display name
  description: >
    Sum of order_amount across completed orders, in USD cents.
  type: simple                    # simple | ratio | derived | cumulative (v0: simple only)
  type_params:
    measure:
      name: order_amount          # column name in the source table
      agg: sum                    # sum | count | count_distinct | avg | min | max
      expr: order_amount          # optional: expression override
    filter: "order_status = 'COMPLETED'"   # optional: WHERE clause fragment
  group_by:
    - region
    - product_category
  meta:
    owner: finance-team
    sensitivity: internal
```

Required fields:
- `metric.name` — must be unique per dataset; alphanumeric + underscore only.
- `metric.type` — one of `simple`, `ratio`, `derived`, `cumulative`.
- `metric.type_params.measure.name` — column name in an UPLOADED or DERIVED
  table within the dataset.
- `metric.type_params.measure.agg` — aggregation function.

Optional fields:
- `filter` — a SQL WHERE fragment; compiled verbatim; validated for single
  statement and no DDL.
- `group_by` — list of column names to include as grouping dimensions.
- `meta` — arbitrary metadata; stored in `metadata_json`; not used in compilation.

---

## 4. Metric types

### SIMPLE (v0 — fully supported)

A straightforward aggregate over a single measure with an optional filter.

```yaml
metric:
  name: completed_order_count
  type: simple
  type_params:
    measure:
      name: order_id
      agg: count_distinct
    filter: "order_status = 'COMPLETED'"
```

Compiled SQL template:
```sql
SELECT {group_by_cols}, COUNT(DISTINCT order_id) AS completed_order_count
FROM {table_ref}
WHERE order_status = 'COMPLETED'
  {extra_filter}
GROUP BY {group_by_cols}
```

### RATIO (v1+)

Numerator and denominator are separate SIMPLE measures.

```yaml
metric:
  name: win_rate
  type: ratio
  type_params:
    numerator:
      name: closed_won_deals
      agg: count
    denominator:
      name: total_deals
      agg: count
```

Stored and validated; compilation deferred to v1.

### DERIVED (v1+)

Arithmetic combination of other published metrics.

```yaml
metric:
  name: gross_margin
  type: derived
  type_params:
    expr: "(total_revenue - cogs) / total_revenue"
    metrics:
      - name: total_revenue
      - name: cogs
```

### CUMULATIVE (v1+)

Rolling window over time.

```yaml
metric:
  name: mtd_revenue
  type: cumulative
  type_params:
    measure:
      name: order_amount
      agg: sum
    window: 30
    grain: day
    time_column: order_date
```

---

## 5. Dimensions and entities

Dimensions are reusable grouping attributes that can be referenced across
multiple metrics.

```yaml
dimension:
  name: order_region
  label: Order Region
  type: categorical          # categorical | time
  expr: region               # column expression
  description: >
    The geographic region where the order was placed.
```

**Time dimensions** add temporal grain for cumulative and time-series metrics:

```yaml
dimension:
  name: order_day
  type: time
  expr: order_date
  grain: day
```

Dimensions live in `flyquery_semantic_dimensions` and follow the same
CRUD + publish/retire lifecycle as metrics.

---

## 6. Glossary

Glossary terms are workspace-scoped (not per-dataset). They define business
vocabulary that the `GroundingAgent` uses to disambiguate questions.

```json
POST /api/v1/glossary
{
  "term": "ARR",
  "definition": "Annual Recurring Revenue. Sum of all active subscription MRR × 12.",
  "synonyms": ["annual recurring revenue", "annual run rate"],
  "related_metrics": ["total_mrr"]
}
```

When a user asks "What is our ARR?", the `GroundingAgent` retrieves the
glossary term, finds `related_metrics: ["total_mrr"]`, and routes via the
`SEMANTIC_LAYER` path using `total_mrr` as the basis metric.

---

## 7. Compilation: YAML → DuckDB SQL

Compilation is **deterministic**: the same YAML always produces the same SQL
template. The compiled template is stored in
`flyquery_semantic_metrics.compiled_sql_template` and updated whenever the
YAML changes.

### Compilation rules (SIMPLE type)

1. **Source table** — resolved to `{dataset}.{table_name}` where
   `table_name` matches `measure.name`'s parent table in the dataset's
   schema knowledge base.
2. **Aggregate expression** — `SUM(expr)`, `COUNT(DISTINCT expr)`, etc.
3. **Filter** — appended to the WHERE clause verbatim.
4. **Group-by columns** — validated to exist in the source table.
5. **Parameterisation** — `{extra_filter}` and `{group_by_append}` are
   runtime substitution slots for query-time dimension pruning.

### Example compilation

YAML:
```yaml
metric:
  name: total_revenue
  type: simple
  type_params:
    measure:
      name: order_amount
      agg: sum
    filter: "order_status = 'COMPLETED'"
  group_by:
    - region
```

Compiled SQL template:
```sql
SELECT
    region,
    SUM(order_amount) AS total_revenue
FROM "sales-2026"."orders"
WHERE order_status = 'COMPLETED'
  {extra_filter_clause}
GROUP BY region
  {group_by_append}
```

At query time, `SemanticCompiler.bind(template, params)` substitutes the
runtime slots. If the user asks for a specific date range, `{extra_filter_clause}`
becomes `AND order_date >= '2026-01-01' AND order_date < '2026-04-01'`.

### Validation

Before storing `compiled_sql_template`, the compiler:
1. Parses the SQL template with sqlglot (DuckDB dialect).
2. Verifies the SQL is a single SELECT statement.
3. Checks all column references exist in the schema knowledge base.
4. Checks the filter fragment contains no DDL, no subqueries, and no
   function calls outside an allowlist.

Validation failures surface as `400 Bad Request` with `code=semantic_compile_error`.

---

## 8. Versioning and history

Every time a metric's `definition_yaml` changes, a new `flyquery_semantic_versions`
row is appended:

```json
{
  "version_id": "01906f70-...",
  "metric_id": "01906f60-...",
  "version_number": 3,
  "definition_yaml": "...",
  "compiled_sql_template": "...",
  "created_at": "2026-05-23T14:00:00Z",
  "created_by": "alice@acme.com"
}
```

The current definition lives in `flyquery_semantic_metrics.definition_yaml`
and `current_version`. History is available via:

```
GET /api/v1/semantic/metrics/{id}/history
```

**Snapshot pinning** — `flyquery_queries.table_id_snapshot_pins_json` records
the snapshot used for each query. When a metric is used in a query, the
`current_version` at query time is recorded alongside the table snapshot pin.
This makes historical queries reproducible even after metric edits.

---

## 9. Query integration

The `GroundingAgent` selects the `SEMANTIC_LAYER` path when:
1. A published SIMPLE metric's `label` or `name` closely matches the question
   (retrieved via BM25 + pgvector over `flyquery_semantic_metrics`).
2. Required dimensions (columns in `group_by`) are referenced by the question.
3. The metric's source table is within the request's `dataset_allowlist`.

When the `SEMANTIC_LAYER` path is taken:
- `SemanticCompiler.bind(template, runtime_params)` produces the final SQL.
- The SQL goes directly to the AST firewall and executor — **no GenerationAgent
  is invoked**.
- `semantic_path_taken = "SEMANTIC_LAYER"` in the query record.
- The compiled SQL is audited as-is.

When a non-SIMPLE metric is retrieved or confidence is below threshold, the
agent falls back to `SYNTHESIS` with the metric definition passed as few-shot
context in the GenerationAgent prompt.

---

## 10. API quick-reference

| Method | Path | Notes |
|--------|------|-------|
| `POST` | `/api/v1/semantic/metrics` | Create metric; validates YAML; compiles SQL |
| `GET` | `/api/v1/semantic/metrics` | List; optional `status`, `dataset_id` |
| `GET` | `/api/v1/semantic/metrics/{id}` | Full detail including `compiled_sql_template` |
| `PUT` | `/api/v1/semantic/metrics/{id}` | Update YAML; triggers recompile + new version |
| `POST` | `/api/v1/semantic/metrics/{id}:publish` | DRAFT → PUBLISHED; enters retrieval pool |
| `POST` | `/api/v1/semantic/metrics/{id}:retire` | PUBLISHED → RETIRED; removed from retrieval |
| `GET` | `/api/v1/semantic/metrics/{id}/history` | Immutable version log |
| `POST` | `/api/v1/semantic/dimensions` | Create dimension |
| `GET` | `/api/v1/semantic/dimensions` | List dimensions |
| `PUT` | `/api/v1/semantic/dimensions/{id}` | Update |
| `POST` | `/api/v1/semantic/dimensions/{id}:publish` | DRAFT → PUBLISHED |
| `GET` | `/api/v1/semantic/dimensions/{id}/history` | Version log |
| `POST` | `/api/v1/glossary` | Create glossary term |
| `GET` | `/api/v1/glossary` | List terms (workspace-scoped) |
| `PUT` | `/api/v1/glossary/{id}` | Update |
| `DELETE` | `/api/v1/glossary/{id}` | Remove |

Agent-tier mirrors exist under `/api/v1/agent/semantic/metrics` with scope
`flyquery.semantic:author`.

---

## 11. Configuration

| Variable | Default | Notes |
|----------|---------|-------|
| `FLYQUERY_TOP_K_METRICS` | `8` | Metrics retrieved per query for grounding |
| `FLYQUERY_GROUNDING_MODEL` | `anthropic:claude-sonnet-4-6` | Model used for GroundingAgent (selects semantic path) |
| `FLYQUERY_GROUNDING_MIN_CONFIDENCE` | `0.55` | Below this, clarification frame is emitted |
