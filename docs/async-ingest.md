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
[pipeline.md](pipeline.md). For the full worker fleet (IngestWorker +
RetentionWorker), scaling, and recovery, see [workers.md](workers.md).

### Two upload entry points

| Endpoint | Stages run synchronously | Stages run on worker | Response |
|---|---|---|---|
| `POST /datasets/{id}/files` | All 10 stages (in-process) | none | `200 OK` with full `IngestJobResult` once everything settles. |
| `POST /datasets/{id}/files:async` (new in 26.5.10) | Stage 1 only (receive: caps check, hash, format detect, store bytes, write `flyquery_files` row, track storage) | Stages 2-10 (parse / reconcile / sample / profile / relations / describe / PII / embed / publish) | `202 Accepted` with `{job_id, file_id, dataset_id, status}` plus `Location: /api/v1/ingest-jobs/{job_id}`. |

The async form queues the job with an `already_received` flag in
`request_json`. When the worker picks the job up it inspects the flag
and skips Stage 1 — re-running receive would create a duplicate
`file_id` and overwrite the object-store key. See
[`workers.py:374`](../src/flyquery/core/services/ingestion/workers.py)
for the worker-side branch and
[`files_controller.py:328`](../src/flyquery/web/controllers/files_controller.py)
for the `mark_already_received` call on the controller side.

---

## 2. IngestWorker lifecycle

`IngestWorker` is a long-running process. As of 26.5.10 it ships under
its own CLI subcommand (`flyquery worker ingest`); the previous
`flyquery worker` form is gone. See
[`src/flyquery/cli.py:74`](../src/flyquery/cli.py) for the click group
and [workers.md](workers.md) for the deployment topologies.

```bash
# Production (one process per worker type, scale independently):
flyquery worker ingest         # this doc
flyquery worker retention      # see workers.md

# Dev / docker-compose convenience (both in one process — NOT production):
flyquery worker all
```

The ingest worker:

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

### Stuck-job recovery (RetentionWorker, added 26.5.10)

The original v0 design planned periodic heartbeat writes from the
worker plus a heartbeat-timeout reaper. 26.5.10 took a different
approach: the new `RetentionWorker` polls `flyquery_ingest_jobs`
periodically and atomically resets jobs whose `started_at` is older
than `processing_lease_s` (default 1800s) back to `PENDING`, then
republishes them onto the bus. The reaper is implemented at
[`retention_worker.py:162`](../src/flyquery/core/services/retention/retention_worker.py)
(`_reap_stuck_running`); see [workers.md](workers.md) for the full
operator picture.

This replaces the heartbeat scheme: instead of writing a heartbeat
column from every worker, we use the existing `started_at` timestamp +
a single polling sweep. The trade-off is detection latency
(`processing_lease_s` instead of `FLYQUERY_INGEST_HEARTBEAT_S`) in
exchange for zero per-handler write overhead and a simpler model.

`FLYQUERY_INGEST_HANDLER_TIMEOUT_S` (default 600 s) is still the
per-job in-process wall-clock cap; it bounds `asyncio.wait_for` around
each handler. `FLYQUERY_INGEST_MAX_ATTEMPTS` (default 3) is reserved
for a future change.

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
| Worker crashes mid-stage | Job remains `RUNNING` until the RetentionWorker's `_reap_stuck_running` sweep (every `retention_scan_interval_s`, default 300s) finds `started_at < now() - processing_lease_s` (default 1800s). Then: reset to `PENDING`, republish onto the bus. The next worker to claim it via the atomic update wins. |
| Stage raises a retriable error | Job transitions to `FAILED`; operator must re-queue via `POST /ingest-jobs` with a new job or use REPARSE |
| DESCRIBE_PASS budget exhausted | Normal `SUCCEEDED`; auto-creates another DESCRIBE_PASS for remaining objects |
| Zip-bomb or FORMAT_MISMATCH | Immediate `FAILED` with structured `error_json`; no retry |

Automatic retries are intentionally not implemented for parse failures.
Business logic errors (wrong format, malformed JSON, encrypted XLSX) require
operator attention, not silent retry.

For transient infrastructure errors (Postgres unavailable, object-store
timeout), the RetentionWorker re-queues the job once the
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
worker crashes between these two steps, the orphaned Parquet blob remains
on the object store until the dataset is purged. There is **no** orphan-
blob sweep in the RetentionWorker as of 26.5.10 -- the sweep only resets
the **SQL** state (the `RetentionWorker._reap_stuck_running` step flips
the job back to PENDING so the bus redelivers, and the next successful
run writes a fresh snapshot pointing at a NEW Parquet key). The leaked
blob from the crashed run is reclaimed when `DELETE /datasets/{id}:purge`
walks the dataset prefix.

Operators that need tighter Parquet GC have two options:
1. Run periodic dataset purges (operator policy).
2. Add object-store lifecycle rules at the bucket tier (S3 / GCS / Azure
   all support "delete objects older than N days"). The
   `flyquery/{tenant}/{workspace}/{dataset}/` prefix layout makes
   per-dataset rules straightforward.

See [`docs/workers.md`](workers.md) for the full RetentionWorker
behaviour.

---

## 8. Configuration reference

### IngestWorker

| Variable | Default | Purpose |
|----------|---------|---------|
| `FLYQUERY_INGEST_TOPIC` | `flyquery.ingest` | EDA topic name for ingest jobs |
| `FLYQUERY_INGEST_WORKER_CONCURRENCY` | `4` | Concurrent job slots per worker process |
| `FLYQUERY_INGEST_HANDLER_TIMEOUT_S` | `600` | Max seconds any one handler runs before being cancelled |
| `FLYQUERY_INGEST_HEARTBEAT_S` | `30` | Reserved for future use (replaced by RetentionWorker reap loop) |
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

### RetentionWorker (new in 26.5.10)

All settings live on `FlyquerySettings`
([`config.py:187`](../src/flyquery/config.py)). Set any TTL to `0` to
disable that sweep entirely.

| Variable | Default | Purpose |
|----------|---------|---------|
| `FLYQUERY_RETENTION_SCAN_INTERVAL_S` | `300` | Sweep loop interval (clamped to ≥ 60s) |
| `FLYQUERY_PROCESSING_LEASE_S` | `1800` | Stuck-RUNNING threshold — jobs older than this get reset to PENDING |
| `FLYQUERY_ORPHAN_QUEUED_GRACE_S` | `600` | Orphan-PENDING threshold — PENDING jobs older than this get republished |
| `FLYQUERY_RETENTION_INGEST_EVENTS_DAYS` | `30` | TTL for `flyquery_ingest_events`; `0` disables |
| `FLYQUERY_RETENTION_AUDIT_EVENTS_DAYS` | `365` | TTL for `flyquery_audit_events`; `0` disables |
| `FLYQUERY_RETENTION_COST_EVENTS_DAYS` | `365` | TTL for `flyquery_cost_events`; `0` disables |
| `FLYQUERY_DATASET_PURGE_TOMBSTONE_DAYS` | `90` | PURGING dataset hard-delete delay |
