# Async-job webhook callbacks

> **Status — live as of 26.5.11.** See [`CHANGELOG.md`](../CHANGELOG.md#26511---2026-05-24).

Every async ingest job in flyquery (created via
`POST /api/v1/ingest-jobs` or `POST /api/v1/datasets/{ds}/files:async`)
can attach an HTTPS webhook target. When the job reaches a terminal
status (`SUCCEEDED` / `FAILED` / `CANCELLED`) the worker POSTs the
canonical `IngestJobRead` payload to the configured URL.

The design constraints:

- **No lost callbacks**. The webhook target is written to a
  transactional outbox (`flyquery_callback_outbox`) in the SAME
  database transaction as the job's status flip. A process crash
  between the two writes is impossible.
- **At-least-once delivery**. A separate `CallbackWorker` drains the
  outbox with exponential backoff (5 attempts: 0s, 30s, 5m, 1h, 6h).
- **Tamper-evident**. Optional shared secret produces an
  `X-Flyquery-Signature: sha256=<hmac>` header so the receiver can
  verify authenticity.
- **Horizontally scalable**. The outbox claim uses
  `FOR UPDATE SKIP LOCKED`, so N peer `CallbackWorker` processes
  never double-deliver the same row.

## Quick start

### 1. Configure a callback at job creation

**Per-request (PARSE_AND_INGEST via async upload):**

```bash
curl -X POST "https://flyquery/api/v1/datasets/$DS/files:async" \
  -H "X-Tenant-Id: $TENANT" -H "X-Workspace-Id: $WS" \
  -F "file=@orders.xlsx" \
  -F "callback_url=https://hooks.example.com/flyquery" \
  -F "callback_secret=$WEBHOOK_SECRET" \
  -F 'callback_headers={"X-Pipeline": "prod"}'
```

The same three knobs can also arrive via headers:
`X-Flyquery-Callback-Url`, `X-Flyquery-Callback-Secret`,
`X-Flyquery-Callback-Headers`. Form fields win when both are
present.

**Per-request (REPARSE / SAMPLE_REFRESH / DESCRIBE_PASS /
RELATION_PASS via POST `/api/v1/ingest-jobs`):**

```json
{
  "dataset_id": "...",
  "job_kind": "REPARSE",
  "table_id": "...",
  "callback": {
    "url": "https://hooks.example.com/flyquery",
    "secret": "shared-secret-min-8-chars",
    "headers": { "X-Pipeline": "prod" }
  }
}
```

**Process-wide default (configuration):**

```bash
# .env (or any pydantic-settings source)
FLYQUERY_DEFAULT_CALLBACK_URL=https://hooks.example.com/flyquery
FLYQUERY_DEFAULT_CALLBACK_SECRET=shared-secret-min-8-chars
FLYQUERY_DEFAULT_CALLBACK_HEADERS={"X-Pipeline":"prod"}
```

Every async job whose request omits `callback_url` will fall through
to this bundle. The **whole bundle** (URL + secret + headers) moves
together: a request that supplies its own URL does NOT inherit the
default's secret -- the default secret was authored for the default
URL and may not be safe to share with another receiver.

### 2. Implement the receiver

The webhook request:

| Header | Always set | Value |
|---|---|---|
| `Content-Type` | yes | `application/json` |
| `User-Agent` | yes | `flyquery-callback/26` |
| `X-Flyquery-Event` | yes | `ingest.succeeded` \| `ingest.failed` |
| `X-Flyquery-Job-Id` | yes | the UUID of the ingest job |
| `X-Flyquery-Signature` | only when `secret` set | `sha256=<hex hmac over body>` |
| (your custom headers) | per `callback_headers` | as configured |

The body is the canonical `IngestJobRead`, plus an explicit
`result_json` field with the same shape the GET endpoint returns:

```json
{
  "ingest_job_id": "c820f1b7-d416-4b54-9e5a-41bb18af72fc",
  "tenant_id": "acme",
  "workspace_id": "8b7c…",
  "dataset_id": "d394…",
  "table_id": null,
  "file_id": "928a…",
  "snapshot_id": null,
  "job_kind": "PARSE_AND_INGEST",
  "status": "SUCCEEDED",
  "attempts": 1,
  "request_json": {"actor": "acme", "dataset_name": "orders"},
  "result_json": {}
}
```

### 3. Verify the signature

Reject any request whose `X-Flyquery-Signature` does not match
`sha256=` + HMAC-SHA256 of the **raw body** keyed by the shared
secret. Use a constant-time compare to defeat timing-based probes.

A reference Python receiver (the same one used by our E2E test):

```python
import hashlib, hmac, http.server, os

SECRET = os.environ["WEBHOOK_SECRET"].encode()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        sent = self.headers.get("X-Flyquery-Signature") or ""
        want = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sent, want):
            self.send_response(401); self.end_headers(); return
        # Process body, then 2xx.
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

http.server.HTTPServer(("0.0.0.0", 8821), Handler).serve_forever()
```

The receiver must return any 2xx status within
`FLYQUERY_CALLBACK_REQUEST_TIMEOUT_S` (default 10s). Anything else
(non-2xx, transport error, timeout) is a delivery failure and the
row is retried.

## Retry policy

| Attempt | Backoff before this attempt |
|---|---|
| 1 | 0s |
| 2 | 30s |
| 3 | 5min |
| 4 | 1h |
| 5 | 6h |
| 6+ | `DEAD` (no more attempts) |

After attempt 5 fails, the outbox row is flipped to `DEAD` and is
NOT retried again. The row stays in the table for audit; recovery
is a manual ops decision. See **Operations** below.

The backoff schedule is intentionally aggressive at the start
(catch transient blips quickly) and long-tailed (give a multi-hour
outage time to recover before declaring the row dead).

## Observability

Every delivery attempt is one row in `flyquery_callback_outbox`.
Read via:

```bash
GET /api/v1/ingest-jobs/{job_id}/callbacks
GET /api/v1/ingest-jobs/{job_id}/callbacks?status=DEAD
```

Returns a paginated `CallbackDeliveryListResponse`:

```json
{
  "items": [{
    "id": "91707379-...",
    "ingest_job_id": "c820f1b7-...",
    "callback_url": "https://hooks.example.com/flyquery",
    "event_type": "ingest.succeeded",
    "status": "DELIVERED",
    "attempts": 1,
    "last_attempt_at": "2026-05-24T14:48:27.799553Z",
    "last_status_code": 200,
    "last_error": null,
    "next_attempt_at": "2026-05-24T14:48:24.818433Z",
    "created_at": "2026-05-24T14:48:24.818433Z",
    "finished_at": "2026-05-24T14:48:27.799553Z"
  }],
  "total": 1, "limit": 50, "offset": 0
}
```

Worker-side observability:

- `callback_worker_started poll_interval_s=… batch=… timeout_s=…`
  at startup.
- `callback_delivered id=… job_id=… status=200` per success.
- `callback_attempt_failed id=… job_id=… attempts=N/5 terminal=… status=… error=…`
  per failure (including the final attempt that goes `DEAD`).

## Operations

### Recover a DEAD callback

When a receiver outage exceeds 6 hours, all in-flight callback rows
flip to `DEAD`. The job rows themselves are still `SUCCEEDED`; the
caller-facing damage is "no notification".

Manual recovery options:

1. **Queue a REPARSE** for the affected `dataset_id` -- the new job
   inherits the same default callback config, so the receiver gets
   a fresh attempt without losing the catalog state.
2. **Republish in SQL** (DBA path) -- flip selected rows back to
   `PENDING` with a fresh `next_attempt_at`:
   ```sql
   UPDATE flyquery_callback_outbox
   SET status='PENDING', next_attempt_at=now(),
       last_error=last_error || ' [manual_replay]'
   WHERE status='DEAD' AND ingest_job_id = $1;
   ```
   The `CallbackWorker` will pick them up at the next poll.

### Configuration knobs

| Setting | Default | Purpose |
|---|---|---|
| `FLYQUERY_CALLBACK_POLL_INTERVAL_S` | `5.0` | Sleep between empty-outbox polls. |
| `FLYQUERY_CALLBACK_BATCH_SIZE` | `25` | Max rows claimed per poll. `FOR UPDATE SKIP LOCKED` caps this per worker. |
| `FLYQUERY_CALLBACK_REQUEST_TIMEOUT_S` | `10.0` | Per-attempt HTTP timeout. Beyond this is a transport failure. |
| `FLYQUERY_DEFAULT_CALLBACK_URL` | `null` | Process-wide default receiver. |
| `FLYQUERY_DEFAULT_CALLBACK_SECRET` | `null` | Default shared secret. |
| `FLYQUERY_DEFAULT_CALLBACK_HEADERS` | `{}` | Default extra headers (JSON object). |

### Run the worker

Production: one or more dedicated processes per region.

```bash
flyquery worker callback
```

Dev / docker-compose: bundled in `flyquery worker all`.

See [`workers.md`](workers.md) for the full deployment topology.

## Security notes

- **Always set a `secret` in production**. Without it the receiver
  cannot distinguish a genuine flyquery callback from a forged one.
  Use at least 32 bytes of cryptographic randomness.
- **Pin to HTTPS** at the receiver -- the body contains tenant +
  dataset identifiers that should not traverse the public network in
  cleartext.
- **The shared secret never leaves your process** -- only the HMAC
  digest is on the wire.
- **Reserved headers cannot be overridden**. The
  `CallbackConfig.headers` validator rejects
  `X-Flyquery-Signature` / `X-Flyquery-Event` / `X-Flyquery-Job-Id` /
  `Content-Type`. The dispatcher additionally applies these AFTER
  caller-supplied extras, so a malicious or misconfigured extra-
  header bag can never shadow the signature header.
- **Per-request bundles do not inherit the default secret**. If a
  request supplies `callback_url`, the worker uses ONLY the
  request's secret + headers (which may be `null`) -- it does NOT
  merge in `FLYQUERY_DEFAULT_CALLBACK_SECRET`.

## Cross-links

- [`async-ingest.md`](async-ingest.md) -- the upload endpoint where
  most callbacks originate.
- [`workers.md`](workers.md) -- deployment + scaling for
  `CallbackWorker` alongside `IngestWorker` + `RetentionWorker`.
- [`api-reference.md`](api-reference.md) -- canonical schemas for
  `IngestJobCreate.callback` + `CallbackDeliveryRead`.
