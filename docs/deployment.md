# flyquery — Deployment

## Table of Contents

1. [Reference topologies](#1-reference-topologies)
2. [Docker image](#2-docker-image)
3. [Service roles](#3-service-roles)
4. [docker-compose (development)](#4-docker-compose-development)
5. [Environment variables](#5-environment-variables)
6. [Postgres role provisioning](#6-postgres-role-provisioning)
7. [Migration ordering (first deploy)](#7-migration-ordering-first-deploy)
8. [Health checks](#8-health-checks)
9. [Observability](#9-observability)
10. [Object storage configuration](#10-object-storage-configuration)
11. [Scaling considerations](#11-scaling-considerations)
12. [Backup and recovery](#12-backup-and-recovery)

---

## 1. Reference topologies

| Topology | Use case | Components |
|----------|----------|------------|
| **Single host (compose)** | Dev, demo, on-prem POC | `docker compose` with `flyquery-api` + `flyquery-worker` + `postgres` + optional `redis` |
| **Container platform** | Production (k8s, ECS, Cloud Run) | Separate deployments for API, worker, and ingest workers; shared Postgres + Redis |
| **Bare-metal** | Air-gapped | `uv run flyquery serve` + `uv run flyquery worker` + external Postgres |

The Docker image, env vars, and migration step are identical across all three.
Differences are only in how dependencies are wired.

For ASCII topology diagrams and HA considerations see
[deployment-topology.md](deployment-topology.md).

---

## 2. Docker image

```bash
docker pull ghcr.io/firefly-operationos/flyquery:latest        # latest main
docker pull ghcr.io/firefly-operationos/flyquery:26.5.2        # specific release
docker pull ghcr.io/firefly-operationos/flyquery:26.5          # latest 26.5.x patch
```

Multi-arch manifest: `linux/amd64` and `linux/arm64`.

---

## 3. Service roles

The same image runs three commands:

| Command | What it does | Scale policy |
|---------|--------------|-------------|
| `serve` | FastAPI ASGI on port `8520`. Stateless. | Horizontally scalable behind a load balancer |
| `worker` | Consumes `flyquery.ingest` EDA jobs + schema events | At least 1; many is fine — work is idempotent |
| `migrate` | Runs `alembic upgrade head` and exits | Single-shot before `serve` / `worker` start |

The default `CMD` is `serve`. Override via `command:` in compose or Kubernetes.

---

## 4. docker-compose (development)

The repo ships `docker-compose.yml`. Bring it up:

```bash
cp env_template .env
# Edit .env with your API keys, etc.

docker compose up -d

# Run migrations
docker compose exec flyquery-api flyquery migrate

# Verify health
curl -fsS http://localhost:8520/actuator/health | jq .
```

### compose service layout

```
flyquery-api      :8520/tcp   CMD serve
flyquery-worker              CMD worker
flyquery-pg       :5432/tcp   pgvector/pgvector:pg16
flyquery-redis    :6379/tcp   (optional; for EDA Redis adapter + idempotency)
```

Postgres uses the `pgvector/pgvector:pg16` image so the `vector` extension is
pre-installed. No separate extension install step needed.

---

## 5. Environment variables

All keys are prefixed `FLYQUERY_*`. The `env_template` file in the repo root
is the canonical reference. Copy to `.env` and edit.

### Required for any deployment

| Variable | Description |
|----------|-------------|
| `FLYQUERY_DATABASE_URL` | Async SQLAlchemy URL for the app role: `postgresql+asyncpg://flyquery_app:<pw>@host:5432/flyquery` |
| `FLYQUERY_DATABASE_URL_ADMIN` | Admin role URL for migrations: `postgresql+asyncpg://flyquery_admin:<pw>@host:5432/flyquery` |
| `FLYQUERY_OBJECT_STORE` | `local` / `s3` / `gcs` / `azure` |
| `FLYQUERY_OBJECT_STORE_BASE` | Base path/URI: `/var/lib/flyquery/blobs` or `s3://bucket` or `gs://bucket` or `azure://container` |

> **Critical**: `FLYQUERY_DATABASE_URL` must use the non-BYPASSRLS
> `flyquery_app` role. Using the admin URL here silently bypasses RLS in
> production.

### LLM models

| Variable | Default | Notes |
|----------|---------|-------|
| `FLYQUERY_GROUNDING_MODEL` | `anthropic:claude-sonnet-4-6` | GroundingAgent |
| `FLYQUERY_GENERATION_MODEL` | `anthropic:claude-sonnet-4-6` | GenerationAgent |
| `FLYQUERY_CRITIC_MODEL` | `anthropic:claude-sonnet-4-6` | CriticAgent |
| `FLYQUERY_EXPLAINER_MODEL` | `anthropic:claude-haiku-4-5` | ExplainerAgent (cheaper model) |
| `FLYQUERY_DESCRIBE_MODEL` | `anthropic:claude-haiku-4-5` | DescribeAgent |
| `FLYQUERY_RELATION_PROPOSER_MODEL` | `anthropic:claude-sonnet-4-6` | RelationProposerAgent |
| `FLYQUERY_EMBEDDING_MODEL` | `openai:text-embedding-3-small` | Schema embeddings |
| `FLYQUERY_RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder reranker |

### DuckDB execution

| Variable | Default | Notes |
|----------|---------|-------|
| `FLYQUERY_DUCKDB_MEMORY_LIMIT` | `4GB` | Per-connection memory cap |
| `FLYQUERY_DEFAULT_ROW_CAP` | `1000` | Default result row limit |
| `FLYQUERY_DEFAULT_STATEMENT_TIMEOUT_MS` | `30000` | Default query timeout (30 s) |
| `FLYQUERY_RESULT_TTL_HOURS` | `24` | Presigned URL and result object TTL |
| `FLYQUERY_RESULT_PREVIEW_MAX_BYTES` | `131072` | Preview JSON size cap (128 KiB) |
| `FLYQUERY_DUCKDB_HTTPFS` | `true` | Enable httpfs for cloud object storage |

### Ingestion

| Variable | Default | Notes |
|----------|---------|-------|
| `FLYQUERY_MAX_FILE_MB` | `2048` | Upload size cap |
| `FLYQUERY_MAX_WORKSPACE_GB` | `200` | Total storage cap per workspace |
| `FLYQUERY_INGEST_WORKER_CONCURRENCY` | `4` | Parallel ingest workers |
| `FLYQUERY_INGEST_HANDLER_TIMEOUT_S` | `600` | Per-job wall-clock timeout |

### Auth and backends

| Variable | Default | Notes |
|----------|---------|-------|
| `FLYQUERY_REDIS_URL` | *(empty)* | Required if `FLYQUERY_RATE_LIMIT_BACKEND=redis` |
| `FLYQUERY_RATE_LIMIT_BACKEND` | `auto` | `auto` chooses redis if URL set, else memory |
| `FLYQUERY_IDEMPOTENCY_BACKEND` | `auto` | Same selection logic |
| `FLYQUERY_EDA_ADAPTER` | `postgres` | `postgres \| redis \| kafka \| memory` |

---

## 6. Postgres role provisioning

Before the first migration, provision the two Postgres roles:

```sql
-- Run as a superuser (e.g., postgres):

-- Admin role: BYPASSRLS for migrations
CREATE ROLE flyquery_admin WITH LOGIN PASSWORD '<strong_password>'
    BYPASSRLS NOINHERIT;

-- App role: no bypass for runtime queries
CREATE ROLE flyquery_app WITH LOGIN PASSWORD '<strong_password>'
    NOINHERIT;

-- Create the database
CREATE DATABASE flyquery OWNER flyquery_admin;

-- Grant connection + schema usage to app role
GRANT CONNECT ON DATABASE flyquery TO flyquery_app;

\c flyquery

CREATE EXTENSION IF NOT EXISTS vector;

GRANT USAGE ON SCHEMA public TO flyquery_app;
-- Additional table-level grants are handled by the Alembic migration
-- (migration 0007_rls.py includes explicit GRANT statements)
```

After migration, verify with:

```sql
\c flyquery flyquery_app
SET LOCAL app.tenant_id = 'test';
SET LOCAL app.workspace_id = 'test';
SELECT COUNT(*) FROM flyquery_workspaces;  -- should return 0, not error
```

---

## 7. Migration ordering (first deploy)

```bash
# 1. Provision Postgres roles (see §6)
# 2. Run migrations with the admin URL
FLYQUERY_DATABASE_URL_ADMIN=postgresql+asyncpg://flyquery_admin:<pw>@host:5432/flyquery \
    docker run --rm ghcr.io/firefly-operationos/flyquery:26.5.2 flyquery migrate

# 3. Start the API
docker run -d --env-file .env -p 8520:8520 \
    ghcr.io/firefly-operationos/flyquery:26.5.2 flyquery serve

# 4. Start the worker
docker run -d --env-file .env \
    ghcr.io/firefly-operationos/flyquery:26.5.2 flyquery worker

# 5. Verify
curl -fsS http://localhost:8520/actuator/health | jq .
```

### Migration list (v0 baseline)

| Migration | What it creates |
|-----------|----------------|
| `0001_workspaces` | `flyquery_workspaces` + workspace-level RLS |
| `0002_datasets` | `flyquery_datasets` |
| `0003_files_tables` | `flyquery_files`, `flyquery_tables` |
| `0004_snapshots_changes` | `flyquery_schema_snapshots`, `flyquery_schema_changes` |
| `0005_schema_objects` | `flyquery_schema_objects` + pgvector column + BM25 tsvector |
| `0006_relations` | `flyquery_relations` |
| `0007_rls` | RLS policies on all tables; role GRANTs |
| `0008_semantic` | `flyquery_semantic_metrics`, `flyquery_semantic_dimensions`, `flyquery_semantic_versions`, `flyquery_glossary_terms` |
| `0009_examples` | `flyquery_examples` + pgvector column |
| `0010_queries` | `flyquery_queries`, `flyquery_query_results`, `flyquery_conversations`, `flyquery_conversation_turns` |
| `0011_ingest_jobs` | `flyquery_ingest_jobs`, `flyquery_ingest_events` |
| `0012_audit` | `flyquery_audit_events`, `flyquery_cost_events`, `flyquery_agent_tokens` |
| `0013_indexes` | Composite indexes on `(tenant_id, workspace_id)` + HNSW on embeddings |

---

## 8. Health checks

flyquery exposes `/actuator/health` (pyfly standard):

```bash
curl http://localhost:8520/actuator/health
# {"status": "UP", "components": {"db": "UP", "redis": "UP", "object_store": "UP"}}
```

### Component checks

| Component | Check | Healthy condition |
|-----------|-------|------------------|
| `db` | `SELECT 1` via `flyquery_app` role | No error |
| `redis` | `PING` | `PONG` (only if Redis is configured) |
| `object_store` | `head` on a canary key | Object exists or 404 (not auth error) |

Liveness: `/actuator/health/liveness` — returns `UP` if the process is alive.
Readiness: `/actuator/health/readiness` — returns `UP` only when all components
are healthy and migrations are current.

Use the readiness probe for Kubernetes `readinessProbe` and the liveness probe
for `livenessProbe`.

---

## 9. Observability

flyquery inherits pyfly's observability stack:

### Metrics

Prometheus metrics exposed at `/actuator/metrics`. Key gauges and counters:

| Metric | Description |
|--------|-------------|
| `flyquery_ingest_jobs_total{status}` | Ingest jobs by status |
| `flyquery_ingest_job_duration_seconds` | Histogram of job duration |
| `flyquery_queries_total{status,path}` | Queries by execution status and semantic path |
| `flyquery_query_duration_seconds` | Query end-to-end latency |
| `flyquery_agent_calls_total{agent}` | Agent invocations per agent type |
| `flyquery_cost_cents_total{kind}` | Cumulative LLM cost |
| `flyquery_storage_used_bytes{workspace_id}` | Storage by workspace |

### Tracing

OpenTelemetry traces are emitted if `FLYQUERY_OTEL_ENDPOINT` is set. Each
request gets a root span; agent invocations, DuckDB execution, and object
store calls are child spans.

### Logging

Structured JSON logs to stdout. Log level: `FLYQUERY_LOG_LEVEL` (default
`INFO`). Sensitive fields (`X-Agent-Token`, credentials) are redacted by the
logging middleware.

### Pyfly admin endpoint

`/actuator/info` returns `{version, git_sha, pyfly_version, uptime_s}`.
`/actuator/metrics` returns the Prometheus text format.

---

## 10. Object storage configuration

### Local filesystem (dev)

```
FLYQUERY_OBJECT_STORE=local
FLYQUERY_OBJECT_STORE_BASE=/var/lib/flyquery/blobs
```

Ensure the path is on a volume mount in Docker. The `local` adapter uses
`aiofiles` for async I/O.

### S3

```
FLYQUERY_OBJECT_STORE=s3
FLYQUERY_OBJECT_STORE_BASE=s3://my-bucket/flyquery
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

Requires the `[s3]` extra: `pip install flyquery[s3]` or in compose `ghcr.io/firefly-operationos/flyquery:26.5.2-s3`.

For presigned URLs, the IAM role needs `s3:GetObject` + `s3:PutObject` +
`s3:DeleteObject` + `s3:ListBucket` on the target bucket prefix.

### GCS

```
FLYQUERY_OBJECT_STORE=gcs
FLYQUERY_OBJECT_STORE_BASE=gs://my-bucket/flyquery
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gsa.json
```

Requires the `[gcs]` extra.

### Azure Blob

```
FLYQUERY_OBJECT_STORE=azure
FLYQUERY_OBJECT_STORE_BASE=azure://my-container/flyquery
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
```

Requires the `[azure]` extra.

---

## 11. Scaling considerations

### API (`serve`)

Stateless. Scale horizontally behind a load balancer. All request state is
in Postgres and object storage.

Memory per pod: ~256 MiB base + DuckDB per-connection limit
(`FLYQUERY_DUCKDB_MEMORY_LIMIT`). The DuckDB in-process executor means a
concurrent query uses memory proportional to the result set. Size pods
accordingly (e.g., 2 GB pods support ~4 concurrent 4 GB queries with
multiplexing overhead).

### Worker

Each worker process consumes `FLYQUERY_INGEST_WORKER_CONCURRENCY` parallel
ingest jobs. Scale worker replicas with the expected ingest queue depth.
Jobs are claimed atomically via the EDA topic; duplicate processing is safe
because reconcile is idempotent.

### Postgres

Single Postgres instance is sufficient for moderate workloads. For high
throughput:
- Use a connection pool (PgBouncer) between flyquery and Postgres.
- The `pgvector` HNSW index on `flyquery_schema_objects.embedding` is the
  hottest index during query grounding; size Postgres shared_buffers to fit it.

### Redis

Required for rate limiting with `FLYQUERY_RATE_LIMIT_BACKEND=redis` and for
the Redis EDA adapter. A single Redis instance is sufficient for most workloads.
Use Redis Sentinel or cluster mode for HA.

---

## 12. Backup and recovery

### Postgres

Use standard `pg_dump` or continuous WAL archiving (Barman, pgBackRest,
cloud-managed Postgres). The dump captures all schema knowledge, relations,
queries, audit events, and agent tokens. No special flyquery-specific backup
step is needed.

Recovery: restore the dump, then verify with `alembic current` that migrations
are at head.

### Object storage

- **S3 / GCS / Azure**: enable versioning and lifecycle rules on the bucket.
  Cross-region replication is recommended for production.
- **Local filesystem**: standard volume snapshot or rsync backup of
  `FLYQUERY_OBJECT_STORE_BASE`.

### Consistency notes

Postgres and object storage are **not transactionally consistent** with each
other. The recommended backup sequence:

1. Quiesce ingest workers (scale to 0 or drain the job queue).
2. Take a Postgres snapshot.
3. Take an object-storage snapshot.
4. Resume workers.

If a Postgres snapshot is restored without the corresponding object-storage
snapshot, `flyquery_schema_snapshots` rows may reference Parquet keys that no
longer exist. These appear as `status=READY` snapshots with missing blobs;
the service will return `500` on queries that try to ATTACH them. Resolution:
run `REPARSE` jobs to re-materialise from the original upload blobs.

### GDPR purge recovery

The 30-day tombstone window on workspace purge allows accidental purge
recovery. During the tombstone window, the workspace is soft-deleted (not
queryable) but bytes are intact. Contact support to reverse a tombstone before
the 30-day window expires.
