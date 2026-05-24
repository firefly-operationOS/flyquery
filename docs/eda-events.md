# flyquery — EDA Events

## Table of Contents

1. [Overview](#1-overview)
2. [flyquery.ingest — IngestRequested](#2-flyqueryingest--ingestrequested)
3. [flyquery.schema — SchemaUpdated](#3-flyqueryschema--schemaupdated)
4. [Durable outbox (Postgres LISTEN/NOTIFY default)](#4-durable-outbox-postgres-listennotify-default)
5. [Consumer guide](#5-consumer-guide)
6. [EDA adapter selection](#6-eda-adapter-selection)

---

## 1. Overview

flyquery publishes two EDA topics:

| Topic | Emitted by | Consumed by |
|-------|-----------|-------------|
| `flyquery.ingest` | Upload endpoints | `IngestWorker` processes |
| `flyquery.schema` | Stage 10 of ingestion | Downstream services (flycanon, flyradar, dashboards) |

Both topics use the `pyfly.eda.EventPublisher` bean, which is injectable at
the service layer. The default transport is Postgres LISTEN/NOTIFY with a
durable outbox in `flyquery_ingest_events`. See §4 for durability guarantees.

Additional internal events (audit, cost) flow through `flyquery.audit` but
are not documented here as they are append-only internal audit trails — use
`GET /api/v1/audit` to read them.

---

## 2. flyquery.ingest — IngestRequested

### When emitted

Published immediately after an upload endpoint writes the blob to object
storage and inserts the `flyquery_ingest_jobs` row. This event is the trigger
for `IngestWorker` to pick up the job.

### Schema

```json
{
  "event": "IngestRequested",
  "version": "1",
  "tenant_id": "acme",
  "workspace_id": "analytics",
  "dataset_id": "ds_01",
  "ingest_job_id": "job_01",
  "job_kind": "PARSE_AND_INGEST",
  "file_id": "f_01",
  "table_id": null,
  "snapshot_id": null,
  "triggered_by": "USER",
  "idempotency_key": "upload-abc-123",
  "created_at": "2026-05-23T10:00:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `event` | string | Always `"IngestRequested"` |
| `version` | string | Payload schema version (`"1"` in v0) |
| `tenant_id` | string | Tenant scope |
| `workspace_id` | string | Workspace scope |
| `dataset_id` | string | Dataset that owns the job |
| `ingest_job_id` | uuid | Primary lookup key for the job |
| `job_kind` | enum | `PARSE_AND_INGEST` \| `REPARSE` \| `SAMPLE_REFRESH` \| `DESCRIBE_PASS` \| `RELATION_PASS` |
| `file_id` | uuid \| null | Set for PARSE_AND_INGEST and REPARSE; null for dataset-level jobs |
| `table_id` | uuid \| null | Set for SAMPLE_REFRESH targeting a specific table |
| `snapshot_id` | uuid \| null | Null at publish time (assigned during ingestion) |
| `triggered_by` | enum | `USER` \| `AGENT` \| `SCHEDULED` \| `REPARSE` |
| `idempotency_key` | string | From the `Idempotency-Key` header; used for deduplication |
| `created_at` | ISO 8601 | Event creation timestamp |

### Consumer contract

`IngestWorker` is the only production consumer of this topic. If you subscribe
to it for observability purposes:

- Expect exactly-once delivery per `ingest_job_id` under the Postgres outbox
  adapter (re-delivery on Postgres restart may occur; idempotency on
  `ingest_job_id` is safe).
- Do not modify `flyquery_ingest_jobs` directly from a consumer.
- Use `GET /api/v1/ingest-jobs/{id}/stream` for per-stage progress instead
  of subscribing to this topic.

### Second publisher: RetentionWorker republish

As of 26.5.10, the [`RetentionWorker`](../src/flyquery/core/services/retention/retention_worker.py)
also publishes `IngestRequested` events as part of its periodic sweep
(see [workers.md](workers.md)). Two paths:

1. **Stuck-RUNNING reap** — `started_at > processing_lease_s` jobs are
   reset to PENDING and republished, recovering from a crashed worker.
2. **Orphan-PENDING grace** — PENDING jobs older than
   `orphan_queued_grace_s` are republished in case the original event
   never made it to the bus.

In both cases the event payload is reconstructed from the persisted
job row, so the schema is identical to the original. Idempotency on
the consumer side relies on the atomic PENDING → RUNNING claim in
`flyquery_ingest_jobs`: a job that's already RUNNING (or done)
short-circuits in the worker handler.

---

## 3. flyquery.schema — SchemaUpdated

### When emitted

Published in stage 10 (publish + close snapshot) as part of the atomic
snapshot-close transaction. At the time of emission, `flyquery_tables.current_snapshot_id`
has already flipped to the new snapshot, and the snapshot is `READY`.

### Schema

```json
{
  "event": "SchemaUpdated",
  "version": "1",
  "tenant_id": "acme",
  "workspace_id": "analytics",
  "dataset_id": "ds_01",
  "table_id": "t_01",
  "snapshot_id": "snap_02",
  "prev_snapshot_id": "snap_01",
  "diff_summary": {
    "added": ["new_column"],
    "removed": [],
    "type_changed": [],
    "renamed_candidates": ["old_col -> new_col (confidence 0.82)"]
  },
  "parquet_object_key": "flyquery/acme/analytics/ds_01/tables/t_01/v2.parquet",
  "n_rows_actual": 12500,
  "n_columns": 8,
  "snapshot_hash": "sha256:abc123",
  "created_at": "2026-05-23T10:05:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `event` | string | Always `"SchemaUpdated"` |
| `version` | string | Payload schema version (`"1"` in v0) |
| `tenant_id` | string | Tenant scope |
| `workspace_id` | string | Workspace scope |
| `dataset_id` | uuid | Dataset containing the table |
| `table_id` | uuid | The table whose snapshot just went READY |
| `snapshot_id` | uuid | The new (current) snapshot |
| `prev_snapshot_id` | uuid \| null | The previous snapshot; null for first upload |
| `diff_summary` | object | Column-level diff relative to prev_snapshot |
| `diff_summary.added` | string[] | New column qualified names |
| `diff_summary.removed` | string[] | Removed column qualified names |
| `diff_summary.type_changed` | string[] | Columns where data_type changed |
| `diff_summary.renamed_candidates` | string[] | Rename proposals; human confirmation pending |
| `parquet_object_key` | string | Full object-store key for the new Parquet snapshot |
| `n_rows_actual` | int | Row count (from stage 2 parse); null if unavailable |
| `n_columns` | int | Column count in the new snapshot |
| `snapshot_hash` | string | Deterministic SHA-256 over column names + types |
| `created_at` | ISO 8601 | Emission timestamp (same transaction as snapshot close) |

### When to subscribe

Subscribe to `flyquery.schema` when you need to:

- Invalidate a downstream schema cache when flyquery data changes.
- Trigger a re-index or re-embedding in another service.
- Notify users that a dataset they query has been updated.
- Feed flycanon with new context about the workspace's structured data
  (see [integration-with-firefly-os.md](integration-with-firefly-os.md)).
- Drive a flyradar discovery that re-evaluates relations across datasets
  after a new upload.

### Consumer example (Python, asyncio)

```python
from pyfly.eda import subscribe

@subscribe(topic="flyquery.schema", event="SchemaUpdated", version="1")
async def on_schema_updated(event: dict, *, tenant_id: str, workspace_id: str):
    dataset_id = event["dataset_id"]
    table_id = event["table_id"]
    snapshot_id = event["snapshot_id"]
    diff = event["diff_summary"]
    # invalidate cache, trigger re-index, etc.
    if diff["added"] or diff["type_changed"]:
        await refresh_downstream_cache(dataset_id, table_id, snapshot_id)
```

---

## 4. Durable outbox (Postgres LISTEN/NOTIFY default)

The default EDA adapter (`FLYQUERY_EDA_ADAPTER=postgres`) uses Postgres
LISTEN/NOTIFY with an outbox table.

### How it works

1. **Publish** — the event is written to `flyquery_ingest_events`
   (for `flyquery.ingest`) or a separate outbox row (for `flyquery.schema`)
   inside the same database transaction as the triggering write.
   This means the event is only visible after the transaction commits —
   no phantom events.

2. **Relay** — a lightweight relay goroutine reads undelivered outbox rows
   and fires `NOTIFY flyquery.<topic>` via Postgres. Workers listen via
   `LISTEN flyquery.<topic>`.

3. **Deduplication** — each event has an `idempotency_key` or
   `ingest_job_id`. Workers that receive a duplicate NOTIFY (on Postgres
   reconnect) skip it if the job is already in a terminal state.

### Durability guarantee

Because the event write and the triggering write are in the same transaction:

- If the transaction commits → the event WILL eventually be delivered.
- If the transaction rolls back → the event is never written.
- If the relay crashes → Postgres will redeliver on reconnect.

This gives **at-least-once** delivery. Consumers should be idempotent on
`ingest_job_id` / `snapshot_id`.

### Checking outbox health

```bash
# Count undelivered outbox events older than 5 minutes
SELECT COUNT(*) FROM flyquery_ingest_events
  WHERE delivered_at IS NULL
    AND created_at < NOW() - INTERVAL '5 minutes';

# If count > 0 and growing, check relay logs
docker compose logs flyquery-worker | grep "outbox relay"
```

---

## 5. Consumer guide

### Idempotency

Both events carry stable, deterministic IDs:

- `flyquery.ingest` → `ingest_job_id` (uuid)
- `flyquery.schema` → `(table_id, snapshot_id)` pair is stable and unique

Design consumer handlers to be idempotent on these keys. Re-delivery is
possible under all adapters on restart.

### Filtering by workspace

All events carry `tenant_id` and `workspace_id`. Multi-tenant consumers
should filter to the tenant/workspace they manage before processing:

```python
if event["tenant_id"] != MY_TENANT or event["workspace_id"] != MY_WORKSPACE:
    return  # not for us
```

### Error handling

If a consumer fails to process a `SchemaUpdated` event, it should record
the failure and retry. The flyquery service does not know about downstream
consumer failures. The canonical recovery pattern:

1. Catch the exception in the handler.
2. Log with `(tenant_id, workspace_id, event_id)` for tracing.
3. Push to a dead-letter queue.
4. Alert on dead-letter queue depth.
5. Replay from dead-letter once root cause is fixed.

### Schema evolution

Fields may be **added** to event payloads in minor releases without a version
bump. Consumers should ignore unknown fields (tolerant reader pattern).

Breaking changes (field removal or type change) bump `version` from `"1"` to
`"2"`. Consumers should check the `version` field and reject events with an
unknown version rather than silently mis-parsing.

---

## 6. EDA adapter selection

`FLYQUERY_EDA_ADAPTER` controls the transport:

| Adapter | Durability | Notes |
|---------|-----------|-------|
| `postgres` (default) | Durable (transactional outbox) | Recommended for v0 |
| `redis` | Non-durable (Pub/Sub) | Low-latency; requires Redis; messages lost on restart |
| `kafka` | Durable (log-based) | High throughput multi-consumer; requires Kafka cluster |
| `memory` | In-process only | Testing; messages lost on process exit |

For multi-worker production deployments, `postgres` (default) is the safest
choice without additional infrastructure. Switch to `kafka` when you have
multiple independent downstream consumers (e.g., flycanon + flyradar +
custom analytics) that each need independent offset tracking.

Additional env vars for Kafka:
```
FLYQUERY_KAFKA_BOOTSTRAP_SERVERS=kafka:9092
FLYQUERY_EDA_GROUP=flyquery-workers
FLYQUERY_EDA_DESTINATIONS=flyquery.ingest,flyquery.schema,flyquery.audit
```
