<div align="center">

<img src="../../docs/assets/logo.png" alt="flyquery" width="380" />

### **Python SDK** &nbsp;&middot;&nbsp; asyncio &nbsp;&middot;&nbsp; Python 3.9+

</div>

---

Async-first Python client for the
[flyquery](https://github.com/firefly-operationOS/flyquery) Tabular
Intelligence service — Text-to-SQL over user-uploaded structured
files.

- **Async-first**: every endpoint returns a coroutine; pairs naturally
  with `asyncio`, FastAPI, Starlette, Jupyter's top-level await, or
  any other event-loop host.
- **Pydantic v2-typed request + response models** — full
  IDE-completion + runtime validation on the wire payloads.
- **`aiohttp` under the hood** — pooled connections, retries
  (via `aiohttp-retry`), timeouts you control.
- Carries the firefly four-header wire contract
  (`X-Tenant-Id` / `X-Workspace-Id` / `X-Correlation-Id` /
  `X-Agent-Token`) on every outbound request.
- **18 split API classes** — one per resource family: workspaces,
  datasets, files, tables, schema, relations, semantic, glossary,
  examples, query, conversations, ingest, sql, agent-tokens, meta,
  agent-query, agent-sql, agent-examples.
- No service dependency — the SDK ships its own Pydantic schemas so
  it installs cleanly alongside any client codebase without pulling
  the framework.
- Apache-2.0; auto-generated from `flyquery/openapi.json` via
  [`openapi-generator-cli`](https://openapi-generator.tech/).

## Wire-contract compatibility

Compatible with **flyquery service version `26.5.x`**.

| SDK | Service |
|-----|---------|
| `26.5.4` | `26.5.x` |

## Install

```bash
uv add flyquery-sdk==26.5.4
# or
pip install flyquery-sdk==26.5.4
```

From a sibling-repo checkout (development):

```bash
pip install -e ./sdks/python
```

## Quick start

```python
import asyncio
from flyquery_sdk import ApiClient, Configuration
from flyquery_sdk.api import WorkspacesApi, DatasetsApi, QueryApi
from flyquery_sdk.models import WorkspaceCreate, DatasetCreate, QueryRequest


async def main() -> None:
    config = Configuration(host="https://flyquery.example.com")

    async with ApiClient(config) as client:
        workspaces = WorkspacesApi(client)
        datasets   = DatasetsApi(client)
        query      = QueryApi(client)

        # 1) Create a workspace
        ws = await workspaces.create_workspace(
            WorkspaceCreate(slug="alpha", name="Alpha"),
            x_tenant_id="demo",
            x_workspace_id="alpha",
        )

        # 2) Create a dataset inside it
        ds = await datasets.create_dataset(
            DatasetCreate(name="Sales 2026"),
            x_tenant_id="demo",
            x_workspace_id=ws.id,
        )

        # 3) Upload a CSV (see FilesApi.upload_file in your SDK)
        # 4) Ask a question
        answer = await query.post_query(
            QueryRequest(
                dataset_id=ds.id,
                question="what is total revenue by region?",
            ),
            x_tenant_id="demo",
            x_workspace_id=ws.id,
        )
        print(answer.sql)
        print(answer.preview)


asyncio.run(main())
```

## Authentication

The flyquery service expects either a user-tier JWT bearer token (on
`/api/v1/*` routes) or an agent-tier `X-Agent-Token` (on
`/api/v1/agent/*` routes). Wire them up on the `Configuration`:

```python
# User-tier (JWT)
config = Configuration(
    host="https://flyquery.example.com",
    access_token="eyJhbGciOiJSUzI1NiIs...",
)

# Agent-tier (long-lived token, agt_<8hex>_<32hex>)
config = Configuration(
    host="https://flyquery.example.com",
    api_key={"X-Agent-Token": "agt_aabbccdd_eeff00112233445566778899aabbccddeeff"},
)
```

Every request **must** carry `X-Tenant-Id` and `X-Workspace-Id`
header parameters — the service uses them to bind the
request-scoped RLS GUCs. They're explicit on every API method;
see the per-method signatures.

For agent-tier write endpoints (uploads, derives, mutations), pass
an `Idempotency-Key` via the `idempotency_key` kwarg — the service
deduplicates on the (token-prefix, key) pair for 24 hours.

## Streaming endpoints (SSE)

`/query/stream` and `/ingest-jobs/{id}/stream` are
Server-Sent Events. The generated method returns a streaming
response you iterate per-line:

```python
async with query.post_query_stream_with_http_info(
    QueryRequest(dataset_id=ds.id, question="how many orders per region?"),
    x_tenant_id="demo", x_workspace_id=ws.id,
) as resp:
    async for line in resp.content:
        decoded = line.decode("utf-8").strip()
        if decoded.startswith("event:"):
            print("stage:", decoded[len("event:"):].strip())
```

The event sequence is documented in
[`docs/pipeline.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/pipeline.md):
`schema_linked → sql_generated → executed → explained → final`,
with an optional `clarification` frame when Grounding confidence is
below threshold.

## Error handling

All API methods raise `flyquery_sdk.ApiException` on non-2xx
responses. The service emits
[RFC 7807](https://www.rfc-editor.org/rfc/rfc7807) ProblemDetails;
parse `ApiException.body` (or `.data` for typed responses) to access
the `code`, `title`, `detail`, and per-field `errors[]`.

```python
from flyquery_sdk.exceptions import ApiException

try:
    await workspaces.create_workspace(...)
except ApiException as exc:
    if exc.status == 409:
        # Workspace slug already exists for this tenant
        ...
    elif exc.status == 403:
        # Missing scope / dataset not in token allowlist
        ...
    else:
        raise
```

Common error codes:

| Status | `code`                    | Meaning                                            |
|--------|---------------------------|----------------------------------------------------|
| 400    | `validation_error`        | Request body failed Pydantic validation            |
| 401    | `unauthenticated`         | Missing/invalid token                              |
| 403    | `scope_denied`            | Token scope insufficient for this operation        |
| 404    | `resource_not_found`      | Dataset / table / workspace not visible under RLS  |
| 409    | `conflict`                | Slug / name collision (per workspace)              |
| 413    | `file_too_large`          | Upload exceeds `FLYQUERY_MAX_FILE_MB`              |
| 507    | `workspace_quota_exceeded`| Workspace storage cap reached                      |
| 503    | `rate_limited`            | Per-token rate limit exceeded                      |

## API reference

The 18 API classes mirror the resource families exposed by the
service. Per-family methods cover the endpoints documented in
[`docs/api-reference.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/api-reference.md).

| API class                | Resource family                  |
|--------------------------|----------------------------------|
| `WorkspacesApi`          | `/api/v1/workspaces`             |
| `DatasetsApi`            | `/api/v1/datasets`               |
| `FilesApi`               | `/api/v1/datasets/{id}/files`    |
| `TablesApi`              | `/api/v1/tables`                 |
| `SchemaApi`              | `/api/v1/schema-objects`         |
| `RelationsApi`           | `/api/v1/datasets/{id}/relations`|
| `SemanticApi`            | `/api/v1/semantic/*`             |
| `GlossaryApi`            | `/api/v1/glossary`               |
| `ExamplesApi`            | `/api/v1/examples`               |
| `QueryApi`               | `/api/v1/query/*`                |
| `ConversationsApi`       | `/api/v1/conversations`          |
| `IngestApi`              | `/api/v1/ingest-jobs`            |
| `SqlApi`                 | `/api/v1/sql:execute`            |
| `AgentTokensApi`         | `/api/v1/agent-tokens`           |
| `MetaApi`                | `/actuator/health`, `/version`   |
| `AgentQueryApi`          | `/api/v1/agent/query/*`          |
| `AgentSqlApi`            | `/api/v1/agent/sql:execute`      |
| `AgentExamplesApi`       | `/api/v1/agent/examples`         |

## Regenerating

The SDK is auto-generated from the service's OpenAPI spec. To pull
the latest:

```bash
# From the flyquery repo root:
task openapi-snapshot   # writes openapi.json
task sdk:python         # regenerates this directory
```

Hand-written files (`README.md`, `pyproject.toml`) are preserved
across regeneration via `.openapi-generator-ignore`.

## Development

```bash
cd sdks/python
uv venv
uv pip install -e ".[dev]"
pytest tests/         # smoke tests
mypy flyquery_sdk     # type-check
```

## License

Apache-2.0. See [LICENSE](LICENSE).

The upstream **flyquery service** is proprietary and licensed
separately; the SDK is the Apache-licensed wire-protocol client.

## Links

- Service repo: <https://github.com/firefly-operationOS/flyquery>
- Documentation index: [`docs/README.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/README.md)
- API reference: [`docs/api-reference.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/api-reference.md)
- Wire payloads: [`docs/payload-reference.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/payload-reference.md)
- Changelog: [`CHANGELOG.md`](https://github.com/firefly-operationOS/flyquery/blob/main/CHANGELOG.md)
