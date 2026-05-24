# Worker architecture

> Audience: SREs, on-call engineers, and developers extending the asynchronous
> side of flyquery. Read [concurrency.md](concurrency.md) first if you need
> the request-scoped session model -- this doc picks up where the synchronous
> request path ends and the long-running async pipeline begins.

## TL;DR

flyquery runs as **three distinct process types**, each scaled and operated
independently:

| Process       | CLI                          | What it does                                              | Scale axis            |
|---------------|------------------------------|-----------------------------------------------------------|-----------------------|
| API server    | `flyquery serve`             | Synchronous HTTP -- controllers + services + repos        | replicas              |
| IngestWorker  | `flyquery worker ingest`     | EDA consumer for `flyquery.ingest` -- runs the pipeline   | replicas + `_CONCURRENCY` |
| RetentionWorker | `flyquery worker retention`| Periodic janitor -- TTL deletes + stuck-job reaper        | single replica usually |

The API server is the only process that handles request traffic; every
long-running pipeline stage lives in `IngestWorker`. `RetentionWorker` is the
new single-replica janitor that keeps the operational tables bounded and
recovers crashed workers' jobs.

All three processes share the same Postgres + object store + EDA bus, and the
same `pyfly` DI container. They differ only in which beans they spin up at
boot and which Postgres role they connect as.

The single piece of cross-process state is the EDA topic
(`flyquery.ingest` -- see [pyfly.yaml:60-65](../pyfly.yaml#L60-L65)). Every
ingest job submission either:

1. Inserts a `PENDING` row in `flyquery_ingest_jobs`, then publishes
   `IngestRequested {ingest_job_id}` to the topic
   ([ingest_job_service.py:103-143](../src/flyquery/core/services/ingest_jobs/ingest_job_service.py#L103-L143)),
   **or**
2. Runs synchronously inside the upload endpoint (the legacy
   `PARSE_AND_INGEST` path; the async upload endpoint takes path 1).

The bus's at-least-once delivery + the atomic `PENDING -> RUNNING` claim
([workers.py:683-695](../src/flyquery/core/services/ingestion/workers.py#L683-L695))
makes horizontal scaling safe: any number of `IngestWorker` replicas can
subscribe to the same topic and at most one will execute a given job.

---

## 1. What runs where

### 1.1 API server (Uvicorn)

**Entry point**: `flyquery serve` -> `uvicorn flyquery.main:app`
([cli.py:17-24](../src/flyquery/cli.py#L17-L24)).

**Role**: synchronous HTTP request handling -- controllers -> services ->
repositories. Connects to Postgres as `flyquery_app`
([config.py:30](../src/flyquery/config.py#L30)), the non-`BYPASSRLS` role
that respects the RLS policies installed in
[0007_rls.py:44-96](../migrations/versions/0007_rls.py#L44-L96).

The API server does **not** run long-running background loops or consume
the `flyquery.ingest` topic. The `IngestWorker` bean is registered with
`@service` ([workers.py:48](../src/flyquery/core/services/ingestion/workers.py#L48))
but its `run_forever()` is only called by the worker CLI. The API server
publishes via `IngestJobService._enqueue`
([ingest_job_service.py:138-141](../src/flyquery/core/services/ingest_jobs/ingest_job_service.py#L138-L141))
and returns 202.

Why the split: a Uvicorn worker pool is sized for HTTP latency, not
30-minute LLM-bound jobs. Mixing them means a multi-minute DESCRIBE pass
starves request handlers in the same process. Splitting also lets you
deploy API fixes without restarting in-flight ingest jobs.

### 1.2 IngestWorker

**Entry point**: `flyquery worker ingest` (new in 26.5.10; see Section 9).

**Class**:
[`flyquery.core.services.ingestion.workers.IngestWorker`](../src/flyquery/core/services/ingestion/workers.py).
Registered as a `@service_bean` (line 48). Constructor takes
`EventPublisher`, `FlyquerySettings`, and an `async_sessionmaker` (lines
57-68).

**Topic**: `flyquery.ingest`
([config.py:54](../src/flyquery/config.py#L54)). The bus subscription is
single-event-type: `IngestRequested`
([ingest_publisher.py:20](../src/flyquery/core/eda/ingest_publisher.py#L20),
[workers.py:78-81](../src/flyquery/core/services/ingestion/workers.py#L78-L81)).

**Job kinds it drives** (dispatched by `_run_stages` at
[workers.py:250-302](../src/flyquery/core/services/ingestion/workers.py#L250-L302)):

```
PARSE_AND_INGEST   stages 1-3 + 9-10  (re-queue fallback only; primary path is sync upload)
REPARSE            stages 1-3 + 9-10  (skips stage 4-8 by design)
SAMPLE_REFRESH     stage  4 only      (refresh sample without touching schema)
DESCRIBE_PASS      stage  7 only      (LLM describe per snapshot)
RELATION_PASS      stage  6 only      (relation proposer + heuristic)
```

The `_STARTABLE_KINDS` frozenset
([ingest_jobs.py:22](../src/flyquery/interfaces/ingest_jobs.py#L22)) -- and
the guard in `IngestJobCreate.validate_startable`
([ingest_jobs.py:34-40](../src/flyquery/interfaces/ingest_jobs.py#L34-L40))
-- enforces that only the four standalone kinds can come in via
`POST /ingest-jobs`. `PARSE_AND_INGEST` arrives at the worker only when it's
been re-queued from the async upload endpoint
([ingest_job_service.py:70-101](../src/flyquery/core/services/ingest_jobs/ingest_job_service.py#L70-L101));
the handler treats it as a `REPARSE` fallback
([workers.py:270-279](../src/flyquery/core/services/ingestion/workers.py#L270-L279)).

**One logical worker, N physical processes**: the class itself owns no
cross-process coordination state. Every replica subscribes to the same
topic. EDA semantics + the atomic claim in `_mark_running`
([workers.py:683-695](../src/flyquery/core/services/ingestion/workers.py#L683-L695))
ensure each `IngestRequested` event is processed exactly once across the
fleet (modulo retries; see Section 5).

### 1.3 RetentionWorker (NEW in 26.5.10)

**Entry point**: `flyquery worker retention` (new in 26.5.10; see Section 9).

**Class**: `flyquery.core.services.workers.retention_worker.RetentionWorker`.
Modeled directly on
[flyradar/.../retention_worker.py](../../flyradar/src/flyradar/core/services/workers/retention_worker.py)
-- same `run_once()` / `run_forever()` / `request_stop()` shape, same
`stats: dict[str, int]` return contract so dashboards and tests are
predictable.

**Driving model**: NOT EDA-driven. It is a periodic sleep/sweep loop,
interruptible via `asyncio.Event` so SIGTERM mid-sweep drains cleanly.
The flyradar reference at
[retention_worker.py:196-209](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L196-L209)
shows the exact pattern: `while not shutdown.is_set: await run_once(); await
wait_for(shutdown.wait, timeout=interval_s)`. Errors inside the sweep are
logged and swallowed so a transient DB blip doesn't crash the worker
([retention_worker.py:201-206](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L201-L206)).

**Tables it sweeps** (per `run_once`):

| Table                          | Sweep                                                                                  | Setting                                                |
|--------------------------------|----------------------------------------------------------------------------------------|--------------------------------------------------------|
| `flyquery_ingest_jobs`         | Reset RUNNING rows older than `processing_lease_s` back to PENDING and republish       | `FLYQUERY_PROCESSING_LEASE_S` (default 3600)           |
| `flyquery_ingest_jobs`         | Republish PENDING rows older than `orphan_queued_grace_s` (rescues lost EDA publishes) | `FLYQUERY_ORPHAN_QUEUED_GRACE_S` (default 600)         |
| `flyquery_ingest_events`       | DELETE rows older than the retention window (high-cardinality progress stream)         | `FLYQUERY_RETENTION_INGEST_EVENTS_DAYS` (default 30)   |
| `flyquery_audit_events`        | DELETE rows older than the retention window                                            | `FLYQUERY_RETENTION_AUDIT_EVENTS_DAYS` (default 0=off) |
| `flyquery_cost_events`         | DELETE rows older than the retention window                                            | `FLYQUERY_RETENTION_COST_EVENTS_DAYS` (default 0=off)  |
| `flyquery_datasets` (PURGING)  | Hard-delete rows whose `status='PURGING'` and `updated_at` older than tombstone window | `FLYQUERY_DATASET_PURGE_TOMBSTONE_DAYS` (default 90)   |

The two "0=off" defaults follow the flyradar convention -- operators with
audit retention requirements (PCI, GDPR) keep cost+audit forever and rely
on per-tenant export rather than TTL deletion. See
[retention_worker.py:115-122](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L115-L122)
for the canonical `0` = disabled idiom.

**Return shape** (mirrors flyradar's
[run_once at line 71-111](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L71-L111)):

```python
stats = {
    "ingest_jobs_stuck_reaped":   int,  # RUNNING -> PENDING + republished
    "ingest_jobs_orphan_republished": int,  # PENDING rows republished
    "ingest_events_deleted":      int,
    "audit_events_deleted":       int,
    "cost_events_deleted":        int,
    "datasets_purged":            int,
}
```

When **any** value is non-zero the worker emits one `retention_sweep_completed`
log line at INFO with the full breakdown -- silent sweeps stay at DEBUG so the
log volume scales with cleanup pressure, not wall-clock time.

### 1.4 CallbackWorker (NEW in 26.5.11)

**Entry point**: `flyquery worker callback`. Also bundled into
`flyquery worker all` for dev / docker-compose.

**Class**: `flyquery.core.services.callbacks.callback_worker.CallbackWorker`.
Drains `flyquery_callback_outbox` -- the transactional outbox that
captures one row per terminal-state ingest job whose request (or the
process-wide `FLYQUERY_DEFAULT_CALLBACK_URL` default) attached a
webhook target. Outbox writes happen in the SAME txn as the job's
status flip, so a crash can never leave a "succeeded" job without
its callback queued.

**Driving model**: periodic claim loop (default poll 5s). Each poll
runs:

```sql
SELECT … FROM flyquery_callback_outbox
WHERE status='PENDING' AND next_attempt_at <= now()
ORDER BY next_attempt_at
LIMIT :batch
FOR UPDATE SKIP LOCKED
```

`FOR UPDATE SKIP LOCKED` is the critical primitive: N peer
`CallbackWorker` processes never grab the same row. This is the
postgres-native equivalent of the `IngestWorker`'s EDA fan-out
(see Section 3 below).

For each claimed row the worker:

1. Calls `CallbackDispatcher.deliver()` -- HTTP POST with reserved
   headers + optional `X-Flyquery-Signature: sha256=<hmac>` from
   the shared secret.
2. Marks `DELIVERED` on 2xx, or schedules the next attempt with
   exponential backoff (0s, 30s, 5m, 1h, 6h then `DEAD`).

**Settings**:

| Setting | Default | Purpose |
|---|---|---|
| `FLYQUERY_CALLBACK_POLL_INTERVAL_S` | `5.0` | Sleep between empty-outbox polls. |
| `FLYQUERY_CALLBACK_BATCH_SIZE` | `25` | Max rows claimed per poll. |
| `FLYQUERY_CALLBACK_REQUEST_TIMEOUT_S` | `10.0` | Per-attempt HTTP timeout. |
| `FLYQUERY_DEFAULT_CALLBACK_URL` | _unset_ | Process-wide default receiver. |
| `FLYQUERY_DEFAULT_CALLBACK_SECRET` | _unset_ | Default shared secret. |
| `FLYQUERY_DEFAULT_CALLBACK_HEADERS` | `{}` | Default extra headers (JSON). |

Per-request callback fields on `IngestJobCreate.callback` and the
`callback_*` multipart form fields on the async upload endpoint
override the defaults as a **whole bundle** (URL + secret + headers
move together; we do not merge the default secret into a
request-supplied URL).

See [`callbacks.md`](callbacks.md) for the full wire contract +
receiver example.

---

## 2. The concurrency primitives

`IngestWorker` composes four asyncio primitives. Together they bound CPU,
bound memory, and let SIGTERM drain cleanly without dropping in-flight work.

### 2.1 `asyncio.Semaphore` -- bounded inflight

[workers.py:67](../src/flyquery/core/services/ingestion/workers.py#L67):

```python
self._sem = asyncio.Semaphore(settings.ingest_worker_concurrency)
```

The semaphore is acquired inside `_guarded_handle`
([workers.py:127-148](../src/flyquery/core/services/ingestion/workers.py#L127-L148))
before the handler runs. With `FLYQUERY_INGEST_WORKER_CONCURRENCY=4` (the
default at
[config.py:55](../src/flyquery/config.py#L55)), at most 4 handlers execute
concurrently per worker process. The 5th event spawned by the dispatcher
[workers.py:118-123](../src/flyquery/core/services/ingestion/workers.py#L118-L123)
parks on `_sem.acquire()` until a slot frees -- which means the underlying
bus's delivery loop also blocks (it's awaiting the dispatcher coroutine),
naturally back-pressuring upstream.

### 2.2 `asyncio.wait_for` -- per-handler timeout

[workers.py:131-134](../src/flyquery/core/services/ingestion/workers.py#L131-L134):

```python
await asyncio.wait_for(
    self._handle_ingest_requested(envelope),
    timeout=self._settings.ingest_handler_timeout_s,
)
```

`FLYQUERY_INGEST_HANDLER_TIMEOUT_S` (default 600s, see
[config.py:56](../src/flyquery/config.py#L56)) caps any single job at 10
minutes. A stuck LLM call or pathological XLSX can't pin a worker slot
indefinitely. Timeouts log a warning
([workers.py:139-143](../src/flyquery/core/services/ingestion/workers.py#L139-L143))
and release the semaphore. The job row stays `RUNNING` until the retention
worker's stuck-job reaper (Section 5) flips it back to `PENDING` for redelivery.

### 2.3 `asyncio.Event` -- cooperative shutdown

[workers.py:66, 95, 105](../src/flyquery/core/services/ingestion/workers.py#L66):

```python
self._stop_event = asyncio.Event()
...
try:
    await self._stop_event.wait()
finally:
    await self._drain_inflight()
```

`stop()` sets the event. The dispatcher checks `is_set()` on every delivery
([workers.py:115-117](../src/flyquery/core/services/ingestion/workers.py#L115-L117))
and drops new events the moment shutdown starts -- those are safe to drop
because the at-least-once bus + durable `PENDING` row mean another worker
(or this one after restart) picks them up.

### 2.4 Inflight task set -- drain on shutdown

[workers.py:68, 122-123, 149-164](../src/flyquery/core/services/ingestion/workers.py#L68):

```python
self._inflight: set[asyncio.Task[None]] = set()
...
task = asyncio.create_task(self._guarded_handle(envelope), name="flyquery-ingest-worker")
self._inflight.add(task)
task.add_done_callback(self._inflight.discard)
```

`_drain_inflight`
([workers.py:149-164](../src/flyquery/core/services/ingestion/workers.py#L149-L164))
waits up to `ingest_shutdown_grace_s` (default 30s, see
[config.py:57](../src/flyquery/config.py#L57)) for inflight tasks to finish.
After the budget burns out it cancels them and waits 5 more seconds for the
cancellations to propagate.

### 2.5 How the four compose

```
+--------- IngestWorker.run_forever ----------+
|  subscribe(topic, _dispatch); start()       |
|  await _stop_event.wait()  <-- park loop    |
|                                             |
|  _dispatch(envelope):                       |
|    if _stop_event.is_set: drop              |
|    else: task = create_task(...); track     |
|                                             |
|  _guarded_handle(envelope):                 |
|    async with _sem:                         |
|      try: wait_for(_handle, timeout)        |
|      except (Timeout, Exception): log       |
+---------------------------------------------+
        (stop_event set --> drain --> stop bus)
```

Semaphore caps **concurrency**, timeout caps **per-job wall time**, event
triggers **shutdown**, task set lets shutdown **drain cleanly**. Remove any
one and you lose bounded memory, bounded latency, or graceful restart.

---

## 3. Horizontal scaling

**Run more processes**. That is the entire scaling story.

```
   publish IngestRequested --> flyquery.ingest --> [Worker A | B | C ...]
                                                          |
                                                          v
                                +-------------------------------------+
                                |  UPDATE flyquery_ingest_jobs        |
                                |    SET status='RUNNING'             |
                                |  WHERE id=:id AND status='PENDING'  |
                                |  RETURNING id                       |
                                +-------------------------------------+
                                       (only ONE wins; rest no-op)
```

**Safety**: the atomic claim in `_mark_running`
([workers.py:683-695](../src/flyquery/core/services/ingestion/workers.py#L683-L695))
is the load-bearing piece. The `WHERE id=:id AND status='PENDING'` filter
makes the UPDATE single-row optimistic-concurrency -- when two workers
receive the same envelope (at-least-once redelivery), the loser's
`RETURNING id` returns no row, the worker logs `could not be claimed`, and
drops. The pipeline runs exactly once. The terminal-state guard
([workers.py:200-202](../src/flyquery/core/services/ingestion/workers.py#L200-L202))
covers redeliveries of already-finished jobs the same way.

### 3.1 Per-process semaphore vs cross-process coordination

flyquery follows flycanon's and flyradar's pattern: **each process owns its
own semaphore**, and there is no cross-process concurrency cap. This is a
deliberate trade:

- **Pro**: zero coordination cost. No distributed locks. Adding a replica
  doesn't require updating any registry. The only shared state is the
  durable job row.
- **Con**: total fleet inflight is `N_processes * ingest_worker_concurrency`.
  If you size each process for "use at most 4 LLM slots" and then run 10
  replicas, you have implicitly told the LLM provider you'd like 40
  concurrent requests. Plan capacity at the fleet level, not the process
  level.

The flycanon worker pattern at
[flycanon/.../ingest_worker.py:96-107](../../flycanon/src/flycanon/core/services/workers/ingest_worker.py#L96-L107)
documents this trade in the most detail; the same calculus applies here.

### 3.2 Capacity formula

```
total_inflight_jobs = N_processes * FLYQUERY_INGEST_WORKER_CONCURRENCY
fleet_LLM_RPS_ceiling = total_inflight_jobs * (avg_LLM_calls_per_job / avg_job_duration_s)
```

For a DESCRIBE_PASS over a 60-section workbook with
`ingest_section_concurrency=8` ([config.py:96](../src/flyquery/config.py#L96)),
each job fires up to 8 describe LLM calls in parallel and runs ~4 minutes,
so a worker with `INGEST_WORKER_CONCURRENCY=4` peaks at 32 in-flight LLM
calls per worker (4 jobs × 8 sections). Two workers = 64 in-flight calls
-- comfortably under Anthropic's standard 1000 RPM per key, but you can
see how four workers would start brushing against it.

### 3.3 When to scale up vs out

| Bottleneck                  | Symptom                                           | Action                            |
|-----------------------------|---------------------------------------------------|-----------------------------------|
| CPU-bound parse (Parquet)   | High CPU on workers, low LLM provider latency     | Scale up cores per pod            |
| LLM-bound describe          | High wall-clock per job, provider RPM headroom    | Scale out replicas                |
| LLM rate-limited (429s)     | Jobs stuck in describe                            | DO NOT scale -- lower `ingest_section_concurrency` or buy quota |
| Postgres connection ceiling | `too many clients` from pool                      | Scale OUT API replicas, tune `engine.pool_size` |
| Object store throttling     | S3 503s                                           | Scale out (request rate scales with replicas) |

CPU/IO bottlenecks are process-level; LLM-call bottlenecks are fleet-level.

---

## 4. Backpressure

There is no in-memory queue inside `IngestWorker`. The dispatcher
([workers.py:114-125](../src/flyquery/core/services/ingestion/workers.py#L114-L125))
creates a task and immediately returns to the bus; that task then awaits
`self._sem` and blocks if the semaphore is empty. The throttle point is
not the dispatcher, it's `_guarded_handle`:

```
EDA adapter buffer  (e.g. postgres outbox: ~100/batch)
        |
        v
_dispatch  --returns synchronously, scheduling a task--
        |
        v
asyncio task queue (one Task per inflight envelope; holds payload)
        |
        v
_guarded_handle:  async with self._sem    <-- ACTUAL throttle point
```

When the semaphore is exhausted, tasks pile up in the asyncio scheduler
holding envelope references. The pile is bounded only by worker memory.
Three things keep it sane:

1. **Lower per-process concurrency** if you see memory pressure (4 is
   already conservative).
2. **The bus's own buffer.** The postgres outbox adapter won't pull the
   next batch until the current one is in-flight, naturally slowing the
   poll cadence.
3. **At-least-once redelivery.** Timed-out / un-acked deliveries get
   redelivered on the next poll; the `PENDING` durability in
   `flyquery_ingest_jobs` means we never lose work to a dropped envelope.

**Operator signals**:

- `bus_delivery_p99_ms` -- rising means workers can't keep up.
- `len(IngestWorker._inflight)` (gauge to export) -- rising = semaphore
  contention.
- `SELECT count(*) FROM flyquery_ingest_jobs WHERE status='PENDING'` --
  the durable backlog; trending up with healthy workers = need more
  replicas.

---

## 5. Crashed-worker recovery

The problem: `_mark_running`
([workers.py:683-695](../src/flyquery/core/services/ingestion/workers.py#L683-L695))
moves the row to `RUNNING`. If the worker process then OOMs, gets
SIGKILLed, or has its node terminated, the row sits at `RUNNING` forever:

- The bus won't redeliver because the original handler "completed" (the
  process is gone; the consumer ack never fired, but neither did a NACK).
- A redelivery that *does* arrive can't claim the row because
  `_mark_running`'s `WHERE status='PENDING'` filter rejects it.
- A human operator has to manually flip the row, and they don't know to
  look.

This was called out in the existing
[async-ingest.md:73-80](async-ingest.md#L73-L80) doc as a known v1 gap.
**The RetentionWorker closes that gap**, mirroring the pattern at
[flyradar/.../retention_worker.py:152-194](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L152-L194):

```
+-- RetentionWorker.run_once ------------------------------+
|                                                          |
|  cutoff = now - processing_lease_s                       |
|                                                          |
|  stuck_ids = SELECT id FROM flyquery_ingest_jobs        |
|              WHERE status='RUNNING'                      |
|              AND started_at < cutoff                     |
|              LIMIT 200                                   |
|                                                          |
|  UPDATE flyquery_ingest_jobs                             |
|     SET status='PENDING', started_at=NULL                |
|   WHERE id = ANY(stuck_ids)                              |
|     AND status='RUNNING'   <-- race guard                |
|                                                          |
|  for id in stuck_ids:                                    |
|      publisher.publish(                                  |
|          destination='flyquery.ingest',                  |
|          event_type='IngestRequested',                   |
|          payload={'ingest_job_id': id}                   |
|      )                                                   |
+----------------------------------------------------------+
```

The republished envelope hits whichever live worker the bus routes it to.
That worker re-runs `_mark_running`, succeeds (the row is `PENDING`
again), and processes the job normally. The atomic claim guarantees that
if **another** worker observed the same redelivery, only one will run.

### Lease tuning

Set `FLYQUERY_PROCESSING_LEASE_S` **higher than the longest expected
legitimate job**. The single biggest job in flyquery today is DESCRIBE_PASS
on a 60-column XLSX, which empirically runs ~4 minutes -- well under the
default 3600s. If you raise `ingest_handler_timeout_s` for a custom
deployment, raise the lease in lockstep so the reaper doesn't republish
healthy in-flight work.

Conversely, if you set it too high, a crashed worker leaves stuck jobs
unprocessed for that whole window. The flyradar convention -- "the longest
async timeout plus a safety margin" -- applies here directly
([flyradar/config.py:125-132](../../flyradar/src/flyradar/config.py#L125-L132)).

### Orphan PENDING (publish failure)

There's a sibling failure mode: `IngestJobService._enqueue`
([ingest_job_service.py:103-143](../src/flyquery/core/services/ingest_jobs/ingest_job_service.py#L103-L143))
inserts the job row, **then** publishes the event. If the publish step
fails (transient bus blip), the row sits `PENDING` with no worker waking
up to process it. The publisher itself swallows failures by design
([ingest_publisher.py:105-110](../src/flyquery/core/eda/ingest_publisher.py#L105-L110))
so the upload endpoint doesn't 500 on a transient EDA outage.

The RetentionWorker's second sweep -- modelled on
[flyradar/.../retention_worker.py:113-150](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L113-L150)
-- finds `PENDING` rows older than `orphan_queued_grace_s` (default 600s)
and republishes them. The worker's `_mark_running` atomic claim safely drops
the duplicate when the original envelope did make it.

---

## 6. Cooperative cancellation

`POST /ingest-jobs/{id}:cancel`
([ingest_job_service.py:184-202](../src/flyquery/core/services/ingest_jobs/ingest_job_service.py#L184-L202))
returns immediately after flipping `status='CANCELLED'` in the database.
The actual stop is **best-effort**.

The worker checks for cancellation at every stage boundary via
`_check_cancelled`
([workers.py:653-658](../src/flyquery/core/services/ingestion/workers.py#L653-L658)):

```python
async def _check_cancelled(self, job_id):
    job = await self._load_job(job_id)
    if job is not None and job["status"] == "CANCELLED":
        raise asyncio.CancelledError(f"job {job_id} cancelled by user")
```

The REPARSE flow calls it 6 times per table
([workers.py:335, 351, 429, 466, 488, 506](../src/flyquery/core/services/ingestion/workers.py#L335)):
before receive, before parse, before each table's reconcile/embed/publish.
DESCRIBE_PASS calls it once per snapshot
([workers.py:597](../src/flyquery/core/services/ingestion/workers.py#L597)).
This means cancel latency is bounded by the longest single stage -- typically
one describe LLM call (~5-30s), occasionally one parse pass (~30-60s for a
large XLSX).

There is no inner-stage cancel propagation. A 5-minute LLM call cannot be
interrupted mid-flight without provider support. Operators should expect
"cancel in flight" jobs to flip to `CANCELLED` within a stage boundary, not
instantly.

**SSE behaviour**: when the worker observes the cancel and raises
`CancelledError`, the surrounding `try` falls through to the error path
([workers.py:237-248](../src/flyquery/core/services/ingestion/workers.py#L237-L248)).
Note that `CancelledError` is intentionally re-raised inside
`_guarded_handle`
([workers.py:144-145](../src/flyquery/core/services/ingestion/workers.py#L144-L145))
-- it does NOT call `emit_error`, because the cancel is the operator's
explicit intent, not a failure. The SSE stream sees the terminal
`emit_final` from the next event poll *or* observes the row hit
`CANCELLED` and closes.

---

## 7. Heartbeats and observability

### Structured logs

`IngestWorker` logs at four key moments:

- **Boot** (`workers.py:87-92`): one INFO line with topic, concurrency,
  timeout.
- **Drain** (`workers.py:153, 160`): one INFO at drain start, one WARNING
  if drain timed out.
- **Per-dispatch** (`workers.py:135-148`): DEBUG on success, WARNING on
  timeout or unexpected exception, INFO on the per-job "succeeded" line
  ([workers.py:235](../src/flyquery/core/services/ingestion/workers.py#L235)).
- **Cooperative cancel** (`workers.py:657`): INFO when a job flips.

`RetentionWorker` follows the flyradar logging convention
([retention_worker.py:101-110](../../flyradar/src/flyradar/core/services/workers/retention_worker.py#L101-L110)):
one INFO `retention_sweep_completed` line per non-empty sweep with the full
stats breakdown; silent sweeps stay at DEBUG.

### Per-stage events

Each completed stage emits a row to `flyquery_ingest_events` via the
helpers in
[events.py](../src/flyquery/core/services/ingestion/events.py):
`emit_running`, `emit_stage`, `emit_final`, `emit_error`. The repository
wrapping these writes is intentionally best-effort
([ingest_event_repository.py:67-107](../src/flyquery/core/services/ingestion/ingest_event_repository.py#L67-L107))
-- a broken event row never aborts the pipeline. The durable truth is the
`flyquery_ingest_jobs` row; events are an audit + SSE trail layered on top.

The full event taxonomy is documented in
[events.py:12-27](../src/flyquery/core/services/ingestion/events.py#L12-L27).

### Prometheus / actuator

`/actuator/health` includes worker health when the indicators are wired
into the worker process's `PyFlyApplication`
([main.py:66-72](../src/flyquery/main.py#L66-L72)). The worker pod's
healthcheck should hit `/actuator/health/liveness` if the worker exposes
HTTP, OR -- more commonly -- use a heartbeat-file mtime check, following
the flyradar pattern
([flyradar/cli.py:117-144](../../flyradar/src/flyradar/cli.py#L117-L144)).
flyquery currently has `FLYQUERY_INGEST_HEARTBEAT_S=30`
([config.py:58](../src/flyquery/config.py#L58)) reserved for this --
the worker driver in `flyquery worker ingest` touches a heartbeat file at
that cadence.

Recommended Prometheus metric names (TODO -- not yet emitted):

- `flyquery_ingest_worker_inflight` (gauge, `len(self._inflight)`)
- `flyquery_ingest_worker_handler_seconds` (histogram, per-stage latency)
- `flyquery_retention_sweep_seconds` (histogram, per-sweep wall time)
- `flyquery_retention_rows_reaped_total{table,reason}` (counter)

---

## 8. RLS bypass

Workers connect to Postgres as **`flyquery_admin`**, which is provisioned
with the `BYPASSRLS` attribute in
[0007_rls.py:48-50](../migrations/versions/0007_rls.py#L48-L50). The API
server connects as **`flyquery_app`**
([config.py:30](../src/flyquery/config.py#L30)), which does NOT have
`BYPASSRLS` and is bound to the per-request tenant context by the
`TenantContextMiddleware` -> `after_begin` GUC hook
([main.py:197-207](../src/flyquery/main.py#L197-L207),
[concurrency.md §3](concurrency.md#3-rls-guc-binding-via-after_begin-hook)).

**Why workers bypass RLS**: a single ingest worker process drains a single
queue that interleaves jobs from every tenant in the deployment. It has no
per-request tenant context to bind. The worker's handler at
[workers.py:184-217](../src/flyquery/core/services/ingestion/workers.py#L184-L217)
loads the job row, reads `tenant_id` and `workspace_id` out of it, and then
passes those values as explicit parameters to every downstream call
(`emit_running`, `run_receive`, `run_parse`, ...). All inserts and updates
manipulate the tenant scope via parameter binding, not via Postgres GUCs.

This is the lock-step pattern flycanon uses
([flycanon/.../ingest_worker.py:37-46](../../flycanon/src/flycanon/core/services/workers/ingest_worker.py#L37-L46))
and the pattern referenced at
[workers.py:184](../src/flyquery/core/services/ingestion/workers.py#L184):
`Load job row (cross-workspace: worker has BYPASSRLS privilege)`.

**Operational consequence**: deploy workers with
`FLYQUERY_DATABASE_URL_ADMIN` set, never `FLYQUERY_DATABASE_URL`. A worker
booted on the `flyquery_app` role will fail to read jobs whose tenant
context isn't bound -- i.e., always -- and silently return 0 rows from
`_load_job`, logging "unknown job_id" for everything. This is one of the
sharpest gotchas in the system.

The repository layer adds a defence-in-depth note at
[schema_object_repository.py:46](../src/flyquery/core/services/schema_objects/schema_object_repository.py#L46):
some cross-workspace queries explicitly call out "BYPASSRLS roles (the
ingestion worker can be that role)" so future readers know the design
intent.

---

## 9. Worker CLI reference (NEW in 26.5.10)

Today the CLI exposes only `flyquery serve` and `flyquery version`
([cli.py:11-37](../src/flyquery/cli.py#L11-L37)). Version 26.5.10 expands it:

```
flyquery serve              -- API server (existing; unchanged)
flyquery worker ingest      -- IngestWorker only
flyquery worker retention   -- RetentionWorker only
flyquery worker all         -- both workers in one process (dev / docker compose)
```

The driver pattern -- boot `PyFlyApplication`, resolve the worker out of
the DI container, run forever with SIGTERM/SIGINT wired to a cooperative
stop event -- follows the flyradar CLI at
[flyradar/cli.py:52-193](../../flyradar/src/flyradar/cli.py#L52-L193).

### SIGTERM / SIGINT handling

Both signals route through one `_request_stop(reason)` closure (see
[flyradar/cli.py:126-149](../../flyradar/src/flyradar/cli.py#L126-L149)):
sets a local `stop_requested` event, calls `worker.stop()` (sets
`IngestWorker._stop_event`), calls `retention_worker.request_stop()` if
present, awaits each task with a `wait_for(timeout=shutdown_grace_s)`
budget, cancels overruns, then runs `pyfly_app.shutdown()` to close the DB
pool.

Docker's `stop_grace_period` (and Kubernetes'
`terminationGracePeriodSeconds`) should be **at least**
`ingest_shutdown_grace_s` plus a few seconds of slack. Default
`ingest_shutdown_grace_s=30` ([config.py:57](../src/flyquery/config.py#L57))
-> 45s grace is a safe choice for an LLM-bound fleet.

---

## 10. Settings reference

All settings are environment-variable-bound via pydantic-settings; the
`FLYQUERY_` prefix is automatic
([config.py:19-25](../src/flyquery/config.py#L19-L25)).

### Ingest worker

| Env var                              | Default | Purpose                                                          |
|--------------------------------------|---------|------------------------------------------------------------------|
| `FLYQUERY_INGEST_TOPIC`              | `flyquery.ingest` | EDA topic the worker subscribes to              |
| `FLYQUERY_INGEST_WORKER_CONCURRENCY` | `4`     | Per-process semaphore size                                       |
| `FLYQUERY_INGEST_HANDLER_TIMEOUT_S`  | `600`   | Per-job wall-clock timeout                                       |
| `FLYQUERY_INGEST_SHUTDOWN_GRACE_S`   | `30`    | Drain budget after SIGTERM                                       |
| `FLYQUERY_INGEST_HEARTBEAT_S`        | `30`    | Heartbeat file touch interval (driver)                           |
| `FLYQUERY_INGEST_MAX_ATTEMPTS`       | `3`     | Reserved -- caps the retry count when retry policy lands         |
| `FLYQUERY_INGEST_SECTION_CONCURRENCY`| `8`     | Per-job XLSX section parallelism (LLM rate-limit safety, see [config.py:86-96](../src/flyquery/config.py#L86-L96)) |

### Retention worker (NEW in 26.5.10)

| Env var                                    | Default | Purpose                                                       |
|--------------------------------------------|---------|---------------------------------------------------------------|
| `FLYQUERY_RETENTION_SCAN_INTERVAL_S`       | `3600`  | Sleep between sweeps                                          |
| `FLYQUERY_RETENTION_INGEST_EVENTS_DAYS`    | `30`    | TTL for `flyquery_ingest_events` (`0` disables)               |
| `FLYQUERY_RETENTION_AUDIT_EVENTS_DAYS`     | `0`     | TTL for `flyquery_audit_events` (`0` = keep forever)          |
| `FLYQUERY_RETENTION_COST_EVENTS_DAYS`      | `0`     | TTL for `flyquery_cost_events` (`0` = keep forever)           |
| `FLYQUERY_PROCESSING_LEASE_S`              | `3600`  | RUNNING-row reap threshold (must exceed longest job timeout)  |
| `FLYQUERY_ORPHAN_QUEUED_GRACE_S`           | `600`   | PENDING-row republish threshold                               |
| `FLYQUERY_DATASET_PURGE_TOMBSTONE_DAYS`    | `90`    | Hard-delete PURGING datasets after N days (see [dataset_service.py:127-131](../src/flyquery/core/services/datasets/dataset_service.py#L127-L131)) |

### Capacity planning table

| Tier         | API pods | Ingest pods | Ingest conc. | Total inflight | Retention pods |
|--------------|----------|-------------|--------------|----------------|----------------|
| dev          | 1 (`flyquery worker all`) | -           | 4            | 4              | -              |
| small prod   | 1        | 1           | 4            | 4              | 1              |
| mid prod     | 2-4      | 2-4         | 4-8          | 8-32           | 1              |
| large prod   | HPA      | HPA         | 4            | scales w/ HPA  | 1 (dedicated)  |

Pick `INGEST_WORKER_CONCURRENCY` so that the worker's RAM footprint
(`size_of(job_payload) + len(parquet_buffer)`) times concurrency stays
under your container's memory limit. The dominant memory consumer is the
fully-loaded file bytes during stage 1
([workers.py:340-348](../src/flyquery/core/services/ingestion/workers.py#L340-L348))
-- a `max_file_mb=2048` upload with concurrency=4 can pin 8 GB of RSS
during a redelivery storm.

---

## 11. Deployment topologies

### Dev (`docker compose up`)

One `flyquery serve` container + one `flyquery worker all` container +
postgres + ollama. The two-container split is what
[deployment-topology.md:79-93](deployment-topology.md#L79-L93) already
describes; `flyquery worker all` collapses ingest + retention into one
process for laptops.

### Small prod (<= 10 ingest jobs/sec)

`1 API pod` + `1 ingest pod` + `1 retention pod`, sharing one Postgres and
one object store. The retention pod can co-locate on the API or ingest
node -- it does almost no work most of the time.

### Mid prod

`N API pods` + `M ingest pods` (sized to LLM RPM headroom) + `1 retention
pod`. Size `M` so that
`M * INGEST_WORKER_CONCURRENCY * avg_LLM_calls_per_job` stays under the
provider RPM minus the synchronous request path's usage. The sync upload
endpoint runs LLMs too (optional grounding pass), so the budget is shared.

### Large prod (Kubernetes)

Three Deployments -- `flyquery-api`, `flyquery-ingest`, `flyquery-retention`
-- with HPAs on the first two and `replicas: 1` on retention. The ingest
HPA target should be **Postgres-side queue depth**:
`SELECT count(*) FROM flyquery_ingest_jobs WHERE status='PENDING'`, scraped
into Prometheus on a 30s interval, target `< 50` pending per ingest replica.
Run separate node pools for API (latency-sensitive) and ingest (CPU + memory
heavy, latency-tolerant). The retention pod stays single-replica -- two
replicas running the same sweep is wasteful but safe (the atomic claim
handles it).

---

## 12. Failure modes catalog

| Symptom                                       | Root cause                                                            | What the system does                                                            | Operator action                                                              |
|-----------------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Jobs accumulate in `PENDING`                  | EDA bus down (outbox channel stalled / broker down)                   | Rows persist; retention sweep republishes after `orphan_queued_grace_s`         | Check bus health (`pg_listening_channels()` or kafka lag)                    |
| One tenant's describe jobs all fail           | LLM provider rate-limited                                             | `_guarded_handle` logs WARNING; job marked `FAILED`. No auto-backoff in flyquery yet (cf. flyradar's [_schedule_retry](../../flyradar/src/flyradar/core/services/workers/discovery_worker.py#L343-L405)) | Re-queue via REPARSE; check `embedding_rate_limit_rpm` ([config.py:121](../src/flyquery/config.py#L121)) |
| Upload endpoint 500s on object store outage   | Stage 1 (`run_receive`) fails before any DB write                     | No `flyquery_files` row, no `flyquery_ingest_jobs` row; endpoint returns 7807   | Retry from client; OS failures are not silently absorbed                     |
| Job stuck `RUNNING` for hours                 | Worker OOM/SIGKILL/node terminated mid-pipeline                       | Retention sweep flips row to `PENDING`, republishes; healthy worker resumes     | Check pod restarts; verify `processing_lease_s` exceeds longest job          |
| `IngestWorker handler timed out` in logs      | Single job exceeded `ingest_handler_timeout_s`                        | Row stays `RUNNING`; reaped after `processing_lease_s`. Next worker re-runs     | If recurring, raise the timeout or investigate the stage                     |
| All workers idle, queue rising                | Worker booted with `flyquery_app` role -- can't see cross-tenant jobs | Every `_load_job` returns None; logs `unknown job_id=...` for everything        | Set `FLYQUERY_DATABASE_URL_ADMIN`; verify role on the connection             |
| Postgres failover mid-pipeline                | New primary elected; in-flight tx aborted                             | Stage tx raises `OperationalError`. Bus considers delivery un-acked. Redelivery | Confirm via `GET /ingest-jobs/{id}` -- row will be `PENDING` shortly         |
| Cancel doesn't propagate                      | Cancelled mid-stage; LLM call uninterruptible                         | Observed at next `_check_cancelled` boundary; raises `CancelledError`           | Wait one stage; for sub-stage density would require code change              |
| Retention sweep takes minutes                 | Massive `flyquery_ingest_events` backlog (no TTL set initially)       | Sweep logs `retention_sweep_completed` with high counts; next sweep is faster   | Set `FLYQUERY_RETENTION_INGEST_EVENTS_DAYS=30` from day 1; backfill via SQL  |

### Bus-down deep dive

The Postgres outbox adapter (default;
[pyfly.yaml:64-66](../pyfly.yaml#L64-L66)) polls an event table. If
NOTIFY stalls but the DB stays up, publishers keep writing rows (publish
returns success on commit) while consumers don't wake. Diagnostic:
`pyfly_outbox WHERE status='PENDING'` trending up alongside
`flyquery_ingest_jobs WHERE status='PENDING'`. With
`FLYQUERY_EDA_ADAPTER=kafka` ([config.py:144](../src/flyquery/config.py#L144))
the diagnostic shifts to broker-side topic lag.

### Postgres failover

Worker transaction boundary is per-stage. On failover the current
`s.begin()` raises `OperationalError`, the bare-`except` at
[workers.py:237-248](../src/flyquery/core/services/ingestion/workers.py#L237-L248)
fires, the `_mark_failed` attempt also fails (DB still down), the bus
sees an un-acked delivery, and the row stays `RUNNING`. The retention
reaper picks it up after `processing_lease_s`. A lease shorter than the
failover RTO causes a redundant republish during failover, which is safe
-- the republished envelope queues until the bus recovers.

---

## Cross-references

- Per-stage pipeline detail: [ingestion.md](ingestion.md), [pipeline.md](pipeline.md)
- Cancel semantics + state machine: [async-ingest.md](async-ingest.md)
- AsyncSession + RLS GUC mechanics: [concurrency.md](concurrency.md)
- EDA topic schemas + envelopes: [eda-events.md](eda-events.md)
- Deployment knobs (helm values, env files): [deployment.md](deployment.md), [deployment-topology.md](deployment-topology.md)
- Operations runbook (alerts + runbooks per failure mode): [operations-runbook.md](operations-runbook.md)
