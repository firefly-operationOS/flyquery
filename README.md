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
