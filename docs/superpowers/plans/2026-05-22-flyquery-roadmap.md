# flyquery Implementation Roadmap

> Four successor plans turn the spec (`docs/superpowers/specs/2026-05-22-flyquery-design.md`) into a shippable v0; six v1+ items follow once v0 ships. Each plan produces working, testable software on its own and unlocks the next plan. Plans are written one at a time so each draws on the real-world signal from its predecessor's execution.

## v0 sequencing

| # | Plan | Phases (from spec §15) | Shipped capability | File |
| --- | --- | --- | --- | --- |
| 1 | **Foundation** | 1, 2, 3, 4, 5, 6, 7 | Bootable service. Repo published. Lock-step auth + RLS in place. Full Alembic schema (~20 tables: workspaces, datasets, files, tables, snapshots, changes, schema_objects, relations, semantic_*, glossary, examples, queries, query_results, conversations*, agent_tokens, audit, cost, ingest_jobs, ingest_events). Workspace + dataset CRUD with RLS integration tests. Agent tokens + flyquery scope catalog. `ObjectStore` port + LocalFs + S3 adapters. `scripts/check_lockstep.py` CI gate. | [`2026-05-22-flyquery-01-foundation.md`](./2026-05-22-flyquery-01-foundation.md) *(to be drafted via `superpowers:writing-plans`)* |
| 2 | **File ingestion** | 8, 9, 10, 11, 12, 13, 14, 15 | `FileReader` port + 12 format readers + 3 compression handlers. 10-stage pipeline (receive → parse → reconcile → sample → profile → relation discovery → describe → PII tag → embed → publish). SSE on `/ingest-jobs/{id}/stream`. `DescribeAgent`, `RelationProposerAgent`, `RenameDetectionAgent`. Re-upload with schema drift + annotation transplant. GCS + AzureBlob adapters. End-to-end demo: upload a Northwind-style fixture (`orders.csv` + `customers.csv` + `products.xlsx` + a JSON export) and observe the schema KB populate with descriptions, samples, profiles, embeddings, and AI-proposed joins. | _TBD after Plan 1_ |
| 3 | **Query pipeline** | 16, 17, 18, 19, 20, 21, 22 | Examples + glossary CRUD + `AGENT_LEARNED` auto-promotion. Semantic-layer compiler (MetricFlow YAML → DuckDB SQL). Multi-agent query pipeline (Grounding → Generation → DuckDB Executor → Critic → Explainer) with cross-encoder reranker on by default. Hybrid clarification frame + drill-down conversation context. SSE `/query/stream`. `/sql:execute` behind `workspace.allow_direct_sql`. `/tables:derive` + DML on derived tables. Both user-tier and agent-tier surfaces. | _TBD after Plan 2_ |
| 4 | **Packaging** | 23, 24, 25 | Python + Java SDKs generated from OpenAPI. Full `docs/` set (architecture, api-reference, ingestion, file-formats, semantic-layer, security, deployment, payload-reference). CI workflows mirroring canon (lint, test-unit, test-integration, build, publish-sdk, lockstep-check). | _TBD after Plan 3_ |

## v0 cut-line

Plans **1 + 2 + 3 + 4** constitute the v0 demoable cut. Unlike the previous (now superseded) plan structure, there is no parallel-optional plan: all four are required.

## v1+ follow-ups (individually shippable)

| Item | Capability | Notes |
| --- | --- | --- |
| 26 | flydesk-frontend `/flyquery` route | Drag-drop upload, dataset browser, chat-style query, SSE pipeline view, result viewer + chart hint render |
| 27 | MCP server | File-attach + `/query` natively from Claude / agent IDEs |
| 28 | Cost enforcement | Activate `rate_limit_rpm` + per-workspace monthly budget; soft-warn at 80%, hard reject at 100% with RFC 7807 error |
| 29 | Per-workspace KMS/CMEK plumbing | Past storage-native default — KEK/DEK envelope so a key-revocation makes a tenant's data unreadable (GDPR-safe) |
| 30 | `GovernanceClassifierAgent` | Sensitivity / retention class for regulated industries |
| 31 | `/tables:explode` | Nested-JSON array → new table |
| 32 | Drift watchdog | Scheduled REPARSE jobs when an external process refreshes a file under a known URI |

## How we run the sequence

For each plan in order:

1. The plan is fully drafted with bite-sized TDD tasks (`2026-05-22-flyquery-NN-<name>.md`) via `superpowers:writing-plans`.
2. The plan is executed via `superpowers:subagent-driven-development` (one fresh subagent per task) or `superpowers:executing-plans` (inline with checkpoints).
3. Execution surfaces drift between spec and reality. The next plan is drafted after the previous one lands so it reflects what we actually learned.
4. Each plan ends at a commit that boots, passes its tests, and is demoable to a stakeholder.

## Cross-cutting invariants enforced in every plan

- Every new table carries `(tenant_id, workspace_id)` columns and an RLS policy. New migrations carry an isolation test before they're allowed to merge.
- Every new module that mirrors a canon/radar module must be byte-equivalent (except for service-name substitutions). `scripts/check_lockstep.py` (Plan 1, Task 7) is the CI gate.
- Every new agent is built via `core/agents/builder.py:build_agent` with `auto_register=False`, structured `output_type`, no tools, fresh per call.
- Every new agent-tier endpoint carries `X-Agent-Token`, mandatory `Idempotency-Key` on writes, and a scope from the catalog in spec §7.3.
- Every new endpoint that runs SQL passes the DuckDB `ast_classify()` AND the scope check AND (for writes) confirms the target `table.kind=DERIVED`.
- Every cost-incurring operation records to `flyquery_cost_events`; `result.usage()` not `stream.usage()` (memory: `agent_test_mocking`).
- Every `ObjectStore` adapter passes the shared conformance pack before merging.
- Every `FileReader` adds a golden + 3-5 edge-case tests under `tests/integration/parsers/` before merging.
- Commits are frequent (per task) and pass `task lint test:unit` before push.

## Diff vs. the original 2026-05-22 roadmap

The original roadmap had 6 plans:

| # (old) | Plan | Fate |
| --- | --- | --- |
| 1 | Foundation | **Kept** (renumbered as Plan 1; tasks adjusted for upload-only model) |
| 2 | Ingestion pipeline (over Postgres DBs) | **Replaced** by Plan 2 "File ingestion" — same pipeline shape, different sources (files instead of DSN introspection) |
| 3 | Query pipeline | **Kept** (renumbered as Plan 3) — adds clarification frame, drill-down context, reranker on by default, `/sql:execute`, `/tables:derive` |
| 4 | Transformation sources (dbt + file bundles + drift) | **Dropped** — file ingestion is now the core (folded into new Plan 2), no dbt, no drift watchdog in v0 |
| 5 | Multi-dialect (MySQL/Snowflake/BigQuery/Redshift/DuckDB) | **Dropped** — no remote DBs; DuckDB is the sole query engine |
| 6 | Packaging | **Kept** (renumbered as Plan 4) |

Net change: **4 v0 plans instead of 6**, with file ingestion promoted from a v1 transformation source to the v0 core. Cloud-warehouse adapters and dbt support are eliminated, not deferred.
