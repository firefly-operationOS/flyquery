---
name: flyquery-design
description: Design spec for flyquery, the upload-driven Text-to-SQL service in Firefly OperationOS (multi-tenant ingestion of structured files + multi-agent NL→SQL over Parquet/DuckDB)
status: approved
created: 2026-05-22
revised: 2026-05-23
owner: ancongui
---

# flyquery — Operational Structured-Data Intelligence (upload-driven)

> **flycanon is the Operational Knowledge Repository for unstructured content. flyradar is the operations-discovery service over heterogeneous corpus. flyquery is their counterpart for structured data the customer brings in as files: a multi-tenant ingestion + Text-to-SQL service that turns natural-language questions into governed, auditable SQL against user-uploaded `.csv`, `.tsv`, `.xlsx`, `.xls`, `.ods`, `.json`, `.jsonl`, `.parquet`, `.avro`, `.orc`, `.arrow`, `.feather` (plus `.gz`/`.zip`/`.bz2` variants), materialised as Parquet on object storage and queried by DuckDB, with a long-lived schema knowledge base, an OSI/MetricFlow-shape semantic layer, a Vanna-style example store, multi-agent grounding/generation/critic/explainer pipeline, and a hexagonal adapter ring at every external boundary.**

## 1. Mission and position in Firefly OperationOS

flyquery is the third pillar alongside flycanon (unstructured knowledge) and flyradar (operations discovery & diagnostics). It owns:

- **Ingestion of user-uploaded structured files** — every common business + technical format, multi-table extraction (XLSX sheets, JSON top-level arrays), per-format readers behind a hexagonal `FileReader` port, materialised as Parquet on object storage.
- **The schema knowledge base** — every table/column a workspace exposes (post-materialisation), with embeddings, samples, profiles, PII tags, and human + AI-curated descriptions. Snapshots are immutable; re-uploads produce new versions with annotation transplant.
- **The relation graph** — across all tables in a dataset, heuristic + AI-proposed joins (no FK catalog exists in the upload world). Operator approval flips `AGENT_PROPOSED` → `MANUAL`.
- **The semantic layer** — MetricFlow-shape YAML metrics, dimensions, glossary, versioned per dataset. Open Semantic Interchange compatible.
- **The example store** — `(question, SQL)` pairs that drive Vanna-style few-shot retrieval. Auto-populated from successful runs as `AGENT_LEARNED, quality=PROPOSED` (not in retrieval pool until an operator approves).
- **The query execution path** — multi-agent pipeline (`Grounding → Generation → Executor → Critic → Explainer`) gated by per-token scopes, AST firewall, row caps, statement timeouts, PII scanning, with a hybrid clarification SSE frame when grounding confidence is below threshold, and conversation memory carrying prior `executed_sql + table_qnames + snapshot_pins` for drill-down follow-ups.
- **The history & audit trail** — every upload, every snapshot diff, every question, every candidate, every executed statement, every cost event, append-only.

It does not own:

- ingestion of unstructured documents (that is flycanon)
- operations discovery / pain-point analysis (that is flyradar)
- connections to customer databases (no DSNs, no driver pool, no introspection over `information_schema`)
- dbt manifests, dbt models, dbt lineage
- OpenAPI specs as data sources
- BI dashboard rendering (we emit chart hints only)

flyquery owns the data after upload. Compliance (encryption-at-rest, retention, GDPR purge) is first-class.

## 2. Architectural principles

1. **We own the data.** Customer files land in our object store, materialise to Parquet in our layout, are queried by our DuckDB. Encryption-at-rest, retention SLA, and GDPR purge are first-class concerns rather than caller responsibilities.
2. **Hexagonal at every external boundary.** Ports: `ObjectStore` (LocalFs/S3/GCS/AzureBlob), `FileReader` (one per format family), `VectorStore`, `PiiScanner`, `RateLimiter`, `IdempotencyStore`, `SemanticCompiler`. The `DialectAdapter` port is retained for future engine swaps; v0 ships a single `DuckDBAdapter`.
3. **Mirror flycanon framework usage verbatim.** `@pyfly_application` + `scan_packages`, `@configuration` beans, `@rest_controller` + `@request_mapping`, lock-step `web/conventions/*`, byte-equivalent `agent_deps.py`, `agent_token_service.py`, `agent_tokens_controller.py` (with flyquery scope catalog), `core/agents/builder.py:build_agent`. No reinvented plumbing.
4. **Multi-tenancy is Postgres-native.** Every domain row carries `tenant_id` and `workspace_id`; RLS policies use the same `app.tenant_id` / `app.workspace_id` GUCs set by the lock-step middleware. Two-role split (admin BYPASSRLS for migrations, app no-bypass for sessions) — per the `postgres_test_role_bypasses_rls` memory.
5. **Agent-tier is first-class.** `/api/v1/agent/*` paths exist for every operator endpoint an AI agent needs, protected by `X-Agent-Token` and mandatory `Idempotency-Key` on writes; same scope model as flycanon/flyradar.
6. **Read-default, write only on derived tables.** Generated SQL is SELECT-only against ingested tables. Mutations to ingested data happen via re-upload (atomic snapshot swap). Derived tables (`POST /tables:derive`) are mutable under `flyquery.derived:write` scope. A direct-SQL endpoint (`POST /sql:execute`) is gated by `workspace.allow_direct_sql`.
7. **Self-correction is the default.** A Critic agent reruns failed statements with execution feedback up to `MAX_REFINE_RETRIES` (default 2). Costs and retry counts are recorded.
8. **Streaming-first.** Every long-running endpoint streams pipeline-stage events over SSE; sync endpoints drain the stream. The hybrid clarification frame rides alongside the answer when grounding confidence is below threshold.
9. **Open standards over lock-in.** Parquet on disk. OSI/MetricFlow YAML for the semantic layer. SDKs auto-generated from OpenAPI. Vector-store interface allows pgvector/sqlite-vec/Chroma/Qdrant/Pinecone (pgvector in v0).
10. **Lock-step strictness.** Byte-equivalent modules across canon/radar/flyquery are diffed in CI (`scripts/check_lockstep.py`) against pinned SHAs.

## 3. State-of-the-art alignment (2025–2026)

| SOTA technique | Source | flyquery realisation |
| --- | --- | --- |
| Schema linking → 15-20% accuracy gain on BIRD | BIRD benchmark, AutoLink | Hybrid (BM25+pgvector+RRF) retrieval over `flyquery_schema_objects` + cross-encoder reranker (on by default) + Grounding agent prunes |
| Multi-agent decomposition | CHESS (IR/SS/CG/UT), MARS-SQL (Grounding/Generation/Validation) | Four FireflyAgents (Grounding, Generation, Critic, Explainer) wired by `QueryService`; two more for ingestion (Describe, RelationProposer) and an optional `RenameDetectionAgent` for reconcile ambiguity |
| Few-shot `(Q, SQL)` retrieval | Vanna AI | `flyquery_examples` with embeddings; auto-populated as `AGENT_LEARNED, quality=PROPOSED`, operator-approved into the retrieval pool |
| Self-correction with execution feedback | SQLCritic, ReFoRCE, MARS-SQL ReAct | Critic agent consumes executor error/result + structured `RefinementHint` to regenerate |
| Multiple candidate generation + voting | CHESS unit-testing | Generation agent emits N candidates (default 3); Critic ranks against executed result + heuristic checks |
| Iterative schema expansion | AutoLink | Grounding-agent loop can request more schema rows if confidence below `GROUNDING_MIN_CONFIDENCE` and `missing_info` is non-empty (up to `EXPAND_ITERS=2`) |
| Semantic-layer-first as alternative path | Snowflake Cortex Analyst, dbt MetricFlow, Cube, OSI | Grounding agent picks `SEMANTIC_LAYER` path when a published metric covers the question; MetricFlow compiles SQL deterministically |
| Cross-encoder reranking on schema retrieval | Recent BIRD/Spider top-line approaches | `FLYQUERY_RERANKER_MODEL` defaults to a small cross-encoder; top-30 → top-10 before grounding |
| Drill-down conversation memory | Operational pattern | Conversation turns persist `executed_sql + table_qnames + snapshot_pins`; the next turn feeds the prior SQL into Grounding/Generation as `starting_point` |
| Hybrid clarification | Operational pattern | When grounding confidence < threshold AND `missing_info` is non-empty, SSE emits a `clarification` frame **alongside** the best-guess answer; conversation follow-up consumes it |

## 4. Resource hierarchy

```
Workspace                  (canon-lock-step row; RLS root)
  └── Dataset              flyquery_datasets       (logical grouping)
        └── File           flyquery_files          (one upload, original blob URI)
              └── Table    flyquery_tables         (1 from CSV; N from XLSX sheets; N from JSON top-level arrays)
                    └── Snapshot  flyquery_schema_snapshots  (versioned per re-upload)
                    └── Schema metadata (flyquery_schema_objects: kind=TABLE + kind=COLUMN rows)
                    └── Relations (flyquery_relations: scoped to dataset, references this table)
```

### Identity rules

- **First upload** → `POST /datasets/{id}/files` (multipart). Server returns `{file_id, tables: [{table_id, qualified_name, sheet_or_path, n_rows_estimate}]}`. XLSX with 3 sheets returns 3 `table_id`s. JSON with `{"orders": [...], "customers": [...]}` returns 2.
- **Re-upload into existing slot** → `PUT /datasets/{ds}/tables/{table_id}:upload`. New snapshot, same `table_id`. Annotations carry forward by `(qualified_name, column_name)`; ambiguous renames flagged as `RENAMED_CANDIDATE` for one-click confirm.
- **Snapshot pointer** → `flyquery_tables.current_snapshot_id` flips atomically when a new snapshot reaches `READY` (stage 10).
- **Snapshot pinning** → `flyquery_queries.table_id_snapshot_pins_json` records which snapshot answered each query, so historical answers stay reproducible across re-uploads.

## 5. Domain model

All tables live in Postgres, prefixed `flyquery_`. Every multi-tenant row carries `(tenant_id, workspace_id)` with RLS enabled and FORCED. Single-workspace tables (`flyquery_agent_tokens`) follow canon's pattern (tenant-only with workspace allowlist in the row).

```
flyquery_workspaces                                 -- canon_workspaces lock-step +
   kms_key_uri (text|null)             -- per-workspace CMK/CMEK/Key Vault URI; null = storage-native SSE
   retention_days (int|null)           -- null = keep forever
   allow_direct_sql (bool, default false)
   default_locale (text, default 'en-US')
   storage_used_bytes (bigint, default 0; denormalised cache)

flyquery_datasets                                   -- logical container
   id (uuid), tenant_id, workspace_id, name (UQ per workspace),
   description, drift_policy (AUTO|REVIEW, default AUTO),
   default_locale (text|null),
   ingest_policy_json (jsonb),           -- include/exclude patterns, sample disable,
                                          -- describe budget overrides, table extraction overrides
   status (ACTIVE|ARCHIVED),
   created_at, updated_at, metadata_json

flyquery_files                                      -- one row per upload
   id (uuid), tenant_id, workspace_id, dataset_id (FK),
   original_filename, file_format (csv|tsv|xlsx|xls|ods|json|jsonl|parquet|avro|orc|arrow|feather),
   compression (none|gz|zip|bz2),
   size_bytes, content_hash_sha256,
   object_store_key,                     -- see §9.5 layout: {tenant}/{workspace}/{dataset}/files/{file_id}.{ext}
   table_extraction_rules_json (jsonb),  -- sheet allowlist, JSON path spec, header skip rows
   uploaded_at, uploaded_by,
   status (RECEIVED|PARSED|FAILED|DELETED), error_json (jsonb|null)

flyquery_tables                                     -- logical table identity + lifecycle
   id (uuid), tenant_id, workspace_id, dataset_id (FK),
   source_file_id (FK; latest source file),
   name (UQ per dataset), qualified_name (text),
   kind (UPLOADED|DERIVED),
   sheet_or_json_path (text|null),       -- 'Sheet1' or '$.orders' or null
   current_snapshot_id (FK to flyquery_schema_snapshots; null until first READY snapshot),
   description (text|null), description_source (HUMAN|INTROSPECTED|AGENT|null),
   business_owner (text|null), governance_json (jsonb|null),
   locale_override (text|null),
   is_active (bool, default true),
   created_at, updated_at, archived_at

flyquery_schema_snapshots                           -- one per upload of a table
   id (uuid), tenant_id, workspace_id, dataset_id, table_id (FK),
   taken_at, snapshot_hash (deterministic over column names + types),
   n_columns, n_rows_estimate, n_rows_actual (nullable until parse completes),
   parquet_object_key,                   -- see §9.5 layout: {tenant}/{workspace}/{dataset}/tables/{table}/v{n}.parquet
   parquet_byte_size,
   status (PARTIAL|READY|FAILED), failure_json (jsonb|null),
   triggered_by (USER|AGENT|SCHEDULED|REPARSE), created_by

flyquery_schema_changes                             -- append-only delta log
   id (uuid), tenant_id, workspace_id, table_id (FK),
   prev_snapshot_id (FK|null), next_snapshot_id (FK),
   column_name, change (ADDED|REMOVED|TYPE_CHANGED|RENAMED|RENAMED_CANDIDATE),
   before_json, after_json,
   llm_rationale (text|null),            -- populated when change=RENAMED_CANDIDATE
   approved_by, approved_at,
   created_at

flyquery_schema_objects                             -- query-time metadata for tables + columns
   id (uuid), tenant_id, workspace_id, table_id (FK), snapshot_id (FK),
   kind (TABLE|COLUMN), parent_id (FK self|null when kind=COLUMN),
   qualified_name (text),                -- "dataset.table" or "dataset.table.column"
   data_type (text|null), is_nullable (bool|null),
   description (text|null), description_source (HUMAN|INTROSPECTED|AGENT|null),
   synonyms_json (jsonb|null),
   pii_tag (text|null), pii_source (REGEX|PRESIDIO|AGENT|HUMAN|null),
   business_owner (text|null), governance_json (jsonb|null),
   sample_values_json (jsonb|null), sample_taken_at,
   profile_json (jsonb|null),            -- null_fraction, distinct_estimate, top_values, min/max
   embedding (vector(1536) | null), embedding_model (text|null),
   source_hash (text),                   -- detects column-level drift across re-uploads
   is_active (bool, default true),
   content_tsv (tsvector),               -- BM25 over name + description + synonyms
   created_at, last_seen_at, last_changed_at

flyquery_relations                                  -- proposed/manual joins (no FK catalog in file-upload world)
   id (uuid), tenant_id, workspace_id, dataset_id (FK),
   from_table_id (FK), from_column_name,
   to_table_id (FK), to_column_name,
   condition (text|null),                -- non-equi / virtual join
   kind (HEURISTIC|AGENT_PROPOSED|MANUAL),
   confidence (float), reason (text|null),
   status (PROPOSED|APPROVED|REJECTED),
   approved_by, created_at, updated_at

flyquery_semantic_metrics                           -- MetricFlow OSI shape
   id (uuid), tenant_id, workspace_id, dataset_id (FK; metrics scoped per dataset in v0),
   name (UQ per dataset), label, description,
   definition_yaml, compiled_sql_template,
   metric_type (SIMPLE|RATIO|DERIVED|CUMULATIVE),
   status (DRAFT|PUBLISHED|RETIRED),
   current_version, created_at, updated_at

flyquery_semantic_dimensions                        -- mirror metrics for dimensions / entities
flyquery_semantic_versions                          -- immutable history per metric/dim
flyquery_glossary_terms                             -- workspace-scoped (not per-dataset)

flyquery_examples                                   -- Vanna-style few-shot
   id (uuid), tenant_id, workspace_id, dataset_id (nullable; workspace-wide if null),
   question, generated_sql, normalised_sql,
   source (USER_CURATED|AGENT_LEARNED),
   quality (PROPOSED|APPROVED|REJECTED),
   embedding (vector(1536)),
   citations_json,                       -- {executed_query_id?}
   created_at, created_by, last_used_at, usage_count

flyquery_queries                                    -- every run, append-only
   id (uuid), tenant_id, workspace_id, dataset_id,
   question, prior_turn_ids (uuid[]),
   table_id_snapshot_pins_json,          -- {table_id: snapshot_id}
   semantic_path_taken (SEMANTIC_LAYER|SYNTHESIS|HYBRID),
   candidates_json,                      -- N candidate SQL with reasoning
   chosen_candidate_index (int),
   executed_sql, ast_classification (SELECT|INSERT|UPDATE|DELETE|DDL),
   execution_engine (duckdb),
   execution_status (OK|REFINED_OK|FAILED|REJECTED_BY_FIREWALL), retries (int),
   row_count (int|null), elapsed_ms (int), cost_cents (numeric),
   clarification_emitted (bool), clarification_json (jsonb|null),
   pii_findings_json, error_json,
   model_grounding, model_generation, model_critic, model_explainer,
   created_at, finalised_at

flyquery_query_results                              -- preview cache (full result in object store)
   query_id (FK, PK),
   result_preview_json,                  -- capped at FLYQUERY_RESULT_PREVIEW_MAX_BYTES
   result_object_key (text|null),        -- see §9.5 layout: {tenant}/{workspace}/{dataset}/results/{query_id}.parquet
   result_byte_size, ttl_expires_at

flyquery_conversations                              -- multi-turn; mirrors canon_conversations
flyquery_conversation_turns
   id (uuid), tenant_id, workspace_id, conversation_id (FK), turn_index,
   question, executed_sql, summary, table_qnames_json,
   snapshot_pins_json,                   -- {table_id: snapshot_id}
   citations_json, no_answer (bool),
   elapsed_ms, model, created_at
   UQ (conversation_id, turn_index)

flyquery_agent_tokens                               -- lock-step canon/radar +
   dataset_allowlist_json,               -- restrict by dataset
   workspace_allowlist_json,             -- restrict by workspace (existing canon shape)
   scopes_json                           -- see §7 scope catalog

flyquery_audit_events                               -- append-only, mirrors canon_audit_events
flyquery_cost_events                                -- mirrors canon_cost_events +
   ingest_job_id (FK|null), query_id (FK|null)

flyquery_ingest_jobs                                -- async ingest orchestration
   id (uuid), tenant_id, workspace_id, dataset_id, table_id (FK|null),
   file_id (FK|null), snapshot_id (FK|null until READY),
   job_kind (PARSE_AND_INGEST|REPARSE|SAMPLE_REFRESH|DESCRIBE_PASS|RELATION_PASS),
   request_json, result_json,
   status (PENDING|RUNNING|SUCCEEDED|FAILED|CANCELLED), attempts,
   started_at, finished_at, cost_cents (numeric), elapsed_ms

flyquery_ingest_events                              -- streamable per-stage progress
   id (serial), tenant_id, workspace_id, ingest_job_id (FK),
   stage, status, message, payload_json, created_at
```

### RLS

Standard policy on every multi-tenant table:

```sql
USING (tenant_id = current_setting('app.tenant_id')
   AND workspace_id = current_setting('app.workspace_id'))
```

`flyquery_workspaces` policy: `tenant_id = ... AND id = current_setting('app.workspace_id')`.
`flyquery_agent_tokens` policy: `tenant_id = ...` (workspace check is in code against allowlist).
Migrations run under a BYPASSRLS admin role; the app uses a non-bypass role.

## 6. Ingestion pipeline (10 stages)

Asynchronous, restartable, streamable, idempotent across re-ingests. Human annotations preserved verbatim. Each stage is one transition; failures persisted to `flyquery_ingest_jobs.result_json` + `flyquery_ingest_events` and surfaced via SSE.

```
                       POST /datasets/{id}/files
                          PUT /datasets/{ds}/tables/{id}:upload
                                  │
                                  ▼
                        write bytes to object store under
                        {tenant}/{workspace}/{dataset}/files/{file_id}.{ext}      (see §9.5)
                                  │
                                  ▼
                       publish to "flyquery.ingest" EDA topic
                                  │
                                  ▼
                  IngestWorker picks up flyquery_ingest_jobs row
                          (status PENDING → RUNNING)
                                  │
                                  ▼
       ┌────────────────── 1. receive ──────────────────────────────────┐
       │ verify content_hash, size cap (FLYQUERY_MAX_FILE_MB), format   │
       │ detection from magic bytes + extension; reject mismatch.       │
       │ flyquery_files.status = RECEIVED. Emits received event.        │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────────── 2. parse ────────────────────────────────────┐
       │ Per file_format dispatch via FileReader port:                  │
       │  - CSV/TSV: chardet/charset-normalizer + delimiter sniff +     │
       │    DuckDB read_csv_auto(sample_size=FLYQUERY_TYPE_INFER_       │
       │    SAMPLE_ROWS, auto_detect=true). One table.                  │
       │  - XLSX/XLS/ODS: python-calamine enumerates sheets; each       │
       │    sheet → one table (sanitised name); skip merged-cell        │
       │    title rows up to FLYQUERY_MAX_TITLE_ROWS.                   │
       │  - JSON: top-level array → one table; top-level object with    │
       │    array-valued keys → one table per key.                      │
       │  - JSONL/NDJSON: one table.                                    │
       │  - Parquet/Avro/ORC/Feather/Arrow: pass-through schema read.   │
       │  - Compressed variants: transparent decompression to temp +    │
       │    delegate to the inner reader.                               │
       │ Apply file.table_extraction_rules_json overrides (sheet        │
       │ allowlist, JSON paths). For each logical table, materialise a  │
       │ Parquet under {dataset}/tables/{table}/v{n}.parquet (§9.5);    │
       │ capture columns + types. DuckDB auto_detect resolves types;    │
       │ workspace.locale resolves date ambiguity (en-US vs en-GB vs    │
       │ de-DE…). LLM-suggested derived virtual columns persisted as    │
       │ schema_objects with description_source=AGENT, only applied     │
       │ after PUT /schema-objects/{id}/type-hint approves. Emits       │
       │ parsed event with per-table counts.                            │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────── 3. reconcile + persist snapshot ─────────────────┐
       │ For each new table_id: insert flyquery_schema_snapshots row    │
       │ (status PARTIAL). If previous snapshot exists, compute diff:   │
       │ ADDED / REMOVED / TYPE_CHANGED / RENAMED. Rename rule:         │
       │ auto-RENAMED only when the (position + type) signature of a   │
       │ removed column matches exactly one new column AND no other    │
       │ column matches; otherwise → RenameDetectionAgent               │
       │ proposes, row inserted as RENAMED_CANDIDATE with               │
       │ llm_rationale; PUT /schema-changes/{id}:confirm flips to       │
       │ RENAMED. Mark vanished columns is_active=false on              │
       │ schema_objects (NOT deleted; historical pinning preserved).    │
       │ Annotation transplant: description (HUMAN), pii_tag (HUMAN),   │
       │ business_owner, governance_json, synonyms preserved verbatim   │
       │ across snapshots. Emits reconciled event with diff summary.    │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────────── 4. sample ───────────────────────────────────┐
       │ For columns added/changed AND prior pii_tag NULL/NONE AND      │
       │ policy allows: read N=FLYQUERY_SAMPLE_N values from Parquet    │
       │ via DuckDB; inline PII scanner gate refuses to persist if      │
       │ value looks like PII; writes to schema_objects.                │
       │ sample_values_json. Privacy-restrictive datasets can disable   │
       │ globally via ingest_policy_json.sample_disabled=true.          │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────────── 5. profile ──────────────────────────────────┐
       │ Per column: null_fraction, distinct_estimate (DuckDB           │
       │ approx_count_distinct), top_values (low-cardinality only),     │
       │ min/max (numeric + temporal). Skipped above                    │
       │ FLYQUERY_PROFILE_ROW_THRESHOLD (default 10M). Persist to       │
       │ profile_json.                                                  │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌─────────────── 6. relation discovery ──────────────────────────┐
       │ Across ALL tables in the dataset (not only this upload).       │
       │ Two layers fused (no FK catalog in file-upload world):         │
       │  (a) heuristic — column-name equality + compatible types +     │
       │      one-sided unique constraint (distinct_estimate ≥ 0.95     │
       │      of n_rows). flyquery_relations kind=HEURISTIC,            │
       │      status=PROPOSED, confidence ∝ uniqueness × name           │
       │      specificity.                                              │
       │  (b) RelationProposerAgent inspects (table_descriptions,       │
       │      column_descriptions, samples) → ProposedRelations.        │
       │      Inserted as kind=AGENT_PROPOSED, status=PROPOSED,         │
       │      reason populated.                                         │
       │ Operator approves via POST /datasets/{id}/relations/{rel_id}:  │
       │ approve → status=APPROVED, kind=MANUAL.                        │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────────── 7. describe ─────────────────────────────────┐
       │ Tables + columns lacking description fed to DescribeAgent in   │
       │ batches of FLYQUERY_DESCRIBE_BATCH. Outputs per-object short   │
       │ summary + business synonyms; description_source=AGENT. Budget  │
       │ cap FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN; remaining objects  │
       │ deferred to a follow-up DESCRIBE_PASS job.                     │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────────── 8. PII tag ──────────────────────────────────┐
       │ PIIScanner classifies each column from (name + description +   │
       │ samples). Sets pii_tag + pii_source. Policy 'warn' logs +      │
       │ continues; 'redact' purges sample_values; 'reject' flags as    │
       │ not-queryable until reviewed. Re-uses canon's PIIScanner port  │
       │ verbatim. Late-set tags: if pii_tag flips from NONE → SET,     │
       │ samples are scrubbed in-place.                                 │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌─────────────── 9. embed + index ───────────────────────────────┐
       │ Build per-object embedding text:                               │
       │   "<dataset>.<table>.<column>: <data_type>\n                   │
       │   <description>\nSamples: <preview>\nSynonyms: <list>"         │
       │ Per-table aggregate embedding rolls up columns. Persist into   │
       │ embedding + embedding_model. Refresh pgvector HNSW + content_  │
       │ tsv for BM25.                                                  │
       └─────────────────────────────────┬──────────────────────────────┘
                                         ▼
       ┌────────────── 10. publish + close snapshot ────────────────────┐
       │ Atomic transaction: flyquery_schema_snapshots.status = READY,  │
       │ flyquery_tables.current_snapshot_id flips to the new           │
       │ snapshot. Publish flyquery.schema.updated event with diff      │
       │ summary. Emit snapshot_ready + final SSE frames.               │
       └────────────────────────────────────────────────────────────────┘
```

Stages 4-8 are skippable per `ingest_policy_json`; stages 1-3, 9, 10 are mandatory. Each transition records to `flyquery_ingest_events`.

### Ingestion agents

| Agent | output_type | Stage | Notes |
| --- | --- | --- | --- |
| `DescribeAgent` | `DescribedObjects` (per-object short summary + business synonyms) | 7 | Batched up to `FLYQUERY_DESCRIBE_BATCH`; budget-capped per ingest. |
| `RelationProposerAgent` | `ProposedRelations` (cross-table join hints with reasoning) | 6 | Cross-table view across the whole dataset; status=PROPOSED until human approval. |
| `RenameDetectionAgent` | `RenameProposals` | 3 | Only invoked on ambiguous reconcile; persists rationale to `schema_changes.llm_rationale`. |
| `GovernanceClassifierAgent` *(v1+)* | `GovernanceTags` (sensitivity, retention class) | 8 | Off by default; for regulated industries. |

All four follow the `build_agent` recipe: structured `output_type`, `auto_register=False`, no tools, fresh per call, observability middleware. Cost events recorded under the originating `ingest_job_id`.

## 7. REST surface

### 7.1 User-tier (`/api/v1/*`, JWT + tenant/workspace headers)

```
Workspaces
  POST   /workspaces                       create (canon-lock-step)
  GET    /workspaces
  GET    /workspaces/{id}
  PUT    /workspaces/{id}                  update kms_key_uri, retention_days, allow_direct_sql, default_locale
  DELETE /workspaces/{id}:purge            hard delete with 30-day soft tombstone

Datasets
  POST   /datasets
  GET    /datasets
  GET    /datasets/{id}
  PUT    /datasets/{id}                    drift_policy, ingest_policy_json, default_locale
  DELETE /datasets/{id}                    archive (soft)

Files & tables (the upload entry-points)
  POST   /datasets/{id}/files              multipart upload; first time
  GET    /datasets/{id}/files
  GET    /files/{id}
  DELETE /files/{id}
  GET    /datasets/{id}/tables
  GET    /tables/{id}
  PUT    /tables/{id}                      rename, description, locale_override
  PUT    /datasets/{ds}/tables/{id}:upload re-upload into existing slot (new snapshot)
  DELETE /tables/{id}
  POST   /tables:derive                    {name, sql, dataset_id} → DERIVED table (materialised + tracked)
  GET    /tables/{id}/snapshots
  GET    /tables/{id}/snapshots/{snap_id}
  GET    /tables/{id}/changes              paginated diff log
  POST   /tables/{id}:explode              {json_path} → nested-array explode (v1+)

Ingest jobs
  POST   /ingest-jobs                      start job (PARSE_AND_INGEST | REPARSE | SAMPLE_REFRESH | DESCRIBE_PASS | RELATION_PASS)
  GET    /ingest-jobs                      paginated; filters by status, kind, dataset, table
  GET    /ingest-jobs/{id}
  GET    /ingest-jobs/{id}/stream          SSE
  GET    /ingest-jobs/{id}/events          paginated event ledger
  POST   /ingest-jobs/{id}:cancel          cooperative

Schema annotation
  PUT    /schema-objects/{id}              description, pii_tag, business_owner, governance_json, synonyms
  POST   /schema-objects/{id}:sample       refresh sample_values
  POST   /schema-objects/{id}:profile      refresh profile_json
  POST   /schema-objects/{id}/type-hint    apply LLM-suggested derived-virtual type
  GET    /schema-objects:search            BM25 + vector debug surface
  GET    /schema-objects/{id}/lineage      upstream (file lineage) + downstream (derived-table provenance)
  POST   /schema-objects:rename-merge      transplant annotations across an ambiguous rename
  POST   /schema-changes/{id}:confirm      flip RENAMED_CANDIDATE → RENAMED

Relations
  GET    /datasets/{id}/relations
  POST   /datasets/{id}/relations          add manual relation
  POST   /datasets/{id}/relations/{rel_id}:approve   PROPOSED → APPROVED (kind=MANUAL)
  POST   /datasets/{id}/relations/{rel_id}:reject
  DELETE /datasets/{id}/relations/{rel_id}

Semantic layer
  POST   /semantic/metrics
  GET    /semantic/metrics
  GET    /semantic/metrics/{id}
  PUT    /semantic/metrics/{id}
  POST   /semantic/metrics/{id}:publish
  POST   /semantic/metrics/{id}:retire
  GET    /semantic/metrics/{id}/history
  (mirror endpoints for dimensions)
  POST   /glossary
  GET    /glossary
  PUT    /glossary/{id}
  DELETE /glossary/{id}

Examples (Q→SQL few-shot)
  POST   /examples                         user-curated example
  GET    /examples                         filters by source, quality, dataset
  POST   /examples/{id}:approve            PROPOSED → APPROVED (enters retrieval)
  POST   /examples/{id}:reject

Query
  POST   /query                            sync; drains stream
  POST   /query/stream                     SSE
  POST   /query:explain                    generate SQL + EXPLAIN, do not execute
  POST   /query:validate                   parse + classify generated SQL, do not execute

Direct SQL  (gated by workspace.allow_direct_sql)
  POST   /sql:execute                      sync
  POST   /sql:execute/stream               SSE

Conversations
  POST   /conversations
  GET    /conversations
  GET    /conversations/{id}
  POST   /conversations/{id}/turn          next NL turn (carries drill-down context automatically)

History & ops
  GET    /queries                          paginated history with filters
  GET    /queries/{id}                     one run, full detail
  GET    /queries/{id}/result              {preview_json, parquet_presigned_url, ttl_expires_at}
  GET    /audit
  GET    /billing
  GET    /stats
  GET    /version

Agent tokens (operator-only)
  POST   /agent-tokens                     mint
  GET    /agent-tokens                     list
  DELETE /agent-tokens/{id}                revoke
```

### 7.2 Agent-tier (`/api/v1/agent/*`, `X-Agent-Token` + mandatory `Idempotency-Key` on writes)

```
POST   /agent/datasets/{id}/files                  scope: flyquery.files:upload
PUT    /agent/datasets/{ds}/tables/{id}:upload     scope: flyquery.files:upload
POST   /agent/tables:derive                        scope: flyquery.derived:write
GET    /agent/tables/{id}                          scope: flyquery.schema:read
GET    /agent/tables/{id}/snapshots                scope: flyquery.schema:read
GET    /agent/tables/{id}/changes                  scope: flyquery.schema:read
PUT    /agent/schema-objects/{id}                  scope: flyquery.schema:annotate
GET    /agent/schema-objects/{id}/lineage          scope: flyquery.lineage:read
POST   /agent/ingest-jobs                          scope: flyquery.ingest:run
GET    /agent/ingest-jobs/{id}                     scope: flyquery.ingest:read
GET    /agent/ingest-jobs/{id}/stream              scope: flyquery.ingest:read
POST   /agent/semantic/metrics                     scope: flyquery.semantic:author
POST   /agent/examples                             scope: flyquery.examples:author
GET    /agent/examples                             scope: flyquery.examples:read
POST   /agent/query                                scope: flyquery.query:read
POST   /agent/query/stream                         scope: flyquery.query:read
POST   /agent/query:explain                        scope: flyquery.query:read
POST   /agent/query:validate                       scope: flyquery.query:read
POST   /agent/sql:execute                          scope: flyquery.sql:execute (workspace.allow_direct_sql required)
POST   /agent/sql:execute/stream                   scope: flyquery.sql:execute
```

All carry standard headers: `X-Tenant-Id`, `X-Workspace-Id`, `X-Correlation-Id`, `X-Agent-Token`, `Idempotency-Key` (on writes).

### 7.3 Scope catalog (token scopes)

```
flyquery.datasets:read         list/get datasets
flyquery.datasets:write        create/update/delete datasets
flyquery.files:upload          POST /files + PUT /tables/{id}:upload
flyquery.files:read            read file metadata
flyquery.schema:read           read schema catalog (incl. samples)
flyquery.schema:annotate       edit description/pii_tag/synonyms/governance/type-hint
flyquery.relations:read        read relations
flyquery.relations:write       create/approve/reject relations
flyquery.semantic:read         read metrics/dimensions/glossary
flyquery.semantic:author       create/edit metrics/dimensions/glossary
flyquery.examples:read         read APPROVED examples
flyquery.examples:author       propose/approve/reject examples
flyquery.query:read            POST /query (SELECT-only against ingested tables)
flyquery.derived:write         POST /tables:derive + INSERT/UPDATE/DELETE on DERIVED tables
flyquery.sql:execute           POST /sql:execute (workspace.allow_direct_sql=true required)
flyquery.conversations:*       manage conversations
flyquery.ingest:read           list jobs + events
flyquery.ingest:run            start any ingest job kind
flyquery.lineage:read          read lineage (relations + derived-table provenance)
flyquery.audit:read            read audit events
flyquery.billing:read          read cost rollups
*                              operator-only wildcard (never default)
```

A token's effective grant is the intersection of (token scopes) ∩ (`dataset_allowlist_json`) ∩ (`workspace_allowlist_json`) ∩ (AST classification of generated SQL) ∩ (target `table.kind` — `UPLOADED` rejects all writes; `DERIVED` accepts writes only with `flyquery.derived:write`). The executor refuses if any of these denies.

## 8. Query pipeline (the heart of `/query`)

```
NL question + (conversation_id?, dataset_id?)
       │
       ▼
Hybrid Retrieval (BM25 + pgvector + RRF) over:
  flyquery_schema_objects (TABLE + COLUMN, current snapshot only, is_active=true)
  flyquery_relations
    (status=APPROVED ∪
     (status=PROPOSED AND kind=HEURISTIC AND confidence ≥ FLYQUERY_RELATION_HEURISTIC_MIN_CONFIDENCE))
    -- AGENT_PROPOSED relations are NEVER auto-used; they require human approval first
  flyquery_semantic_metrics (status=PUBLISHED)
  flyquery_glossary_terms
  flyquery_examples (quality=APPROVED only)
       │
       ▼
Cross-encoder reranker  (top-30 → top-10; on by default; FLYQUERY_RERANKER_MODEL)
       │
       ▼
GroundingAgent
   output: GroundedContext {
     path: SEMANTIC_LAYER | SYNTHESIS | HYBRID,
     tables[], columns[], joins[], metrics[], examples[], glossary_terms[],
     confidence, missing_info: list[str] | None
   }
   if conversation_id: starting_point = prior turn's
     {executed_sql, table_qnames, snapshot_pins}
   if confidence < FLYQUERY_GROUNDING_MIN_CONFIDENCE AND missing_info:
     emit clarification SSE frame alongside the answer that follows
       │  (expand loop max EXPAND_ITERS=2 when missing_info is non-empty)
       ▼
   ┌── SEMANTIC_LAYER ──┐    ┌── SYNTHESIS ──┐
   │ MetricFlow → SQL    │    │ GenerationAgent │
   │ (deterministic)     │    │ N=3 candidates  │
   └─────────┬───────────┘    └────────┬────────┘
             └────────► merge ◄────────┘
       │
       ▼
AST classifier (sqlglot + DuckDB parse) + scope/firewall check
   single-statement only;
   reject DDL on uploaded tables;
   reject INSERT/UPDATE/DELETE on uploaded tables (allowed on derived with scope);
   reject SQL referencing tables outside dataset_allowlist;
   reject DuckDB host-touching functions outside our prefix
       │
       ▼
DuckDB executor (in-process per-request)
   ATTACH parquet/v{snapshot_n} for each referenced table (httpfs for cloud; local fs otherwise)
   SET memory_limit = FLYQUERY_DUCKDB_MEMORY_LIMIT,
       statement_timeout = call's effective value,
       wrap result in LIMIT row_cap+1 to detect overflow
       │
   ┌───┴───┐
   ▼       ▼
 OK    ERROR
   │     ▼
   │  CriticAgent (max RETRIES = FLYQUERY_MAX_REFINE_RETRIES, default 2)
   │     │ output: RefinedSql + reasoning
   │     ▼ loop back to AST check
   ▼
ExplainerAgent → NLAnswer + ChartHint (line | bar | table | pie | none)
       │
       ▼
Conversation memory: if conversation_id given, append turn with executed_sql + summary
   + table_qnames + snapshot_pins
       │
       ▼
Auto-learn: if execution_status=OK AND retries=0 AND no PII findings AND
   no clarification emitted, insert flyquery_examples
   (source=AGENT_LEARNED, quality=PROPOSED, embedding, citation=this query_id)
       │
       ▼
Recorder → flyquery_queries + audit_events + cost_events
   Write full result to results/{query_id}.parquet via ObjectStore
   Write preview JSON to flyquery_query_results
       │
       ▼
AnswerResponse / SSE final frame  (final includes presigned URL)
```

### 8.1 Query-pipeline agents

| Agent | output_type | Reads | Writes | Notes |
| --- | --- | --- | --- | --- |
| GroundingAgent | `GroundedContext` | Retrieval hits (post-rerank) + drill-down starting_point | — | Iterative expansion if confidence < `GROUNDING_MIN_CONFIDENCE` and `missing_info` non-empty (up to `EXPAND_ITERS`). |
| GenerationAgent | `GeneratedCandidates` (N candidates) | `GroundedContext` | — | N = `FLYQUERY_GENERATION_CANDIDATES` (default 3). Prompt explicitly orders trust: `SEMANTIC_LAYER > UPLOADED_TABLE`. |
| CriticAgent | `RefinedSql` | candidates + execution error/result | — | Always invoked on error; optionally on success to rank when N>1. |
| ExplainerAgent | `ResultExplanation` | executed_sql + result_preview | — | NL summary + chart hint. |

Following canon/radar: every agent built fresh per call (`auto_register=False`), no tool calls, structured `output_type`. Streaming at controller level (SSE), not inside agents. `timed_agent_run` middleware records elapsed + token usage to `flyquery_cost_events`. Beware `stream.usage()` vs `result.usage()` (per `agent_test_mocking` memory).

## 9. Hexagonal adapters

### 9.1 `ObjectStore` port

```python
class ObjectStore(Protocol):
    async def put(self, key: str, body: bytes | AsyncIterator[bytes],
                  content_type: str, kms_key_uri: str | None = None) -> ObjectMeta: ...
    async def get(self, key: str) -> AsyncIterator[bytes]: ...
    async def head(self, key: str) -> ObjectMeta: ...
    async def delete(self, key: str) -> None: ...
    async def list(self, prefix: str) -> AsyncIterator[ObjectMeta]: ...
    async def presign_get(self, key: str, ttl_s: int) -> str: ...
    async def copy(self, src_key: str, dst_key: str) -> None: ...
```

Adapters under `core/services/storage/adapters/`:
- `local_fs_object_store.py` — aiofiles; bucket-base = `FLYQUERY_OBJECT_STORE_BASE`
- `s3_object_store.py` — `aiobotocore`; honours `kms_key_uri` via SSE-KMS
- `gcs_object_store.py` — `gcloud-aio-storage`; honours `kms_key_uri` via CMEK
- `azure_blob_object_store.py` — `azure-storage-blob`; honours `kms_key_uri` via customer-provided keys

Factory: `core/services/storage/object_store_factory.py` selects by `FLYQUERY_OBJECT_STORE`. Cloud SDKs behind `pyproject.toml` extras: `[s3,gcs,azure]`. Default install brings local-fs only.

### 9.2 `FileReader` port

```python
class FileReader(Protocol):
    formats: ClassVar[tuple[str, ...]]    # e.g., ("csv", "tsv")
    compressions: ClassVar[tuple[str, ...]] = ("none", "gz", "zip", "bz2")
    async def detect(self, head_bytes: bytes, filename: str) -> bool: ...
    async def enumerate_tables(self, file_handle: AsyncIO,
                                rules: TableExtractionRules) -> list[ProposedTable]: ...
    async def materialise(self, file_handle: AsyncIO, table: ProposedTable,
                           target_parquet: ObjectStoreKey, *,
                           workspace_locale: str,
                           type_infer_sample_rows: int) -> MaterialiseResult: ...
```

Implementations under `core/services/ingestion/readers/`:
- `csv_reader.py` (CSV + TSV) — chardet + delimiter sniff + DuckDB `read_csv_auto`
- `excel_reader.py` (xlsx + xls + ods) — `python-calamine`; one table per sheet
- `json_reader.py` (json + jsonl) — DuckDB `read_json_auto`
- `parquet_reader.py` — pass-through (write-through to snapshot key)
- `avro_reader.py`, `orc_reader.py`, `arrow_reader.py` — DuckDB read functions where available; Arrow IPC + Feather via PyArrow

Factory: `core/services/ingestion/reader_factory.py` selects by (format, compression). Compression handlers (`gzip`, `zipfile`, `bz2`) decompress to temp then delegate.

### 9.3 `DialectAdapter` port (single adapter in v0)

```python
class DialectAdapter(Protocol):
    dialect: Literal["duckdb"]
    async def execute(self, sql: str, *, attached_tables: dict[str, str],
                      row_cap: int, statement_timeout_ms: int,
                      memory_limit: str) -> ExecutionResult: ...
    async def explain(self, sql: str, *, attached_tables: dict[str, str]) -> ExplainPlan: ...
    def ast_classify(self, sql: str) -> AstClassification: ...
    def lint(self, sql: str) -> list[LintFinding]: ...
```

Implementation: `core/services/execution/adapters/duckdb_adapter.py`. ATTACHes Parquet paths under `attached_tables` (qualified_name → object-store key resolved via httpfs or local fs). Read-only connection mode; rejects extensions touching the host (only `httpfs` + `parquet` + `json` + `arrow` allowed).

### 9.4 Other ports (already proven in canon)

```
core/services/retrieval/    VectorStore + Corpus (reuse canon corpus_factory verbatim)
core/services/auth/         RateLimiter (memory|redis), IdempotencyStore (memory|redis)
core/services/pii/          PiiScanner (regex|presidio|disabled)
core/services/semantic/     SemanticCompiler (default: metricflow_compiler.py)
```

### 9.5 Object-store key layout

All keys are namespaced by `(tenant_id, workspace_id, dataset_id)`. Original files live under `files/` (one blob per upload, shared across the tables that derive from it). Per-table snapshots live under `tables/{table_id}/`. Derived-table snapshots live under `derived/{table_id}/`. Query results live under `results/`. The leading `flyquery/` prefix is bucket-relative and configurable via `FLYQUERY_OBJECT_STORE_BASE`.

```
flyquery/
  {tenant_id}/
    {workspace_id}/
      {dataset_id}/
        files/{file_id}.{ext}                          # original upload, kept for audit + re-derive
                                                       # one blob even when a file produces multiple tables
        tables/{table_id}/v{snapshot_n}.parquet         # ingested-table snapshots (atomic-swap target)
        derived/{table_id}/v{snapshot_n}.parquet        # derived-table snapshots (CREATE TABLE … AS SELECT)
        results/{query_id}.parquet                      # full query results (TTL = FLYQUERY_RESULT_TTL_HOURS)
```

Implications:
- A single `flyquery_files` row (one upload) maps to one `files/{file_id}.{ext}` blob, even when XLSX with 3 sheets produces 3 `flyquery_tables` rows. Each table's snapshots are stored separately and reference the file via `flyquery_tables.source_file_id` for lineage.
- Re-uploading into a table slot (`PUT /datasets/{ds}/tables/{table_id}:upload`) creates a *new* `flyquery_files` row → a new `files/{file_id}.{ext}` blob → a new `tables/{table_id}/v{n+1}.parquet`. The previous blob and parquet are retained for snapshot pinning + audit until workspace retention expires.
- Workspace-wide purge (`DELETE /workspaces/{id}:purge`) walks the `{tenant_id}/{workspace_id}/` prefix and removes everything in one pass after a 30-day tombstone window.

## 10. Conversation memory

Same wiring as canon `AnswerService`, with drill-down extensions:

- Endpoint: `POST /conversations/{id}/turn` carries `question`
- `QueryService.answer()` resolves prior turns: `[(question_n-2, summary_n-2, executed_sql_n-2, table_qnames_n-2, snapshot_pins_n-2), …]`
- Build pydantic-ai `ModelRequest`/`ModelResponse` history → passed as `message_history=` to GroundingAgent (only)
- GenerationAgent receives a structured `starting_point` block with the prior turn's `executed_sql`, list of in-scope `table_qnames`, and `snapshot_pins` to keep historical reproducibility
- Each new turn persists its own `executed_sql`, `summary`, `table_qnames_json`, `snapshot_pins_json`
- Rolling conversation `summary` lives on the conversation row, fed into the system-instructions slot (same as canon)

## 11. Streaming contract

SSE frames on `/query/stream` and `/agent/query/stream` (all JSON):

```
event: schema_linked     data: {grounded_context_summary, semantic_path, missing_info, candidate_table_count}
event: clarification     data: {questions: [str], reasons: [str]}             -- alongside answer, non-blocking
event: sql_generated     data: {candidate_count, chosen_index, candidate_summaries}
event: executed          data: {row_count, elapsed_ms, retried_after_error, snapshot_pins: {table_id: snapshot_id}}
event: explained         data: {summary, chart_hint}
event: final             data: <AnswerResponse JSON>   -- includes presigned URL to results/{query_id}.parquet
event: error             data: {type, title, status, code, detail, errors[]}   -- RFC 7807
```

SSE on `/ingest-jobs/{id}/stream` and `/agent/ingest-jobs/{id}/stream` mirror the 10 stages of §6:

```
event: received           data: {file_id, file_format, compression, size_bytes}
event: parsed             data: {tables_extracted: [{table_id, name, n_columns, n_rows_estimate}]}
event: reconciled         data: {table_id, n_added, n_removed, n_type_changed, n_renamed_candidate}
event: sampled            data: {table_id, columns_sampled, columns_skipped}
event: profiled           data: {table_id, tables_profiled, tables_skipped}
event: relations_proposed data: {heuristic, agent_proposed, dataset_total_relations}
event: described          data: {table_id, objects_described, budget_remaining_cents}
event: pii_tagged         data: {table_id, tags_set, redactions, late_redactions}
event: embedded           data: {table_id, embeddings_written}
event: snapshot_ready     data: {table_id, snapshot_id, snapshot_hash, parquet_byte_size}
event: final              data: <IngestJobResult JSON>
event: error              data: {type, title, status, code, detail, errors[]}
```

SSE on `/sql:execute/stream`:

```
event: ast_classified     data: {classification, single_statement, table_refs[]}
event: executed           data: {row_count, elapsed_ms, snapshot_pins: {...}}
event: final              data: <SqlExecuteResponse JSON>
event: error              data: {type, title, status, code, detail, errors[]}
```

## 12. Configuration

env_template mirrors canon's shape. Service-specific keys:

```
# Service
FLYQUERY_LOG_LEVEL=INFO
FLYQUERY_PORT=8520
FLYQUERY_DATABASE_URL=postgresql+asyncpg://flyquery@localhost:5432/flyquery
RUN_MIGRATIONS=true

# Object store (ObjectStore port)
FLYQUERY_OBJECT_STORE=local                          # local|s3|gcs|azure
FLYQUERY_OBJECT_STORE_BASE=/var/lib/flyquery/blobs   # or s3://bucket | gs://bucket | azure://container
FLYQUERY_OBJECT_STORE_KMS_DEFAULT=                   # default KMS URI; workspace.kms_key_uri overrides
FLYQUERY_OBJECT_STORE_PRESIGN_TTL_S=86400            # 24h

# DuckDB execution
FLYQUERY_DUCKDB_HTTPFS=true
FLYQUERY_DUCKDB_HTTPFS_METADATA_CACHE_MB=512
FLYQUERY_DUCKDB_MEMORY_LIMIT=4GB
FLYQUERY_DEFAULT_ROW_CAP=1000
FLYQUERY_DEFAULT_STATEMENT_TIMEOUT_MS=30000
FLYQUERY_RESULT_PREVIEW_MAX_BYTES=131072             # 128 KiB
FLYQUERY_RESULT_TTL_HOURS=24

# Upload caps
FLYQUERY_MAX_FILE_MB=2048                            # 2 GB
FLYQUERY_MAX_WORKSPACE_GB=200

# Ingestion knobs
FLYQUERY_INGEST_TOPIC=flyquery.ingest
FLYQUERY_INGEST_WORKER_CONCURRENCY=4
FLYQUERY_INGEST_HANDLER_TIMEOUT_S=600
FLYQUERY_INGEST_SHUTDOWN_GRACE_S=30
FLYQUERY_SAMPLE_N=8
FLYQUERY_PROFILE_ROW_THRESHOLD=10000000
FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN=200
FLYQUERY_DESCRIBE_BATCH=20
FLYQUERY_RELATION_PROPOSER_ENABLED=true
FLYQUERY_RELATION_PROPOSER_MAX_PER_PAIR=3
FLYQUERY_RELATION_HEURISTIC_MIN_CONFIDENCE=0.85       # PROPOSED+HEURISTIC relations enter retrieval at this threshold
FLYQUERY_MAX_TITLE_ROWS=3
FLYQUERY_TYPE_INFER_SAMPLE_ROWS=8192
FLYQUERY_DEFAULT_LOCALE=en-US

# Pipeline knobs (LLM)
FLYQUERY_GROUNDING_MODEL=anthropic:claude-sonnet-4-6
FLYQUERY_GENERATION_MODEL=anthropic:claude-sonnet-4-6
FLYQUERY_CRITIC_MODEL=anthropic:claude-sonnet-4-6
FLYQUERY_EXPLAINER_MODEL=anthropic:claude-haiku-4-5
FLYQUERY_DESCRIBE_MODEL=anthropic:claude-haiku-4-5
FLYQUERY_RELATION_PROPOSER_MODEL=anthropic:claude-sonnet-4-6
FLYQUERY_RENAME_DETECT_MODEL=anthropic:claude-haiku-4-5
FLYQUERY_FALLBACK_MODEL=openai:gpt-4o
FLYQUERY_GENERATION_CANDIDATES=3
FLYQUERY_MAX_REFINE_RETRIES=2
FLYQUERY_EXPAND_ITERS=2
FLYQUERY_GROUNDING_MIN_CONFIDENCE=0.55
FLYQUERY_AGENT_MAX_OUTPUT_TOKENS=8192

# Embeddings + retrieval (lock-step canon)
FLYQUERY_EMBEDDING_MODEL=openai:text-embedding-3-small
FLYQUERY_EMBEDDING_DIMENSIONS=1536
FLYQUERY_VECTOR_STORE=pgvector
FLYQUERY_TOP_K_SCHEMA=12
FLYQUERY_TOP_K_EXAMPLES=5
FLYQUERY_TOP_K_METRICS=8
FLYQUERY_RRF_K=60
FLYQUERY_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
FLYQUERY_RERANKER_TOP_N=30
FLYQUERY_QUERY_EXPANSION_ENABLED=false

# PII
FLYQUERY_PII_SCANNER=regex                           # regex|presidio|disabled
FLYQUERY_PII_POLICY_SAMPLES=redact                   # warn|redact|reject
FLYQUERY_PII_POLICY_RESULTS=warn                     # warn|redact|reject

# Auth + backends (lock-step)
FLYQUERY_REDIS_URL=
FLYQUERY_RATE_LIMIT_BACKEND=auto
FLYQUERY_IDEMPOTENCY_BACKEND=auto

# EDA
FLYQUERY_EDA_ADAPTER=postgres                        # postgres|redis|kafka|memory
FLYQUERY_EDA_DESTINATIONS=flyquery.ingest,flyquery.schema,flyquery.audit
FLYQUERY_EDA_GROUP=flyquery-workers
```

`pyfly.yaml` mirrors canon's: `web/server/observability/metrics/tracing/actuator/admin/aop/resilience/cqrs/cache/eda/data.relational` sections, with `service-name: flyquery` and `port: 8520`.

## 13. Testing strategy

- **Unit (`tests/unit/`)**: in-memory SQLite for the KB (with pgvector shim), mocked agents (return canned structured outputs), in-memory ObjectStore, real DuckDB in-process for SQL surface tests. Run via `pytest -m 'not llm and not integration'`.
- **Integration (`tests/integration/`, mark `@pytest.mark.integration`)**: testcontainers `pgvector/pgvector:pg16`; LocalFs ObjectStore on tmp dir; real DuckDB in-process. Two-role split — `flyquery_admin` BYPASSRLS for migrations + `flyquery_app` no-bypass for sessions, per `postgres_test_role_bypasses_rls`. Real RLS isolation tests.
- **Object-store adapter tests** (`tests/integration/object_store/`): MinIO behind `@pytest.mark.s3`; `fake-gcs-server` behind `@pytest.mark.gcs`; Azurite behind `@pytest.mark.azure_blob`. Cloud-creds adapters skipped without env.
- **File-format tests** (`tests/integration/parsers/`): golden CSV/TSV/XLSX/XLS/ODS/JSON/JSONL/Parquet/Avro/ORC/Feather + compressed variants. Each format gets happy + 3-5 edge cases: BOM detection, mixed-quote CSV, merged-cell title rows, ragged JSON arrays, schema drift, encoding misdetection, zip-bomb rejection, gzip-pass-through.
- **Pipeline tests**: tiny Northwind-style fixture (4 CSVs: orders, customers, products, employees). Cover: first-upload happy path, second-upload column added, third-upload column renamed (RENAMED_CANDIDATE flow), conversation drill-down ("now by region" carries prior SQL), semantic-layer metric usage, write-rejected-on-ingested-table, write-allowed-on-derived-table, direct-SQL gated by `workspace.allow_direct_sql`.
- **Adapter conformance tests**: each ObjectStore adapter must pass the shared conformance pack (put/get/head/delete/list/presign/copy + KMS round-trip + concurrent puts + large-file streaming).
- **Agent test gotcha**: per `agent_test_mocking`, `MagicMock(stream.usage())` blows up cost tracking — fixtures must return `None` or a real `Usage` object.

## 14. Lock-step modules

Copied byte-equivalent from canon/radar:

```
src/flyquery/web/agent_deps.py                                        (~3.7 KB)
src/flyquery/web/conventions/{middleware,deps,headers,actor,context,
    validation,errors,idempotency,redis_idempotency,db,handlers}.py
src/flyquery/core/services/auth/agent_token_service.py                (modulo service-name strings)
src/flyquery/core/services/auth/redis_rate_limiter.py
src/flyquery/web/controllers/agent_tokens_controller.py               (adapted for flyquery scope catalog)
src/flyquery/core/agents/builder.py                                   (build_agent factory)
src/flyquery/core/observability/__init__.py                           (DEFAULT_MIDDLEWARE stack)
src/flyquery/web/openapi_override.py
```

Per the `lock_step_conventions_canon_radar` memory, every patch to these in flyquery must be diffed against the canon/radar twins. `scripts/check_lockstep.py` (Plan 1) is the CI gate.

## 15. Build order (high-level)

### Plan 1 — Foundation

1. Scaffold repo + pyproject + Dockerfile + pyfly.yaml + Taskfile + CHANGELOG/CONTRIBUTING/README/QUICKSTART/LICENSE
2. Copy lock-step modules verbatim from canon
3. Alembic baseline migration covering all ~20 tables + RLS policies (admin/app role split)
4. Workspace + dataset CRUD with RLS integration tests
5. Agent tokens + scope catalog mint/verify flow
6. `ObjectStore` port + LocalFs adapter + S3 adapter (behind `[s3]` extra)
7. `scripts/check_lockstep.py` CI gate

### Plan 2 — File ingestion

8. `FileReader` port + readers (csv/tsv/xlsx/xls/ods/json/jsonl/parquet/avro/orc/arrow/feather) + compression handlers (gz/zip/bz2)
9. Ingestion pipeline phase 1 — synchronous receive + parse + reconcile + snapshot persist + atomic READY swap + RLS-aware repositories
10. Ingestion pipeline phase 2 — async orchestrator (EDA topic, IngestWorker, ingest_events streaming, SSE controller, ingest_jobs lifecycle, cooperative cancel)
11. Ingestion pipeline phase 3 — sample + profile collection (with PIIScanner port reused from canon, ordering guarantee §6 stage 4)
12. Ingestion pipeline phase 4 — relation discovery (heuristic + `RelationProposerAgent`) + `DescribeAgent` (with budget cap, batched)
13. Ingestion pipeline phase 5 — embedding + hybrid retrieval + cross-encoder reranker setup over schema KB
14. Re-upload + schema drift + `RenameDetectionAgent` + annotation transplant
15. GCS + AzureBlob ObjectStore adapters (behind `[gcs]` + `[azure]` extras)

### Plan 3 — Query pipeline

16. Examples + glossary CRUD + `AGENT_LEARNED` auto-promotion on first-shot OK runs
17. Semantic layer (MetricFlow YAML schema, validation, deterministic compilation to DuckDB SQL)
18. Query pipeline: Grounding → Generation → DuckDB Executor → Critic → Explainer
19. Clarification frame + drill-down conversation context (prior `executed_sql + table_qnames + snapshot_pins`)
20. SSE on `/query/*` + agent-tier mirrors
21. `/sql:execute` (direct SQL behind `workspace.allow_direct_sql`)
22. `/tables:derive` + INSERT/UPDATE/DELETE on derived tables (scope `flyquery.derived:write`)

### Plan 4 — Packaging

23. SDK generation (`sdks/python`, `sdks/java`)
24. Docs (`docs/architecture.md`, `docs/api-reference.md`, `docs/ingestion.md`, `docs/file-formats.md`, `docs/semantic-layer.md`, `docs/security.md`, `docs/deployment.md`, `docs/payload-reference.md`, `QUICKSTART.md`)
25. CI workflows mirroring canon (lint, test-unit, test-integration, build, publish-sdk, lockstep-check)

### v1+ follow-ups

26. flydesk-frontend `/flyquery` route (drag-drop upload, dataset browser, chat-style query, SSE pipeline view, result table + chart hint render)
27. MCP server (file-attach + `/query`)
28. Cost enforcement (rate_limit_rpm + per-workspace budget gating)
29. Per-workspace KMS/CMEK plumbing past storage-native default (KEK/DEK envelope, GDPR-safe key revocation)
30. `GovernanceClassifierAgent` (sensitivity / retention class) for regulated industries
31. `/tables:explode` (nested JSON explode into a new table)
32. Drift watchdog for scheduled REPARSE jobs (e.g., source file refreshed by external process)

**v0 cut-line**: Plans 1+2+3+4 ship the demoable v0. Items 26-32 are v1+, individually shippable.

A detailed implementation plan per phase is produced via the `superpowers:writing-plans` skill once this design is approved.

## 16. Out of scope (for v0)

- Web frontend (deferred to v1; backend-only with SDK + agent-tier for v0)
- MCP server (v1+)
- Streaming results (we return preview + presigned Parquet URL; no row-level stream)
- Federation across workspaces or tenants
- Connections to remote databases (DSNs, JDBC, ODBC)
- dbt manifest ingestion + dbt lineage
- OpenAPI specs as data sources
- Push to canon as canon knowledge items (deferrable; same `agent/canon/handoff` shape if/when wanted)
- BI dashboard rendering / chart generation (we emit chart hints only)
- Online learning from user feedback beyond promoting `(Q, SQL)` examples
- Fine-tuning local models
- Drift watchdog scheduling for external file refreshes
- Cost enforcement (observe v0, enforce v1)

## 17. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Malicious upload (zip bomb, polyglot file, billion-laughs JSON) | Size cap (`FLYQUERY_MAX_FILE_MB`) + magic-byte format verify + per-reader hardening (zip with N-file + decompressed-size caps); each parse opens in a worker with cgroup memory limit. |
| Stored file leaks (object-store misconfig) | Per-tenant key prefix + storage-native SSE; presigned URLs scoped to single key + short TTL (`FLYQUERY_OBJECT_STORE_PRESIGN_TTL_S`); never include raw URIs in API responses. |
| Generated SQL slips through firewall (multi-statement, DDL, file-system functions) | sqlglot AST per statement + DuckDB parse double-check + read-only DuckDB connection mode + reject extensions touching the host (only `httpfs` + `parquet` + `json` + `arrow` allowed; httpfs paths restricted to our prefix). |
| PII in samples leaks via `/schema-objects:search` | PIIScanner gate BEFORE sample persistence; runtime re-redact on late tag flip; samples gated on `flyquery.schema:read` scope. |
| Cross-tenant DuckDB contamination | New connection per request; no shared ATTACH state; no shared temp tables; explicit memory_limit per connection. |
| Drift in lock-step modules | `scripts/check_lockstep.py` CI gate diffs against canon/radar SHAs; PR blocked on mismatch. |
| Schema KB blowup (10k+ columns from a CRM export) | `ingest_policy_json` include/exclude mandatory above warn threshold; embedding budget cap per ingest; partial snapshots persisted on overflow with `status=PARTIAL`. |
| Re-upload silently changes annotated columns | Annotations preserved by `(qualified_name, column_name)` match; `RENAMED_CANDIDATE` rows surface ambiguity for one-click confirm; `flyquery_schema_changes` retained for audit. |
| Long-running parse blocks workers | Per-file parse timeout (`FLYQUERY_INGEST_HANDLER_TIMEOUT_S`); oversize files rejected at upload; FAILED jobs retain original for retry. |
| DuckDB OOM on huge ad-hoc aggregation | Per-connection `FLYQUERY_DUCKDB_MEMORY_LIMIT`; per-call `statement_timeout`; result `LIMIT row_cap+1` for overflow detection. |
| Semantic-layer YAML drift across MetricFlow versions | Parser pins to a tested MetricFlow schema range; unknown keys logged not raised; `metadata_json.metricflow_raw` preserves the raw definition. |
| User mismaps re-upload (orders.csv into customers slot) | PUT verb + explicit `table_id` in path forces intent; `/tables/{id}/changes` exposes diff before READY swap. |
| GDPR purge race with in-flight queries | `:purge` enqueues a synchronous purge job that drains in-flight queries (cooperative cancel) before walking the workspace prefix; 30-day tombstone retained for accident recovery before bytes vanish. |
| Atomic snapshot swap interrupted mid-flight | Snapshot transitions `PARTIAL → READY` only after stage 10; the previous READY snapshot remains the source of truth for queries until the new one fully lands; no half-ingested window. |

## 18. Resolved open items (from initial spec §16)

The original spec listed 4 open items; the brainstorming round resolved them:

| Item | Resolution |
| --- | --- |
| GitHub topics | See §20 below |
| `flyquery_examples` per-data_source vs workspace-wide | **Per-dataset OR workspace-wide** — `dataset_id` nullable; null = workspace-wide |
| Initial port number | **8520** (canon=8500, radar=8510) |
| Semantic-layer YAML also in object storage | **DB-only in v0**; export endpoint can be added in v1 if needed |

Additionally resolved in the brainstorming round:
- Source-kind taxonomy → single **upload** kind (no DATABASE, DBT_MANIFEST, OPENAPI)
- Storage architecture → **Parquet on object storage + DuckDB query layer**
- Object stores → **LocalFs + S3 + GCS + Azure Blob** behind hexagonal port
- File formats → **CSV/TSV/XLSX/XLS/ODS/JSON/JSONL/Parquet/Avro/ORC/Feather/Arrow** + .gz/.zip/.bz2
- Hierarchy → **Workspace > Dataset > File > Table**
- Re-upload identity → **user selects target** via `PUT /datasets/{ds}/tables/{table_id}:upload`
- v0 UI → **backend-only**; SPA in v1
- Write paths → **read on uploaded; read + DML on derived only** (`POST /tables:derive`)
- Direct SQL → **`POST /sql:execute` behind `workspace.allow_direct_sql`**
- Clarification → **hybrid guess + clarification frame** alongside answer
- DuckDB mode → **in-process per-request**
- Encryption → **storage-native SSE default; per-workspace CMK/CMEK upgrade**
- Retention/purge → **per-workspace `retention_days` default null; `DELETE /workspaces/{id}:purge` with 30-day tombstone**
- Schema drift → **auto-apply + diff log + annotation transplant + LLM rename detection**
- Multi-table rules → **spec-driven conservative**
- Conversation drill-down → **prior SQL + table_qnames + snapshot_pins carried forward**
- Auto-learning → **auto-propose, human-approve**
- Quotas → **observe v0, enforce v1**
- Reranker default → **cross-encoder on**; embedding lock-step with canon
- Type inference → **DuckDB auto + workspace locale + LLM fallback**
- Result delivery → **preview JSON + presigned Parquet URL**
- MCP → **v1+**
- Op defaults → port **8520**, max file **2 GB**, max workspace **200 GB**, EDA = postgres LISTEN/NOTIFY, PII scanner = regex, Idempotency-Key store auto

## 19. Open items (post-approval)

- Confirm `pyfly.yaml` sections match canon's verbatim (will be verified during Plan 1 task 1)
- Confirm precise `python-calamine` vs `openpyxl` choice for XLSX (sample first; default `python-calamine` for performance)
- Decide whether `flyquery_glossary_terms` is workspace-only or dataset-scoped (current spec: workspace-only for cross-dataset terms)
- Confirm `pyproject.toml` extras boundary: `[s3,gcs,azure,presidio,ml-reranker]` — extras names + which adapters they pull
- Decide whether the `RenameDetectionAgent` is always-on or behind `dataset.drift_policy=REVIEW` (current spec: always-on, but the rename row is `RENAMED_CANDIDATE` until human confirms)

## 20. GitHub repo metadata (for `gh repo create`)

- **Owner**: `firefly-operationOS`
- **Name**: `flyquery`
- **Visibility**: `private`
- **License**: proprietary `LICENSE` mirroring canon's wording (SDKs Apache-2.0 in `sdks/`)
- **Description**:
  > Operational Structured-Data Intelligence (upload-driven) — multi-tenant ingestion + Text-to-SQL service over user-uploaded structured files (CSV / TSV / XLSX / XLS / ODS / JSON / JSONL / Parquet / Avro / ORC / Arrow / Feather + compressed variants). Materialises uploads to Parquet on object storage (LocalFs / S3 / GCS / AzureBlob), indexes a long-lived schema knowledge base with samples, profiles, PII tags, embeddings and AI-proposed relations; answers natural-language questions via a multi-agent pipeline (Grounding → Generation → DuckDB Executor → Critic → Explainer) with cross-encoder reranking, semantic-layer (OSI/MetricFlow), Vanna-style few-shot example store, hybrid clarification, conversation drill-down. Hexagonal at every external boundary. Built on fireflyframework-pyfly + fireflyframework-agentic. Part of Firefly OperationOS.
- **Topics**: `text-to-sql`, `nl2sql`, `semantic-layer`, `metricflow`, `osi`, `multi-agent`, `agentic-ai`, `ai-agents`, `claude`, `openai`, `pydantic-ai`, `firefly-framework`, `firefly-operationos`, `pyfly`, `pgvector`, `bm25`, `hybrid-search`, `cross-encoder-reranker`, `duckdb`, `parquet`, `object-storage`, `csv`, `xlsx`, `json`, `data-ingestion`, `data-lakehouse`, `fastapi`, `python`, `openapi`, `microservice`
