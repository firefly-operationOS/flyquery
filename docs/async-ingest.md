# flyquery — Async Ingest

## Table of Contents

1. [Overview](#1-overview)
2. [IngestWorker lifecycle](#2-ingestworker-lifecycle)
3. [Job kinds](#3-job-kinds)
4. [Cooperative cancel semantics](#4-cooperative-cancel-semantics)
5. [Retry behaviour](#5-retry-behaviour)
6. [Dead-letter handling](#6-dead-letter-handling)
7. [Sequencing guarantees](#7-sequencing-guarantees)
8. [Configuration reference](#8-configuration-reference)

---

## 1. Overview

Every file upload kicks off an asynchronous ingestion job. The HTTP endpoint
returns `202 Accepted` immediately; the 10-stage pipeline runs in a separate
`IngestWorker` process, consuming from the `flyquery.ingest` EDA topic.

This document describes the worker internals, the five job kinds, cancel
semantics, retry behaviour, and the sequencing guarantees the system provides.

For the stage-by-stage pipeline description see [ingestion.md](ingestion.md).
For the stage diagrams and mode coupling with the query pipeline see
[pipeline.md](pipeline.md).

---

## 2. IngestWorker lifecycle

`IngestWorker` is a long-running process (`uv run flyquery worker`) that:

1. Subscribes to the `flyquery.ingest` EDA topic.
2. Claims jobs from `flyquery_ingest_jobs` via a transactional SELECT … FOR
   UPDATE SKIP LOCKED (prevents two workers claiming the same job).
3. Transitions the job to `RUNNING`.
4. Executes the stage chain for the job kind.
5. Transitions to `SUCCEEDED` or `FAILED` and records `result_json`.

### Concurrency

Multiple workers can run in parallel. The number per process is set by
`FLYQUERY_INGEST_WORKER_CONCURRENCY` (default 4). Each worker slot processes
one job at a time.

With two flyquery worker pods each at `FLYQUERY_INGEST_WORKER_CONCURRENCY=4`,
eight jobs can run concurrently. Postgres SELECT … FOR UPDATE SKIP LOCKED
ensures no two slots claim the same job.

### State machine

```
              (upload)
                 │
                 ▼
             PENDING
                 │ worker claims
                 ▼
             RUNNING  ──── cancel request ───────► CANCELLED
                 │                                     ▲
             ┌───┴──────┐                              │
          SUCCESS      FAIL                 (cooperative at checkpoint)
             │           │
        SUCCEEDED     FAILED
```

Every transition is a single `UPDATE flyquery_ingest_jobs SET status=…`
inside a database transaction. The transition is permanent; there is no
rollback of already-completed stages.

### Heartbeat + stale-job recovery

> **v1+:** Periodic heartbeat writes and automatic stale-job recovery are
> planned for v1. Currently, stale RUNNING jobs are detected only at restart
> via the handler timeout (`FLYQUERY_INGEST_HANDLER_TIMEOUT_S`, default 600 s);
> manual `FAILED` marking via `POST /ingest-jobs/{id}:cancel` is the operator
> workaround. `FLYQUERY_INGEST_HEARTBEAT_S` (default 30) and
> `FLYQUERY_INGEST_MAX_ATTEMPTS` (default 3) are reserved for v1 use.

---

## 3. Job kinds

The `job_kind` field on `flyquery_ingest_jobs` controls which stages run.

### PARSE_AND_INGEST

Full 10-stage pipeline. Created automatically by:
- `POST /datasets/{id}/files` (first upload)
- `PUT /datasets/{ds}/tables/{id}:upload` (re-upload)

Can also be created manually via `POST /ingest-jobs` with
`{job_kind: "PARSE_AND_INGEST", file_id: "..."}`.

Stages: 1 (receive) → 2 (parse) → 3 (reconcile + snapshot) → 4 (sample) →
5 (profile) → 6 (relations) → 7 (describe) → 8 (PII) → 9 (embed + index) →
10 (publish + close).

Stages 4–8 are individually skippable via `ingest_policy_json`.

### REPARSE

Identical to PARSE_AND_INGEST in stages run. Triggered by operator when
re-ingesting from an existing object-store blob without a new upload
(e.g., after a policy change, after updating `FLYQUERY_DEFAULT_LOCALE`,
after a description or synonym update that needs re-embedding).

The difference from PARSE_AND_INGEST is that REPARSE does NOT overwrite the
original blob; it re-reads the existing `flyquery_files.object_store_key`.

### SAMPLE_REFRESH

Runs stage 4 only (sample). Triggered by:
- `POST /schema-objects/{id}:sample` (manual refresh)
- Operator-defined scheduled refresh (v1+)

Useful when samples were redacted by a PII policy change and need to be
re-collected after the column is cleared.

### DESCRIBE_PASS

Runs stage 7 only (describe). Created automatically when a `PARSE_AND_INGEST`
or `REPARSE` run exhausts `FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN` before
describing all objects. The partial result is persisted; the DESCRIBE_PASS
job resumes from the first undescribed object.

Can also be triggered manually via `POST /ingest-jobs` with
`{job_kind: "DESCRIBE_PASS", dataset_id: "..."}`.

### RELATION_PASS

Runs stage 6 only (relation discovery). Triggered when a new table is added
to a dataset that already has other tables, or manually for a full dataset
re-analysis.

`POST /ingest-jobs` with `{job_kind: "RELATION_PASS", dataset_id: "..."}`.

RELATION_PASS always scans ALL tables in the dataset, not just the newly
added one.

---

## 4. Cooperative cancel semantics

`POST /ingest-jobs/{id}:cancel` sets a cancellation flag
(`flyquery_ingest_jobs.cancel_requested=true`) in the database. It does NOT
kill the worker goroutine immediately.

Workers check this flag at **checkpoints** between stages. When the flag is
detected:

1. The current stage completes or is rolled back cleanly (partial Parquet
   writes are removed from object storage if the stage had not committed).
2. The job transitions to `CANCELLED`.
3. The SSE stream emits a final `event: error` frame with
   `code=JOB_CANCELLED`.

### What can be cancelled

| Stage | Cancellable before starting? | In-flight behaviour |
|-------|--------------------------|-------------------|
| 1–3 | Yes | Checked before each stage |
| 4–8 | Yes | Checked before each stage; in-flight LLM calls complete |
| 9 | Yes | Embedding batch in flight completes; partial embeddings are rolled back |
| 10 | No | Atomic snapshot close cannot be interrupted once started |

### GDPR purge and in-flight jobs

`DELETE /workspaces/{id}:purge` triggers a workspace-wide cooperative cancel
before walking the object-store prefix. All `RUNNING` jobs for the workspace
receive `cancel_requested=true`; the purge waits up to
`FLYQUERY_INGEST_SHUTDOWN_GRACE_S` (default 30 s) for them to drain.

---

## 5. Retry behaviour

`flyquery_ingest_jobs.attempts` tracks how many times the job has been picked
up by a worker.

| Scenario | Behaviour |
|----------|-----------|
| Worker crashes mid-stage | Job remains `RUNNING`; heartbeat times out → reset to `PENDING` + `attempts++` |
| Stage raises a retriable error | Job transitions to `FAILED`; operator must re-queue via `POST /ingest-jobs` with a new job or use REPARSE |
| DESCRIBE_PASS budget exhausted | Normal `SUCCEEDED`; auto-creates another DESCRIBE_PASS for remaining objects |
| Zip-bomb or FORMAT_MISMATCH | Immediate `FAILED` with structured `error_json`; no retry |

Automatic retries are intentionally not implemented for parse failures.
Business logic errors (wrong format, malformed JSON, encrypted XLSX) require
operator attention, not silent retry.

For transient infrastructure errors (Postgres unavailable, object-store
timeout), the heartbeat-timeout mechanism re-queues the job once the
infrastructure recovers. `FLYQUERY_INGEST_MAX_ATTEMPTS` (default 3) caps
total attempts to prevent loops.

---

## 6. Dead-letter handling

Jobs that exceed `FLYQUERY_INGEST_MAX_ATTEMPTS` are left in `FAILED` status
with `attempts ≥ max`. They do NOT re-enter the queue automatically.

Dead-letter triage:

```bash
# List all dead-letter jobs
GET /api/v1/ingest-jobs?status=FAILED&attempts_gte=3

# Inspect the last failure reason
GET /api/v1/ingest-jobs/{id}
# → result_json.error_code + result_json.error_detail

# Re-queue manually after fixing the root cause
POST /api/v1/ingest-jobs  {job_kind: "REPARSE", file_id: "<id>"}
```

`flyquery_ingest_events` retains the per-stage event log for each job
(including failed attempts), providing a full audit trail of what
succeeded before the failure.

---

## 7. Sequencing guarantees

### Within a single job

Stages execute in strict order (1 → 2 → … → 10). A stage does not start
until the prior stage has committed to the database. If a stage fails, later
stages do not run.

### Cross-job ordering within a dataset

When a PARSE_AND_INGEST and a DESCRIBE_PASS for the same dataset run
concurrently, the DESCRIBE_PASS may read schema objects that are mid-update.
flyquery tolerates this: DESCRIBE_PASS only writes to columns where
`description IS NULL`; any column that received a description from the
concurrent PARSE_AND_INGEST will be skipped.

### Snapshot visibility

`flyquery_tables.current_snapshot_id` flips atomically in stage 10. Between
stages 1 and 9, queries against the table still use the prior snapshot
(which may be `NULL` for a first upload, meaning the table is not yet
queryable). There is no half-ingested window.

### Object-store and Postgres consistency

Object-store writes (Parquet materialisation in stage 2) happen before the
corresponding `flyquery_schema_snapshots` row is inserted (stage 3). If the
worker crashes between these two steps, the orphaned Parquet blob is cleaned
up by a background retention sweep that looks for blobs without a
corresponding `flyquery_schema_snapshots` row older than 1 hour.

---

## 8. Configuration reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `FLYQUERY_INGEST_TOPIC` | `flyquery.ingest` | EDA topic name for ingest jobs |
| `FLYQUERY_INGEST_WORKER_CONCURRENCY` | `4` | Concurrent job slots per worker process |
| `FLYQUERY_INGEST_HANDLER_TIMEOUT_S` | `600` | Max seconds before heartbeat-timeout triggers |
| `FLYQUERY_INGEST_HEARTBEAT_S` | `30` | Heartbeat write interval |
| `FLYQUERY_INGEST_SHUTDOWN_GRACE_S` | `30` | Grace period for in-flight jobs on SIGTERM |
| `FLYQUERY_INGEST_MAX_ATTEMPTS` | `3` | Max total attempts before dead-letter |
| `FLYQUERY_EDA_ADAPTER` | `postgres` | EDA transport: postgres\|redis\|kafka\|memory |
| `FLYQUERY_EDA_GROUP` | `flyquery-workers` | Consumer group name (for Kafka) |
| `FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN` | `200` | LLM budget cap per DESCRIBE pass (cents) |
| `FLYQUERY_DESCRIBE_BATCH` | `20` | Columns per DescribeAgent call |
| `FLYQUERY_RELATION_PROPOSER_ENABLED` | `true` | Enable/disable RelationProposerAgent in stage 6 |
| `FLYQUERY_RELATION_PROPOSER_MAX_PER_PAIR` | `3` | Max proposals per table-pair |
| `FLYQUERY_SAMPLE_N` | `8` | Sample values per column in stage 4 |
| `FLYQUERY_PROFILE_ROW_THRESHOLD` | `10000000` | Row count above which stage 5 is skipped |
