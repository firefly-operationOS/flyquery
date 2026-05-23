# flyquery

> Operational Structured-Data Intelligence (upload-driven). Multi-tenant
> ingestion + Text-to-SQL over user-uploaded structured files
> (CSV / TSV / XLSX / XLS / ODS / JSON / JSONL / Parquet / Avro / ORC /
> Arrow / Feather + .gz/.zip/.bz2). Materialises uploads to Parquet on
> object storage; indexes a long-lived schema knowledge base; answers
> natural-language questions via a multi-agent pipeline. Part of
> Firefly OperationOS.

## Status

v0 complete (Plans 1-4: Foundation, Ingestion, Query Pipeline, Packaging).
The service boots, supports workspace + dataset CRUD with RLS, ingests
uploads in 10 stages, answers natural-language questions via a 4-agent
Text-to-SQL pipeline, and ships OpenAPI-generated Python + Java SDKs (see
`docs/superpowers/plans/`).

## Quick start

See [`QUICKSTART.md`](./QUICKSTART.md).

## Design

See [`docs/superpowers/specs/2026-05-22-flyquery-design.md`](./docs/superpowers/specs/2026-05-22-flyquery-design.md).

## Documentation

- [`docs/architecture.md`](./docs/architecture.md) — system design, pipelines, hexagonal ports
- [`docs/api-reference.md`](./docs/api-reference.md) — REST surface (user-tier + agent-tier) + scopes
- [`docs/ingestion.md`](./docs/ingestion.md) — 10-stage upload pipeline + job kinds
- [`docs/file-formats.md`](./docs/file-formats.md) — per-format reader matrix
- [`docs/semantic-layer.md`](./docs/semantic-layer.md) — MetricFlow YAML + compilation
- [`docs/payload-reference.md`](./docs/payload-reference.md) — DTO catalog
- [`docs/security.md`](./docs/security.md) — RLS, tokens, AST firewall, PII policy
- [`docs/deployment.md`](./docs/deployment.md) — ops runbook
- [`docs/firefly-intelligence-system.md`](./docs/firefly-intelligence-system.md) — flycanon + flyradar + flyquery cross-narrative

SDKs: [`sdks/python/`](./sdks/python/) (Apache-2.0, `flyquery-sdk` on PyPI) and [`sdks/java/`](./sdks/java/) (Apache-2.0, `io.firefly:flyquery-sdk` Maven).

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
