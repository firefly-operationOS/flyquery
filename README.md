<div align="center">

<img src="docs/assets/logo.png" alt="flyquery — tabular intelligence" width="520" />

### **Tabular Intelligence**

The Text-to-SQL service for user-uploaded structured files.
Multi-tenant ingestion of CSV/TSV/XLSX/XLS/ODS/JSON/JSONL/Parquet/Avro/ORC/Arrow/Feather
+ compressed variants, materialised as Parquet on object storage and
queried by DuckDB through a multi-agent pipeline (Grounding → Generation
→ Critic → Explainer) with hybrid retrieval over a long-lived schema
knowledge base — all behind a single HTTP service.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org)
[![Java 25](https://img.shields.io/badge/java%20sdk-25-orange)](sdks/java/README.md)
[![pyfly](https://img.shields.io/badge/runtime-fireflyframework--pyfly-orange)](https://github.com/fireflyframework/fireflyframework-pyfly)
[![agentic](https://img.shields.io/badge/genai-fireflyframework--agentic-purple)](https://github.com/fireflyframework/fireflyframework-agentic)
[![OpenAPI](https://img.shields.io/badge/api-openapi%203.1-green)](docs/api-reference.md)
[![DuckDB](https://img.shields.io/badge/query%20engine-duckdb-yellow)](docs/architecture.md)
[![pgvector](https://img.shields.io/badge/vector--store-pgvector-336791)](docs/architecture.md)
[![Version](https://img.shields.io/badge/version-26.5.3-green.svg)](#)
[![License](https://img.shields.io/badge/license-Proprietary-lightgrey.svg)](LICENSE)

</div>

---

> **In a hurry?** &nbsp;Jump to the [**Quickstart →**](QUICKSTART.md) &nbsp;·&nbsp; SDK paths: [Python](sdks/python/README.md) · [Java](sdks/java/README.md) &nbsp;·&nbsp; Wire payloads: [**Payload reference →**](docs/payload-reference.md)

---

## Why this service exists

flyquery is the third pillar of **Firefly OperationOS**, alongside
[flycanon](../flycanon) (operational knowledge repository for unstructured
content) and [flyradar](../flyradar) (operations-discovery and diagnostic
intelligence).

When customers bring operational data as structured files — quarterly sales
exports, CRM extracts, inventory snapshots, financial ledger CSVs — they
need natural-language access without writing SQL, maintaining database
connections, or mastering schema details. flyquery handles that boundary:
upload a file, ask a question in plain English, get a cited, auditable answer.

What makes this non-trivial:

- **Structured data is messy.** Real-world files have inconsistent headers,
  mixed date formats, merged cells, compressed archives, and multi-sheet XLSX
  with completely different schemas per sheet.
- **Re-uploads break queries.** Column renames across versions silently break
  historical analytics. flyquery detects drifts, preserves annotations, and
  pins historical queries to specific Parquet snapshots.
- **SQL generation is unreliable.** A single-pass LLM call mis-identifies
  tables, invents columns, and silently drops GROUP BY. flyquery uses a
  four-agent pipeline with an AST firewall and self-correcting Critic to ensure
  only valid, scoped SQL executes.

---

## The shape of the system

```
                        User / Agent caller
                               │
                  REST API  /api/v1/*
                               │
         ┌─────────────────────┼──────────────────────┐
         │                     │                      │
   Upload surface         Query surface         Schema annotation
  POST /datasets/{id}/files  POST /query         PUT /schema-objects/{id}
  PUT  /tables/{id}:upload   POST /conversations  POST /examples/{id}:approve
         │                     │
         ▼                     ▼
  [IngestWorker]       [QueryService]
  10-stage async         Hybrid Retrieval
  pipeline               GroundingAgent
  (EDA topic)            GenerationAgent
         │               DuckDB Executor
         ▼               CriticAgent
  Parquet on             ExplainerAgent
  ObjectStore                  │
  (LocalFs/S3/GCS/Azure)       ▼
         │               AnswerResponse + SSE
         ▼               + presigned Parquet URL
  Postgres + pgvector
  (schema KB, relations,
   examples, audit)
```

Three tiers: **upload surface** (async ingest into object storage + schema KB),
**query surface** (multi-agent NL→SQL over Parquet), **annotation surface**
(human governance of descriptions, PII tags, relations, examples).

---

## 10-second example

```bash
# Upload a CSV
curl -X POST http://localhost:8520/api/v1/datasets/ds_01/files \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" \
  -F "file=@sales_q1.csv"
# → {"file_id": "f_01", "tables": [{"table_id": "t_01", "name": "sales_q1", ...}]}

# Wait for ingest (or stream progress)
curl http://localhost:8520/api/v1/ingest-jobs/job_01/stream  # SSE

# Ask a question
curl -X POST http://localhost:8520/api/v1/query \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: acme" -H "X-Workspace-Id: analytics" \
  -d '{"question": "Total revenue by region for Q1", "dataset_id": "ds_01"}'
# → {"answer": "Total Q1 revenue is $4.2M. Northeast led at $1.8M (43%).",
#    "executed_sql": "SELECT region, SUM(revenue) ...",
#    "chart_hint": "bar", "result_url": "https://...presigned..."}
```

---

## What ships in v0

| Capability | Detail |
|------------|--------|
| **12 file formats** | CSV, TSV, XLSX, XLS, ODS, JSON, JSONL, Parquet, Avro, ORC, Arrow, Feather |
| **Compression** | .gz, .zip, .bz2 transparently unwrapped |
| **10-stage pipeline** | Receive → Parse → Reconcile → Sample → Profile → Relations → Describe → PII → Embed → Publish |
| **4-agent query pipeline** | GroundingAgent → GenerationAgent → CriticAgent → ExplainerAgent |
| **AST firewall** | sqlglot + DuckDB double-check; single-statement SELECT only on uploaded tables |
| **Schema knowledge base** | pgvector HNSW + BM25 + cross-encoder reranker |
| **Semantic layer** | OSI/MetricFlow YAML metrics, deterministic SQL compilation |
| **Conversation memory** | Multi-turn drill-down with snapshot pinning |
| **Multi-tenancy** | Postgres RLS on all tables; two-role split (admin/app) |
| **Auto-learning** | First-shot OK queries auto-propose `(question, SQL)` examples |
| **PII scanning** | regex/Presidio; warn/redact/reject policy |
| **Agent surface** | Full `/api/v1/agent/*` mirror with `X-Agent-Token` + `Idempotency-Key` |
| **SDKs** | Python (`flyquery-sdk`) and Java (`io.firefly:flyquery-sdk`) auto-generated from OpenAPI |

---

## Documentation

All docs live in [`docs/`](docs/). Start with:

| Document | Purpose |
|----------|---------|
| [**docs/README.md**](docs/README.md) | Navigation hub — reading paths by intent |
| [docs/architecture.md](docs/architecture.md) | System design, pipelines, hexagonal ports |
| [docs/api-reference.md](docs/api-reference.md) | REST surface — every endpoint, header, scope |
| [docs/pipeline.md](docs/pipeline.md) | Upload + query pipelines end-to-end with diagrams |
| [docs/ingestion.md](docs/ingestion.md) | 10-stage ingestion detail |
| [docs/file-formats.md](docs/file-formats.md) | Per-format reader matrix |
| [docs/semantic-layer.md](docs/semantic-layer.md) | MetricFlow YAML + compilation |
| [docs/payload-reference.md](docs/payload-reference.md) | DTO catalog |
| [docs/security-model.md](docs/security-model.md) | RLS, tokens, AST firewall, PII policy |
| [docs/deployment.md](docs/deployment.md) | Ops reference |
| [docs/conversations.md](docs/conversations.md) | Multi-turn query memory + drill-down |
| [docs/eda-events.md](docs/eda-events.md) | Events published: flyquery.ingest + flyquery.schema |
| [docs/glossary.md](docs/glossary.md) | Term definitions |
| [docs/firefly-intelligence-system.md](docs/firefly-intelligence-system.md) | flycanon + flyradar + flyquery cross-narrative |

Full index with reading paths: [**docs/README.md →**](docs/README.md)

---

## Status

**v0 complete.** Plans 1–4 shipped:

| Plan | Scope | Status |
|------|-------|--------|
| 1 — Foundation | Scaffold, lock-step modules, RLS schema, workspace/dataset CRUD, agent tokens, ObjectStore | Done |
| 2 — File ingestion | FileReader port (12 formats), 10-stage async pipeline, IngestWorker, EDA, PII, embeddings | Done |
| 3 — Query pipeline | 4-agent pipeline, AST firewall, DuckDB executor, conversations, auto-learn | Done |
| 4 — Packaging | OpenAPI drift gate, Python + Java SDKs, full docs | Done |

v1+ roadmap: frontend `/flyquery` route, MCP server, cost enforcement,
per-workspace KMS/CMEK, drift watchdog, `GovernanceClassifierAgent`.

---

## Local dev

```bash
task dev          # docker compose up postgres + redis
task migrate      # alembic upgrade head
task serve        # uvicorn flyquery.main:app --reload
```

### Running tests

```bash
task lint
task test:unit
task test:integration
```

Integration tests require Docker (testcontainers spins up `pgvector/pgvector:pg16`).
Tests marked `@pytest.mark.s3` / `@pytest.mark.gcs` / `@pytest.mark.azure_blob`
need local credentials or MinIO/fake-gcs/Azurite — see [`QUICKSTART.md`](QUICKSTART.md).

Tests marked `@pytest.mark.llm` require `ANTHROPIC_API_KEY`. Exclude them in CI
with `-m 'not llm'`.

---

## Architecture quick-take

flyquery uses a **two-tier storage design**: Parquet on object storage (LocalFs in
dev; S3/GCS/Azure Blob in production) queried by DuckDB in-process per request.
Postgres stores all metadata, embeddings, relations, audit, and agent tokens.
There is no persistent DuckDB database — every query ATTACHes Parquet snapshots
fresh, eliminating shared mutable state between requests.

The **hexagonal adapter ring** means every external boundary (object store, file
reader, vector store, PII scanner, semantic compiler, rate limiter) is a Python
`Protocol`; the domain core never depends on a concrete implementation.

Lock-step modules (`web/conventions/*`, `agent_deps.py`, `agent_token_service.py`,
`builder.py`) are byte-equivalent with flycanon and flyradar. A CI gate
(`scripts/check_lockstep.py`) blocks PRs that drift.

See [docs/architecture.md](docs/architecture.md) for the full picture.

---

## License

The flyquery service is **Proprietary**. See [`LICENSE`](LICENSE).

The Python SDK (`sdks/python/`) and Java SDK (`sdks/java/`) are licensed under
[Apache 2.0](sdks/python/LICENSE) and intended for public consumption by
service integrators.
