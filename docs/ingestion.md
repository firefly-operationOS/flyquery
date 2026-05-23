# flyquery — Ingestion

## Table of Contents

1. [Overview](#1-overview)
2. [Job kinds](#2-job-kinds)
3. [10-stage pipeline](#3-10-stage-pipeline)
   - [Stage 1: receive](#stage-1-receive)
   - [Stage 2: parse](#stage-2-parse)
   - [Stage 3: reconcile + persist snapshot](#stage-3-reconcile--persist-snapshot)
   - [Stage 4: sample](#stage-4-sample)
   - [Stage 5: profile](#stage-5-profile)
   - [Stage 6: relation discovery](#stage-6-relation-discovery)
   - [Stage 7: describe](#stage-7-describe)
   - [Stage 8: PII tag](#stage-8-pii-tag)
   - [Stage 9: embed + index](#stage-9-embed--index)
   - [Stage 10: publish + close snapshot](#stage-10-publish--close-snapshot)
4. [Re-upload semantics](#4-re-upload-semantics)
5. [RENAMED_CANDIDATE flow](#5-renamed_candidate-flow)
6. [Annotation transplant](#6-annotation-transplant)
7. [ingest_policy_json reference](#7-ingest_policy_json-reference)
8. [SSE progress stream](#8-sse-progress-stream)
9. [Configuration knobs](#9-configuration-knobs)

---

## 1. Overview

Ingestion is the process that takes a raw uploaded file and makes it queryable
via DuckDB. It runs asynchronously in `IngestWorker` processes that consume
jobs from the `flyquery.ingest` EDA topic.

Properties of the pipeline:
- **Asynchronous** — upload returns `202 Accepted` + `ingest_job_id`. The
  caller polls or streams to track progress.
- **Restartable** — each stage transition is persisted to
  `flyquery_ingest_events`. A failed job retains the failure reason and can be
  re-queued.
- **Streamable** — `GET /ingest-jobs/{id}/stream` emits SSE events as each
  stage completes.
- **Idempotent across re-ingests** — stage 3 (reconcile) preserves human
  annotations; re-running a `REPARSE` job on the same file produces the same
  snapshot hash.
- **Staged skip policy** — stages 4–8 are individually skippable via
  `ingest_policy_json`. Stages 1–3, 9, and 10 are mandatory.

---

## 2. Job kinds

| Job kind | When to use | Starts from |
|----------|-------------|-------------|
| `PARSE_AND_INGEST` | New file upload or re-upload into an existing slot | Stage 1 (receive) |
| `REPARSE` | Re-run parsing from the existing blob without a new upload (e.g. locale correction) | Stage 2 (parse) |
| `SAMPLE_REFRESH` | Refresh `sample_values_json` for changed columns (skips parse + reconcile) | Stage 4 (sample) |
| `DESCRIBE_PASS` | Run `DescribeAgent` on objects still lacking descriptions (budget-safe background job) | Stage 7 (describe) |
| `RELATION_PASS` | Re-run heuristic + `RelationProposerAgent` across an entire dataset | Stage 6 (relation discovery) |

All five are started via `POST /api/v1/ingest-jobs` or triggered automatically
by uploads.

---

## 3. 10-stage pipeline

### Stage 1: receive

**Input**: `file_id` row in `flyquery_files` with `status=RECEIVED` written
synchronously at upload time.

**What happens**:
1. Verify `content_hash_sha256` matches the bytes stored in object storage.
2. Check `size_bytes` ≤ `FLYQUERY_MAX_FILE_MB × 1048576`.
3. Detect format from magic bytes + file extension. Reject on mismatch (e.g.,
   a renamed ZIP presented as CSV).

**On success**: emits `received` SSE event with `{file_id, file_format, compression, size_bytes}`.

**On failure**: `flyquery_files.status = FAILED`, `error_json` populated.
Job halts; original bytes retained for retry.

---

### Stage 2: parse

**Input**: file bytes from object storage + `table_extraction_rules_json`.

**Per-format dispatch** (via `FileReader` port):

| Format | Behaviour |
|--------|-----------|
| CSV/TSV | `chardet` / `charset-normalizer` encoding detection; delimiter sniffed from first 8 KiB; DuckDB `read_csv_auto(sample_size=FLYQUERY_TYPE_INFER_SAMPLE_ROWS, auto_detect=true)`. Produces one table. |
| XLSX/XLS/ODS | `python-calamine` enumerates sheets; each sheet → one table (sanitised name); merged-cell title rows skipped up to `FLYQUERY_MAX_TITLE_ROWS`. |
| JSON | Top-level array → one table; top-level object with array-valued keys → one table per key. Processed via DuckDB `read_json_auto`. |
| JSONL/NDJSON | One table via DuckDB `read_json_auto`. |
| Parquet | Pass-through schema read; write-through to the snapshot Parquet key. |
| Avro | DuckDB `read_avro` or `pyarrow`; converts to Parquet. |
| ORC | DuckDB `read_orc` or `pyarrow`; converts to Parquet. |
| Arrow / Feather | PyArrow IPC read; converts to Parquet. |
| `.gz` / `.zip` / `.bz2` | Transparent decompression to a temp file; delegates to the inner reader. ZIP archives with more than one entry or decompressed size > cap are rejected. |

**Table extraction rule overrides** (from `table_extraction_rules_json`):
- `sheet_allowlist: [str]` — only materialise named sheets (XLSX/ODS).
- `json_path_spec: [str]` — explicit list of JSON keys to extract.
- `header_skip_rows: int` — skip additional header rows beyond auto-detection.

**Workspace locale** (`default_locale` on the workspace or dataset) is passed
to DuckDB to resolve date-format ambiguity. Example: `FLYQUERY_DEFAULT_LOCALE=de-DE`
causes `01.02.2026` to be read as February 1st rather than January 2nd.

**On success**: Each logical table is materialised as
`{dataset_id}/tables/{table_id}/v{n}.parquet` in object storage.
Emits `parsed` SSE event with `{tables_extracted: [{table_id, name, n_columns, n_rows_estimate}]}`.

---

### Stage 3: reconcile + persist snapshot

**Input**: Materialised Parquet for each logical table; existing
`flyquery_schema_snapshots` row if this is a re-upload.

**What happens**:

1. Insert `flyquery_schema_snapshots` row with `status=PARTIAL`.
2. If a previous `READY` snapshot exists, compute a column-level diff:
   - `ADDED` — column present in new schema but absent in old.
   - `REMOVED` — column present in old but absent in new.
   - `TYPE_CHANGED` — column name unchanged but inferred type changed.
   - `RENAMED` — column absent by name in old, but a uniquely-matching
     (position + type) signature exists in a removed column. Auto-applied.
   - `RENAMED_CANDIDATE` — ambiguous rename (multiple matches, or the
     `RenameDetectionAgent` disagrees with the heuristic). Inserted with
     `llm_rationale`; requires human confirmation.
3. Mark vanished columns `is_active=false` on `flyquery_schema_objects`
   (NOT deleted; historical snapshot pinning relies on them).
4. Run annotation transplant (see [§6](#6-annotation-transplant)).

**On success**: emits `reconciled` SSE event with
`{table_id, n_added, n_removed, n_type_changed, n_renamed_candidate}`.

---

### Stage 4: sample

**Input**: Parquet snapshot + current `flyquery_schema_objects` rows.

**What happens**:
- For each column with `pii_tag=NULL/NONE` and `sample_values_json=NULL`
  (or where the snapshot changed the column):
  1. Read `N=FLYQUERY_SAMPLE_N` values from Parquet via DuckDB.
  2. Pass each value through the `PIIScanner` gate.
  3. If any value triggers a PII match, **do not persist** the sample.
     Set the `pii_source` flag to trigger stage 8 re-tagging.
  4. Otherwise, write to `schema_objects.sample_values_json`.

**Skip conditions**:
- `ingest_policy_json.sample_disabled = true` — skip entire stage.
- Column already has `pii_tag` set to a non-NONE value.

**On success**: emits `sampled` SSE event with
`{table_id, columns_sampled, columns_skipped}`.

---

### Stage 5: profile

**Input**: Parquet snapshot.

**What happens**: Per column:
- `null_fraction` — `COUNT(CASE WHEN col IS NULL THEN 1 END) / COUNT(*)`
- `distinct_estimate` — DuckDB `approx_count_distinct`
- `top_values` — low-cardinality columns only (distinct_estimate < 100)
- `min` / `max` — numeric and temporal columns

Written to `schema_objects.profile_json`.

**Skip conditions**:
- `n_rows_estimate > FLYQUERY_PROFILE_ROW_THRESHOLD` (default 10 million).
  The profile is deferred for large tables to keep ingest time bounded.
- `ingest_policy_json.profile_disabled = true`.

**On success**: emits `profiled` SSE event.

---

### Stage 6: relation discovery

**Input**: All tables in the dataset (not only this upload), their
schema_objects, and existing approved relations.

**Two discovery layers, applied in sequence**:

**Heuristic** — for each column pair `(A.col, B.col)` across tables:
1. Column names are equal (case-insensitive, ignoring `_id` suffix normalisation).
2. Inferred types are compatible (`text ↔ text`, `integer ↔ integer`, etc.).
3. One side satisfies a weak uniqueness constraint:
   `distinct_estimate ≥ FLYQUERY_RELATION_HEURISTIC_MIN_CONFIDENCE × n_rows`.
4. A new `flyquery_relations` row is inserted as
   `kind=HEURISTIC, status=PROPOSED, confidence ∝ uniqueness × name_specificity`.

**Agent-proposed** (requires `FLYQUERY_RELATION_PROPOSER_ENABLED=true`):
- `RelationProposerAgent` receives table summaries, column descriptions, and
  samples for all tables in the dataset.
- Output: a list of `ProposedRelations` with reasoning.
- Inserted as `kind=AGENT_PROPOSED, status=PROPOSED`.
- These are **never** auto-used in query retrieval; they require operator
  approval (`POST /datasets/{id}/relations/{rel_id}:approve`).

High-confidence heuristic relations (`confidence ≥ FLYQUERY_RELATION_HEURISTIC_MIN_CONFIDENCE`)
enter the query-retrieval pool automatically. Agent-proposed relations enter
only after approval.

**On success**: emits `relations_proposed` SSE event.

---

### Stage 7: describe

**Input**: All `flyquery_schema_objects` rows for the current snapshot where
`description IS NULL`.

**What happens**:
- `DescribeAgent` is called in batches of `FLYQUERY_DESCRIBE_BATCH` (default 20).
- Output: per-object short summary + business synonyms.
- Written to `schema_objects.description` with `description_source=AGENT`.
- Budget cap: `FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN` (default 200 cents).
  Objects that exceed the budget are skipped; a `DESCRIBE_PASS` job can be
  scheduled later to pick them up.

**On success**: emits `described` SSE event with
`{table_id, objects_described, budget_remaining_cents}`.

---

### Stage 8: PII tag

**Input**: All schema_objects for the current snapshot.

**What happens**:
- `PIIScanner` classifies each column from `(name + description + sample_values)`.
- Sets `pii_tag` + `pii_source`.
- Policy effects:
  - `warn` — log + continue; samples are retained.
  - `redact` — purge `sample_values_json` for the flagged column; log.
  - `reject` — set column `is_active=false`; the column is not queryable
    until a human reviews and either approves or purges it.
- **Late tag flip**: if `pii_tag` is updated on a column that already has
  `sample_values_json`, samples are scrubbed in-place immediately.

PIIScanner backend is selected by `FLYQUERY_PII_SCANNER`:
- `regex` — built-in pattern library (e-mail, phone, SSN, IBAN, IP, …)
- `presidio` — Microsoft Presidio (requires `[presidio]` extra)
- `disabled` — no PII checks (not recommended for production)

**On success**: emits `pii_tagged` SSE event.

---

### Stage 9: embed + index

**Input**: All schema_objects for the current snapshot.

**Embedding text template** per column:
```
<dataset>.<table>.<column>: <data_type>
<description>
Samples: <preview>
Synonyms: <list>
```

Per-table aggregate embedding rolls up column embedding vectors into a
single centroid for fast table-level retrieval.

Vectors are written to `schema_objects.embedding` and indexed into the
pgvector HNSW index. `content_tsv` is refreshed for BM25.

**On success**: emits `embedded` SSE event.

---

### Stage 10: publish + close snapshot

**What happens** (single atomic transaction):
1. `flyquery_schema_snapshots.status = READY`
2. `flyquery_tables.current_snapshot_id` flips to the new snapshot ID.
3. Publish `flyquery.schema.updated` EDA event with diff summary.
4. Emit `snapshot_ready` SSE event + `final` SSE frame.

Until this transaction commits, the previous READY snapshot remains the
source of truth for all active queries. There is no half-ingested window.

---

## 4. Re-upload semantics

Re-uploading a file into an existing table slot preserves the table's identity
(`table_id` is unchanged) while creating a new versioned snapshot.

```
PUT /api/v1/datasets/{ds}/tables/{table_id}:upload
```

Effect:
1. A new `flyquery_files` row is created (new `file_id`, new blob in object
   storage at `files/{new_file_id}.{ext}`).
2. A new `flyquery_schema_snapshots` row is created (`v{n+1}`).
3. Ingestion runs from stage 2 onward.
4. The previous Parquet blob (`tables/{table_id}/v{n}.parquet`) is **retained**
   until workspace retention expires. Queries that recorded `snapshot_pins`
   pointing to the old snapshot remain reproducible.

**After stage 10 commits**, the new snapshot becomes the default for all
new queries.

**Blob retention policy**: neither the original upload blob nor older Parquet
snapshots are deleted on re-upload. Only workspace purge
(`DELETE /workspaces/{id}:purge`) removes them.

---

## 5. RENAMED_CANDIDATE flow

When stage 3 detects a column rename that does not satisfy the unique-match
heuristic, it invokes `RenameDetectionAgent`:

```
Old schema: [order_id, customer_ref, amount]
New schema: [order_id, cust_id, amount]
```

`customer_ref` removed; `cust_id` added. Name differs; type compatible. Two
rows are inserted in `flyquery_schema_changes`:
- `change=RENAMED_CANDIDATE`, `column_name=customer_ref → cust_id`,
  `llm_rationale="Likely a rename from 'customer_ref' to 'cust_id';
   both are integer FK-style columns."`

Operator reviews via:
- `GET /api/v1/tables/{id}/changes` — see the diff.
- `POST /api/v1/schema-changes/{id}:confirm` — flip to `RENAMED`.
  Annotation transplant from `customer_ref` to `cust_id` runs immediately.
- `POST /api/v1/schema-objects:rename-merge` — manual transplant if needed.

Until confirmed, both `customer_ref` (inactive) and `cust_id` (active) exist in
`flyquery_schema_objects`. The new snapshot is READY; the old column is just
`is_active=false` and excluded from retrieval.

---

## 6. Annotation transplant

When a snapshot is reconciled (stage 3), human-curated annotations are
automatically carried forward from the previous snapshot to matching columns
in the new snapshot by `(qualified_name, column_name)`:

| Annotation | Transplanted? | Notes |
|------------|--------------|-------|
| `description` (HUMAN source) | Yes | AI-generated descriptions are **not** transplanted; they are regenerated in stage 7 |
| `pii_tag` (HUMAN source) | Yes | Preserves human PII decisions across re-uploads |
| `business_owner` | Yes | |
| `governance_json` | Yes | |
| `synonyms_json` | Yes | |
| `description` (AGENT source) | No | Re-generated in stage 7 |
| `pii_tag` (REGEX/PRESIDIO/AGENT source) | No | Re-detected in stage 8 |
| `sample_values_json` | No | Re-collected in stage 4 |
| `profile_json` | No | Re-computed in stage 5 |

Transplant only applies to exact name matches. Columns that changed type
have their annotations transplanted but `TYPE_CHANGED` is logged in
`flyquery_schema_changes`.

---

## 7. ingest_policy_json reference

Set at dataset level via `PUT /api/v1/datasets/{id}`. Overrides are JSON:

```json
{
  "sample_disabled": false,
  "profile_disabled": false,
  "describe_disabled": false,
  "relation_proposer_disabled": false,
  "pii_scanner_override": "regex",
  "pii_policy_samples_override": "redact",
  "include_columns": ["order_id", "amount", "region"],
  "exclude_columns": ["internal_note", "raw_json"],
  "describe_budget_cents_override": 500,
  "describe_batch_override": 50,
  "type_infer_sample_rows_override": 16384,
  "max_title_rows_override": 5
}
```

All keys are optional. Absent keys fall back to service-level env defaults.

`include_columns` and `exclude_columns` apply to the embedding and sample
stages. Excluded columns are still materialised in Parquet (for query
correctness) but are not sampled, embedded, or described.

---

## 8. SSE progress stream

Connect to `GET /api/v1/ingest-jobs/{id}/stream` for live stage events.
Events arrive as each stage completes; the stream closes on `final` or `error`.

```
event: received
data: {"file_id": "...", "file_format": "xlsx", "compression": "none", "size_bytes": 204800}

event: parsed
data: {"tables_extracted": [{"table_id": "...", "name": "Sheet1", "n_columns": 12, "n_rows_estimate": 5000}]}

event: reconciled
data: {"table_id": "...", "n_added": 1, "n_removed": 0, "n_type_changed": 0, "n_renamed_candidate": 1}

event: sampled
data: {"table_id": "...", "columns_sampled": 11, "columns_skipped": 1}

event: profiled
data: {"table_id": "...", "tables_profiled": 1, "tables_skipped": 0}

event: relations_proposed
data: {"heuristic": 3, "agent_proposed": 1, "dataset_total_relations": 7}

event: described
data: {"table_id": "...", "objects_described": 13, "budget_remaining_cents": 187}

event: pii_tagged
data: {"table_id": "...", "tags_set": 1, "redactions": 1, "late_redactions": 0}

event: embedded
data: {"table_id": "...", "embeddings_written": 13}

event: snapshot_ready
data: {"table_id": "...", "snapshot_id": "...", "snapshot_hash": "sha256:abc...", "parquet_byte_size": 98304}

event: final
data: {"job_id": "...", "status": "SUCCEEDED", "elapsed_ms": 34500, "cost_cents": 120}
```

On failure, an `error` frame is emitted with the RFC 7807 envelope and the
stream closes.

---

## 9. Configuration knobs

| Variable | Default | Affects |
|----------|---------|---------|
| `FLYQUERY_INGEST_TOPIC` | `flyquery.ingest` | EDA topic name |
| `FLYQUERY_INGEST_WORKER_CONCURRENCY` | `4` | Parallel ingest workers |
| `FLYQUERY_INGEST_HANDLER_TIMEOUT_S` | `600` | Per-job timeout |
| `FLYQUERY_INGEST_SHUTDOWN_GRACE_S` | `30` | Worker drain on SIGTERM |
| `FLYQUERY_MAX_FILE_MB` | `2048` | Upload size cap |
| `FLYQUERY_MAX_WORKSPACE_GB` | `200` | Total storage per workspace |
| `FLYQUERY_SAMPLE_N` | `8` | Sample values per column |
| `FLYQUERY_PROFILE_ROW_THRESHOLD` | `10000000` | Skip profiling above this row count |
| `FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN` | `200` | DescribeAgent budget per ingest |
| `FLYQUERY_DESCRIBE_BATCH` | `20` | Objects per DescribeAgent batch |
| `FLYQUERY_DESCRIBE_MODEL` | `anthropic:claude-haiku-4-5` | LLM for DescribeAgent |
| `FLYQUERY_RELATION_PROPOSER_ENABLED` | `true` | Enable RelationProposerAgent |
| `FLYQUERY_RELATION_PROPOSER_MODEL` | `anthropic:claude-sonnet-4-6` | LLM for RelationProposerAgent |
| `FLYQUERY_RELATION_HEURISTIC_MIN_CONFIDENCE` | `0.85` | Threshold for auto-retrieval use |
| `FLYQUERY_RENAME_DETECT_MODEL` | `anthropic:claude-haiku-4-5` | LLM for RenameDetectionAgent |
| `FLYQUERY_MAX_TITLE_ROWS` | `3` | Title rows to skip in XLSX |
| `FLYQUERY_TYPE_INFER_SAMPLE_ROWS` | `8192` | DuckDB type inference sample |
| `FLYQUERY_DEFAULT_LOCALE` | `en-US` | Date-format locale fallback |
| `FLYQUERY_PII_SCANNER` | `regex` | PII backend |
| `FLYQUERY_PII_POLICY_SAMPLES` | `redact` | Action on PII in samples |
