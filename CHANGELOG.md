# Changelog

All notable changes to flyquery are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project uses [CalVer](https://calver.org/) (YY.MM.PP) per the
Firefly Framework convention (memory: `firefly_uses_calver`).

## [26.5.4] - 2026-05-23

### Added

- `config.py`: 13 new env vars that docs already referenced but were missing
  (`FLYQUERY_CONV_TTL_DAYS`, `FLYQUERY_CONV_HISTORY_TURNS`,
  `FLYQUERY_CONV_SUMMARY_MAX_TOKENS`, `FLYQUERY_CONV_SUMMARY_INTERVAL`,
  `FLYQUERY_AUTOLEARN_ENABLED`, `FLYQUERY_INGEST_HEARTBEAT_S`,
  `FLYQUERY_INGEST_MAX_ATTEMPTS`, `FLYQUERY_KAFKA_BOOTSTRAP_SERVERS`,
  `FLYQUERY_EMBEDDING_RATE_LIMIT_RPM`, `FLYQUERY_PII_REGEX_PATTERNS_PATH`,
  `FLYQUERY_PRESIDIO_SPACY_MODEL`, `FLYQUERY_OTEL_ENDPOINT`,
  `FLYQUERY_CONV_SUMMARY_INTERVAL`)
- `sdks/java/LICENSE` + `sdks/python/LICENSE`: Apache 2.0 (SDKs are public)
- `sdks/java/README.md`: updated for Java 25 + Spring Boot 3.5.9 + WebFlux coords

### Changed

- **Java SDK regenerated**: `library=webclient` (Spring WebFlux reactive client),
  package `com.firefly.flyquery` (was `io.firefly.flyquery`),
  groupId `com.firefly` (was `io.firefly`), Java 25, Spring Boot 3.5.9
- `Taskfile.yml sdk:java` task updated accordingly
- `.github/workflows/publish-sdk-java.yml`: java-version 21 → 25
- `sdks/python/pyproject.toml`: license `Proprietary` → `Apache-2.0`
- `sdks/java/pom.xml`: full rewrite with Spring Boot 3.5.9 parent, Java 25 compiler
- `README.md`: "Why this service exists" rewritten; new "Why not part of flycanon?"
  section; full 5-step copy-pasteable quickstart; "Status" section removed;
  "What ships in v0" → "Capabilities" (present tense)
- `openapi.json`: re-snapshotted at version 26.5.4

### Fixed

- `docs/conversations.md`: removed non-existent SSE turn + agent/conversations
  endpoints; marked `GET /conversations/{id}/turns` as v1+; TTL default 30d→90d
- `docs/billing.md`: marked `/api/v1/billing` as v1+ (not in current release);
  replaced fake curl example with real DB query
- `docs/stats.md`: marked `/api/v1/stats` as v1+ (not in current release)
- `docs/async-ingest.md`: heartbeat + stale-job recovery marked v1+ (not yet
  implemented in IngestWorker)
- `docs/auto-learning.md`: fixed grammatical error in FLYQUERY_AUTOLEARN_ENABLED
- `docs/operations-runbook.md`: clarified EMBEDDING_RATE_LIMIT_RPM is defined
  but rate-limit enforcement is v1+
- `src/flyquery/core/services/ingestion/stages/publish.py`: removed stale
  "stub in Phase B" comment (EDA publish is fully implemented)
- `src/flyquery/core/services/ingestion/workers.py`: removed stale
  "(Phase D/E; NotImplementedError for now)" comments
- `src/flyquery/core/services/query/query_service.py`: clarified session-borrowing
  rationale in `_table_kinds_by_name`
- Copyright headers added to all `__init__.py` and new test files

### Attribution

Released by ancongui.

---

## [26.5.3] - 2026-05-23

### Added

- Logo asset (`docs/assets/logo.png`) — "tabular intelligence" mark
- README.md polished to canon depth: logo, badges, architecture summary, nav
  table, status matrix for Plans 1–4, local dev and test instructions
- `docs/README.md` — navigation hub with reading paths by user intent and
  full document catalogue
- `docs/pipeline.md` — upload + 10-stage ingestion and query pipeline
  end-to-end with ASCII diagrams and mode coupling (sync vs async via EDA)
- `docs/async-ingest.md` — IngestWorker lifecycle, 5 job kinds, cooperative
  cancel, retry, dead-letter, sequencing guarantees
- `docs/eda-events.md` — `flyquery.ingest` (IngestRequested) and
  `flyquery.schema` (SchemaUpdated) event schemas, durable Postgres outbox,
  consumer guide
- `docs/conversations.md` — multi-turn query memory, drill-down semantics,
  NL→delta-SQL examples, snapshot pinning, API surface
- `docs/prompts.md` — catalog of 7 agent prompts with verbatim instruction
  text, input shape, and output schema (from source)
- `docs/auto-learning.md` — PROPOSED → APPROVED example cycle, eligibility
  criteria, operator approval flow, v1 roadmap
- `docs/pii.md` — 3 scanners (regex/Presidio/disabled), 3 policies
  (warn/redact/reject), ordering guarantee, late-tag flip, custom regex
- `docs/operations-runbook.md` — cold start, daily checks, common errors,
  GDPR purge, key rotation, backup/restore, scaling, incident template
- `docs/troubleshooting.md` — symptom → root cause → fix for 13 common issues
- `docs/deployment-topology.md` — single-node, multi-node, HA ASCII diagrams
  and port reference
- `docs/cicd.md` — 5 workflows, tag-triggered releases, branch protection,
  concurrent worker considerations, required secrets
- `docs/concurrency.md` — AsyncSession scoping, RLS GUC binding, EDA worker
  concurrency, DuckDB per-request isolation, ObjectStore async patterns
- `docs/consumers.md` — SDK patterns (Python + Java + curl), agent-token
  model, idempotency, error handling, 5 integration recipes
- `docs/integration-with-firefly-os.md` — three-pillar narrative,
  flyradar↔flyquery and flycanon↔flyquery integration patterns
- `docs/glossary.md` — full project terminology dictionary (resource
  hierarchy, query pipeline, ingestion, technical terms)
- `docs/scale-and-performance.md` — throughput numbers, bottlenecks, tuning
  knobs, capacity planning
- `docs/billing.md` — per-query + per-ingest LLM cost, `flyquery_cost_events`
  schema, billing API, v0 observe-only + v1 enforcement roadmap
- `docs/stats.md` — `GET /api/v1/stats` response schema, fields reference,
  dashboard usage patterns
- `docs/quality.md` — full testing strategy: unit, integration, conformance,
  parser fixtures, pipeline tests, LLM-gated, lock-step drift gate

### Changed

- `docs/security.md` renamed to `docs/security-model.md` (canon convention)
- Cross-references in `docs/firefly-intelligence-system.md` updated
- `docs/deployment.md` cross-links to `docs/deployment-topology.md`
- README version badge updated to 26.5.3

---

## [26.5.2] - 2026-05-23

### Added
- Plan 4 (Packaging) shipped
- `openapi.json` committed snapshot + drift gate (`task openapi-snapshot`)
- Python SDK auto-generated (`sdks/python/`, package `flyquery-sdk`, asyncio library)
- Java SDK auto-generated (`sdks/java/`, `io.firefly:flyquery-sdk:26.5.2`, okhttp-gson)
- Full `docs/` set: architecture, api-reference, ingestion, file-formats, semantic-layer, payload-reference, security, deployment, firefly-intelligence-system
- CI: `publish-sdk-python` + `publish-sdk-java` workflows (tag-triggered)

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
