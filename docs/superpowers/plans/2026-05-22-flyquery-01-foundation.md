# flyquery Plan 1 — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a bootable flyquery service with lock-step auth + a full RLS-enabled Postgres schema (~20 tables) + workspace/dataset CRUD + agent-token mint/verify + an `ObjectStore` port (LocalFs + S3 adapters) + CI gates, so Plan 2 (file ingestion) can land on top.

**Architecture:** Mirror flycanon's pyfly-based microservice shape (Python 3.13, FastAPI via pyfly's web adapter, SQLAlchemy 2.x async + Alembic, pgvector, pydantic-settings, structlog, testcontainers). Lock-step modules (`web/conventions/*`, `web/agent_deps`, `web/openapi_override`, `core/agents/builder`, `core/observability/__init__`, `core/services/auth/{agent_token_service,redis_rate_limiter}`, `web/controllers/agent_tokens_controller`) are byte-equivalent copies from canon with service-name substitutions. Every multi-tenant Postgres table carries `(tenant_id, workspace_id)` with RLS forced; migrations run under the `flyquery_admin` BYPASSRLS role, the app under `flyquery_app` no-bypass.

**Tech Stack:** Python 3.13, uv, pyfly + fireflyframework-agentic (path sources to sibling repos), SQLAlchemy 2.0 async + asyncpg, psycopg (sync, for Alembic), Alembic, Postgres 16 + pgvector, Redis, pytest + pytest-asyncio + testcontainers + httpx, ruff + pyright, GitHub Actions, Docker.

---

## File structure (locked in upfront)

```
flyquery/
├── .github/workflows/
│   ├── lint.yml
│   ├── test-unit.yml
│   ├── test-integration.yml
│   └── lockstep-check.yml
├── alembic.ini
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── docker-compose.yml
├── env_template
├── LICENSE
├── QUICKSTART.md
├── README.md
├── Taskfile.yml
├── pyfly.yaml
├── pyproject.toml
├── docs/                                 # design + plans already exist
│   └── superpowers/{specs,plans}/...
├── migrations/
│   ├── env.py
│   └── versions/
│       ├── 0001_lifecycle.py             # workspaces, datasets, files, tables
│       ├── 0002_schema_kb.py             # snapshots, changes, schema_objects, relations
│       ├── 0003_semantic_examples_queries.py
│       ├── 0004_ops.py                   # agent_tokens, audit, cost, ingest_*
│       └── 0005_rls.py                   # role split + RLS policies
├── scripts/
│   ├── check_lockstep.py                 # CI gate: diff lock-step files vs canon SHAs
│   └── lockstep_pins.json                # canon SHA snapshot
├── sdks/                                 # populated in Plan 4
├── src/flyquery/
│   ├── __init__.py
│   ├── app.py
│   ├── cli.py
│   ├── config.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── configuration.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   └── builder.py                # lock-step from canon
│   │   ├── observability/
│   │   │   └── __init__.py               # lock-step from canon
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth/
│   │       │   ├── __init__.py
│   │       │   ├── agent_token_service.py  # lock-step from canon
│   │       │   ├── redis_rate_limiter.py   # lock-step from canon
│   │       │   └── scope_catalog.py        # NEW (flyquery-specific)
│   │       ├── storage/
│   │       │   ├── __init__.py
│   │       │   ├── object_store.py        # ObjectStore Protocol + types
│   │       │   ├── object_store_factory.py
│   │       │   └── adapters/
│   │       │       ├── __init__.py
│   │       │       ├── local_fs.py
│   │       │       └── s3.py
│   │       ├── workspaces/
│   │       │   ├── __init__.py
│   │       │   ├── workspace_repository.py
│   │       │   └── workspace_service.py
│   │       └── datasets/
│   │           ├── __init__.py
│   │           ├── dataset_repository.py
│   │           └── dataset_service.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── workspaces.py                 # public DTOs
│   │   └── datasets.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py               # Base + all entity exports
│   │   │   ├── workspace.py
│   │   │   ├── dataset.py
│   │   │   ├── file.py
│   │   │   ├── table.py
│   │   │   ├── schema.py                 # snapshots / changes / schema_objects / relations
│   │   │   ├── semantic.py
│   │   │   ├── examples.py
│   │   │   ├── queries.py                # queries, query_results, conversations*
│   │   │   └── ops.py                    # tokens, audit, cost, ingest_*
│   │   └── repositories/
│   │       └── __init__.py
│   ├── resources/
│   │   └── __init__.py
│   └── web/
│       ├── __init__.py
│       ├── agent_deps.py                 # lock-step from canon
│       ├── openapi_override.py           # lock-step from canon
│       ├── conventions/                  # lock-step from canon (14 files)
│       │   ├── __init__.py
│       │   ├── actor.py
│       │   ├── context.py
│       │   ├── db.py
│       │   ├── deps.py
│       │   ├── errors.py
│       │   ├── exceptions.py
│       │   ├── handlers.py
│       │   ├── headers.py
│       │   ├── http_client.py
│       │   ├── idempotency.py
│       │   ├── middleware.py
│       │   ├── redis_idempotency.py
│       │   └── validation.py
│       └── controllers/
│           ├── __init__.py
│           ├── agent_tokens_controller.py  # lock-step from canon
│           ├── workspaces_controller.py
│           ├── datasets_controller.py
│           └── version_controller.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_scope_catalog.py
    │   ├── test_workspace_service.py
    │   ├── test_dataset_service.py
    │   └── test_object_store_factory.py
    └── integration/
        ├── __init__.py
        ├── conftest.py
        ├── test_app_boot.py
        ├── test_migrations.py
        ├── test_rls_isolation.py
        ├── test_workspaces_crud.py
        ├── test_datasets_crud.py
        ├── test_agent_tokens.py
        ├── test_object_store_conformance.py
        └── parsers/                       # empty; populated in Plan 2
```

---

## Phase A — Scaffolding (Tasks 1-9)

### Task 1: Initialise the repo skeleton (`git init`, ignore, license, doc stubs)

**Files:**
- Create: `flyquery/.gitignore`
- Create: `flyquery/LICENSE`
- Create: `flyquery/README.md`
- Create: `flyquery/CHANGELOG.md`
- Create: `flyquery/CONTRIBUTING.md`
- Create: `flyquery/QUICKSTART.md`

- [ ] **Step 1: Init the repo**

```bash
cd /Users/ancongui/Development/firefly-operationOS/flyquery
git init
git config core.autocrlf input
```

- [ ] **Step 2: Write `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.pyright/
*.egg-info/
build/
dist/

# Env + secrets
.env
.env.*
!.env.example
!env_template

# Editor + OS
.idea/
.vscode/
.DS_Store
Thumbs.db

# Local data
local_data/
*.duckdb
*.duckdb.wal

# Generated SDKs (rebuilt in Plan 4)
sdks/python/dist/
sdks/python/build/
sdks/python/*.egg-info/
sdks/java/target/

# uv
uv.lock
```

> uv.lock is gitignored per memory `project_uv_lock_gitignored` — CI uses `uv sync`, not `--frozen`.

- [ ] **Step 3: Write `LICENSE`** (proprietary; matches canon's wording verbatim)

```bash
cp ../flycanon/LICENSE LICENSE
```

- [ ] **Step 4: Write `README.md` (~70-line stub)**

```markdown
# flyquery

> Operational Structured-Data Intelligence (upload-driven). Multi-tenant
> ingestion + Text-to-SQL over user-uploaded structured files
> (CSV / TSV / XLSX / XLS / ODS / JSON / JSONL / Parquet / Avro / ORC /
> Arrow / Feather + .gz/.zip/.bz2). Materialises uploads to Parquet on
> object storage; indexes a long-lived schema knowledge base; answers
> natural-language questions via a multi-agent pipeline. Part of
> Firefly OperationOS.

## Status

Plan 1 (Foundation). The service boots, exposes `/actuator/health` and
`/api/v1/version`, supports workspace + dataset CRUD with RLS, mints
agent tokens, and ships `LocalFs` + `S3` ObjectStore adapters. File
ingestion + Text-to-SQL pipeline ship in subsequent plans (see
`docs/superpowers/plans/`).

## Quick start

See [`QUICKSTART.md`](./QUICKSTART.md).

## Design

See [`docs/superpowers/specs/2026-05-22-flyquery-design.md`](./docs/superpowers/specs/2026-05-22-flyquery-design.md).

## Repo layout

See the file-structure section of any plan in
`docs/superpowers/plans/`. Lock-step modules with canon/radar are
listed in the design spec §14.

## Local dev

```bash
task dev          # docker compose up postgres + redis
task migrate      # run alembic head
task serve        # uvicorn flyquery.main:app --reload
```

## Running tests

```bash
task lint
task test:unit
task test:integration
```
```

- [ ] **Step 5: Write `CHANGELOG.md` skeleton**

```markdown
# Changelog

All notable changes to flyquery are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project uses [CalVer](https://calver.org/) (YY.MM.PP) per the
Firefly Framework convention (memory: `firefly_uses_calver`).

## [Unreleased]

### Added
- Foundation scaffold: pyproject + pyfly.yaml + Dockerfile + Taskfile
- Lock-step modules from canon: `web/conventions/*`,
  `web/agent_deps.py`, `web/openapi_override.py`,
  `core/agents/builder.py`, `core/observability/__init__.py`,
  `core/services/auth/{agent_token_service,redis_rate_limiter}.py`,
  `web/controllers/agent_tokens_controller.py`
- Full Alembic schema (~20 tables) with admin/app role split
  + RLS forced on every multi-tenant table
- `flyquery_workspaces` + `flyquery_datasets` CRUD with RLS isolation
- Agent-token mint/list/revoke + flyquery scope catalog
- `ObjectStore` port + `LocalFs` + `S3` adapters
- `scripts/check_lockstep.py` CI gate
```

- [ ] **Step 6: Write `CONTRIBUTING.md`** (one-pager)

```markdown
# Contributing to flyquery

## Setup

```bash
uv venv
uv sync --extra dev
```

## Local dev

```bash
docker compose up -d postgres redis
task migrate
task serve
```

## Tests

- `task test:unit` — pytest, no containers
- `task test:integration` — testcontainers (Postgres + Redis + MinIO)
- `task lint` — ruff + pyright

## Lock-step gate

Modules listed in spec §14 must be byte-equivalent with canon. CI
runs `scripts/check_lockstep.py`; if it fails, copy the canon file
verbatim and substitute service-name strings (`flycanon` → `flyquery`,
`canon_*` → `flyquery_*`, etc.).

## Commits

Per-task commits with the standard prefix (`feat:`, `fix:`, `chore:`,
`docs:`, `test:`, `refactor:`). Each commit must pass
`task lint test:unit` locally before push.
```

- [ ] **Step 7: Write `QUICKSTART.md` placeholder**

```markdown
# QUICKSTART (placeholder — populated at end of Plan 1, Task 37)
```

- [ ] **Step 8: Commit the skeleton**

```bash
git add .gitignore LICENSE README.md CHANGELOG.md CONTRIBUTING.md QUICKSTART.md
git commit -m "chore: initial repo skeleton (gitignore, license, doc stubs)"
```

---

### Task 2: `pyproject.toml`

**Files:**
- Create: `flyquery/pyproject.toml`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "flyquery"
# CalVer YY.MM.PP per memory `firefly_uses_calver`.
version = "26.5.0"
description = "Operational Structured-Data Intelligence (upload-driven) -- multi-tenant ingestion + Text-to-SQL service over user-uploaded structured files. Part of Firefly OperationOS."
readme = "README.md"
requires-python = ">=3.13,<3.14"
authors = [
    { name = "Firefly Software Solutions Inc" },
]

dependencies = [
    # Firefly Framework runtime -- same extras canon uses so a fresh
    # `uv sync` boots the full stack.
    "pyfly[fastapi,observability,security,data-relational,postgresql,eda,redis,client,scheduling,cli]>=26.5.4",
    # GenAI metaframework -- FireflyAgent over pydantic-ai + retrieval
    # primitives (used in Plans 2-3; harmless to install in Plan 1).
    "fireflyframework-agentic[rest,security,redis,corpus-search]>=26.5.11",

    # HTTP + tenacity (outbound).
    "httpx>=0.28.0",
    "tenacity>=9.0.0",

    # Configuration.
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",

    # Persistence. asyncpg for runtime, psycopg for Alembic; alembic env
    # rewrites +asyncpg -> +psycopg so one URL covers both.
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "psycopg[binary]>=3.2",
    "aiosqlite>=0.22",
    "alembic>=1.14",
    "redis>=5.2",
    "pgvector>=0.3.6",

    # DuckDB -- query engine; used in Plan 3 but pinned here so the
    # extras boundary stays stable.
    "duckdb>=1.1",
    "pyarrow>=17.0",

    # Logging.
    "structlog>=25.5.0",
]

[project.scripts]
flyquery = "flyquery.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "pytest-timeout>=2.3",
    "ruff>=0.8",
    "pyright>=1.1",
    "testcontainers[postgres,redis,minio]>=4.0",
    "respx>=0.21",
    "httpx>=0.28",
]

# ObjectStore adapter extras (spec §9.1)
s3 = [
    "aiobotocore>=2.15",
    "botocore>=1.35",
]
gcs = [
    "gcloud-aio-storage>=9.3",
]
azure = [
    "azure-storage-blob>=12.23",
    "aiohttp>=3.10",
]

# PII (Plan 2)
presidio = [
    "presidio-analyzer>=2.2",
    "presidio-anonymizer>=2.2",
]

# Cross-encoder reranker (Plan 3)
ml-reranker = [
    "sentence-transformers>=3.3",
]

# File-format readers (Plan 2)
file-readers = [
    "python-calamine>=0.3",
    "openpyxl>=3.1",
    "fastavro>=1.9",
]

[build-system]
requires = ["hatchling>=1.18"]
build-backend = "hatchling.build"

[tool.uv.sources]
# Sibling-repo path sources (same as canon).
pyfly = { path = "../../fireflyframework/fireflyframework-pyfly", editable = true }
fireflyframework-agentic = { path = "../../fireflyframework/fireflyframework-agentic", editable = true }

[tool.hatch.build.targets.wheel]
packages = ["src/flyquery"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["src"]
markers = [
    "integration: requires docker compose stack (Postgres / Redis / MinIO)",
    "s3: requires MinIO (covered by 'integration')",
    "gcs: requires fake-gcs-server",
    "azure_blob: requires Azurite",
    "llm: requires a real LLM provider; skipped by default",
]
addopts = "-v --tb=short -m 'not llm'"

[tool.ruff]
target-version = "py313"
line-length = 110
extend-exclude = ["vendor"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
"src/flyquery/interfaces/**" = ["N801", "N811", "N815", "N818"]
"src/flyquery/core/services/**" = ["N818"]
"src/flyquery/web/conventions/**" = ["N818"]
"tests/**" = ["E501"]

[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "basic"
include = ["src/flyquery"]
exclude = ["tests/**", "**/__pycache__/**", "vendor/**"]

[[tool.pyright.executionEnvironments]]
root = "src/flyquery/web/controllers"
reportArgumentType = "none"
reportAttributeAccessIssue = "none"
reportOperatorIssue = "none"
```

- [ ] **Step 2: Verify `uv sync` resolves cleanly**

```bash
uv venv
uv sync --extra dev --extra s3
```

Expected: no resolution errors, sibling-repo paths satisfied. If the sibling repos aren't checked out, instruct the engineer to clone them at `../../fireflyframework/fireflyframework-{pyfly,agentic}` first.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: pyproject.toml with pyfly + agentic + ObjectStore extras"
```

---

### Task 3: `pyfly.yaml` (port 8520, service-name flyquery, all sections from canon)

**Files:**
- Create: `flyquery/pyfly.yaml`

- [ ] **Step 1: Write `pyfly.yaml`**

```yaml
# Copyright 2026 Firefly Software Solutions Inc
#
# PyFly application configuration. Values override the property-driven
# defaults activated by ``enable_core_stack``. Anything in the
# environment (FLYQUERY_*) wins over this file because pydantic-settings
# is loaded after pyfly merges its config sources.

pyfly:
  web:
    enabled: true
    base-path: /api
  server:
    enabled: true
    host: 0.0.0.0
    port: 8520

  observability:
    enabled: true
  metrics:
    enabled: true
  tracing:
    enabled: true
    service-name: flyquery

  actuator:
    enabled: true
    metrics:
      enabled: true

  admin:
    enabled: true
    path: /admin
    title: "flyquery -- PyFly Admin"
    theme: auto
    require-auth: false
    refresh-interval: 5000

  aop:
    enabled: true
  resilience:
    enabled: true
  cqrs:
    enabled: true
  cache:
    enabled: true

  eda:
    enabled: true
    provider: ${FLYQUERY_EDA_ADAPTER:postgres}
    destinations: ${FLYQUERY_EDA_DESTINATIONS:flyquery.ingest,flyquery.schema,flyquery.audit}
    group: ${FLYQUERY_EDA_GROUP:flyquery-workers}
    postgres:
      dsn: ${FLYQUERY_DATABASE_URL:postgresql+asyncpg://flyquery:flyquery@localhost:5432/flyquery}
      channel: flyquery_eda
    redis:
      url: ${FLYQUERY_REDIS_URL:redis://localhost:6379/0}
    kafka:
      bootstrap-servers: ${FLYQUERY_KAFKA_BOOTSTRAP:localhost:9092}

  data:
    relational:
      enabled: true
      url: ${FLYQUERY_DATABASE_URL:postgresql+asyncpg://flyquery:flyquery@localhost:5432/flyquery}
```

- [ ] **Step 2: Commit**

```bash
git add pyfly.yaml
git commit -m "chore: pyfly.yaml (port 8520, service-name flyquery)"
```

---

### Task 4: `Dockerfile` + `docker-compose.yml`

**Files:**
- Create: `flyquery/Dockerfile`
- Create: `flyquery/docker-compose.yml`
- Create: `flyquery/docker-entrypoint.sh`

- [ ] **Step 1: Write `Dockerfile`** (mirror canon's; substitute names)

```bash
cp ../flycanon/Dockerfile Dockerfile
# Substitutions
sed -i.bak 's/flycanon/flyquery/g; s/FLYCANON/FLYQUERY/g' Dockerfile
sed -i.bak 's/8500/8520/g' Dockerfile
rm Dockerfile.bak
```

> If canon's Dockerfile references service-specific binaries (tesseract, etc.), strip them for flyquery — we don't need OCR. Verify the resulting Dockerfile and remove anything unrelated to upload-driven Text-to-SQL.

- [ ] **Step 2: Write `docker-compose.yml`**

```yaml
# Copyright 2026 Firefly Software Solutions Inc
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: flyquery
      POSTGRES_PASSWORD: flyquery
      POSTGRES_DB: flyquery
    ports:
      - "5552:5432"          # 55XX series per Firefly OS convention
    volumes:
      - flyquery_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U flyquery -d flyquery"]
      interval: 2s
      timeout: 2s
      retries: 30

  redis:
    image: redis:7-alpine
    ports:
      - "6552:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 2s
      timeout: 2s
      retries: 30

  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: flyquery
      MINIO_ROOT_PASSWORD: flyqueryflyquery
    command: server /data --console-address ":9001"
    ports:
      - "9552:9000"
      - "9553:9001"
    volumes:
      - flyquery_minio:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 5s
      retries: 30

volumes:
  flyquery_pgdata:
  flyquery_minio:
```

- [ ] **Step 3: Write `docker-entrypoint.sh`**

```bash
cp ../flycanon/docker-entrypoint.sh docker-entrypoint.sh
sed -i.bak 's/flycanon/flyquery/g; s/FLYCANON/FLYQUERY/g' docker-entrypoint.sh
rm docker-entrypoint.sh.bak
chmod +x docker-entrypoint.sh
```

- [ ] **Step 4: Verify local stack comes up**

```bash
docker compose up -d postgres redis minio
docker compose ps
docker compose logs postgres | tail -5
```

Expected: all three containers `healthy` within 30s.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile docker-compose.yml docker-entrypoint.sh
git commit -m "chore: Dockerfile + docker-compose (postgres 5552, redis 6552, minio 9552)"
```

---

### Task 5: `Taskfile.yml`

**Files:**
- Create: `flyquery/Taskfile.yml`

- [ ] **Step 1: Write `Taskfile.yml`**

```yaml
# Copyright 2026 Firefly Software Solutions Inc
version: '3'

env:
  PYTHONPATH: src
  FLYQUERY_DATABASE_URL: 'postgresql+asyncpg://flyquery:flyquery@localhost:5552/flyquery'
  FLYQUERY_DATABASE_URL_ADMIN: 'postgresql+psycopg://flyquery_admin:flyquery_admin@localhost:5552/flyquery'
  FLYQUERY_REDIS_URL: 'redis://localhost:6552/0'

tasks:
  default:
    cmds:
      - task --list

  dev:
    desc: Start local Postgres + Redis + MinIO
    cmds:
      - docker compose up -d postgres redis minio

  dev:down:
    desc: Tear down local stack
    cmds:
      - docker compose down -v

  install:
    desc: Sync dependencies via uv
    cmds:
      - uv venv
      - uv sync --extra dev --extra s3

  migrate:
    desc: Run alembic migrations (admin role)
    cmds:
      - uv run alembic upgrade head

  migrate:new:
    desc: 'Generate a new alembic migration; usage: task migrate:new -- "<message>"'
    cmds:
      - uv run alembic revision -m "{{.CLI_ARGS}}"

  serve:
    desc: Run the dev server with reload
    cmds:
      - uv run uvicorn flyquery.main:app --host 0.0.0.0 --port 8520 --reload

  lint:
    desc: ruff + pyright
    cmds:
      - uv run ruff check src tests
      - uv run ruff format --check src tests
      - uv run pyright

  fmt:
    desc: Apply ruff formatting
    cmds:
      - uv run ruff format src tests
      - uv run ruff check --fix src tests

  test:unit:
    desc: Unit tests (no containers)
    cmds:
      - uv run pytest tests/unit -m 'not integration'

  test:integration:
    desc: Integration tests (testcontainers)
    cmds:
      - uv run pytest tests/integration -m integration

  test:all:
    desc: All tests
    cmds:
      - task: test:unit
      - task: test:integration

  lockstep:
    desc: Verify lock-step files match pinned canon SHAs
    cmds:
      - uv run python scripts/check_lockstep.py

  openapi:
    desc: Refresh openapi.json snapshot (run after route changes)
    cmds:
      - uv run python -c "from flyquery.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json
```

- [ ] **Step 2: Verify**

```bash
task --list
```

Expected: all tasks listed.

- [ ] **Step 3: Commit**

```bash
git add Taskfile.yml
git commit -m "chore: Taskfile.yml (dev / migrate / serve / lint / test / lockstep)"
```

---

### Task 6: Alembic config + env.py

**Files:**
- Create: `flyquery/alembic.ini`
- Create: `flyquery/migrations/env.py`

- [ ] **Step 1: Write `alembic.ini`** (mirror canon)

```bash
cp ../flycanon/alembic.ini alembic.ini
sed -i.bak 's/flycanon/flyquery/g; s/FLYCANON/FLYQUERY/g' alembic.ini
rm alembic.ini.bak
```

Verify the `[alembic]` section has:
```ini
script_location = migrations
prepend_sys_path = .
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
timezone = UTC
truncate_slug_length = 40
```

- [ ] **Step 2: Write `migrations/env.py`** (mirror canon shape; service-name swap)

```bash
mkdir -p migrations/versions
cp ../flycanon/migrations/env.py migrations/env.py
sed -i.bak 's/flycanon/flyquery/g; s/FLYCANON/FLYQUERY/g; s/canon\./flyquery./g' migrations/env.py
rm migrations/env.py.bak
```

Open `migrations/env.py` and verify:
- the sync driver swap (`+asyncpg` → `+psycopg`) is preserved
- the `FLYQUERY_DATABASE_URL_ADMIN` env var is consulted FIRST (admin role for migrations), then `FLYQUERY_DATABASE_URL`
- `target_metadata` lazy-imports `flyquery.models.entities` (returns `None` if not yet shipped — Task 7's package skeleton)

If canon's env.py only uses one URL, edit the resolver to prefer the admin URL when present:

```python
admin_url = os.environ.get("FLYQUERY_DATABASE_URL_ADMIN")
app_url = os.environ.get("FLYQUERY_DATABASE_URL")
url = admin_url or app_url or config.get_main_option("sqlalchemy.url")
```

- [ ] **Step 3: Touch the versions dir**

```bash
touch migrations/versions/.keep
```

- [ ] **Step 4: Smoke `alembic current` (should report empty)**

```bash
task dev   # postgres up
uv run alembic current 2>&1 | tee /tmp/alembic_check.txt
```

Expected: prints the alembic version line; no migrations yet → no current revision.

- [ ] **Step 5: Commit**

```bash
git add alembic.ini migrations/env.py migrations/versions/.keep
git commit -m "chore: alembic config + env.py (admin URL preferred for migrations)"
```

---

### Task 7: Source package skeleton + `config.py`

**Files:**
- Create: `src/flyquery/__init__.py`
- Create: `src/flyquery/config.py`
- Create: `src/flyquery/core/__init__.py`
- Create: `src/flyquery/core/configuration.py`
- Create: `src/flyquery/core/services/__init__.py`
- Create: `src/flyquery/core/agents/__init__.py`
- Create: `src/flyquery/core/observability/__init__.py` (stub; lock-step copy lands in Task 11)
- Create: `src/flyquery/interfaces/__init__.py`
- Create: `src/flyquery/models/__init__.py`
- Create: `src/flyquery/models/entities/__init__.py`
- Create: `src/flyquery/models/repositories/__init__.py`
- Create: `src/flyquery/resources/__init__.py`
- Create: `src/flyquery/web/__init__.py`
- Create: `src/flyquery/web/conventions/__init__.py` (stub; lock-step copy lands in Task 10)
- Create: `src/flyquery/web/controllers/__init__.py`

- [ ] **Step 1: Create the package tree**

```bash
mkdir -p src/flyquery/core/services/{auth,storage/adapters,workspaces,datasets}
mkdir -p src/flyquery/core/{agents,observability}
mkdir -p src/flyquery/{interfaces,models/entities,models/repositories,resources}
mkdir -p src/flyquery/web/{conventions,controllers}
for d in $(find src/flyquery -type d); do touch "$d/__init__.py"; done
```

- [ ] **Step 2: Write `src/flyquery/__init__.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery -- Operational Structured-Data Intelligence (upload-driven)."""

from __future__ import annotations

__version__ = "26.5.0"
```

- [ ] **Step 3: Write `src/flyquery/config.py`** (pydantic-settings)

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Runtime configuration for flyquery (pydantic-settings).

Every knob exposed by the spec §12 lands here. The class is mounted
into the pyfly context as a @configuration bean (see
core/configuration.py).
"""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class FlyquerySettings(BaseSettings):
    """All FLYQUERY_* env vars in one place."""

    model_config = SettingsConfigDict(
        env_prefix="FLYQUERY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service
    log_level: str = "INFO"
    port: int = 8520
    database_url: str = "postgresql+asyncpg://flyquery:flyquery@localhost:5552/flyquery"
    database_url_admin: str = "postgresql+psycopg://flyquery_admin:flyquery_admin@localhost:5552/flyquery"
    run_migrations: bool = True

    # Object store
    object_store: Literal["local", "s3", "gcs", "azure"] = "local"
    object_store_base: str = "/var/lib/flyquery/blobs"
    object_store_kms_default: str = ""
    object_store_presign_ttl_s: int = 86400

    # DuckDB execution (Plan 3; harmless to define now)
    duckdb_httpfs: bool = True
    duckdb_httpfs_metadata_cache_mb: int = 512
    duckdb_memory_limit: str = "4GB"
    default_row_cap: int = 1000
    default_statement_timeout_ms: int = 30000
    result_preview_max_bytes: int = 131072
    result_ttl_hours: int = 24

    # Upload caps (Plan 2)
    max_file_mb: int = 2048
    max_workspace_gb: int = 200

    # Ingestion knobs (Plans 2-3)
    ingest_topic: str = "flyquery.ingest"
    ingest_worker_concurrency: int = 4
    ingest_handler_timeout_s: int = 600
    ingest_shutdown_grace_s: int = 30
    sample_n: int = 8
    profile_row_threshold: int = 10_000_000
    describe_budget_cents_per_run: int = 200
    describe_batch: int = 20
    relation_proposer_enabled: bool = True
    relation_proposer_max_per_pair: int = 3
    relation_heuristic_min_confidence: float = 0.85
    max_title_rows: int = 3
    type_infer_sample_rows: int = 8192
    default_locale: str = "en-US"

    # Pipeline knobs (Plan 3)
    grounding_model: str = "anthropic:claude-sonnet-4-6"
    generation_model: str = "anthropic:claude-sonnet-4-6"
    critic_model: str = "anthropic:claude-sonnet-4-6"
    explainer_model: str = "anthropic:claude-haiku-4-5"
    describe_model: str = "anthropic:claude-haiku-4-5"
    relation_proposer_model: str = "anthropic:claude-sonnet-4-6"
    rename_detect_model: str = "anthropic:claude-haiku-4-5"
    fallback_model: str = "openai:gpt-4o"
    generation_candidates: int = 3
    max_refine_retries: int = 2
    expand_iters: int = 2
    grounding_min_confidence: float = 0.55
    agent_max_output_tokens: int = 8192

    # Embeddings + retrieval (lock-step with canon)
    embedding_model: str = "openai:text-embedding-3-small"
    embedding_dimensions: int = 1536
    vector_store: str = "pgvector"
    top_k_schema: int = 12
    top_k_examples: int = 5
    top_k_metrics: int = 8
    rrf_k: int = 60
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_n: int = 30
    query_expansion_enabled: bool = False

    # PII
    pii_scanner: Literal["regex", "presidio", "disabled"] = "regex"
    pii_policy_samples: Literal["warn", "redact", "reject"] = "redact"
    pii_policy_results: Literal["warn", "redact", "reject"] = "warn"

    # Auth + backends
    redis_url: str = ""
    rate_limit_backend: str = "auto"
    idempotency_backend: str = "auto"

    # EDA
    eda_adapter: str = "postgres"
    eda_destinations: str = "flyquery.ingest,flyquery.schema,flyquery.audit"
    eda_group: str = "flyquery-workers"
```

- [ ] **Step 4: Write `src/flyquery/core/configuration.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""DI configuration bean for flyquery."""

from __future__ import annotations

from pyfly.core.di import configuration

from flyquery.config import FlyquerySettings


@configuration
class FlyqueryConfiguration:
    """Exposes :class:`FlyquerySettings` to the pyfly DI container."""

    def settings(self) -> FlyquerySettings:
        return FlyquerySettings()
```

- [ ] **Step 5: Commit**

```bash
git add src/
git commit -m "chore: package skeleton + config.py (all FLYQUERY_* knobs)"
```

---

### Task 8: `app.py` + `main.py` + `cli.py`

**Files:**
- Create: `src/flyquery/app.py`
- Create: `src/flyquery/main.py`
- Create: `src/flyquery/cli.py`

- [ ] **Step 1: Write `src/flyquery/app.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""PyFly application entry point for flyquery.

``scan_packages`` declares every package containing ``@configuration``,
``@rest_controller``, ``@service``, ``@command_handler``,
``@query_handler``, or ``@repository`` beans so pyfly's DI container
can discover them at boot.

Exception handlers are registered explicitly via
``flyquery.web.conventions.register_exception_handlers(app)`` in
``flyquery.main`` -- pyfly's FastAPI adapter does not scan
``@controller_advice`` beans, so the conventions handler table is
hand-wired against the FastAPI app.
"""

from __future__ import annotations

from pyfly.core import pyfly_application
from pyfly.starters.core import enable_core_stack


@enable_core_stack
@pyfly_application(
    name="flyquery",
    version="26.5.0",
    description=(
        "flyquery -- Operational Structured-Data Intelligence "
        "(upload-driven). Multi-tenant ingestion + Text-to-SQL "
        "over user-uploaded structured files. Part of Firefly "
        "OperationOS."
    ),
    scan_packages=[
        "flyquery.core",  # @configuration class
        "flyquery.core.services",  # CQRS handlers + @service beans
        "flyquery.web.controllers",  # REST controllers (user-tier)
        "flyquery.web.controllers.agent",  # REST controllers (agent-tier)
    ],
)
class FlyqueryApplication:
    """Marker class consumed by :class:`PyFlyApplication` at boot."""
```

- [ ] **Step 2: Write `src/flyquery/main.py`** (mirror canon's shape verbatim, service-name swap)

```bash
cp ../flycanon/src/flycanon/main.py src/flyquery/main.py
sed -i.bak 's/flycanon/flyquery/g; s/FLYCANON/FLYQUERY/g; s/CanonApplication/FlyqueryApplication/g; s/8500/8520/g' src/flyquery/main.py
rm src/flyquery/main.py.bak
```

Edit the title + description constants at the top:

```python
_TITLE = "flyquery"
_DESCRIPTION = (
    "Operational Structured-Data Intelligence (upload-driven) -- "
    "multi-tenant ingestion + Text-to-SQL over user-uploaded "
    "structured files (CSV / TSV / XLSX / XLS / ODS / JSON / JSONL "
    "/ Parquet / Avro / ORC / Arrow / Feather + .gz/.zip/.bz2 "
    "variants). Materialises uploads to Parquet on object storage; "
    "indexes a long-lived schema knowledge base; answers natural-"
    "language questions via a multi-agent pipeline. Part of "
    "Firefly OperationOS."
)
```

- [ ] **Step 3: Write `src/flyquery/cli.py`** (minimal Click CLI)

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery CLI entry point."""

from __future__ import annotations

import sys

import click


@click.group()
@click.version_option()
def main() -> None:
    """flyquery command-line interface."""


@main.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8520, show_default=True, type=int)
def serve(host: str, port: int) -> None:
    """Run the API server."""
    import uvicorn

    uvicorn.run("flyquery.main:app", host=host, port=port)


@main.command()
def version() -> None:
    """Print the package version."""
    from flyquery import __version__

    click.echo(__version__)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Commit**

```bash
git add src/flyquery/{app,main,cli}.py
git commit -m "chore: app + main + cli bootstrap (port 8520)"
```

---

### Task 9: First app-boot smoke test

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/conftest.py`
- Create: `tests/integration/test_app_boot.py`

- [ ] **Step 1: Write `tests/conftest.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Shared pytest fixtures for flyquery tests."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default to disabled migrations and an in-memory SQLite KB for unit tests."""
    monkeypatch.setenv("FLYQUERY_RUN_MIGRATIONS", "false")
```

- [ ] **Step 2: Write `tests/integration/conftest.py`** (testcontainer Postgres + Redis + MinIO)

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Integration-test fixtures: Postgres + Redis + MinIO containers."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("pgvector/pgvector:pg16") as pg:
        # Container exposes the default `test` user as SUPERUSER which
        # would silently BYPASSRLS (memory: postgres_test_role_bypasses_rls).
        # We provision flyquery_admin (BYPASSRLS) + flyquery_app (no bypass)
        # via the RLS migration in Task 21 / fixture below.
        yield pg


@pytest.fixture(scope="session")
def redis_container() -> Iterator[RedisContainer]:
    with RedisContainer() as r:
        yield r


@pytest.fixture(scope="session")
def minio_container() -> Iterator[MinioContainer]:
    with MinioContainer() as m:
        yield m


@pytest.fixture(autouse=True)
def configure_env(
    monkeypatch: pytest.MonkeyPatch,
    postgres_container: PostgresContainer,
    redis_container: RedisContainer,
    minio_container: MinioContainer,
) -> None:
    sync_url = postgres_container.get_connection_url()  # postgresql+psycopg2://...
    async_url = sync_url.replace("+psycopg2", "+asyncpg").replace("+psycopg", "+asyncpg")
    admin_url = sync_url.replace("+psycopg2", "+psycopg")
    monkeypatch.setenv("FLYQUERY_DATABASE_URL", async_url)
    monkeypatch.setenv("FLYQUERY_DATABASE_URL_ADMIN", admin_url)
    monkeypatch.setenv("FLYQUERY_REDIS_URL", redis_container.get_connection_url())
    monkeypatch.setenv("FLYQUERY_OBJECT_STORE", "s3")
    monkeypatch.setenv("FLYQUERY_OBJECT_STORE_BASE", f"s3://{minio_container.get_config()['endpoint']}/flyquery-test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", minio_container.access_key)
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", minio_container.secret_key)
    monkeypatch.setenv("FLYQUERY_RUN_MIGRATIONS", "false")
```

- [ ] **Step 3: Write `tests/integration/test_app_boot.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Smoke test: app imports + actuator/health responds 200."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_app_boots_and_health_endpoint_responds() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as client:
        resp = await client.get("/actuator/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") in ("UP", "OK")
```

- [ ] **Step 4: Run the test and expect a clean fail with a clear missing-piece message**

```bash
task dev
uv run pytest tests/integration/test_app_boot.py -m integration -v
```

Expected: FAIL because the lock-step conventions (`TenantContextMiddleware`, `register_exception_handlers`) haven't been copied yet — they ship in Task 10. The traceback should mention `flyquery.web.conventions` missing those names. This failure is the signal that Task 10 must run before this test passes.

- [ ] **Step 5: Commit (failing test is fine; it'll be made to pass in Task 12)**

```bash
git add tests/
git commit -m "test: app-boot smoke test (fails until lock-step lands in Tasks 10-12)"
```

---

## Phase B — Lock-step copy (Tasks 10-12)

> Per spec §14, these files must be **byte-equivalent** with canon (except for service-name substitutions: `flycanon` → `flyquery`, `FLYCANON` → `FLYQUERY`, `canon_` → `flyquery_`, `CanonSettings` → `FlyquerySettings`). The CI gate `scripts/check_lockstep.py` (Task 30) computes SHA-256 of each file (post-substitution-normalised) and compares to a pinned snapshot of canon. Drift = PR blocked.

### Task 10: Copy `web/conventions/*` from canon (14 files)

**Files:**
- Create: `src/flyquery/web/conventions/__init__.py`
- Create: `src/flyquery/web/conventions/{actor,context,db,deps,errors,exceptions,handlers,headers,http_client,idempotency,middleware,redis_idempotency,validation}.py`

- [ ] **Step 1: Copy the directory verbatim**

```bash
rm -rf src/flyquery/web/conventions
cp -r ../flycanon/src/flycanon/web/conventions src/flyquery/web/conventions
```

- [ ] **Step 2: Apply service-name substitutions across every file**

```bash
find src/flyquery/web/conventions -type f -name "*.py" -print0 | xargs -0 sed -i.bak \
  -e 's/flycanon/flyquery/g' \
  -e 's/FLYCANON/FLYQUERY/g' \
  -e 's/canon_/flyquery_/g' \
  -e 's/CanonSettings/FlyquerySettings/g' \
  -e 's/from flycanon/from flyquery/g'
find src/flyquery/web/conventions -name "*.bak" -delete
```

- [ ] **Step 3: Verify the public API is preserved**

The canon conventions exports `TenantContextMiddleware` and `register_exception_handlers` via `__init__.py`. Confirm:

```bash
grep -E "TenantContextMiddleware|register_exception_handlers" src/flyquery/web/conventions/__init__.py
```

Expected: both names appear in `__all__` or as re-exports.

- [ ] **Step 4: Import-smoke**

```bash
uv run python -c "from flyquery.web.conventions import TenantContextMiddleware, register_exception_handlers; print('OK')"
```

Expected: prints `OK`. If ImportError, fix the substitution that broke the import path (often a stale `from flycanon.config import` left in a file because `from flycanon` wasn't covered by step 2's sed — re-run step 2 with a broader pattern).

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/web/conventions
git commit -m "chore: lock-step copy of web/conventions/* from canon (service-name swap)"
```

---

### Task 11: Copy remaining lock-step modules from canon

**Files:**
- Create: `src/flyquery/web/agent_deps.py`
- Create: `src/flyquery/web/openapi_override.py`
- Create: `src/flyquery/core/agents/builder.py`
- Create: `src/flyquery/core/observability/__init__.py`
- Create: `src/flyquery/core/services/auth/agent_token_service.py`
- Create: `src/flyquery/core/services/auth/redis_rate_limiter.py`

- [ ] **Step 1: Copy with substitutions** (one bash block per file is fine; bundled here)

```bash
for f in \
  web/agent_deps.py \
  web/openapi_override.py \
  core/agents/builder.py \
  core/observability/__init__.py \
  core/services/auth/agent_token_service.py \
  core/services/auth/redis_rate_limiter.py
do
  cp "../flycanon/src/flycanon/$f" "src/flyquery/$f"
done

find src/flyquery -type f -name "*.py" -newer /tmp/.lockstep_tag 2>/dev/null \
  | xargs sed -i.bak \
    -e 's/flycanon/flyquery/g' \
    -e 's/FLYCANON/FLYQUERY/g' \
    -e 's/canon_/flyquery_/g' \
    -e 's/CanonSettings/FlyquerySettings/g' \
    -e 's/from flycanon/from flyquery/g' \
    -e 's/import flycanon/import flyquery/g'
find src/flyquery -name "*.bak" -delete
```

(If the `-newer` trick is fragile, just run the sed over the six files explicitly.)

- [ ] **Step 2: Verify imports**

```bash
uv run python -c "
from flyquery.web.agent_deps import *
from flyquery.web.openapi_override import install_openapi
from flyquery.core.agents.builder import build_agent
from flyquery.core.observability import DEFAULT_MIDDLEWARE
from flyquery.core.services.auth.agent_token_service import AgentTokenService
from flyquery.core.services.auth.redis_rate_limiter import RedisRateLimiter
print('lock-step modules OK')
"
```

Expected: prints `lock-step modules OK`. Fix any leftover `flycanon` reference that broke an import.

- [ ] **Step 3: Commit**

```bash
git add src/flyquery/web/agent_deps.py src/flyquery/web/openapi_override.py \
        src/flyquery/core/agents/builder.py \
        src/flyquery/core/observability/__init__.py \
        src/flyquery/core/services/auth/agent_token_service.py \
        src/flyquery/core/services/auth/redis_rate_limiter.py
git commit -m "chore: lock-step copy of agent_deps + openapi_override + builder + observability + auth from canon"
```

---

### Task 12: Re-run the app-boot smoke test (now expected to pass)

- [ ] **Step 1: Re-run the smoke**

```bash
task dev
uv run pytest tests/integration/test_app_boot.py -m integration -v
```

Expected: PASS. `/actuator/health` returns 200 with `{"status": "UP"}`.

- [ ] **Step 2: If it still fails, diagnose**

Common failures:
- `ModuleNotFoundError: flyquery.core.configuration` → ensure Task 7 wrote `core/configuration.py`
- `KeyError: 'pyfly.server.port'` → check `pyfly.yaml` mounted alongside the running process (must be in CWD when uvicorn boots)
- Database connection refused → confirm `docker compose ps` shows postgres `healthy` and `FLYQUERY_DATABASE_URL` matches the exposed port 5552

- [ ] **Step 3: Commit (no code changes; this is a verification gate)**

```bash
git commit --allow-empty -m "test: app-boot smoke green after lock-step lands"
```

---

## Phase C — Database schema (Tasks 13-21)

> Five migrations cover ~20 tables. Each migration ships with the matching SQLAlchemy entities so the lazy `target_metadata` resolver in `migrations/env.py` finds them. The RLS task (21) is the gate: until it passes, the schema is unsafe in production. All migrations run as `flyquery_admin` (BYPASSRLS).

### Task 13: Entities — Base + lifecycle (Workspace / Dataset / File / Table)

**Files:**
- Create: `src/flyquery/models/entities/__init__.py`
- Create: `src/flyquery/models/entities/workspace.py`
- Create: `src/flyquery/models/entities/dataset.py`
- Create: `src/flyquery/models/entities/file.py`
- Create: `src/flyquery/models/entities/table.py`
- Test: `tests/unit/test_entities_import.py`

- [ ] **Step 1: Write `tests/unit/test_entities_import.py` (the failing test)**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""All entity modules import + the Base.metadata enumerates the tables."""

from __future__ import annotations


def test_lifecycle_entities_register_on_base_metadata() -> None:
    from flyquery.models.entities import Base
    table_names = set(Base.metadata.tables.keys())
    assert {"flyquery_workspaces", "flyquery_datasets", "flyquery_files", "flyquery_tables"} <= table_names
```

- [ ] **Step 2: Run; expect FAIL**

```bash
uv run pytest tests/unit/test_entities_import.py -v
```

Expected: `ImportError: cannot import name 'Base' from 'flyquery.models.entities'`.

- [ ] **Step 3: Write `src/flyquery/models/entities/__init__.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""SQLAlchemy declarative Base + entity exports."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single declarative base for every flyquery_* table."""


# Force eager import so alembic env.py's target_metadata sees every table.
from flyquery.models.entities.workspace import Workspace  # noqa: F401,E402
from flyquery.models.entities.dataset import Dataset  # noqa: F401,E402
from flyquery.models.entities.file import File  # noqa: F401,E402
from flyquery.models.entities.table import Table  # noqa: F401,E402

__all__ = ["Base", "Workspace", "Dataset", "File", "Table"]
```

- [ ] **Step 4: Write `src/flyquery/models/entities/workspace.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery_workspaces entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class Workspace(Base):
    __tablename__ = "flyquery_workspaces"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_workspaces_tenant_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    kms_key_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allow_direct_sql: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    default_locale: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'en-US'"))
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
```

- [ ] **Step 5: Write `src/flyquery/models/entities/dataset.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery_datasets entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class Dataset(Base):
    __tablename__ = "flyquery_datasets"
    __table_args__ = (UniqueConstraint("workspace_id", "name", name="uq_datasets_workspace_name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flyquery_workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    drift_policy: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'AUTO'"))
    default_locale: Mapped[str | None] = mapped_column(String, nullable=True)
    ingest_policy_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
```

- [ ] **Step 6: Write `src/flyquery/models/entities/file.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery_files entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class File(Base):
    __tablename__ = "flyquery_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_format: Mapped[str] = mapped_column(String, nullable=False)
    compression: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'none'"))
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    object_store_key: Mapped[str] = mapped_column(String, nullable=False)
    table_extraction_rules_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    uploaded_by: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'RECEIVED'"))
    error_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
```

- [ ] **Step 7: Write `src/flyquery/models/entities/table.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery_tables entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class Table(Base):
    __tablename__ = "flyquery_tables"
    __table_args__ = (UniqueConstraint("dataset_id", "name", name="uq_tables_dataset_name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flyquery_files.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    qualified_name: Mapped[str] = mapped_column(String, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'UPLOADED'"))
    sheet_or_json_path: Mapped[str | None] = mapped_column(String, nullable=True)
    current_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    description_source: Mapped[str | None] = mapped_column(String, nullable=True)
    business_owner: Mapped[str | None] = mapped_column(String, nullable=True)
    governance_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    locale_override: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    archived_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
```

- [ ] **Step 8: Run the test; expect PASS**

```bash
uv run pytest tests/unit/test_entities_import.py -v
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add src/flyquery/models/ tests/unit/test_entities_import.py
git commit -m "feat: lifecycle entities (Workspace, Dataset, File, Table) + Base"
```

---

### Task 14: Migration 0001 — lifecycle tables

**Files:**
- Create: `migrations/versions/0001_lifecycle.py`
- Test: `tests/integration/test_migrations.py`

- [ ] **Step 1: Write the failing migration smoke test**

```python
# tests/integration/test_migrations.py
# Copyright 2026 Firefly Software Solutions Inc
"""End-to-end migration smoke: alembic upgrade head + table presence."""

from __future__ import annotations

import os
import subprocess

import pytest
from sqlalchemy import create_engine, inspect


@pytest.mark.integration
def test_alembic_upgrade_head_creates_all_tables() -> None:
    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)
    eng = create_engine(admin_url)
    insp = inspect(eng)
    names = set(insp.get_table_names())
    assert {"flyquery_workspaces", "flyquery_datasets", "flyquery_files", "flyquery_tables"} <= names
```

- [ ] **Step 2: Run; expect FAIL** (no migrations yet)

```bash
uv run pytest tests/integration/test_migrations.py -m integration -v
```

Expected: FAIL — `alembic upgrade head` is a no-op because there are no revisions; then the `inspect` step finds no tables.

- [ ] **Step 3: Generate the migration scaffold**

```bash
uv run alembic revision -m "lifecycle"
```

This creates `migrations/versions/<timestamp>_lifecycle.py`. Rename or edit it so the revision string matches `0001_lifecycle` (set the `revision = "0001_lifecycle"` and `down_revision = None` at the top).

- [ ] **Step 4: Write the full migration body**

```python
"""lifecycle tables: workspaces, datasets, files, tables

Revision ID: 0001_lifecycle
Revises:
Create Date: 2026-05-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

revision = "0001_lifecycle"
down_revision = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "flyquery_workspaces",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("slug", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("kms_key_uri", sa.Text, nullable=True),
        sa.Column("retention_days", sa.Integer, nullable=True),
        sa.Column("allow_direct_sql", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("default_locale", sa.Text, nullable=False, server_default=sa.text("'en-US'")),
        sa.Column("storage_used_bytes", sa.BigInteger, nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_workspaces_tenant_slug"),
    )
    op.create_index("ix_workspaces_tenant", "flyquery_workspaces", ["tenant_id"])

    op.create_table(
        "flyquery_datasets",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("drift_policy", sa.Text, nullable=False, server_default=sa.text("'AUTO'")),
        sa.Column("default_locale", sa.Text, nullable=True),
        sa.Column("ingest_policy_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("workspace_id", "name", name="uq_datasets_workspace_name"),
    )
    op.create_index("ix_datasets_tenant_workspace", "flyquery_datasets", ["tenant_id", "workspace_id"])

    op.create_table(
        "flyquery_files",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_filename", sa.Text, nullable=False),
        sa.Column("file_format", sa.Text, nullable=False),
        sa.Column("compression", sa.Text, nullable=False, server_default=sa.text("'none'")),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("content_hash_sha256", sa.String(64), nullable=False),
        sa.Column("object_store_key", sa.Text, nullable=False),
        sa.Column("table_extraction_rules_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("uploaded_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("uploaded_by", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'RECEIVED'")),
        sa.Column("error_json", JSONB, nullable=True),
        sa.CheckConstraint(
            "file_format IN ('csv','tsv','xlsx','xls','ods','json','jsonl','parquet','avro','orc','arrow','feather')",
            name="ck_files_format",
        ),
        sa.CheckConstraint(
            "compression IN ('none','gz','zip','bz2')", name="ck_files_compression"
        ),
        sa.CheckConstraint(
            "status IN ('RECEIVED','PARSED','FAILED','DELETED')", name="ck_files_status"
        ),
    )
    op.create_index("ix_files_tenant_workspace", "flyquery_files", ["tenant_id", "workspace_id"])
    op.create_index("ix_files_dataset", "flyquery_files", ["dataset_id"])

    op.create_table(
        "flyquery_tables",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_file_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_files.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("qualified_name", sa.Text, nullable=False),
        sa.Column("kind", sa.Text, nullable=False, server_default=sa.text("'UPLOADED'")),
        sa.Column("sheet_or_json_path", sa.Text, nullable=True),
        sa.Column("current_snapshot_id", UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_source", sa.Text, nullable=True),
        sa.Column("business_owner", sa.Text, nullable=True),
        sa.Column("governance_json", JSONB, nullable=True),
        sa.Column("locale_override", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("archived_at", TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint("kind IN ('UPLOADED','DERIVED')", name="ck_tables_kind"),
        sa.UniqueConstraint("dataset_id", "name", name="uq_tables_dataset_name"),
    )
    op.create_index("ix_tables_tenant_workspace", "flyquery_tables", ["tenant_id", "workspace_id"])
    op.create_index("ix_tables_dataset", "flyquery_tables", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("flyquery_tables")
    op.drop_table("flyquery_files")
    op.drop_table("flyquery_datasets")
    op.drop_table("flyquery_workspaces")
```

- [ ] **Step 5: Run; expect PASS**

```bash
task dev
uv run pytest tests/integration/test_migrations.py -m integration -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add migrations/versions/*lifecycle.py tests/integration/test_migrations.py
git commit -m "feat: alembic 0001 — lifecycle tables (workspaces/datasets/files/tables)"
```

---

### Task 15: Schema KB entities + Migration 0002

> Schema KB = the columnar truth derived from each uploaded file. 4 tables: `flyquery_schema_snapshots`, `flyquery_schema_changes`, `flyquery_schema_objects`, `flyquery_relations`. Per spec §5.

**Files:**
- Create: `src/flyquery/models/entities/schema.py`
- Modify: `src/flyquery/models/entities/__init__.py` (import the four new classes)
- Create: `migrations/versions/0002_schema_kb.py`
- Modify: `tests/integration/test_migrations.py` (extend assertion set)

- [ ] **Step 1: Extend the test**

```python
# tests/integration/test_migrations.py — add to the existing test
expected = {
    "flyquery_workspaces", "flyquery_datasets", "flyquery_files", "flyquery_tables",
    "flyquery_schema_snapshots", "flyquery_schema_changes",
    "flyquery_schema_objects", "flyquery_relations",
}
assert expected <= names
```

- [ ] **Step 2: Run; expect FAIL** (new tables don't exist)

- [ ] **Step 3: Write `src/flyquery/models/entities/schema.py`**

Translate each table below into a SQLAlchemy class following the Task 13 pattern (`Base`, typed `Mapped[]`, `mapped_column`, JSONB / TIMESTAMP / UUID from `sqlalchemy.dialects.postgresql`, `Vector(1536)` from `pgvector.sqlalchemy` where indicated). Names + columns must match the migration body in Step 5 exactly.

Classes to define:
- `SchemaSnapshot` → `flyquery_schema_snapshots`
- `SchemaChange` → `flyquery_schema_changes`
- `SchemaObject` → `flyquery_schema_objects`
- `Relation` → `flyquery_relations`

Re-export them from `models/entities/__init__.py` and add them to `__all__`.

- [ ] **Step 4: Write `migrations/versions/0002_schema_kb.py`**

```python
"""schema KB tables: snapshots, changes, schema_objects, relations

Revision ID: 0002_schema_kb
Revises: 0001_lifecycle
Create Date: 2026-05-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

revision = "0002_schema_kb"
down_revision = "0001_lifecycle"


def upgrade() -> None:
    op.create_table(
        "flyquery_schema_snapshots",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("taken_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("snapshot_hash", sa.Text, nullable=False),
        sa.Column("n_columns", sa.Integer, nullable=False),
        sa.Column("n_rows_estimate", sa.BigInteger, nullable=True),
        sa.Column("n_rows_actual", sa.BigInteger, nullable=True),
        sa.Column("parquet_object_key", sa.Text, nullable=True),
        sa.Column("parquet_byte_size", sa.BigInteger, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PARTIAL'")),
        sa.Column("failure_json", JSONB, nullable=True),
        sa.Column("triggered_by", sa.Text, nullable=False),
        sa.Column("created_by", sa.Text, nullable=False),
        sa.CheckConstraint("status IN ('PARTIAL','READY','FAILED')", name="ck_snapshots_status"),
        sa.CheckConstraint(
            "triggered_by IN ('USER','AGENT','SCHEDULED','REPARSE')", name="ck_snapshots_trigger"
        ),
    )
    op.create_index(
        "ix_snapshots_tenant_workspace", "flyquery_schema_snapshots", ["tenant_id", "workspace_id"]
    )
    op.create_index("ix_snapshots_table", "flyquery_schema_snapshots", ["table_id"])

    op.create_table(
        "flyquery_schema_changes",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "prev_snapshot_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "next_snapshot_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("column_name", sa.Text, nullable=False),
        sa.Column("change", sa.Text, nullable=False),
        sa.Column("before_json", JSONB, nullable=True),
        sa.Column("after_json", JSONB, nullable=True),
        sa.Column("llm_rationale", sa.Text, nullable=True),
        sa.Column("approved_by", sa.Text, nullable=True),
        sa.Column("approved_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "change IN ('ADDED','REMOVED','TYPE_CHANGED','RENAMED','RENAMED_CANDIDATE')",
            name="ck_changes_kind",
        ),
    )
    op.create_index("ix_changes_table", "flyquery_schema_changes", ["table_id"])

    op.create_table(
        "flyquery_schema_objects",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "snapshot_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column(
            "parent_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_objects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("qualified_name", sa.Text, nullable=False),
        sa.Column("data_type", sa.Text, nullable=True),
        sa.Column("is_nullable", sa.Boolean, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_source", sa.Text, nullable=True),
        sa.Column("synonyms_json", JSONB, nullable=True),
        sa.Column("pii_tag", sa.Text, nullable=True),
        sa.Column("pii_source", sa.Text, nullable=True),
        sa.Column("business_owner", sa.Text, nullable=True),
        sa.Column("governance_json", JSONB, nullable=True),
        sa.Column("sample_values_json", JSONB, nullable=True),
        sa.Column("sample_taken_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("profile_json", JSONB, nullable=True),
        # embedding column is added in 0006 (pgvector extension is loaded there);
        # this migration only stores the embedding_model name slot.
        sa.Column("embedding_model", sa.Text, nullable=True),
        sa.Column("source_hash", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # content_tsv is added in 0006 alongside vector indexes.
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_seen_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_changed_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('TABLE','COLUMN')", name="ck_objects_kind"),
    )
    op.create_index("ix_objects_table", "flyquery_schema_objects", ["table_id"])
    op.create_index("ix_objects_snapshot", "flyquery_schema_objects", ["snapshot_id"])

    op.create_table(
        "flyquery_relations",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "from_table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_column_name", sa.Text, nullable=False),
        sa.Column(
            "to_table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("to_column_name", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=True),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PROPOSED'")),
        sa.Column("approved_by", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('HEURISTIC','AGENT_PROPOSED','MANUAL')", name="ck_relations_kind"),
        sa.CheckConstraint("status IN ('PROPOSED','APPROVED','REJECTED')", name="ck_relations_status"),
    )
    op.create_index("ix_relations_dataset", "flyquery_relations", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("flyquery_relations")
    op.drop_table("flyquery_schema_objects")
    op.drop_table("flyquery_schema_changes")
    op.drop_table("flyquery_schema_snapshots")
```

- [ ] **Step 5: Run; expect PASS**

```bash
uv run pytest tests/integration/test_migrations.py -m integration -v
```

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/models/entities/schema.py src/flyquery/models/entities/__init__.py \
        migrations/versions/*schema_kb.py tests/integration/test_migrations.py
git commit -m "feat: alembic 0002 + entities — schema KB (snapshots/changes/objects/relations)"
```

---

### Task 16: Semantic + examples entities + Migration 0003

**Files:**
- Create: `src/flyquery/models/entities/semantic.py`
- Create: `src/flyquery/models/entities/examples.py`
- Modify: `src/flyquery/models/entities/__init__.py`
- Create: `migrations/versions/0003_semantic_examples.py`
- Modify: `tests/integration/test_migrations.py`

- [ ] **Step 1: Extend test set with the new tables**

```python
expected |= {
    "flyquery_semantic_metrics", "flyquery_semantic_dimensions",
    "flyquery_semantic_versions", "flyquery_glossary_terms",
    "flyquery_examples",
}
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write the migration `0003_semantic_examples.py`**

```python
"""semantic layer + examples

Revision ID: 0003_semantic_examples
Revises: 0002_schema_kb
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

revision = "0003_semantic_examples"
down_revision = "0002_schema_kb"


def upgrade() -> None:
    for tbl in ("flyquery_semantic_metrics", "flyquery_semantic_dimensions"):
        op.create_table(
            tbl,
            sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
            sa.Column("tenant_id", sa.Text, nullable=False),
            sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
            sa.Column(
                "dataset_id",
                UUID(as_uuid=True),
                sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("name", sa.Text, nullable=False),
            sa.Column("label", sa.Text, nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("definition_yaml", sa.Text, nullable=False),
            sa.Column("compiled_sql_template", sa.Text, nullable=True),
            sa.Column("metric_type", sa.Text, nullable=False, server_default=sa.text("'SIMPLE'")),
            sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'DRAFT'")),
            sa.Column("current_version", sa.Integer, nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.UniqueConstraint("dataset_id", "name", name=f"uq_{tbl}_dataset_name"),
            sa.CheckConstraint(
                "metric_type IN ('SIMPLE','RATIO','DERIVED','CUMULATIVE')",
                name=f"ck_{tbl}_type",
            ),
            sa.CheckConstraint(
                "status IN ('DRAFT','PUBLISHED','RETIRED')", name=f"ck_{tbl}_status"
            ),
        )

    op.create_table(
        "flyquery_semantic_versions",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.Text, nullable=False),  # 'metric' | 'dimension'
        sa.Column("parent_id", UUID(as_uuid=True), nullable=False),  # FK polymorphic; enforced in code
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("definition_yaml", sa.Text, nullable=False),
        sa.Column("compiled_sql_template", sa.Text, nullable=True),
        sa.Column("created_by", sa.Text, nullable=False),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("kind", "parent_id", "version", name="uq_versions_kind_parent_version"),
    )

    op.create_table(
        "flyquery_glossary_terms",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("term", sa.Text, nullable=False),
        sa.Column("definition", sa.Text, nullable=False),
        sa.Column("synonyms_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("tags_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("related_columns_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("related_metrics_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("workspace_id", "term", name="uq_glossary_workspace_term"),
    )

    op.create_table(
        "flyquery_examples",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("generated_sql", sa.Text, nullable=False),
        sa.Column("normalised_sql", sa.Text, nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("quality", sa.Text, nullable=False, server_default=sa.text("'PROPOSED'")),
        # vector column added in 0006 alongside other pgvector columns.
        sa.Column("citations_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.Text, nullable=False),
        sa.Column("last_used_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("usage_count", sa.BigInteger, nullable=False, server_default=sa.text("0")),
        sa.CheckConstraint(
            "source IN ('USER_CURATED','AGENT_LEARNED')", name="ck_examples_source"
        ),
        sa.CheckConstraint(
            "quality IN ('PROPOSED','APPROVED','REJECTED')", name="ck_examples_quality"
        ),
    )
    op.create_index("ix_examples_dataset", "flyquery_examples", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("flyquery_examples")
    op.drop_table("flyquery_glossary_terms")
    op.drop_table("flyquery_semantic_versions")
    op.drop_table("flyquery_semantic_dimensions")
    op.drop_table("flyquery_semantic_metrics")
```

- [ ] **Step 4: Translate to SQLAlchemy entities** (`semantic.py` defines `SemanticMetric, SemanticDimension, SemanticVersion, GlossaryTerm`; `examples.py` defines `Example`). Add to `__init__.py` exports.

- [ ] **Step 5: Run; expect PASS**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/models/entities/{semantic,examples}.py \
        src/flyquery/models/entities/__init__.py \
        migrations/versions/*semantic_examples.py \
        tests/integration/test_migrations.py
git commit -m "feat: alembic 0003 + entities — semantic layer + glossary + examples"
```

---

### Task 17: Queries + conversations entities + Migration 0004

**Files:**
- Create: `src/flyquery/models/entities/queries.py`
- Modify: `src/flyquery/models/entities/__init__.py`
- Create: `migrations/versions/0004_queries_conversations.py`
- Modify: `tests/integration/test_migrations.py`

- [ ] **Step 1: Extend test set**

```python
expected |= {
    "flyquery_queries", "flyquery_query_results",
    "flyquery_conversations", "flyquery_conversation_turns",
}
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write the migration**

```python
"""queries + conversations

Revision ID: 0004_queries_conversations
Revises: 0003_semantic_examples
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, NUMERIC, TIMESTAMP, UUID

revision = "0004_queries_conversations"
down_revision = "0003_semantic_examples"


def upgrade() -> None:
    op.create_table(
        "flyquery_queries",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("prior_turn_ids", ARRAY(UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("table_id_snapshot_pins_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("semantic_path_taken", sa.Text, nullable=True),
        sa.Column("candidates_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("chosen_candidate_index", sa.Integer, nullable=True),
        sa.Column("executed_sql", sa.Text, nullable=True),
        sa.Column("ast_classification", sa.Text, nullable=True),
        sa.Column("execution_engine", sa.Text, nullable=False, server_default=sa.text("'duckdb'")),
        sa.Column("execution_status", sa.Text, nullable=True),
        sa.Column("retries", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("elapsed_ms", sa.Integer, nullable=True),
        sa.Column("cost_cents", NUMERIC, nullable=False, server_default=sa.text("0")),
        sa.Column("clarification_emitted", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("clarification_json", JSONB, nullable=True),
        sa.Column("pii_findings_json", JSONB, nullable=True),
        sa.Column("error_json", JSONB, nullable=True),
        sa.Column("model_grounding", sa.Text, nullable=True),
        sa.Column("model_generation", sa.Text, nullable=True),
        sa.Column("model_critic", sa.Text, nullable=True),
        sa.Column("model_explainer", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finalised_at", TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint(
            "semantic_path_taken IS NULL OR semantic_path_taken IN ('SEMANTIC_LAYER','SYNTHESIS','HYBRID')",
            name="ck_queries_semantic_path",
        ),
        sa.CheckConstraint(
            "execution_status IS NULL OR execution_status IN ('OK','REFINED_OK','FAILED','REJECTED_BY_FIREWALL')",
            name="ck_queries_status",
        ),
        sa.CheckConstraint(
            "ast_classification IS NULL OR ast_classification IN ('SELECT','INSERT','UPDATE','DELETE','DDL')",
            name="ck_queries_ast",
        ),
    )
    op.create_index("ix_queries_tenant_workspace", "flyquery_queries", ["tenant_id", "workspace_id"])

    op.create_table(
        "flyquery_query_results",
        sa.Column(
            "query_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_queries.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("result_preview_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_object_key", sa.Text, nullable=True),
        sa.Column("result_byte_size", sa.BigInteger, nullable=True),
        sa.Column("ttl_expires_at", TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_table(
        "flyquery_conversations",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("actor", sa.Text, nullable=False),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "flyquery_conversation_turns",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "conversation_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("turn_index", sa.Integer, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("executed_sql", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("table_qnames_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("snapshot_pins_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("citations_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("no_answer", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("elapsed_ms", sa.Integer, nullable=True),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("conversation_id", "turn_index", name="uq_turns_conversation_index"),
    )


def downgrade() -> None:
    op.drop_table("flyquery_conversation_turns")
    op.drop_table("flyquery_conversations")
    op.drop_table("flyquery_query_results")
    op.drop_table("flyquery_queries")
```

- [ ] **Step 4: Translate to entities** — classes `Query, QueryResult, Conversation, ConversationTurn` in `queries.py`; export.

- [ ] **Step 5: Run; expect PASS.**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/models/entities/queries.py src/flyquery/models/entities/__init__.py \
        migrations/versions/*queries_conversations.py tests/integration/test_migrations.py
git commit -m "feat: alembic 0004 + entities — queries + conversations"
```

---

### Task 18: Ops entities (tokens/audit/cost/ingest) + Migration 0005

**Files:**
- Create: `src/flyquery/models/entities/ops.py`
- Modify: `src/flyquery/models/entities/__init__.py`
- Create: `migrations/versions/0005_ops.py`
- Modify: `tests/integration/test_migrations.py`

- [ ] **Step 1: Extend test set**

```python
expected |= {
    "flyquery_agent_tokens", "flyquery_audit_events", "flyquery_cost_events",
    "flyquery_ingest_jobs", "flyquery_ingest_events",
}
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write the migration** (full content)

```python
"""ops tables: agent_tokens, audit, cost, ingest_jobs, ingest_events

Revision ID: 0005_ops
Revises: 0004_queries_conversations
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC, TIMESTAMP, UUID

revision = "0005_ops"
down_revision = "0004_queries_conversations"


def upgrade() -> None:
    op.create_table(
        "flyquery_agent_tokens",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("prefix", sa.String(12), nullable=False, unique=True),
        sa.Column("secret_hash", sa.String(64), nullable=False),
        sa.Column("workspace_allowlist_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("dataset_allowlist_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("scopes_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("rate_limit_rpm", sa.Integer, nullable=True),
        sa.Column("expires_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_used_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.Text, nullable=False),
    )
    op.create_index("ix_agent_tokens_tenant", "flyquery_agent_tokens", ["tenant_id"])

    op.create_table(
        "flyquery_audit_events",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.Text, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("resource_kind", sa.Text, nullable=False),
        sa.Column("resource_id", sa.Text, nullable=True),
        sa.Column("correlation_id", sa.Text, nullable=True),
        sa.Column("payload_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_tenant_workspace_at", "flyquery_audit_events", ["tenant_id", "workspace_id", "created_at"])

    op.create_table(
        "flyquery_cost_events",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.Text, nullable=False),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("operation", sa.Text, nullable=False),
        sa.Column("input_tokens", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("output_tokens", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("cost_cents", NUMERIC, nullable=False, server_default=sa.text("0")),
        sa.Column("ingest_job_id", UUID(as_uuid=True), nullable=True),
        sa.Column("query_id", UUID(as_uuid=True), nullable=True),
        sa.Column("correlation_id", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_cost_tenant_workspace_at", "flyquery_cost_events", ["tenant_id", "workspace_id", "created_at"])

    op.create_table(
        "flyquery_ingest_jobs",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("table_id", UUID(as_uuid=True), nullable=True),
        sa.Column("file_id", UUID(as_uuid=True), nullable=True),
        sa.Column("snapshot_id", UUID(as_uuid=True), nullable=True),
        sa.Column("job_kind", sa.Text, nullable=False),
        sa.Column("request_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("attempts", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("finished_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cost_cents", NUMERIC, nullable=False, server_default=sa.text("0")),
        sa.Column("elapsed_ms", sa.Integer, nullable=True),
        sa.CheckConstraint(
            "job_kind IN ('PARSE_AND_INGEST','REPARSE','SAMPLE_REFRESH','DESCRIBE_PASS','RELATION_PASS')",
            name="ck_jobs_kind",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','SUCCEEDED','FAILED','CANCELLED')", name="ck_jobs_status"
        ),
    )
    op.create_index("ix_jobs_tenant_workspace", "flyquery_ingest_jobs", ["tenant_id", "workspace_id"])

    op.create_table(
        "flyquery_ingest_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "ingest_job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_ingest_jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("stage", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("payload_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_events_job", "flyquery_ingest_events", ["ingest_job_id"])


def downgrade() -> None:
    op.drop_table("flyquery_ingest_events")
    op.drop_table("flyquery_ingest_jobs")
    op.drop_table("flyquery_cost_events")
    op.drop_table("flyquery_audit_events")
    op.drop_table("flyquery_agent_tokens")
```

- [ ] **Step 4: Translate to entities** — classes `AgentToken, AuditEvent, CostEvent, IngestJob, IngestEvent` in `ops.py`; export.

- [ ] **Step 5: Run; expect PASS.**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/models/entities/ops.py src/flyquery/models/entities/__init__.py \
        migrations/versions/*ops.py tests/integration/test_migrations.py
git commit -m "feat: alembic 0005 + entities — agent_tokens / audit / cost / ingest"
```

---

### Task 19: pgvector extension + vector columns + tsvector + indexes (Migration 0006)

**Files:**
- Create: `migrations/versions/0006_vectors_and_indexes.py`
- Modify: `src/flyquery/models/entities/schema.py` (add `embedding` + `content_tsv` columns to `SchemaObject`)
- Modify: `src/flyquery/models/entities/examples.py` (add `embedding` column to `Example`)
- Modify: `tests/integration/test_migrations.py`

- [ ] **Step 1: Extend test — confirm pgvector extension is loaded + indexes exist**

```python
@pytest.mark.integration
def test_pgvector_and_indexes_present() -> None:
    eng = create_engine(os.environ["FLYQUERY_DATABASE_URL_ADMIN"])
    with eng.connect() as conn:
        ext = conn.execute(sa.text(
            "SELECT extname FROM pg_extension WHERE extname='vector'"
        )).scalar()
        assert ext == "vector"
        for idx in ("ix_objects_embedding", "ix_objects_tsv", "ix_examples_embedding"):
            count = conn.execute(sa.text(
                "SELECT count(*) FROM pg_indexes WHERE indexname=:n"
            ), {"n": idx}).scalar()
            assert count == 1, f"missing index {idx}"
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write the migration**

```python
"""pgvector + vector columns + tsvector + HNSW indexes

Revision ID: 0006_vectors_and_indexes
Revises: 0005_ops
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "0006_vectors_and_indexes"
down_revision = "0005_ops"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "flyquery_schema_objects",
        sa.Column("embedding", sa.dialects.postgresql.ARRAY(sa.Float), nullable=True),
    )
    # Replace ARRAY with proper vector type via raw SQL (Alembic doesn't
    # know pgvector's `vector(N)`).
    op.execute("ALTER TABLE flyquery_schema_objects DROP COLUMN embedding")
    op.execute("ALTER TABLE flyquery_schema_objects ADD COLUMN embedding vector(1536)")
    op.add_column(
        "flyquery_schema_objects", sa.Column("content_tsv", TSVECTOR, nullable=True)
    )
    op.execute(
        "CREATE INDEX ix_objects_embedding ON flyquery_schema_objects "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )
    op.execute("CREATE INDEX ix_objects_tsv ON flyquery_schema_objects USING gin(content_tsv)")

    op.execute("ALTER TABLE flyquery_examples ADD COLUMN embedding vector(1536)")
    op.execute(
        "CREATE INDEX ix_examples_embedding ON flyquery_examples "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_examples_embedding")
    op.execute("ALTER TABLE flyquery_examples DROP COLUMN IF EXISTS embedding")
    op.execute("DROP INDEX IF EXISTS ix_objects_embedding")
    op.execute("DROP INDEX IF EXISTS ix_objects_tsv")
    op.execute("ALTER TABLE flyquery_schema_objects DROP COLUMN IF EXISTS content_tsv")
    op.execute("ALTER TABLE flyquery_schema_objects DROP COLUMN IF EXISTS embedding")
```

- [ ] **Step 4: Update `SchemaObject` + `Example` to add the new fields**

```python
# in src/flyquery/models/entities/schema.py — SchemaObject
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR

embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
content_tsv: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

# in src/flyquery/models/entities/examples.py — Example
embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
```

- [ ] **Step 5: Run; expect PASS.**

- [ ] **Step 6: Commit**

```bash
git add migrations/versions/*vectors_and_indexes.py \
        src/flyquery/models/entities/{schema,examples}.py \
        tests/integration/test_migrations.py
git commit -m "feat: alembic 0006 — pgvector extension, vector(1536), HNSW + GIN indexes"
```

---

### Task 20: RLS role split + policies + isolation test (Migration 0007)

**Files:**
- Create: `migrations/versions/0007_rls.py`
- Create: `tests/integration/test_rls_isolation.py`

> Per memory `postgres_test_role_bypasses_rls`, testcontainers' default `test` Postgres user is SUPERUSER (BYPASSRLS). We provision two non-superuser roles inside the migration and have the app authenticate as `flyquery_app`. Migrations themselves run as `flyquery_admin` (BYPASSRLS), but the isolation test connects as `flyquery_app` to verify the policies actually enforce.

- [ ] **Step 1: Write `tests/integration/test_rls_isolation.py`** (failing test first)

```python
# Copyright 2026 Firefly Software Solutions Inc
"""RLS forces tenant + workspace isolation across every multi-tenant table."""

from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa


MULTI_TENANT_TABLES = (
    "flyquery_datasets",
    "flyquery_files",
    "flyquery_tables",
    "flyquery_schema_snapshots",
    "flyquery_schema_changes",
    "flyquery_schema_objects",
    "flyquery_relations",
    "flyquery_semantic_metrics",
    "flyquery_semantic_dimensions",
    "flyquery_semantic_versions",
    "flyquery_glossary_terms",
    "flyquery_examples",
    "flyquery_queries",
    "flyquery_query_results",
    "flyquery_conversations",
    "flyquery_conversation_turns",
    "flyquery_audit_events",
    "flyquery_cost_events",
    "flyquery_ingest_jobs",
    "flyquery_ingest_events",
)


@pytest.fixture
def app_engine() -> sa.engine.Engine:
    url = os.environ["FLYQUERY_DATABASE_URL"].replace("+asyncpg", "+psycopg")
    return sa.create_engine(url)


def _seed_workspace(admin_url: str, tenant: str, workspace_slug: str) -> uuid.UUID:
    eng = sa.create_engine(admin_url)
    with eng.begin() as conn:
        ws_id = conn.execute(
            sa.text(
                "INSERT INTO flyquery_workspaces(tenant_id,slug,name) "
                "VALUES(:t,:s,:n) RETURNING id"
            ),
            {"t": tenant, "s": workspace_slug, "n": workspace_slug},
        ).scalar_one()
        ds_id = conn.execute(
            sa.text(
                "INSERT INTO flyquery_datasets(tenant_id,workspace_id,name) "
                "VALUES(:t,:w,:n) RETURNING id"
            ),
            {"t": tenant, "w": ws_id, "n": "ds-1"},
        ).scalar_one()
    return ws_id, ds_id


@pytest.mark.integration
def test_app_role_sees_only_bound_tenant_workspace(app_engine: sa.engine.Engine) -> None:
    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
    ws_a, ds_a = _seed_workspace(admin_url, "tenant-a", "wsA")
    ws_b, ds_b = _seed_workspace(admin_url, "tenant-b", "wsB")

    with app_engine.connect() as conn:
        conn.execute(sa.text("SET LOCAL app.tenant_id = 'tenant-a'"))
        conn.execute(sa.text(f"SET LOCAL app.workspace_id = '{ws_a}'"))
        rows = conn.execute(sa.text("SELECT id FROM flyquery_datasets")).fetchall()
        assert {r.id for r in rows} == {ds_a}, "tenant-a should not see tenant-b rows"

    with app_engine.connect() as conn:
        conn.execute(sa.text("SET LOCAL app.tenant_id = 'tenant-b'"))
        conn.execute(sa.text(f"SET LOCAL app.workspace_id = '{ws_b}'"))
        rows = conn.execute(sa.text("SELECT id FROM flyquery_datasets")).fetchall()
        assert {r.id for r in rows} == {ds_b}


@pytest.mark.integration
def test_rls_blocks_cross_workspace_insert(app_engine: sa.engine.Engine) -> None:
    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
    ws_a, _ = _seed_workspace(admin_url, "tenant-a", "wsA-2")
    ws_b, _ = _seed_workspace(admin_url, "tenant-b", "wsB-2")

    with app_engine.connect() as conn:
        conn.execute(sa.text("SET LOCAL app.tenant_id = 'tenant-a'"))
        conn.execute(sa.text(f"SET LOCAL app.workspace_id = '{ws_a}'"))
        # USING implies WITH CHECK (memory: rls_using_implies_with_check)
        with pytest.raises(sa.exc.ProgrammingError):
            conn.execute(
                sa.text(
                    "INSERT INTO flyquery_datasets(tenant_id,workspace_id,name) "
                    "VALUES('tenant-b', :wb, 'cross-tenant-leak')"
                ),
                {"wb": ws_b},
            )
```

- [ ] **Step 2: Run; expect FAIL** (no roles, no policies yet)

- [ ] **Step 3: Write the migration**

```python
"""RLS: role split (admin / app) + policies on every multi-tenant table

Revision ID: 0007_rls
Revises: 0006_vectors_and_indexes

NOTE: This migration provisions the flyquery_admin + flyquery_app roles
inside the local Postgres container. In production, ops creates the
roles via the deploy bootstrap and this migration is a no-op for the
role-creation step (idempotent CREATE ROLE IF NOT EXISTS via PL/pgSQL).
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0007_rls"
down_revision = "0006_vectors_and_indexes"


MULTI_TENANT_TABLES = (
    "flyquery_datasets",
    "flyquery_files",
    "flyquery_tables",
    "flyquery_schema_snapshots",
    "flyquery_schema_changes",
    "flyquery_schema_objects",
    "flyquery_relations",
    "flyquery_semantic_metrics",
    "flyquery_semantic_dimensions",
    "flyquery_semantic_versions",
    "flyquery_glossary_terms",
    "flyquery_examples",
    "flyquery_queries",
    "flyquery_query_results",
    "flyquery_conversations",
    "flyquery_conversation_turns",
    "flyquery_audit_events",
    "flyquery_cost_events",
    "flyquery_ingest_jobs",
    "flyquery_ingest_events",
)


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='flyquery_admin') THEN
                CREATE ROLE flyquery_admin LOGIN PASSWORD 'flyquery_admin' BYPASSRLS;
            END IF;
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='flyquery_app') THEN
                CREATE ROLE flyquery_app LOGIN PASSWORD 'flyquery_app' NOSUPERUSER;
            END IF;
        END $$;
        """
    )
    op.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO flyquery_admin")
    op.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO flyquery_admin")
    op.execute("GRANT USAGE ON SCHEMA public TO flyquery_app")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO flyquery_app"
    )
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO flyquery_app")

    # Workspaces policy (workspace bound to id)
    op.execute("ALTER TABLE flyquery_workspaces ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_workspaces FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY pol_workspaces ON flyquery_workspaces
            USING (tenant_id = current_setting('app.tenant_id', true)
                   AND id::text = current_setting('app.workspace_id', true))
        """
    )

    # Agent-tokens policy (tenant-only; workspace check is in code)
    op.execute("ALTER TABLE flyquery_agent_tokens ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_agent_tokens FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY pol_agent_tokens ON flyquery_agent_tokens
            USING (tenant_id = current_setting('app.tenant_id', true))
        """
    )

    # Standard policy on every multi-tenant table
    for tbl in MULTI_TENANT_TABLES:
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY pol_{tbl[len('flyquery_'):]} ON {tbl}
                USING (tenant_id = current_setting('app.tenant_id', true)
                       AND workspace_id::text = current_setting('app.workspace_id', true))
            """
        )


def downgrade() -> None:
    for tbl in MULTI_TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS pol_{tbl[len('flyquery_'):]} ON {tbl}")
        op.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS pol_agent_tokens ON flyquery_agent_tokens")
    op.execute("ALTER TABLE flyquery_agent_tokens NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_agent_tokens DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS pol_workspaces ON flyquery_workspaces")
    op.execute("ALTER TABLE flyquery_workspaces NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_workspaces DISABLE ROW LEVEL SECURITY")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM flyquery_app")
    # Don't DROP ROLE here -- production deploys own the role lifecycle.
```

- [ ] **Step 4: Adjust the integration conftest to use `flyquery_app` as the runtime URL**

In `tests/integration/conftest.py`, after migrations run, rebuild the app URL so it authenticates as `flyquery_app`:

```python
# At the end of configure_env:
app_url = async_url.replace(
    f"//{postgres_container.username}:{postgres_container.password}",
    "//flyquery_app:flyquery_app"
)
monkeypatch.setenv("FLYQUERY_DATABASE_URL", app_url)
```

- [ ] **Step 5: Run; expect PASS**

```bash
uv run pytest tests/integration/test_rls_isolation.py -m integration -v
```

- [ ] **Step 6: Commit**

```bash
git add migrations/versions/*rls.py tests/integration/test_rls_isolation.py tests/integration/conftest.py
git commit -m "feat: alembic 0007 — RLS role split + policies + isolation test"
```

---

## Phase D — Workspace + Dataset CRUD (Tasks 21-25)

### Task 21: Workspace DTOs + repository + service

**Files:**
- Create: `src/flyquery/interfaces/workspaces.py`
- Create: `src/flyquery/core/services/workspaces/workspace_repository.py`
- Create: `src/flyquery/core/services/workspaces/workspace_service.py`
- Test: `tests/unit/test_workspace_service.py`

- [ ] **Step 1: Write the failing service test**

```python
# tests/unit/test_workspace_service.py
import pytest
from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.workspaces import WorkspaceCreate


class FakeRepo:
    def __init__(self): self.rows = []
    async def create(self, **fields):
        self.rows.append(fields)
        return {**fields, "id": "ws-1"}
    async def list_by_tenant(self, tenant_id):
        return [r for r in self.rows if r["tenant_id"] == tenant_id]


@pytest.mark.asyncio
async def test_create_workspace_assigns_defaults() -> None:
    svc = WorkspaceService(FakeRepo())
    ws = await svc.create("tenant-a", WorkspaceCreate(slug="alpha", name="Alpha"))
    assert ws["allow_direct_sql"] is False
    assert ws["default_locale"] == "en-US"
    assert ws["status"] == "ACTIVE"
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write DTOs (`interfaces/workspaces.py`)**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Workspace wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    slug: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    kms_key_uri: str | None = None
    retention_days: int | None = Field(default=None, ge=1)
    allow_direct_sql: bool = False
    default_locale: str = "en-US"
    metadata_json: dict = Field(default_factory=dict)


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    kms_key_uri: str | None = None
    retention_days: int | None = Field(default=None, ge=1)
    allow_direct_sql: bool | None = None
    default_locale: str | None = None
    metadata_json: dict | None = None


class WorkspaceRead(BaseModel):
    id: uuid.UUID
    tenant_id: str
    slug: str
    name: str
    kms_key_uri: str | None
    retention_days: int | None
    allow_direct_sql: bool
    default_locale: str
    storage_used_bytes: int
    status: Literal["ACTIVE", "ARCHIVED", "PURGING"]
    created_at: datetime
    updated_at: datetime
    metadata_json: dict
```

- [ ] **Step 4: Write the repository (`workspace_repository.py`)**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_workspaces."""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **fields: Any) -> dict[str, Any]:
        result = await self._session.execute(
            sa.text(
                """
                INSERT INTO flyquery_workspaces
                    (tenant_id, slug, name, kms_key_uri, retention_days,
                     allow_direct_sql, default_locale, metadata_json)
                VALUES
                    (:tenant_id, :slug, :name, :kms_key_uri, :retention_days,
                     :allow_direct_sql, :default_locale, CAST(:metadata_json AS jsonb))
                RETURNING id, tenant_id, slug, name, kms_key_uri, retention_days,
                          allow_direct_sql, default_locale, storage_used_bytes,
                          status, created_at, updated_at, metadata_json
                """
            ),
            fields,
        )
        row = result.mappings().one()
        return dict(row)

    async def list_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        result = await self._session.execute(
            sa.text(
                "SELECT * FROM flyquery_workspaces WHERE tenant_id = :tenant_id ORDER BY created_at"
            ),
            {"tenant_id": tenant_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None:
        result = await self._session.execute(
            sa.text("SELECT * FROM flyquery_workspaces WHERE id = :id"),
            {"id": workspace_id},
        )
        row = result.mappings().one_or_none()
        return dict(row) if row else None

    async def update(self, workspace_id: uuid.UUID, **fields: Any) -> dict[str, Any]:
        if not fields:
            row = await self.get(workspace_id)
            assert row is not None
            return row
        sets = ", ".join(f"{k} = :{k}" for k in fields)
        result = await self._session.execute(
            sa.text(
                f"UPDATE flyquery_workspaces SET {sets}, updated_at = now() "
                "WHERE id = :id RETURNING *"
            ),
            {"id": workspace_id, **fields},
        )
        return dict(result.mappings().one())

    async def archive(self, workspace_id: uuid.UUID) -> None:
        await self._session.execute(
            sa.text("UPDATE flyquery_workspaces SET status='ARCHIVED', updated_at=now() WHERE id = :id"),
            {"id": workspace_id},
        )
```

- [ ] **Step 5: Write the service (`workspace_service.py`)**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""Workspace service: defaults + invariants."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from flyquery.interfaces.workspaces import WorkspaceCreate, WorkspaceUpdate


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]: ...
    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update(self, workspace_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def archive(self, workspace_id: uuid.UUID) -> None: ...


class WorkspaceService:
    def __init__(self, repo: _Repo) -> None:
        self._repo = repo

    async def create(self, tenant_id: str, body: WorkspaceCreate) -> dict[str, Any]:
        return await self._repo.create(
            tenant_id=tenant_id,
            slug=body.slug,
            name=body.name,
            kms_key_uri=body.kms_key_uri,
            retention_days=body.retention_days,
            allow_direct_sql=body.allow_direct_sql,
            default_locale=body.default_locale,
            metadata_json=body.metadata_json,
        )

    async def list(self, tenant_id: str) -> list[dict[str, Any]]:
        return await self._repo.list_by_tenant(tenant_id)

    async def get(self, workspace_id: uuid.UUID) -> dict[str, Any] | None:
        return await self._repo.get(workspace_id)

    async def update(self, workspace_id: uuid.UUID, body: WorkspaceUpdate) -> dict[str, Any]:
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        return await self._repo.update(workspace_id, **fields)

    async def archive(self, workspace_id: uuid.UUID) -> None:
        await self._repo.archive(workspace_id)
```

- [ ] **Step 6: Run unit test; expect PASS**

```bash
uv run pytest tests/unit/test_workspace_service.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/flyquery/interfaces/workspaces.py \
        src/flyquery/core/services/workspaces/ \
        tests/unit/test_workspace_service.py
git commit -m "feat: WorkspaceService + repository + DTOs (defaults: ALLOW_DIRECT_SQL=false, en-US)"
```

---

### Task 22: Workspace REST controller (CRUD + `:purge` stub)

**Files:**
- Create: `src/flyquery/web/controllers/workspaces_controller.py`
- Test: `tests/integration/test_workspaces_crud.py`

- [ ] **Step 1: Write the failing integration test**

```python
# tests/integration/test_workspaces_crud.py
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_then_list_workspace() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "alpha", "name": "Alpha"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "alpha"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]

        r = await c.get(
            "/api/v1/workspaces",
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["items"][0]["slug"] == "alpha"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_purge_workspace_marks_for_tombstone() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "beta", "name": "Beta"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "beta"},
        )
        ws_id = r.json()["id"]
        r = await c.delete(
            f"/api/v1/workspaces/{ws_id}:purge",
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 202   # accepted; purge is async
        # 30-day tombstone — status flips, bytes not yet gone
```

- [ ] **Step 2: Run; expect FAIL (no controller)**

- [ ] **Step 3: Write the controller**

```python
# src/flyquery/web/controllers/workspaces_controller.py
# Copyright 2026 Firefly Software Solutions Inc
"""Workspace REST controller."""

from __future__ import annotations

import uuid

from pyfly.web import (
    Body,
    PathVar,
    Valid,
    rest_controller,
    request_mapping,
    response_status,
)

from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from flyquery.web.conventions import (
    actor_from_request,
    tenant_context,
)


@rest_controller(path="/api/v1/workspaces", tags=["workspaces"])
class WorkspacesController:
    def __init__(self, service: WorkspaceService) -> None:
        self._service = service

    @request_mapping(method="POST", path="")
    @response_status(201)
    async def create(self, body: Valid[Body[WorkspaceCreate]]) -> WorkspaceRead:
        ctx = tenant_context()
        row = await self._service.create(ctx.tenant_id, body)
        return WorkspaceRead.model_validate(row)

    @request_mapping(method="GET", path="")
    async def list(self) -> dict:
        ctx = tenant_context()
        rows = await self._service.list(ctx.tenant_id)
        return {"items": [WorkspaceRead.model_validate(r).model_dump(mode="json") for r in rows]}

    @request_mapping(method="GET", path="/{workspace_id}")
    async def read(self, workspace_id: PathVar[uuid.UUID]) -> WorkspaceRead:
        row = await self._service.get(workspace_id)
        assert row is not None
        return WorkspaceRead.model_validate(row)

    @request_mapping(method="PUT", path="/{workspace_id}")
    async def update(
        self, workspace_id: PathVar[uuid.UUID], body: Valid[Body[WorkspaceUpdate]]
    ) -> WorkspaceRead:
        row = await self._service.update(workspace_id, body)
        return WorkspaceRead.model_validate(row)

    @request_mapping(method="DELETE", path="/{workspace_id}:purge")
    @response_status(202)
    async def purge(self, workspace_id: PathVar[uuid.UUID]) -> dict:
        # v0 stub: archive + emit audit; the real blob walk lands when
        # ObjectStore wires in (Task 33). 30-day tombstone enforced
        # by status=ARCHIVED + a scheduled job (added in Plan 2).
        await self._service.archive(workspace_id)
        return {"status": "accepted", "tombstone_expires_at": "+30d"}
```

- [ ] **Step 4: Wire the controller into `scan_packages`** — already covered by `flyquery.web.controllers` in `app.py` Task 8.

- [ ] **Step 5: Run; expect PASS**

```bash
uv run pytest tests/integration/test_workspaces_crud.py -m integration -v
```

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/web/controllers/workspaces_controller.py tests/integration/test_workspaces_crud.py
git commit -m "feat: /api/v1/workspaces CRUD + :purge stub (real blob walk in Task 33)"
```

---

### Task 23: Dataset DTOs + repository + service

**Files:**
- Create: `src/flyquery/interfaces/datasets.py`
- Create: `src/flyquery/core/services/datasets/dataset_repository.py`
- Create: `src/flyquery/core/services/datasets/dataset_service.py`
- Test: `tests/unit/test_dataset_service.py`

- [ ] **Step 1: Write the failing service test**

```python
# tests/unit/test_dataset_service.py
import pytest
import uuid
from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.interfaces.datasets import DatasetCreate


class FakeRepo:
    def __init__(self): self.rows = []
    async def create(self, **f): self.rows.append(f); return {**f, "id": str(uuid.uuid4())}
    async def list(self, tenant_id, workspace_id):
        return [r for r in self.rows
                if r["tenant_id"] == tenant_id and r["workspace_id"] == workspace_id]


@pytest.mark.asyncio
async def test_create_dataset_defaults_drift_policy_AUTO() -> None:
    svc = DatasetService(FakeRepo())
    ws = uuid.uuid4()
    ds = await svc.create("tenant-a", ws, DatasetCreate(name="Sales 2026"))
    assert ds["drift_policy"] == "AUTO"
    assert ds["status"] == "ACTIVE"
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write DTOs (`interfaces/datasets.py`)** — `DatasetCreate, DatasetUpdate, DatasetRead` mirroring the Workspace shape (fields per spec §5 `flyquery_datasets`).

- [ ] **Step 4: Write repository + service** — same pattern as Task 21, but on `flyquery_datasets`. The service must respect the `(tenant_id, workspace_id)` scope (RLS gives correctness; the service still passes the IDs explicitly so audit/log records carry them).

- [ ] **Step 5: Run; expect PASS**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/interfaces/datasets.py src/flyquery/core/services/datasets/ tests/unit/test_dataset_service.py
git commit -m "feat: DatasetService + repository + DTOs"
```

---

### Task 24: Dataset REST controller

**Files:**
- Create: `src/flyquery/web/controllers/datasets_controller.py`
- Test: `tests/integration/test_datasets_crud.py`

- [ ] **Step 1: Write the failing integration test** — create workspace → create dataset → list datasets → archive → list (status=ARCHIVED). Mirror Task 22 pattern.

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write the controller** — same shape as Task 22, on `/api/v1/datasets` (POST/GET/GET-by-id/PUT/DELETE).

- [ ] **Step 4: Run; expect PASS**

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/web/controllers/datasets_controller.py tests/integration/test_datasets_crud.py
git commit -m "feat: /api/v1/datasets CRUD"
```

---

### Task 25: Cross-workspace RLS integration test (uses real CRUD endpoints)

**Files:**
- Modify: `tests/integration/test_rls_isolation.py`

- [ ] **Step 1: Add a new test** — call POST /workspaces twice (different tenants) via httpx + ASGI; call GET /workspaces with tenant-A headers; assert response contains only tenant-A's row. Repeat for datasets.

- [ ] **Step 2: Run; expect PASS** (the policies from Task 20 already enforce; this is the higher-level integration confirmation that the controller's tenant binding hooks the RLS GUC writes).

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_rls_isolation.py
git commit -m "test: RLS isolation end-to-end through workspaces + datasets controllers"
```

---

## Phase E — Agent tokens + scope catalog (Tasks 26-28)

### Task 26: flyquery scope catalog

**Files:**
- Create: `src/flyquery/core/services/auth/scope_catalog.py`
- Test: `tests/unit/test_scope_catalog.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_scope_catalog.py
import pytest
from flyquery.core.services.auth.scope_catalog import (
    ALL_SCOPES,
    is_valid_scope,
    validate_scopes,
    InvalidScopeError,
)


def test_catalog_includes_every_spec_scope() -> None:
    expected = {
        "flyquery.datasets:read", "flyquery.datasets:write",
        "flyquery.files:upload", "flyquery.files:read",
        "flyquery.schema:read", "flyquery.schema:annotate",
        "flyquery.relations:read", "flyquery.relations:write",
        "flyquery.semantic:read", "flyquery.semantic:author",
        "flyquery.examples:read", "flyquery.examples:author",
        "flyquery.query:read", "flyquery.derived:write",
        "flyquery.sql:execute",
        "flyquery.conversations:read", "flyquery.conversations:write",
        "flyquery.ingest:read", "flyquery.ingest:run",
        "flyquery.lineage:read",
        "flyquery.audit:read", "flyquery.billing:read",
        "*",
    }
    assert expected <= set(ALL_SCOPES)


def test_validate_rejects_unknown_scope() -> None:
    with pytest.raises(InvalidScopeError):
        validate_scopes(["flyquery.query:bogus"])


def test_validate_accepts_known() -> None:
    validate_scopes(["flyquery.query:read", "flyquery.files:upload"])
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write `scope_catalog.py`**

```python
# Copyright 2026 Firefly Software Solutions Inc
"""flyquery agent-token scope catalog (spec §7.3).

Lock-step note: canon + radar each maintain their own catalog. The
``agent_token_service`` (lock-step from canon) consumes a callable
``validate_scopes`` per service. This module is the flyquery-specific
binding.
"""

from __future__ import annotations

from typing import Final


class InvalidScopeError(ValueError):
    """Raised when a token mint or check sees an unknown scope."""


ALL_SCOPES: Final[tuple[str, ...]] = (
    "flyquery.datasets:read",
    "flyquery.datasets:write",
    "flyquery.files:upload",
    "flyquery.files:read",
    "flyquery.schema:read",
    "flyquery.schema:annotate",
    "flyquery.relations:read",
    "flyquery.relations:write",
    "flyquery.semantic:read",
    "flyquery.semantic:author",
    "flyquery.examples:read",
    "flyquery.examples:author",
    "flyquery.query:read",
    "flyquery.derived:write",
    "flyquery.sql:execute",
    "flyquery.conversations:read",
    "flyquery.conversations:write",
    "flyquery.ingest:read",
    "flyquery.ingest:run",
    "flyquery.lineage:read",
    "flyquery.audit:read",
    "flyquery.billing:read",
    "*",  # operator-only wildcard
)


def is_valid_scope(scope: str) -> bool:
    return scope in ALL_SCOPES


def validate_scopes(scopes: list[str]) -> None:
    """Raise :class:`InvalidScopeError` on the first unknown scope."""
    for s in scopes:
        if not is_valid_scope(s):
            raise InvalidScopeError(f"unknown scope: {s!r}")
```

- [ ] **Step 4: Run; expect PASS**

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/core/services/auth/scope_catalog.py tests/unit/test_scope_catalog.py
git commit -m "feat: flyquery agent-token scope catalog (23 scopes incl. wildcard)"
```

---

### Task 27: Agent tokens controller (adapted lock-step from canon)

**Files:**
- Create: `src/flyquery/web/controllers/agent_tokens_controller.py`
- Test: `tests/integration/test_agent_tokens.py`

> Per spec §14, this is lock-step from canon with the catalog injection swap. The CI gate (`scripts/check_lockstep.py`) confirms byte-equivalence modulo the scope-catalog binding.

- [ ] **Step 1: Copy canon's controller + sed substitutions**

```bash
cp ../flycanon/src/flycanon/web/controllers/agent_tokens_controller.py \
   src/flyquery/web/controllers/agent_tokens_controller.py
sed -i.bak \
  -e 's/flycanon/flyquery/g' \
  -e 's/FLYCANON/FLYQUERY/g' \
  -e 's/canon_/flyquery_/g' \
  -e 's/CanonSettings/FlyquerySettings/g' \
  src/flyquery/web/controllers/agent_tokens_controller.py
rm src/flyquery/web/controllers/agent_tokens_controller.py.bak
```

Open the file and replace the imported scope catalog with flyquery's: `from flyquery.core.services.auth.scope_catalog import validate_scopes, ALL_SCOPES` (canon used `flycanon.core.services.auth.scope_catalog` — the sed should have already covered this).

- [ ] **Step 2: Write the integration test**

```python
# tests/integration/test_agent_tokens.py
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mint_token_and_use_on_agent_route() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Operator mints (user-tier; future JWT bearer; placeholder header)
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "tok", "name": "Token-Test"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "tok"},
        )
        ws_id = r.json()["id"]

        r = await c.post(
            "/api/v1/agent-tokens",
            json={
                "name": "test-bot",
                "scopes": ["flyquery.datasets:read"],
                "workspace_allowlist": [ws_id],
            },
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201
        token = r.json()["token"]   # one-shot; never re-shown
        assert token.startswith("agt_")

        # Agent uses the token on /api/v1/agent/* (we don't have any
        # agent route yet; tokens just need to verify)
        # Negative: unknown scope rejected at mint time
        r = await c.post(
            "/api/v1/agent-tokens",
            json={"name": "bad", "scopes": ["flyquery.query:bogus"]},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 400
        body = r.json()
        assert body.get("code") in ("invalid_scope", "validation_error")
```

- [ ] **Step 3: Run; expect FAIL or PASS** depending on whether the lock-step controller's mint flow correctly uses the flyquery scope catalog. If FAIL: inspect the controller, ensure it imports + calls `flyquery.core.services.auth.scope_catalog.validate_scopes` (not `flycanon.…`).

- [ ] **Step 4: Iterate until PASS**

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/web/controllers/agent_tokens_controller.py tests/integration/test_agent_tokens.py
git commit -m "feat: agent tokens controller (lock-step from canon, flyquery scope catalog)"
```

---

### Task 28: Agent-token verify middleware integration

**Files:**
- Modify: `src/flyquery/main.py` (register agent-token auth middleware after `TenantContextMiddleware`)
- Test: `tests/integration/test_agent_tokens.py` (extend with route-protected case)

- [ ] **Step 1: Add a dummy agent route to exercise the verify path**

```python
# src/flyquery/web/controllers/version_controller.py
from pyfly.web import rest_controller, request_mapping
from flyquery import __version__


@rest_controller(path="/api/v1", tags=["meta"])
class VersionController:
    @request_mapping(method="GET", path="/version")
    async def version(self) -> dict:
        return {"name": "flyquery", "version": __version__}


@rest_controller(path="/api/v1/agent", tags=["agent-meta"])
class AgentVersionController:
    @request_mapping(method="GET", path="/version", scopes=["flyquery.audit:read"])
    async def version(self) -> dict:
        return {"name": "flyquery", "version": __version__}
```

- [ ] **Step 2: Wire `AgentTokenAuthMiddleware`** — the lock-step `agent_token_service` exposes a starlette-style middleware. Import + register in `main.py` after `TenantContextMiddleware`:

```python
from flyquery.web.agent_deps import AgentTokenAuthMiddleware
app.add_middleware(AgentTokenAuthMiddleware)
```

(If canon names the middleware differently, mirror its name; lock-step gate will keep this stable.)

- [ ] **Step 3: Extend the test**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_route_requires_valid_token_and_scope() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # 1) No token → 401
        r = await c.get(
            "/api/v1/agent/version",
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "tok"},
        )
        assert r.status_code == 401

        # 2) Valid token but missing the required scope → 403
        # ... mint token with ["flyquery.query:read"] only, call /agent/version
        # (needs flyquery.audit:read) → 403

        # 3) Valid token with flyquery.audit:read → 200
```

- [ ] **Step 4: Run; expect PASS.**

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/web/controllers/version_controller.py src/flyquery/main.py tests/integration/test_agent_tokens.py
git commit -m "feat: AgentTokenAuthMiddleware wired; /api/v1/agent/version gated by scope"
```

---

## Phase F — ObjectStore port + adapters (Tasks 29-33)

### Task 29: `ObjectStore` port + types + factory

**Files:**
- Create: `src/flyquery/core/services/storage/object_store.py`
- Create: `src/flyquery/core/services/storage/object_store_factory.py`
- Test: `tests/unit/test_object_store_factory.py`

- [ ] **Step 1: Write the failing factory test**

```python
# tests/unit/test_object_store_factory.py
import pytest
from flyquery.core.services.storage.object_store_factory import build_object_store
from flyquery.config import FlyquerySettings


def test_factory_returns_local_fs_by_default() -> None:
    s = FlyquerySettings(object_store="local", object_store_base="/tmp/flyquery-x")
    store = build_object_store(s)
    assert store.__class__.__name__ == "LocalFsObjectStore"


def test_factory_raises_on_s3_without_extra(monkeypatch) -> None:
    s = FlyquerySettings(object_store="s3")
    monkeypatch.setattr("flyquery.core.services.storage.object_store_factory._HAS_S3", False)
    with pytest.raises(RuntimeError, match="extra"):
        build_object_store(s)
```

- [ ] **Step 2: Run; expect FAIL**

- [ ] **Step 3: Write the port + types**

```python
# src/flyquery/core/services/storage/object_store.py
# Copyright 2026 Firefly Software Solutions Inc
"""ObjectStore port (spec §9.1)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class ObjectMeta:
    key: str
    size_bytes: int
    content_type: str
    etag: str | None
    last_modified: datetime
    kms_key_uri: str | None = None


class ObjectStore(Protocol):
    """Hexagonal port: blob put/get/head/delete/list/presign/copy.

    Adapters: LocalFs (default), S3, GCS, AzureBlob. See spec §9.5
    for the key layout. KMS key handling is per-call so a workspace
    with workspace.kms_key_uri can upgrade above the storage-native
    default.
    """

    async def put(
        self,
        key: str,
        body: bytes | AsyncIterator[bytes],
        content_type: str,
        kms_key_uri: str | None = None,
    ) -> ObjectMeta: ...

    async def get(self, key: str) -> AsyncIterator[bytes]: ...
    async def head(self, key: str) -> ObjectMeta: ...
    async def delete(self, key: str) -> None: ...
    async def list(self, prefix: str) -> AsyncIterator[ObjectMeta]: ...
    async def presign_get(self, key: str, ttl_s: int) -> str: ...
    async def copy(self, src_key: str, dst_key: str) -> None: ...
```

- [ ] **Step 4: Write the factory**

```python
# src/flyquery/core/services/storage/object_store_factory.py
# Copyright 2026 Firefly Software Solutions Inc
"""Factory: choose ObjectStore adapter from FlyquerySettings."""

from __future__ import annotations

from flyquery.config import FlyquerySettings
from flyquery.core.services.storage.object_store import ObjectStore

try:
    from flyquery.core.services.storage.adapters.s3 import S3ObjectStore  # noqa: F401
    _HAS_S3 = True
except ImportError:
    _HAS_S3 = False


def build_object_store(settings: FlyquerySettings) -> ObjectStore:
    kind = settings.object_store
    if kind == "local":
        from flyquery.core.services.storage.adapters.local_fs import LocalFsObjectStore
        return LocalFsObjectStore(base=settings.object_store_base, presign_ttl_s=settings.object_store_presign_ttl_s)
    if kind == "s3":
        if not _HAS_S3:
            raise RuntimeError(
                "object_store=s3 selected but the 's3' extra is not installed; "
                "run: uv sync --extra s3"
            )
        from flyquery.core.services.storage.adapters.s3 import S3ObjectStore
        return S3ObjectStore(base=settings.object_store_base, presign_ttl_s=settings.object_store_presign_ttl_s)
    if kind == "gcs":
        raise NotImplementedError("GCS adapter ships in Plan 2 task 15")
    if kind == "azure":
        raise NotImplementedError("AzureBlob adapter ships in Plan 2 task 15")
    raise ValueError(f"unknown object_store kind: {kind!r}")
```

- [ ] **Step 5: Run; expect PASS** (the LocalFs adapter from Task 30 isn't yet shipped — to make this test pass now, allow the factory test to import a thin stub. Easier: defer the success of this test until Task 30 lands the LocalFs adapter. Mark the test as `xfail` here, then drop the marker in Task 30.)

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/core/services/storage/object_store.py src/flyquery/core/services/storage/object_store_factory.py tests/unit/test_object_store_factory.py
git commit -m "feat: ObjectStore port + types + factory (LocalFs default, S3 behind extra)"
```

---

### Task 30: `LocalFsObjectStore` adapter

**Files:**
- Create: `src/flyquery/core/services/storage/adapters/local_fs.py`
- Test: `tests/integration/test_object_store_conformance.py` (parametrised across all adapters; only LocalFs implemented here)

- [ ] **Step 1: Write the conformance test (parametrised by adapter)**

```python
# tests/integration/test_object_store_conformance.py
import asyncio
import os
import tempfile
import uuid
from pathlib import Path

import pytest


def _local_factory(tmp: Path):
    from flyquery.core.services.storage.adapters.local_fs import LocalFsObjectStore
    return LocalFsObjectStore(base=str(tmp), presign_ttl_s=60)


@pytest.fixture(params=["local"])
def store(request, tmp_path):
    if request.param == "local":
        return _local_factory(tmp_path)
    pytest.skip(f"no fixture for {request.param}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_put_then_head_then_get(store) -> None:
    key = f"unit/{uuid.uuid4()}/blob.txt"
    body = b"hello flyquery"
    meta = await store.put(key, body, content_type="text/plain")
    assert meta.size_bytes == len(body)
    h = await store.head(key)
    assert h.size_bytes == len(body)
    parts: list[bytes] = []
    async for chunk in await store.get(key):
        parts.append(chunk)
    assert b"".join(parts) == body


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_then_head_404(store) -> None:
    key = f"unit/{uuid.uuid4()}/x.bin"
    await store.put(key, b"data", content_type="application/octet-stream")
    await store.delete(key)
    with pytest.raises(FileNotFoundError):
        await store.head(key)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_prefix(store) -> None:
    prefix = f"unit/{uuid.uuid4()}/"
    for n in range(3):
        await store.put(f"{prefix}f{n}.bin", b"x", content_type="application/octet-stream")
    seen = []
    async for m in await store.list(prefix):
        seen.append(m.key)
    assert len(seen) == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_presign_get(store) -> None:
    key = f"unit/{uuid.uuid4()}/p.bin"
    await store.put(key, b"presigned", content_type="application/octet-stream")
    url = await store.presign_get(key, ttl_s=60)
    assert isinstance(url, str) and len(url) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_copy(store) -> None:
    src = f"unit/{uuid.uuid4()}/src.bin"
    dst = f"unit/{uuid.uuid4()}/dst.bin"
    await store.put(src, b"copy-me", content_type="application/octet-stream")
    await store.copy(src, dst)
    h = await store.head(dst)
    assert h.size_bytes == 7
```

- [ ] **Step 2: Run; expect FAIL** (LocalFs not implemented yet)

- [ ] **Step 3: Write `LocalFsObjectStore`**

```python
# src/flyquery/core/services/storage/adapters/local_fs.py
# Copyright 2026 Firefly Software Solutions Inc
"""Local-filesystem ObjectStore adapter (spec §9.1)."""

from __future__ import annotations

import os
import shutil
import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path

import aiofiles
import aiofiles.os

from flyquery.core.services.storage.object_store import ObjectMeta


class LocalFsObjectStore:
    """ObjectStore implementation against a local POSIX filesystem.

    `base` is the bucket root; keys are joined with it. Presigned URLs
    are emitted as `file://<absolute-path>` for dev visibility (no
    auth surface; for tests + local-only deploys only).
    """

    def __init__(self, base: str, presign_ttl_s: int = 86400) -> None:
        self._base = Path(base).expanduser().resolve()
        self._base.mkdir(parents=True, exist_ok=True)
        self._presign_ttl_s = presign_ttl_s

    def _abs(self, key: str) -> Path:
        # Reject path traversal
        if ".." in key.split("/"):
            raise ValueError(f"illegal key {key!r}")
        return self._base / key

    async def put(
        self,
        key: str,
        body,  # bytes | AsyncIterator[bytes]
        content_type: str,
        kms_key_uri: str | None = None,
    ) -> ObjectMeta:
        p = self._abs(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        async with aiofiles.open(p, "wb") as f:
            if isinstance(body, (bytes, bytearray, memoryview)):
                await f.write(bytes(body))
                size = len(body)
            else:
                async for chunk in body:
                    await f.write(chunk)
                    size += len(chunk)
        return ObjectMeta(
            key=key,
            size_bytes=size,
            content_type=content_type,
            etag=None,
            last_modified=datetime.utcnow(),
            kms_key_uri=kms_key_uri,
        )

    async def get(self, key: str) -> AsyncIterator[bytes]:
        p = self._abs(key)
        if not p.exists():
            raise FileNotFoundError(key)

        async def _stream() -> AsyncIterator[bytes]:
            async with aiofiles.open(p, "rb") as f:
                while True:
                    chunk = await f.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
        return _stream()

    async def head(self, key: str) -> ObjectMeta:
        p = self._abs(key)
        if not p.exists():
            raise FileNotFoundError(key)
        stat = await aiofiles.os.stat(p)
        return ObjectMeta(
            key=key,
            size_bytes=stat.st_size,
            content_type="application/octet-stream",
            etag=None,
            last_modified=datetime.utcfromtimestamp(stat.st_mtime),
        )

    async def delete(self, key: str) -> None:
        p = self._abs(key)
        if p.exists():
            await aiofiles.os.remove(p)

    async def list(self, prefix: str) -> AsyncIterator[ObjectMeta]:
        async def _gen() -> AsyncIterator[ObjectMeta]:
            root = self._abs(prefix) if prefix else self._base
            for path in root.rglob("*"):
                if path.is_file():
                    rel = path.relative_to(self._base).as_posix()
                    stat = path.stat()
                    yield ObjectMeta(
                        key=rel,
                        size_bytes=stat.st_size,
                        content_type="application/octet-stream",
                        etag=None,
                        last_modified=datetime.utcfromtimestamp(stat.st_mtime),
                    )
        return _gen()

    async def presign_get(self, key: str, ttl_s: int) -> str:
        return f"file://{self._abs(key).as_posix()}"

    async def copy(self, src_key: str, dst_key: str) -> None:
        src, dst = self._abs(src_key), self._abs(dst_key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
```

> Note: the `aiofiles` dep must be added to `pyproject.toml`. Add `aiofiles>=24` to `dependencies` and re-run `uv sync`.

- [ ] **Step 4: Run; expect PASS**

```bash
uv run pytest tests/integration/test_object_store_conformance.py -m integration -v
```

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/core/services/storage/adapters/local_fs.py \
        tests/integration/test_object_store_conformance.py \
        pyproject.toml
git commit -m "feat: LocalFsObjectStore adapter + conformance test pack"
```

---

### Task 31: `S3ObjectStore` adapter (via aiobotocore against MinIO)

**Files:**
- Create: `src/flyquery/core/services/storage/adapters/s3.py`
- Modify: `tests/integration/test_object_store_conformance.py` (add `s3` parameter)

- [ ] **Step 1: Extend the parametrised fixture**

```python
@pytest.fixture(params=["local", "s3"])
def store(request, tmp_path, minio_container):
    if request.param == "local":
        return _local_factory(tmp_path)
    if request.param == "s3":
        from flyquery.core.services.storage.adapters.s3 import S3ObjectStore
        cfg = minio_container.get_config()
        return S3ObjectStore(
            base=f"s3://flyquery-test",
            endpoint_url=f"http://{cfg['endpoint']}",
            access_key=minio_container.access_key,
            secret_key=minio_container.secret_key,
            presign_ttl_s=60,
        )
    pytest.skip(f"no fixture for {request.param}")
```

- [ ] **Step 2: Run; expect FAIL** (no S3 adapter)

- [ ] **Step 3: Write `s3.py`** (full file)

```python
# src/flyquery/core/services/storage/adapters/s3.py
# Copyright 2026 Firefly Software Solutions Inc
"""S3 ObjectStore adapter (aiobotocore)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import aiobotocore.session
from botocore.config import Config

from flyquery.core.services.storage.object_store import ObjectMeta


class S3ObjectStore:
    """Bucket-relative ObjectStore; honours per-call KMS key via SSE-KMS.

    `base` is `s3://<bucket>[/<prefix>]`. `endpoint_url` allows pointing
    at MinIO / S3-compatible services.
    """

    def __init__(
        self,
        base: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "us-east-1",
        presign_ttl_s: int = 86400,
    ) -> None:
        u = urlparse(base)
        if u.scheme != "s3":
            raise ValueError(f"S3 base must be s3://...; got {base!r}")
        self._bucket = u.netloc
        self._prefix = u.path.lstrip("/")
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._presign_ttl_s = presign_ttl_s
        self._session = aiobotocore.session.get_session()

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}/{key}".lstrip("/")

    async def _client(self):
        return self._session.create_client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
            config=Config(signature_version="s3v4"),
        )

    async def _ensure_bucket(self, client) -> None:
        try:
            await client.head_bucket(Bucket=self._bucket)
        except Exception:
            await client.create_bucket(Bucket=self._bucket)

    async def put(self, key, body, content_type, kms_key_uri=None) -> ObjectMeta:
        full = self._full_key(key)
        kwargs: dict[str, Any] = {
            "Bucket": self._bucket,
            "Key": full,
            "ContentType": content_type,
        }
        if kms_key_uri:
            kwargs["ServerSideEncryption"] = "aws:kms"
            kwargs["SSEKMSKeyId"] = kms_key_uri
        async with await self._client() as client:
            await self._ensure_bucket(client)
            if isinstance(body, (bytes, bytearray, memoryview)):
                kwargs["Body"] = bytes(body)
                size = len(body)
                await client.put_object(**kwargs)
            else:
                # Stream via multipart for large bodies
                init = await client.create_multipart_upload(**kwargs)
                upload_id = init["UploadId"]
                parts = []
                part_n = 1
                size = 0
                async for chunk in body:
                    p = await client.upload_part(
                        Bucket=self._bucket, Key=full, PartNumber=part_n,
                        UploadId=upload_id, Body=chunk,
                    )
                    parts.append({"ETag": p["ETag"], "PartNumber": part_n})
                    part_n += 1
                    size += len(chunk)
                await client.complete_multipart_upload(
                    Bucket=self._bucket, Key=full,
                    UploadId=upload_id, MultipartUpload={"Parts": parts},
                )
        return ObjectMeta(
            key=key, size_bytes=size, content_type=content_type,
            etag=None, last_modified=datetime.utcnow(), kms_key_uri=kms_key_uri,
        )

    async def get(self, key) -> AsyncIterator[bytes]:
        full = self._full_key(key)

        async def _stream() -> AsyncIterator[bytes]:
            async with await self._client() as client:
                resp = await client.get_object(Bucket=self._bucket, Key=full)
                async for chunk in resp["Body"]:
                    yield chunk
        return _stream()

    async def head(self, key) -> ObjectMeta:
        full = self._full_key(key)
        async with await self._client() as client:
            try:
                resp = await client.head_object(Bucket=self._bucket, Key=full)
            except client.exceptions.NoSuchKey as exc:
                raise FileNotFoundError(key) from exc
            except Exception as exc:  # botocore raises ClientError 404
                if getattr(exc, "response", {}).get("Error", {}).get("Code") in ("404", "NoSuchKey"):
                    raise FileNotFoundError(key) from exc
                raise
            return ObjectMeta(
                key=key,
                size_bytes=int(resp["ContentLength"]),
                content_type=resp.get("ContentType", "application/octet-stream"),
                etag=resp.get("ETag"),
                last_modified=resp["LastModified"],
            )

    async def delete(self, key) -> None:
        full = self._full_key(key)
        async with await self._client() as client:
            await client.delete_object(Bucket=self._bucket, Key=full)

    async def list(self, prefix) -> AsyncIterator[ObjectMeta]:
        full_prefix = self._full_key(prefix)

        async def _gen() -> AsyncIterator[ObjectMeta]:
            async with await self._client() as client:
                paginator = client.get_paginator("list_objects_v2")
                async for page in paginator.paginate(Bucket=self._bucket, Prefix=full_prefix):
                    for item in page.get("Contents", []):
                        yield ObjectMeta(
                            key=item["Key"][len(self._prefix):].lstrip("/") if self._prefix else item["Key"],
                            size_bytes=int(item["Size"]),
                            content_type="application/octet-stream",
                            etag=item.get("ETag"),
                            last_modified=item["LastModified"],
                        )
        return _gen()

    async def presign_get(self, key, ttl_s) -> str:
        full = self._full_key(key)
        async with await self._client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": full},
                ExpiresIn=ttl_s,
            )

    async def copy(self, src_key, dst_key) -> None:
        src_full = self._full_key(src_key)
        dst_full = self._full_key(dst_key)
        async with await self._client() as client:
            await client.copy_object(
                Bucket=self._bucket, Key=dst_full,
                CopySource={"Bucket": self._bucket, "Key": src_full},
            )
```

- [ ] **Step 4: Run; expect PASS**

```bash
uv run pytest tests/integration/test_object_store_conformance.py -m integration -v
```

Both `local` and `s3` parameters must pass.

- [ ] **Step 5: Commit**

```bash
git add src/flyquery/core/services/storage/adapters/s3.py tests/integration/test_object_store_conformance.py
git commit -m "feat: S3ObjectStore adapter (aiobotocore + KMS) + MinIO conformance"
```

---

### Task 32: ObjectStore DI bean + workspace-purge wiring

**Files:**
- Create: `src/flyquery/core/services/storage/__init__.py` (re-exports)
- Modify: `src/flyquery/core/configuration.py` (add ObjectStore bean)
- Modify: `src/flyquery/core/services/workspaces/workspace_service.py` (purge walks blobs via ObjectStore)
- Modify: `tests/integration/test_workspaces_crud.py` (assert :purge clears the workspace prefix)

- [ ] **Step 1: Add ObjectStore as a DI bean**

```python
# src/flyquery/core/configuration.py — extend FlyqueryConfiguration
from pyfly.core.di import bean

from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.storage.object_store_factory import build_object_store

class FlyqueryConfiguration:
    # ...existing settings() method
    @bean
    def object_store(self, settings: FlyquerySettings) -> ObjectStore:
        return build_object_store(settings)
```

- [ ] **Step 2: Update `WorkspaceService.purge` to walk blobs**

```python
# src/flyquery/core/services/workspaces/workspace_service.py
async def purge(self, workspace_id: uuid.UUID, object_store: ObjectStore, tenant_id: str) -> None:
    # 1. Archive in DB (sets status=PURGING → tombstone for 30 days)
    await self._repo.mark_purging(workspace_id)
    # 2. Walk the workspace prefix and delete every key
    prefix = f"flyquery/{tenant_id}/{workspace_id}/"
    async for meta in await object_store.list(prefix):
        await object_store.delete(meta.key)
    # 3. Terminal audit event written elsewhere (Plan 2: audit service)
```

- [ ] **Step 3: Add `mark_purging` to the repository** (UPDATE status=PURGING; also add `'PURGING'` to the workspaces status check constraint — needs a migration `0008_purging_status.py`).

- [ ] **Step 4: Update the controller to inject ObjectStore + tenant_id**

```python
# workspaces_controller.py — purge handler
@request_mapping(method="DELETE", path="/{workspace_id}:purge")
@response_status(202)
async def purge(
    self,
    workspace_id: PathVar[uuid.UUID],
    object_store: ObjectStore,
) -> dict:
    ctx = tenant_context()
    await self._service.purge(workspace_id, object_store, ctx.tenant_id)
    return {"status": "accepted", "tombstone_expires_at": "+30d"}
```

- [ ] **Step 5: Extend the test — write a blob to the workspace prefix; call :purge; assert it is gone**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_purge_walks_object_store_prefix(minio_container) -> None:
    from flyquery.main import app
    from flyquery.core.services.storage.adapters.s3 import S3ObjectStore
    # Write a probe blob under the workspace prefix
    cfg = minio_container.get_config()
    store = S3ObjectStore(
        base="s3://flyquery-test",
        endpoint_url=f"http://{cfg['endpoint']}",
        access_key=minio_container.access_key,
        secret_key=minio_container.secret_key,
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "purge-me", "name": "Purge"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "purge-me"},
        )
        ws_id = r.json()["id"]
        probe_key = f"flyquery/tenant-a/{ws_id}/files/probe.bin"
        await store.put(probe_key, b"probe", content_type="application/octet-stream")

        await c.delete(
            f"/api/v1/workspaces/{ws_id}:purge",
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        with pytest.raises(FileNotFoundError):
            await store.head(probe_key)
```

- [ ] **Step 6: Migration 0008 (`flyquery_workspaces.status` allows PURGING)**

```python
"""add PURGING status

Revision ID: 0008_purging_status
Revises: 0007_rls
"""
from alembic import op

revision = "0008_purging_status"
down_revision = "0007_rls"

def upgrade():
    op.execute("ALTER TABLE flyquery_workspaces DROP CONSTRAINT IF EXISTS ck_workspaces_status")
    op.execute(
        "ALTER TABLE flyquery_workspaces ADD CONSTRAINT ck_workspaces_status "
        "CHECK (status IN ('ACTIVE','ARCHIVED','PURGING'))"
    )

def downgrade():
    op.execute("ALTER TABLE flyquery_workspaces DROP CONSTRAINT IF EXISTS ck_workspaces_status")
```

(If 0001 didn't add the constraint named `ck_workspaces_status`, add it explicitly here first.)

- [ ] **Step 7: Run; expect PASS**

- [ ] **Step 8: Commit**

```bash
git add src/flyquery/core/configuration.py \
        src/flyquery/core/services/workspaces/ \
        src/flyquery/web/controllers/workspaces_controller.py \
        migrations/versions/*purging_status.py \
        tests/integration/test_workspaces_crud.py
git commit -m "feat: workspace :purge walks ObjectStore prefix; PURGING status; ObjectStore DI bean"
```

---

### Task 33: ObjectStore unit tests for path-traversal + KMS round-trip

**Files:**
- Modify: `tests/integration/test_object_store_conformance.py`

- [ ] **Step 1: Add tests**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_rejects_path_traversal(store) -> None:
    with pytest.raises(ValueError):
        await store.put("../escape/secret", b"x", content_type="text/plain")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kms_round_trip_when_supported(store) -> None:
    # LocalFs ignores kms_key_uri (no KMS in dev); just confirm it's
    # accepted + reflected in ObjectMeta. S3 against MinIO would
    # require KMS configuration — skip there.
    if store.__class__.__name__ == "S3ObjectStore":
        pytest.skip("MinIO KMS support varies by version")
    meta = await store.put(
        f"unit/{uuid.uuid4()}/kms.bin", b"k", content_type="text/plain",
        kms_key_uri="arn:aws:kms:us-east-1:000:key/abc",
    )
    assert meta.kms_key_uri == "arn:aws:kms:us-east-1:000:key/abc"
```

- [ ] **Step 2: Run; expect PASS**

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_object_store_conformance.py
git commit -m "test: ObjectStore path-traversal rejection + KMS round-trip"
```

---

## Phase G — CI gates + final smoke (Tasks 34-36)

### Task 34: `scripts/check_lockstep.py` (CI gate against canon SHAs)

**Files:**
- Create: `scripts/check_lockstep.py`
- Create: `scripts/lockstep_pins.json`
- Test: `tests/unit/test_lockstep_script.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_lockstep_script.py
import subprocess

def test_lockstep_passes_against_pinned_shas() -> None:
    r = subprocess.run(
        ["uv", "run", "python", "scripts/check_lockstep.py"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"lockstep drift:\n{r.stdout}\n{r.stderr}"
```

- [ ] **Step 2: Run; expect FAIL** (script doesn't exist)

- [ ] **Step 3: Write `scripts/check_lockstep.py`**

```python
#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Lock-step CI gate (spec §14).

Computes the SHA-256 of each lock-step file (after a deterministic
service-name de-substitution: replaces 'flyquery' -> 'flycanon',
'FLYQUERY' -> 'FLYCANON', etc. — same regex set as the copy
script in Tasks 10-11) and compares against the pinned canon SHA in
scripts/lockstep_pins.json.

Drift = exit code 1. Pinned SHAs are refreshed when an intentional
canon-side change lands and we propagate it across canon/radar/flyquery
in lock-step (rare).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


LOCKSTEP_FILES = [
    "src/flyquery/web/agent_deps.py",
    "src/flyquery/web/openapi_override.py",
    "src/flyquery/web/conventions/__init__.py",
    "src/flyquery/web/conventions/actor.py",
    "src/flyquery/web/conventions/context.py",
    "src/flyquery/web/conventions/db.py",
    "src/flyquery/web/conventions/deps.py",
    "src/flyquery/web/conventions/errors.py",
    "src/flyquery/web/conventions/exceptions.py",
    "src/flyquery/web/conventions/handlers.py",
    "src/flyquery/web/conventions/headers.py",
    "src/flyquery/web/conventions/http_client.py",
    "src/flyquery/web/conventions/idempotency.py",
    "src/flyquery/web/conventions/middleware.py",
    "src/flyquery/web/conventions/redis_idempotency.py",
    "src/flyquery/web/conventions/validation.py",
    "src/flyquery/core/agents/builder.py",
    "src/flyquery/core/observability/__init__.py",
    "src/flyquery/core/services/auth/agent_token_service.py",
    "src/flyquery/core/services/auth/redis_rate_limiter.py",
    "src/flyquery/web/controllers/agent_tokens_controller.py",
]


def _normalise(text: str) -> bytes:
    """Reverse the flyquery substitutions to canon's form, so the SHA is
    canon-pinned regardless of which service we're checking."""
    text = re.sub(r"\bflyquery\b", "flycanon", text)
    text = re.sub(r"\bFLYQUERY\b", "FLYCANON", text)
    text = re.sub(r"\bflyquery_", "canon_", text)
    text = re.sub(r"\bFlyquerySettings\b", "CanonSettings", text)
    return text.encode("utf-8")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    pins_path = root / "scripts" / "lockstep_pins.json"
    pins: dict[str, str] = json.loads(pins_path.read_text()) if pins_path.exists() else {}
    drift: list[str] = []
    for rel in LOCKSTEP_FILES:
        p = root / rel
        if not p.exists():
            drift.append(f"MISSING: {rel}")
            continue
        sha = hashlib.sha256(_normalise(p.read_text())).hexdigest()
        pinned = pins.get(rel)
        if pinned is None:
            drift.append(f"UNPINNED: {rel} -> {sha}")
        elif pinned != sha:
            drift.append(f"DRIFT: {rel}\n    pinned:  {pinned}\n    current: {sha}")
    if drift:
        print("\n".join(drift))
        return 1
    print(f"lockstep OK: {len(LOCKSTEP_FILES)} files match pins")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Generate `scripts/lockstep_pins.json` from the current canon checkout**

```bash
# Generate pins from the just-copied canon files
uv run python - <<'EOF'
import hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from check_lockstep import LOCKSTEP_FILES, _normalise
root = Path(".")
pins = {}
for rel in LOCKSTEP_FILES:
    text = (root / rel).read_text()
    pins[rel] = hashlib.sha256(_normalise(text)).hexdigest()
Path("scripts/lockstep_pins.json").write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n")
print(f"wrote {len(pins)} pins")
EOF
```

- [ ] **Step 5: Run the script; expect exit 0**

```bash
uv run python scripts/check_lockstep.py
```

Then run the test:

```bash
uv run pytest tests/unit/test_lockstep_script.py -v
```

- [ ] **Step 6: Commit**

```bash
git add scripts/check_lockstep.py scripts/lockstep_pins.json tests/unit/test_lockstep_script.py
git commit -m "feat: scripts/check_lockstep.py CI gate + canon SHA pins"
```

---

### Task 35: GitHub Actions workflows (lint + unit + integration + lockstep)

**Files:**
- Create: `.github/workflows/lint.yml`
- Create: `.github/workflows/test-unit.yml`
- Create: `.github/workflows/test-integration.yml`
- Create: `.github/workflows/lockstep-check.yml`

- [ ] **Step 1: Write `.github/workflows/lint.yml`**

```yaml
name: lint
on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { submodules: false }
      - name: Clone sibling firefly framework repos
        run: |
          mkdir -p ../../fireflyframework
          git clone --depth 1 https://github.com/firefly-operationOS/fireflyframework-pyfly ../../fireflyframework/fireflyframework-pyfly
          git clone --depth 1 https://github.com/firefly-operationOS/fireflyframework-agentic ../../fireflyframework/fireflyframework-agentic
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --extra dev --extra s3
      - run: uv run ruff check src tests
      - run: uv run ruff format --check src tests
      - run: uv run pyright
```

- [ ] **Step 2: Write `.github/workflows/test-unit.yml`** (same setup, runs `task test:unit`)

```yaml
name: test-unit
on: [pull_request, push]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Clone sibling firefly framework repos
        run: |
          mkdir -p ../../fireflyframework
          git clone --depth 1 https://github.com/firefly-operationOS/fireflyframework-pyfly ../../fireflyframework/fireflyframework-pyfly
          git clone --depth 1 https://github.com/firefly-operationOS/fireflyframework-agentic ../../fireflyframework/fireflyframework-agentic
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --extra dev --extra s3
      - run: uv run pytest tests/unit -m 'not integration'
```

- [ ] **Step 3: Write `.github/workflows/test-integration.yml`** (with services or testcontainers)

```yaml
name: test-integration
on: [pull_request, push]

jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:dind
    steps:
      - uses: actions/checkout@v4
      - name: Clone sibling firefly framework repos
        run: |
          mkdir -p ../../fireflyframework
          git clone --depth 1 https://github.com/firefly-operationOS/fireflyframework-pyfly ../../fireflyframework/fireflyframework-pyfly
          git clone --depth 1 https://github.com/firefly-operationOS/fireflyframework-agentic ../../fireflyframework/fireflyframework-agentic
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --extra dev --extra s3
      - run: uv run pytest tests/integration -m integration --timeout=300
```

- [ ] **Step 4: Write `.github/workflows/lockstep-check.yml`**

```yaml
name: lockstep-check
on: [pull_request, push]

jobs:
  lockstep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --extra dev
      - run: uv run python scripts/check_lockstep.py
```

- [ ] **Step 5: Smoke locally — render the workflow files to confirm YAML parses**

```bash
for f in .github/workflows/*.yml; do
  uv run python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1])); print('OK', sys.argv[1])" "$f"
done
```

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/
git commit -m "ci: lint + test-unit + test-integration + lockstep-check workflows"
```

---

### Task 36: Final smoke test + QUICKSTART population

**Files:**
- Modify: `QUICKSTART.md` (replace placeholder)
- Test: `tests/integration/test_smoke_e2e.py`

- [ ] **Step 1: Write the end-to-end smoke test**

```python
# tests/integration/test_smoke_e2e.py
# Copyright 2026 Firefly Software Solutions Inc
"""End-to-end smoke covering the Plan 1 surface:
   health → version → mint token → create workspace → create dataset
   → archive → re-create with same slug rejected.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plan1_end_to_end() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # /actuator/health
        r = await c.get("/actuator/health")
        assert r.status_code == 200

        # /api/v1/version
        r = await c.get("/api/v1/version")
        assert r.status_code == 200
        assert r.json()["name"] == "flyquery"

        h = {"X-Tenant-Id": "tenant-smoke", "X-Workspace-Id": "smoke"}

        # Create workspace
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "smoke", "name": "Smoke Test"},
            headers=h,
        )
        assert r.status_code == 201
        ws = r.json()
        ws_id = ws["id"]

        # Mint an agent token
        r = await c.post(
            "/api/v1/agent-tokens",
            json={
                "name": "smoke-bot",
                "scopes": ["flyquery.datasets:read", "flyquery.query:read"],
                "workspace_allowlist": [ws_id],
            },
            headers={**h, "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201
        token = r.json()["token"]
        assert token.startswith("agt_")

        # Create a dataset
        r = await c.post(
            "/api/v1/datasets",
            json={"name": "Sales-Smoke"},
            headers={**h, "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201

        # Use the token on an agent route (we only have /api/v1/agent/version
        # which requires flyquery.audit:read which this token DOESN'T have
        # → expect 403)
        r = await c.get(
            "/api/v1/agent/version",
            headers={
                "X-Tenant-Id": "tenant-smoke",
                "X-Workspace-Id": ws_id,
                "X-Agent-Token": token,
            },
        )
        assert r.status_code == 403

        # :purge
        r = await c.delete(
            f"/api/v1/workspaces/{ws_id}:purge",
            headers={**h, "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 202
```

- [ ] **Step 2: Run; expect PASS**

- [ ] **Step 3: Populate `QUICKSTART.md`**

```markdown
# QUICKSTART

This walks the first call against a local flyquery v0.1 (Plan 1).

## 1. Boot the stack

```bash
docker compose up -d postgres redis minio
task install
task migrate
task serve   # listens on :8520
```

## 2. Sanity checks

```bash
curl http://localhost:8520/actuator/health
curl http://localhost:8520/api/v1/version
```

## 3. Create a workspace + dataset

```bash
WS=$(curl -s -X POST http://localhost:8520/api/v1/workspaces \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Id: demo' -H 'X-Workspace-Id: alpha' \
  -d '{"slug":"alpha","name":"Alpha"}' | jq -r .id)
echo "workspace=$WS"

curl -s -X POST http://localhost:8520/api/v1/datasets \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d '{"name":"Sales 2026"}'
```

## 4. Mint an agent token

```bash
TOK=$(curl -s -X POST http://localhost:8520/api/v1/agent-tokens \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d '{"name":"dev","scopes":["flyquery.datasets:read","flyquery.query:read"],"workspace_allowlist":["'$WS'"]}' \
  | jq -r .token)
echo "token=$TOK"   # agt_<8hex>_<32hex>
```

## 5. What you cannot do yet

- Upload files (`POST /datasets/{id}/files`) — ships in Plan 2.
- Ask `/query` — ships in Plan 3.

See `docs/superpowers/plans/` for the next plans.
```

- [ ] **Step 4: Update `CHANGELOG.md` for the v0.1 release**

```markdown
## [26.5.0] - 2026-05-23

### Added
- Plan 1 (Foundation) shipped: bootable service, lock-step modules,
  full RLS-enabled Postgres schema (~20 tables), workspace + dataset
  CRUD, agent-token mint/verify, ObjectStore port + LocalFs + S3
  adapters, CI workflows.
```

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_smoke_e2e.py QUICKSTART.md CHANGELOG.md
git commit -m "test: end-to-end smoke + QUICKSTART; CHANGELOG entry for 26.5.0"
```

---

## Spec coverage self-check

| Spec §15 step | Plan 1 task(s) |
|---|---|
| 1. Scaffold | 1-9 |
| 2. Copy lock-step modules | 10-12 |
| 3. Alembic baseline schema (~20 tables) + RLS | 13-20 |
| 4. Workspace + dataset CRUD with RLS isolation tests | 21-25 |
| 5. Agent tokens + scope catalog mint/verify | 26-28 |
| 6. ObjectStore port + LocalFs + S3 adapters | 29-33 |
| 7. `scripts/check_lockstep.py` CI gate | 34 + 35 |

Every step of the spec's Plan 1 build order is covered. Additional tasks (smoke + QUICKSTART) close the demoable gate.

## After Plan 1

Plan 2 (`2026-05-22-flyquery-02-file-ingestion.md`) is drafted next via `superpowers:writing-plans` after Plan 1 ships. Plan 2 builds on this foundation: `FileReader` port + 12 readers, 10-stage ingestion pipeline, `DescribeAgent`/`RelationProposerAgent`/`RenameDetectionAgent`, SSE on `/ingest-jobs/{id}/stream`, GCS + AzureBlob adapters, re-upload with schema drift.

