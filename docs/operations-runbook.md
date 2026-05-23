# flyquery — Operations Runbook

## Table of Contents

1. [Cold start checklist](#1-cold-start-checklist)
2. [Daily health checks](#2-daily-health-checks)
3. [Common errors and fixes](#3-common-errors-and-fixes)
4. [GDPR purge runbook](#4-gdpr-purge-runbook)
5. [Key rotation](#5-key-rotation)
6. [Backup and restore](#6-backup-and-restore)
7. [Scaling up (more workers)](#7-scaling-up-more-workers)
8. [Incident response template](#8-incident-response-template)

---

## 1. Cold start checklist

Use this checklist when deploying flyquery for the first time or after a
full teardown.

### Prerequisites

- Postgres ≥ 15 with `pgvector` extension available.
- Redis (optional; required for `FLYQUERY_EDA_ADAPTER=redis` or
  `FLYQUERY_RATE_LIMIT_BACKEND=redis`).
- Object storage: local directory, S3 bucket, GCS bucket, or Azure Blob
  container. IAM/service-account credentials configured.
- `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY` if using GPT-4o fallback).

### Step-by-step

```bash
# 1. Create Postgres database
psql -c "CREATE DATABASE flyquery;"

# 2. Create roles (copy-paste safe; idempotent on re-run)
psql flyquery << 'SQL'
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'flyquery_admin') THEN
    CREATE ROLE flyquery_admin LOGIN PASSWORD 'CHANGE_ME';
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'flyquery_app') THEN
    CREATE ROLE flyquery_app LOGIN PASSWORD 'CHANGE_ME';
  END IF;
END $$;
GRANT ALL PRIVILEGES ON DATABASE flyquery TO flyquery_admin;
SQL

# 3. Run migrations (uses flyquery_admin role via FLYQUERY_DATABASE_URL_ADMIN)
export FLYQUERY_DATABASE_URL_ADMIN="postgresql+asyncpg://flyquery_admin:CHANGE_ME@localhost:5432/flyquery"
export FLYQUERY_DATABASE_URL="postgresql+asyncpg://flyquery_app:CHANGE_ME@localhost:5432/flyquery"
uv run alembic upgrade head

# 4. Verify pgvector is enabled
psql flyquery -c "SELECT extname FROM pg_extension WHERE extname='vector';"
# If missing: CREATE EXTENSION vector;

# 5. Verify role split
psql "postgresql://flyquery_app:CHANGE_ME@localhost:5432/flyquery" \
  -c "SELECT current_user, pg_has_role('flyquery_app', 'BYPASSRLS', 'MEMBER');"
# pg_has_role should return 'f' (false) — app role must NOT bypass RLS

# 6. Start the service
task serve   # dev
# or: docker compose up flyquery-api flyquery-worker

# 7. Health check
curl -s http://localhost:8520/actuator/health | jq .status
# → "UP"

# 8. Version check
curl -s http://localhost:8520/api/v1/version
# → {"version": "26.5.3", ...}
```

### First-run smoke test

```bash
# Create workspace + dataset
curl -X POST http://localhost:8520/api/v1/workspaces \
  -H "X-Tenant-Id: test" -H "Content-Type: application/json" \
  -d '{"id": "ws01", "name": "Test Workspace"}'

curl -X POST http://localhost:8520/api/v1/datasets \
  -H "X-Tenant-Id: test" -H "X-Workspace-Id: ws01" \
  -H "Content-Type: application/json" \
  -d '{"name": "smoke-test"}'

# Upload a tiny CSV
printf "id,amount,region\n1,100,East\n2,200,West\n" > /tmp/test.csv
curl -X POST http://localhost:8520/api/v1/datasets/ds_smoke/files \
  -H "X-Tenant-Id: test" -H "X-Workspace-Id: ws01" \
  -F "file=@/tmp/test.csv"
# Note ingest_job_id

# Wait for ingestion
sleep 5
curl http://localhost:8520/api/v1/ingest-jobs/<job_id>

# Query
curl -X POST http://localhost:8520/api/v1/query \
  -H "X-Tenant-Id: test" -H "X-Workspace-Id: ws01" \
  -H "Content-Type: application/json" \
  -d '{"question": "Total amount by region", "dataset_id": "ds_smoke"}'
```

---

## 2. Daily health checks

### Service health

```bash
# API health
curl -s http://localhost:8520/actuator/health | jq .

# Worker health (if running separately)
curl -s http://localhost:8521/actuator/health | jq .
```

### Stuck jobs

```bash
# Jobs in RUNNING for > 15 minutes (possible heartbeat failure)
GET /api/v1/ingest-jobs?status=RUNNING&created_before=<15min_ago>

# Jobs in FAILED
GET /api/v1/ingest-jobs?status=FAILED&order=created_at_desc&limit=20
```

### Outbox relay lag (Postgres adapter)

```bash
psql flyquery -c "
  SELECT COUNT(*) AS pending_outbox
  FROM flyquery_ingest_events
  WHERE delivered_at IS NULL
    AND created_at < NOW() - INTERVAL '5 minutes';
"
# If > 0 and growing: check flyquery-worker logs for outbox relay errors
```

### Object-store reachability

```bash
curl -s http://localhost:8520/actuator/health/objectStore | jq .status
# → "UP" or "DOWN" with detail
```

### Embedding freshness

```bash
psql flyquery -c "
  SELECT COUNT(*) AS null_embeddings
  FROM flyquery_schema_objects
  WHERE embedding IS NULL AND is_active = true;
"
# Should be 0 after ingestion completes; non-zero indicates a stuck embed stage
```

---

## 3. Common errors and fixes

### `FORMAT_MISMATCH` on upload

**Symptom:** `POST /datasets/{id}/files` returns 422 with
`error_code=FORMAT_MISMATCH`.

**Cause:** The file's magic bytes don't match the declared extension. Common
case: an XLSX file saved with `.csv` extension.

**Fix:** Rename the file with the correct extension before uploading. Or use
`PUT /datasets/{ds}/tables/{id}:upload` with explicit `file_format` field.

---

### Ingest job stuck in RUNNING

**Symptom:** `GET /ingest-jobs/{id}` returns `status=RUNNING` for >15 minutes.

**Cause:** Worker process died without updating the job; heartbeat-timeout
recovery hasn't fired yet.

**Fix:**
```bash
# Check worker logs
docker compose logs flyquery-worker | tail -50

# If worker is dead, restart it
docker compose restart flyquery-worker

# The heartbeat-timeout background task resets the job to PENDING
# within FLYQUERY_INGEST_HANDLER_TIMEOUT_S (default 600s)
# To force-reset immediately:
psql flyquery -c "
  UPDATE flyquery_ingest_jobs
  SET status='PENDING', attempts=attempts+1
  WHERE id='<job_id>' AND status='RUNNING';
"
```

---

### NULL embeddings after ingestion

**Symptom:** `SELECT COUNT(*) FROM flyquery_schema_objects WHERE embedding IS NULL AND is_active=true` returns > 0.

**Cause:** Stage 9 (embed + index) failed or timed out. Check embedding model
config and API key.

**Fix:**
```bash
# Check ingest job events for stage 9
GET /api/v1/ingest-jobs/{id}/events?stage=embed

# Check embedding model config
echo $FLYQUERY_EMBEDDING_MODEL

# Re-run embed stage only via REPARSE
POST /api/v1/ingest-jobs
  {"job_kind": "REPARSE", "file_id": "<id>"}
```

---

### RLS returning zero rows

**Symptom:** `GET /datasets` returns `[]` even though datasets exist.

**Cause 1:** `X-Tenant-Id` and `X-Workspace-Id` headers are missing or
incorrect — the GUC is set to an empty string, and RLS filters everything.

**Fix:** Ensure `X-Tenant-Id` and `X-Workspace-Id` headers are present on
every request.

**Cause 2:** Runtime database URL uses `flyquery_admin` (BYPASSRLS) but
the query still returns 0 rows — means RLS is working correctly and the
wrong `workspace_id` is being passed.

**Fix:** Verify `app.workspace_id` is set to the correct value by checking
the `TenantContextMiddleware` log output.

---

### Agent timeouts

**Symptom:** Query fails with `error_code=AGENT_TIMEOUT` or
`execution_status=FAILED` after ~30 seconds.

**Cause:** LLM API is slow; `FLYQUERY_DEFAULT_STATEMENT_TIMEOUT_MS` or
`FLYQUERY_AGENT_MAX_OUTPUT_TOKENS` is too tight.

**Fix:**
```bash
# Increase statement timeout (ms)
export FLYQUERY_DEFAULT_STATEMENT_TIMEOUT_MS=60000

# Check LLM API health
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

---

### OpenAPI drift gate failure

**Symptom:** CI fails on `task openapi-snapshot` with "spec drift detected".

**Cause:** A DTO or endpoint changed but `openapi.json` was not regenerated.

**Fix:**
```bash
task openapi-snapshot   # regenerates openapi.json
git add openapi.json
git commit -m "chore: regenerate openapi.json"
```

---

## 4. GDPR purge runbook

Use this runbook when a customer requests full data erasure for a workspace.

### Step 1 — Verify scope

```bash
# List all resources in the workspace
GET /api/v1/datasets?workspace_id=<ws_id>
GET /api/v1/audit?workspace_id=<ws_id>&event_type=workspace.purge_scheduled
```

### Step 2 — Initiate purge

```bash
DELETE /api/v1/workspaces/{workspace_id}:purge
X-Tenant-Id: <tenant>
X-Workspace-Id: <workspace_id>

→ {"purge_job_id": "...", "tombstone_expires_at": "2026-06-22T..."}
```

This starts the 30-day tombstone window. The workspace is immediately marked
as tombstoned (no new uploads or queries accepted), but data is not yet deleted.

### Step 3 — Cancel in-flight jobs

The `:purge` endpoint automatically sends `cancel_requested=true` to all
in-flight ingest jobs for the workspace. Monitor:

```bash
GET /api/v1/ingest-jobs?workspace_id=<ws_id>&status=RUNNING
# Wait until all return CANCELLED or SUCCEEDED
```

### Step 4 — Confirm tombstone expiry

After 30 days, a background task:
1. Deletes all `flyquery_*` rows for `(tenant_id, workspace_id)`.
2. Walks `{tenant_id}/{workspace_id}/` in object storage and deletes all blobs.
3. Records a `workspace.purged` audit event.

To perform an immediate purge (waiving the 30-day window, e.g., on explicit
customer request with signed consent):

```bash
POST /api/v1/workspaces/{id}:purge-immediate
X-Agent-Token: <admin-token>
# Requires scope: * (operator wildcard)
```

### Step 5 — Verify erasure

```bash
# Should return 404 or empty
GET /api/v1/workspaces/{workspace_id}

# Object storage should be empty under tenant/workspace prefix
# (check via provider console or CLI)
```

---

## 5. Key rotation

### EDA Postgres LISTEN/NOTIFY — no keys to rotate

Postgres LISTEN/NOTIFY uses the database connection credentials.
Rotate via standard Postgres password change + update `FLYQUERY_DATABASE_URL`.

### Object store credentials

1. Generate new IAM key / service account.
2. Update `FLYQUERY_OBJECT_STORE_*` credentials in secrets manager.
3. Rolling restart API + worker pods.
4. Revoke old key after all pods are running on new credentials.

### Workspace CMK/CMEK

1. Create new KMS key in your provider.
2. `PUT /api/v1/workspaces/{id}` with new `kms_key_uri`.
3. New uploads use the new key. Existing blobs retain the old key until
   re-ingested.
4. To re-encrypt existing blobs: `POST /ingest-jobs {job_kind:"REPARSE"}`
   for each affected file. This re-materialises Parquet under the new key.
5. Revoke old KMS key after all blobs are migrated.

See [security-model.md § 12](security-model.md#12-future-per-workspace-kmscmek)
for the v1 KEK/DEK roadmap.

### Agent tokens

```bash
# List all active tokens
GET /api/v1/agent-tokens

# Revoke old token
DELETE /api/v1/agent-tokens/{token_id}

# Mint new token
POST /api/v1/agent-tokens
  {"scopes": [...], "expires_at": "2027-05-23T00:00:00Z", ...}
```

---

## 6. Backup and restore

### What to back up

| Component | Backup method | Recovery importance |
|-----------|--------------|-------------------|
| Postgres (`flyquery_*` tables) | Standard Postgres backup (pg_dump, WAL archiving, managed snapshot) | Critical |
| Object storage (Parquet files, original uploads, query results) | Provider-native versioning or cross-region replication | Critical (Parquet is the query source) |
| EDA outbox (if Postgres adapter) | Covered by Postgres backup | High |
| Redis | Optional snapshot; data is ephemeral (idempotency store + rate limiter) | Low |

### Postgres backup

```bash
# Daily dump
pg_dump flyquery > flyquery_$(date +%Y%m%d).dump

# Restore
createdb flyquery_restored
pg_restore -d flyquery_restored flyquery_20260523.dump
```

Point-in-time recovery (PITR) via WAL archiving is strongly recommended for
production. Consult your managed Postgres provider (RDS, Cloud SQL, Azure
Database) for the specific setup.

### Object storage

Enable versioning on your bucket/container:
- S3: Enable versioning on the bucket.
- GCS: Enable Object Versioning.
- Azure Blob: Enable Blob versioning.

For cross-region disaster recovery, set up replication policies in your
provider console.

### Restore procedure

1. Restore Postgres from backup (pg_dump or PITR).
2. Verify object storage is consistent with Postgres (`flyquery_files.object_store_key`
   should resolve to an existing blob).
3. If blobs are missing, re-ingest from original source or from backup.
4. Restart the service — it reads all state from Postgres and object storage;
   no in-memory state to restore.

---

## 7. Scaling up (more workers)

### Horizontal scaling — more worker pods

Increase `replicas` for the `flyquery-worker` deployment. Each pod runs
`FLYQUERY_INGEST_WORKER_CONCURRENCY` goroutines. The SELECT … FOR UPDATE SKIP
LOCKED pattern ensures no job duplication.

```yaml
# Kubernetes example
spec:
  replicas: 4   # was 2; each pod handles 4 concurrent jobs = 16 total
```

### Vertical scaling — more concurrency per pod

Increase `FLYQUERY_INGEST_WORKER_CONCURRENCY` on existing pods. Limited by
per-connection Postgres overhead and embedding API concurrency.

```bash
FLYQUERY_INGEST_WORKER_CONCURRENCY=8   # default 4
```

### API scaling

The API is stateless; add replicas freely. DuckDB connections are per-request
and in-process — no shared connection pool to manage.

```yaml
spec:
  replicas: 8   # API pods; each handles concurrent HTTP requests
```

### Database scaling

Postgres is the scaling bottleneck for the schema knowledge base. Options:
- Read replicas for `GET /schema-objects:search` and retrieval queries.
- Connection pooling via PgBouncer.
- Partition `flyquery_schema_objects` by `workspace_id` for very large
  multi-tenant deployments.

### Embedding throughput

Embedding calls (stage 9) are the most API-rate-limited step. With
`FLYQUERY_INGEST_WORKER_CONCURRENCY=4` and embedding dimension 1536,
expect ~2-4 seconds per table for the embedding batch. Rate-limit
management via `FLYQUERY_EMBEDDING_RATE_LIMIT_RPM` (default 3000 RPM; not
currently enforced in the embedding stage — rate limit enforcement is v1).

---

## 8. Incident response template

Use this template for any severity-1 incident affecting flyquery availability.

```
INCIDENT: flyquery <COMPONENT> <SEVERITY>
Started: <ISO 8601 timestamp>
Responder: <name>

SYMPTOMS:
  <what is observable — HTTP error codes, latency spikes, job failure rate>

BLAST RADIUS:
  Tenants affected: <all | specific tenant list>
  Data affected: <uploads blocked | queries failing | ingest degraded>

INITIAL HYPOTHESIS:
  <1 sentence>

MITIGATION STEPS TAKEN:
  <timestamped list>
  - HH:MM  <step>
  - HH:MM  <step>

ROOT CAUSE:
  <determined after mitigation>

RESOLUTION:
  <what fixed it>

FOLLOW-UP ACTIONS:
  - <action, owner, due date>
```

### Severity definitions

| Severity | Definition | Response time |
|----------|-----------|--------------|
| SEV-1 | All uploads blocked OR all queries failing | 15 minutes |
| SEV-2 | Degraded ingest (>10% failure rate) or high query latency | 1 hour |
| SEV-3 | Single-tenant issue or non-critical feature broken | Next business day |

### Key runbook pointers

- Stuck worker → [§3 Stuck ingest job](#stuck-ingest-job)
- RLS returning empty → [§3 RLS returning zero rows](#rls-returning-zero-rows)
- GDPR request → [§4 GDPR purge](#4-gdpr-purge-runbook)
- Scaling → [§7 Scaling up](#7-scaling-up-more-workers)
- Detailed troubleshooting → [troubleshooting.md](troubleshooting.md)
