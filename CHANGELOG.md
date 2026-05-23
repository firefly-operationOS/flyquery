# Changelog

All notable changes to flyquery are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project uses [CalVer](https://calver.org/) (YY.MM.PP) per the
Firefly Framework convention (memory: `firefly_uses_calver`).

## [26.5.1] - 2026-05-23

### Added
- Plan 3 (Query Pipeline) shipped
- Examples + Glossary CRUD with auto-promotion (AGENT_LEARNED → PROPOSED)
- Semantic layer: MetricFlow-shape YAML + compiler + history versioning
- Hybrid retriever (BM25 + pgvector + RRF) + cross-encoder reranker over schema KB
- 4-agent query pipeline: GroundingAgent → GenerationAgent → CriticAgent → ExplainerAgent
- AST classifier + ScopeGuard (sqlglot + table-kind enforcement + dataset allowlist)
- DuckDB executor (in-process, ATTACH parquet snapshots, row_cap+1 overflow)
- POST /api/v1/query + :explain + :validate + /query/stream (SSE with clarification frame)
- Conversation memory with drill-down (prior executed_sql + table_qnames + snapshot_pins)
- POST /api/v1/sql:execute behind workspace.allow_direct_sql
- POST /api/v1/tables:derive + DML on DERIVED tables (read-modify-write Parquet)
- Agent-tier mirrors: /api/v1/agent/{query,sql:execute,examples}

## [26.5.0] - 2026-05-23

### Added
- Plan 1 (Foundation) shipped: bootable service, lock-step modules,
  full RLS-enabled Postgres schema (~20 tables), workspace + dataset
  CRUD, agent-token mint/verify, ObjectStore port + LocalFs + S3
  adapters, CI workflows.

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
