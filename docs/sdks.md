# SDKs

flyquery ships two officially-supported SDKs that are byte-equivalent
wire-contract clients, generated from the same
[`openapi.json`](../openapi.json) snapshot per release.

| SDK | Language | Distribution | Source |
|-----|----------|--------------|--------|
| `flyquery_sdk` | Python 3.9+ (asyncio) | PyPI / GitHub Release wheel | [`sdks/python/`](../sdks/python/) |
| `flyquery-sdk` | Java 25 + Spring WebFlux | GitHub Packages (Maven) | [`sdks/java/`](../sdks/java/) |

Both SDKs are regenerated from `openapi.json` every release; the
Python SDK additionally ships a hand-written `FlyqueryClient`
ergonomic wrapper on top of the generated API classes.

## Capability matrix

| Capability | Python | Java |
|------------|--------|------|
| Workspace CRUD | ✅ generated | ✅ generated |
| Dataset CRUD | ✅ generated | ✅ generated |
| Single file upload | ✅ `FlyqueryClient.upload` | ✅ `FilesApi.uploadFile` |
| **Bulk file upload** | ✅ `FlyqueryClient.upload_bulk` + `upload_directory` | ✅ raw `WebClient` against `:bulk` (snippet in README) |
| **Async file upload** (`files:async`, new in 26.5.10) | ✅ generated `FilesApi.uploadFileAsync` | ✅ generated `FilesApi.uploadFileAsync` |
| Single NL query | ✅ `FlyqueryClient.ask` | ✅ `QueryApi.query` |
| **Batch NL query** | ✅ `FlyqueryClient.ask_batch` | ✅ `QueryApi.batch` |
| Streaming SSE | ✅ `QueryApi.stream` (raw) | ✅ `QueryApi.stream` (raw) |
| **Query history list** (new in 26.5.10) | ✅ `FlyqueryClient.recent_queries` (ergonomic) + `QueriesApi.list_queries` (raw) | ✅ `QueriesApi.listQueries` |
| **Query detail** (new in 26.5.10) | ✅ `FlyqueryClient.get_query` (ergonomic) + `QueriesApi.get_query` (raw) | ✅ `QueriesApi.getQuery` |
| **Query result re-download** (new in 26.5.10) | ✅ `FlyqueryClient.fetch_query_result` (ergonomic) + `QueriesApi.get_query_result` (raw) | ✅ `QueriesApi.getQueryResult` |
| **Billing rollup** (new in 26.5.10) | ✅ `FlyqueryClient.billing_rollup` (ergonomic) + `BillingApi.rollup` (raw) | ✅ `BillingApi.rollup` |
| **Workspace stats** (new in 26.5.10) | ✅ `FlyqueryClient.workspace_stats` (ergonomic) + `StatsApi.workspace_summary` (raw) | ✅ `StatsApi.workspaceSummary` |
| Idempotent workspace lookup-or-create | ✅ `FlyqueryClient.find_or_create_workspace` | manual chain via `readBySlug` + `onErrorResume` |
| Idempotent dataset lookup-or-create | ✅ `FlyqueryClient.find_or_create_dataset` | manual chain via `readByName` + `onErrorResume` |
| Sync helpers | ✅ `_sync` mirror per async method | reactive only (block at the edge) |

The Java SDK is intentionally lower-level — Spring WebFlux users
expect to chain `Mono`s themselves and the ergonomic wrapper
pattern adds more confusion than value in that ecosystem.

The Python `FlyqueryClient` ergonomic wrapper lives at
[`sdks/python/flyquery_sdk/client.py`](../sdks/python/flyquery_sdk/client.py).
The Java equivalent `FlyqueryClient` lives at
[`sdks/java/src/main/java/com/firefly/flyquery/FlyqueryClient.java`](../sdks/java/src/main/java/com/firefly/flyquery/FlyqueryClient.java)
and wires base URL + tenant/workspace/agent-token headers into every
Api class. For the new v1 history / billing / stats endpoints, both SDKs
expose the generated API classes directly — see
[consumers.md § Recipe F + G](consumers.md#recipe-f-query-history--re-download-new-in-26510)
for end-to-end snippets.

## Authentication contract

Both SDKs carry the wire-level headers documented in
[security-model.md](./security-model.md):

| Header | When required |
|--------|---------------|
| `X-Tenant-Id` | All non-agent operations |
| `X-Workspace-Id` | All non-agent operations |
| `X-Agent-Token` | All `/api/v1/agent/*` operations |
| `X-Correlation-Id` | Optional everywhere (echoed in response) |
| `Idempotency-Key` | Optional on `POST/PUT/DELETE/PATCH` |

The Python `FlyqueryClient` sets them once at construction. The Java
`ApiClient.addDefaultHeader(...)` does the same.

## Bulk endpoints

Both SDKs target the same two wire-level bulk endpoints:

| Wire | Verb | Body |
|------|------|------|
| `/api/v1/datasets/{dataset_id}/files:bulk` | POST | `multipart/form-data` with N `files` parts |
| `/api/v1/query:batch` | POST | JSON `{queries: [{question, dataset_id}, ...]}` |

Per-item failures (one bad file, one mis-grounded question) DO NOT
abort the request — the response carries `status="OK"` or
`status="FAILED"` + `error` per item, and aggregate
`succeeded`/`failed`/`total` counts.

## Versioning

Both SDKs use the project's CalVer scheme: ``YY.M.P`` (e.g.
`26.5.6`). The SDK version matches the service's `openapi.json`
snapshot version at the time of regeneration. SDK consumers can
safely pin to a CalVer prefix (e.g. ``flyquery-sdk~=26.5``) — patch
bumps add wire-compatible methods only.

## Regenerating

```bash
# Refresh openapi.json from the running service
uv run python scripts/openapi_snapshot.py

# Regenerate the Python SDK (in-place)
task sdk:python

# Regenerate the Java SDK (in-place)
task sdk:java
```

The hand-written `FlyqueryClient` lives at
[`sdks/python/flyquery_sdk/client.py`](../sdks/python/flyquery_sdk/client.py)
and is preserved through `.openapi-generator-ignore`.

## Examples

* Python: [`sdks/python/examples/`](../sdks/python/examples/)
* Java: [`sdks/java/examples/`](../sdks/java/examples/)
* Synthetic fixtures used by the examples: [`examples/`](../examples/)
