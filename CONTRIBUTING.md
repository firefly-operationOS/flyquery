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
