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
