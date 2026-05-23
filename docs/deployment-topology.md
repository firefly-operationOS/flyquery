# flyquery — Deployment Topology

## Table of Contents

1. [Overview](#1-overview)
2. [Single-node (docker-compose)](#2-single-node-docker-compose)
3. [Multi-node (separate services)](#3-multi-node-separate-services)
4. [HA considerations](#4-ha-considerations)
5. [Service port reference](#5-service-port-reference)

---

## 1. Overview

flyquery separates into two runtime processes:

| Process | Role |
|---------|------|
| `flyquery-api` | HTTP server — handles uploads, queries, schema annotation, stats |
| `flyquery-worker` | Ingest worker — consumes `flyquery.ingest` EDA topic, runs 10-stage pipeline |

Both processes connect to the same Postgres and object storage. The API does
not run ingestion stages; it only publishes the EDA event that triggers the
worker.

See [deployment.md](deployment.md) for environment variables and migration
steps. See [async-ingest.md](async-ingest.md) for worker internals.

---

## 2. Single-node (docker-compose)

All components on one host. Appropriate for development, demos, and
small-scale on-prem deployments.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          docker-compose host                        │
│                                                                     │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────────┐  │
│  │  flyquery-api   │   │ flyquery-worker  │   │   postgres       │  │
│  │  :8520          │   │ (no HTTP port)   │   │   :5432          │  │
│  │                 │   │                  │   │   pgvector ext.  │  │
│  │  handles:       │   │  handles:        │   │   flyquery_*     │  │
│  │  - uploads      │   │  - 10-stage      │   │   tables         │  │
│  │  - queries      │   │    ingest        │   └──────────────────┘  │
│  │  - annotation   │   │  - embed/index   │                         │
│  │  - conversations│   │  - LLM calls     │   ┌──────────────────┐  │
│  └────────┬────────┘   └────────┬─────────┘   │  local-fs blobs  │  │
│           │                     │              │  /var/lib/flyquery│  │
│           └──────── EDA ────────┘              │  (dev only)      │  │
│           (Postgres LISTEN/NOTIFY)             └──────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

External:
  Browser / API client → http://host:8520/api/v1/...
  LLM API            → https://api.anthropic.com
  Embedding API      → https://api.openai.com
```

### docker-compose.yml excerpt

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: flyquery
      POSTGRES_USER: flyquery_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  flyquery-api:
    image: ghcr.io/firefly-operationos/flyquery:26.5.3
    command: flyquery serve
    ports:
      - "8520:8520"
    environment:
      FLYQUERY_DATABASE_URL: postgresql+asyncpg://flyquery_app:${APP_PW}@postgres:5432/flyquery
      FLYQUERY_OBJECT_STORE: local
      FLYQUERY_OBJECT_STORE_BASE: /var/lib/flyquery/blobs
      FLYQUERY_EDA_ADAPTER: postgres
    depends_on: [postgres]
    volumes:
      - blobs:/var/lib/flyquery/blobs

  flyquery-worker:
    image: ghcr.io/firefly-operationos/flyquery:26.5.3
    command: flyquery worker
    environment:
      FLYQUERY_DATABASE_URL: postgresql+asyncpg://flyquery_app:${APP_PW}@postgres:5432/flyquery
      FLYQUERY_OBJECT_STORE: local
      FLYQUERY_OBJECT_STORE_BASE: /var/lib/flyquery/blobs
      FLYQUERY_INGEST_WORKER_CONCURRENCY: "4"
    depends_on: [postgres]
    volumes:
      - blobs:/var/lib/flyquery/blobs

volumes:
  pgdata:
  blobs:
```

---

## 3. Multi-node (separate services)

Production topology. Each component runs on its own infrastructure. Suitable
for Kubernetes, ECS, or bare-metal servers.

```
                         ┌──────────────────────────────┐
External clients ──────► │   Load balancer / ingress    │
                         │   (TLS termination)           │
                         └──────────────┬───────────────┘
                                        │ :8520
                         ┌──────────────▼───────────────┐
                         │   flyquery-api  (N replicas)  │
                         │                               │
                         │   stateless; horizontal scale │
                         └─┬────────────────────────┬───┘
                           │                        │
                           │ LISTEN/NOTIFY          │ SQL + pgvector
                           ▼                        ▼
         ┌─────────────────────┐        ┌───────────────────────┐
         │  flyquery-worker    │        │     Postgres          │
         │  (M replicas)       │        │     (managed or self- │
         │                     │        │      hosted)          │
         │  SELECT FOR UPDATE  │        │     pgvector ext.     │
         │  SKIP LOCKED        │◄──────►│                       │
         │  per job claim      │        │  flyquery_* tables    │
         └──────────┬──────────┘        │  pgvector HNSW index  │
                    │                   │  LISTEN/NOTIFY outbox │
                    │ read/write        └───────────────────────┘
                    ▼
         ┌──────────────────────┐
         │   Object Storage     │
         │   S3 / GCS / Azure   │
         │                      │
         │  {tenant}/{ws}/      │
         │    files/            │
         │    tables/           │
         │    derived/          │
         │    results/          │
         └──────────────────────┘

         ┌──────────────────────┐
         │   Redis (optional)   │
         │   rate limiter +     │
         │   idempotency store  │
         └──────────────────────┘
```

### Component sizing (starting point)

| Component | Starting size | Scale trigger |
|-----------|--------------|--------------|
| `flyquery-api` | 2 replicas, 2 vCPU, 4 GB RAM | p95 latency > 2 s |
| `flyquery-worker` | 2 replicas, 2 vCPU, 8 GB RAM | ingest queue depth > 20 |
| Postgres | db.t3.large (AWS) / n1-standard-2 (GCP) | Connection pool saturation |
| Redis | cache.t3.micro | Only needed with redis adapter |
| Object storage | Serverless (S3/GCS/Azure Blob) | N/A |

Workers need more RAM than API nodes because DuckDB runs in-process during
ingestion stages and embedding models may load in RAM (if using local reranker).

---

## 4. HA considerations

### API tier

Stateless; multiple replicas behind a load balancer. No sticky sessions
required. Health check endpoint: `GET /actuator/health`.

### Worker tier

Multiple workers safely process different jobs (SELECT … FOR UPDATE SKIP LOCKED).
No sticky sessions or leader election required. Worker crashes are recovered
by heartbeat-timeout; surviving workers continue processing.

**Graceful shutdown:**

```
SIGTERM → flyquery-worker
  1. Stop accepting new jobs
  2. Complete current stage for in-flight jobs (up to FLYQUERY_INGEST_SHUTDOWN_GRACE_S = 30 s)
  3. Exit cleanly
  Jobs not completed return to PENDING (heartbeat recovery)
```

### Postgres

Use a managed service (RDS Multi-AZ, Cloud SQL HA, Azure Database with
zone-redundant standby) or configure Patroni/Repmgr for self-hosted.

flyquery does NOT use any Postgres-specific features beyond pgvector HNSW
indexes and LISTEN/NOTIFY. A standard HA setup is sufficient.

### Object storage

Use provider-native redundancy (S3 Multi-AZ, GCS multi-region, Azure ZRS).
Enable versioning for point-in-time recovery.

### Redis (if used)

Use Redis Sentinel or Redis Cluster for HA. flyquery's use of Redis (rate
limiter + idempotency) is non-critical: losing Redis state does not cause
data loss, only transient rate-limit state reset.

If Redis becomes unavailable and `FLYQUERY_RATE_LIMIT_BACKEND=redis`, the
service falls back to the in-memory rate limiter automatically (`auto` mode).

### EDA adapter and HA

With `FLYQUERY_EDA_ADAPTER=postgres` (default):
- Outbox events survive Postgres failover (they're in the database).
- LISTEN/NOTIFY connections are re-established on reconnect.
- No messages are lost on Postgres failover.

With `FLYQUERY_EDA_ADAPTER=redis` or `kafka`:
- Messages can be lost on Redis restart (not durable).
- Kafka provides durable, replicated topics; use for strict at-least-once
  delivery across replicas.

---

## 5. Service port reference

| Port | Component | Protocol | Notes |
|------|-----------|----------|-------|
| 8520 | `flyquery-api` | HTTP | REST API + SSE + Swagger UI (`/docs`) |
| 8521 | `flyquery-worker` | HTTP | Actuator only (`/actuator/health`) |
| 5432 | Postgres | TCP | Internal only; not exposed externally |
| 6379 | Redis | TCP | Internal only |

Firefly OperationOS port conventions:
- flycanon: 8500
- flyradar: 8510
- flyquery: 8520

When updating [deployment.md](deployment.md), cross-link to this document for
topology diagrams.
