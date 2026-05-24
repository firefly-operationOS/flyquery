# flyquery — Consumers

## Table of Contents

1. [Overview](#1-overview)
2. [SDK patterns](#2-sdk-patterns)
3. [Agent-token model](#3-agent-token-model)
4. [Idempotency](#4-idempotency)
5. [Error handling](#5-error-handling)
6. [EDA subscription](#6-eda-subscription)
7. [Common integration recipes](#7-common-integration-recipes)

---

## 1. Overview

This document is for engineers building services or automation that consume
flyquery — whether that is the flydesk frontend, a reporting pipeline, a
flyradar integration, or a custom AI agent.

flyquery exposes two surfaces:
- **User-tier** (`/api/v1/*`) — protected by JWT + `X-Tenant-Id` /
  `X-Workspace-Id` headers. For human-facing applications.
- **Agent-tier** (`/api/v1/agent/*`) — protected by `X-Agent-Token` +
  mandatory `Idempotency-Key` on writes. For automated callers, AI agents,
  and inter-service calls.

For the complete endpoint list see [api-reference.md](api-reference.md).
For event subscriptions see [eda-events.md](eda-events.md).

---

## 2. SDK patterns

### Python SDK (async-first)

```python
from flyquery_sdk import FlyqueryClient
import asyncio

async def main():
    client = FlyqueryClient(
        base_url="http://localhost:8520",
        tenant_id="acme",
        workspace_id="analytics",
        # For user-tier: jwt_token="..."
        # For agent-tier: agent_token="agt_abc123_<secret>"
    )

    # Upload a file
    result = await client.files.upload(
        dataset_id="ds_01",
        file_path="sales.csv",
    )
    ingest_job_id = result.ingest_job_id

    # Wait for ingestion (poll or stream)
    async for event in client.ingest_jobs.stream(ingest_job_id):
        print(event.stage, event.status)

    # Ask a question
    answer = await client.query.ask(
        dataset_id="ds_01",
        question="Total revenue by region",
    )
    print(answer.answer)
    print(answer.executed_sql)
    print(answer.chart_hint)

asyncio.run(main())
```

### Java SDK (Spring Boot)

```java
import com.firefly.flyquery.FlyqueryClient;
import com.firefly.flyquery.model.*;

@Service
public class FlyqueryService {
    private final FlyqueryClient client;

    public FlyqueryService(FlyqueryConfiguration config) {
        this.client = new FlyqueryClient(
            config.getBaseUrl(),
            config.getTenantId(),
            config.getWorkspaceId()
        );
        this.client.setAgentToken(config.getAgentToken());
    }

    public AnswerResponse ask(String datasetId, String question) {
        QueryRequest req = new QueryRequest()
            .datasetId(datasetId)
            .question(question);
        return client.getQueryApi().query(req);
    }
}
```

### Direct HTTP (curl)

```bash
# Agent-tier example
curl -X POST http://localhost:8520/api/v1/agent/query \
  -H "X-Tenant-Id: acme" \
  -H "X-Workspace-Id: analytics" \
  -H "X-Agent-Token: agt_abc123_<secret>" \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which products had the highest return rate in Q1?",
    "dataset_id": "ds_01"
  }'
```

---

## 3. Agent-token model

Agent tokens enable non-human callers without JWT.

### Minting a token

```
POST /api/v1/agent-tokens
{
  "name": "reporting-pipeline",
  "scopes": [
    "flyquery.query:read",
    "flyquery.schema:read",
    "flyquery.files:upload"
  ],
  "dataset_allowlist": ["ds_01", "ds_02"],
  "workspace_allowlist": ["analytics"],
  "expires_at": "2027-05-23T00:00:00Z",
  "rate_limit_rpm": 60
}
→ {
    "token_id": "agt_abc123",
    "token": "agt_abc123_<32-hex-secret>",   ← shown once; store securely
    "scopes": [...],
    ...
  }
```

Store the token value in a secrets manager. flyquery only stores the
`SHA-256(token)` — the plain-text token cannot be recovered after creation.

### Scope enforcement

The effective grant for an agent call is the intersection of:
1. Token scopes
2. `workspace_allowlist` vs `X-Workspace-Id`
3. `dataset_allowlist` vs the request's `dataset_id`
4. AST classification of any SQL generated
5. Target table kind (UPLOADED is read-only)

See [security-model.md § 5](security-model.md#5-scope-catalog-and-enforcement)
for the full scope catalog.

### Token rotation

```bash
# Mint new token
POST /api/v1/agent-tokens {...}

# Deploy new token to all consumers

# Revoke old token
DELETE /api/v1/agent-tokens/{old_token_id}
```

---

## 4. Idempotency

All mutating calls on the agent-tier require an `Idempotency-Key` header.

```
Idempotency-Key: <unique-per-call UUID>
```

**Behaviour:**
- Same key + same method + same path → replay: returns the original response.
- Same key + different payload → `409 Conflict` (key collision).
- Different key → fresh call.

flyquery stores the idempotency key in Redis (or in-memory if Redis is
unavailable) with a 24-hour TTL. After TTL expiry, the same key can be reused
safely (it will trigger a fresh call).

**When to generate a new key:**

Generate a new UUID per logical operation. For retries of the same operation
(e.g., network timeout), reuse the same key — this is the intended use case
for idempotency.

```python
import uuid

async def upload_with_retry(client, dataset_id, file_path, max_retries=3):
    idempotency_key = str(uuid.uuid4())   # generate once per logical upload
    for attempt in range(max_retries):
        try:
            return await client.files.upload(
                dataset_id=dataset_id,
                file_path=file_path,
                idempotency_key=idempotency_key,  # same key on retry
            )
        except NetworkError:
            if attempt == max_retries - 1:
                raise
```

---

## 5. Error handling

flyquery uses RFC 7807 Problem Details for all error responses.

```json
{
  "type": "https://flyquery.firefly.dev/errors/format-mismatch",
  "title": "File format mismatch",
  "status": 422,
  "code": "FORMAT_MISMATCH",
  "detail": "File extension '.csv' does not match detected format 'xlsx'",
  "instance": "/api/v1/datasets/ds_01/files"
}
```

### Common error codes

| Code | Status | Meaning |
|------|--------|---------|
| `FORMAT_MISMATCH` | 422 | Extension doesn't match magic bytes |
| `ZIP_MULTI_ENTRY` | 422 | ZIP archive with multiple files |
| `INGEST_JOB_NOT_FOUND` | 404 | Invalid ingest_job_id |
| `SNAPSHOT_EXPIRED` | 410 | Pinned snapshot no longer available |
| `REJECTED_BY_FIREWALL` | 422 | SQL failed AST firewall check |
| `PII_IN_RESULTS` | 422 | PII detected in results with policy=reject |
| `WORKSPACE_QUOTA_EXCEEDED` | 413 | Workspace storage limit reached |
| `AGENT_TOKEN_EXPIRED` | 401 | Token expired |
| `INSUFFICIENT_SCOPE` | 403 | Token lacks required scope |
| `IDEMPOTENCY_CONFLICT` | 409 | Same key, different payload |
| `JOB_CANCELLED` | 200 | Job was cancelled (in SSE stream) |

### Retry-safe vs non-retry-safe errors

| Status | Retry-safe? |
|--------|------------|
| 5xx | Yes (with backoff) |
| 429 (rate limit) | Yes (after `Retry-After`) |
| 409 (idempotency conflict) | No — bug in caller |
| 4xx (other) | No — fix the request |

---

## 6. EDA subscription

Subscribe to `flyquery.schema` if you need to react to schema changes
without polling.

```python
from pyfly.eda import subscribe

@subscribe(topic="flyquery.schema", event="SchemaUpdated")
async def on_schema_change(event: dict, **_):
    # Invalidate cache, re-index, notify users, etc.
    table_id = event["table_id"]
    snapshot_id = event["snapshot_id"]
    diff = event["diff_summary"]
    if diff["added"] or diff["type_changed"]:
        await invalidate_query_cache(table_id)
```

See [eda-events.md](eda-events.md) for the full event schema and consumer guide.

---

## 7. Common integration recipes

### Recipe A: Upload-and-wait (synchronous wrapper)

For callers that need synchronous ingestion semantics:

```python
async def upload_and_wait(client, dataset_id, file_path, timeout_s=120):
    """Upload a file and wait for ingestion to complete."""
    upload = await client.files.upload(dataset_id=dataset_id, file_path=file_path)
    job_id = upload.ingest_job_id
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        job = await client.ingest_jobs.get(job_id)
        if job.status in ("SUCCEEDED", "FAILED", "CANCELLED"):
            return job
        await asyncio.sleep(2)
    raise TimeoutError(f"Ingest job {job_id} did not complete in {timeout_s}s")
```

### Recipe B: Bulk schema annotation

```python
# Fetch all unannotated columns
objects = await client.schema_objects.search(
    description=None,  # only unannotated
    limit=100,
)
for obj in objects:
    await client.schema_objects.update(
        schema_object_id=obj.id,
        description=f"Column '{obj.qualified_name}' from the {obj.table_name} table.",
    )
```

### Recipe C: Scheduled relation approval review

```python
# List PROPOSED relations once a day
async def daily_relation_review(client, dataset_id):
    relations = await client.relations.list(
        dataset_id=dataset_id,
        status="PROPOSED",
        kind="AGENT_PROPOSED",
    )
    for rel in relations:
        if rel.confidence > 0.9:
            await client.relations.approve(
                dataset_id=dataset_id, relation_id=rel.id
            )
        elif rel.confidence < 0.3:
            await client.relations.reject(
                dataset_id=dataset_id, relation_id=rel.id
            )
        # else: leave for manual review
```

### Recipe D: flyradar integration — reference a flyquery dataset

```python
# From within a flyradar discovery handler:
async def enrich_with_flyquery_schema(dataset_id: str, workspace_id: str):
    """Fetch schema objects from flyquery to inform a discovery step."""
    async with FlyqueryClient(agent_token=AGENT_TOKEN, ...) as client:
        tables = await client.tables.list(dataset_id=dataset_id)
        for table in tables:
            schema = await client.schema_objects.list(
                table_id=table.table_id,
                kind="COLUMN",
                is_active=True,
            )
            # use schema in the discovery analysis...
```

See [integration-with-firefly-os.md](integration-with-firefly-os.md) for the
full three-pillar integration narrative.

### Recipe E: Question + result in a conversation loop

```python
async def interactive_session(client, dataset_id):
    conv = await client.conversations.create(dataset_id=dataset_id)
    print("Ask questions about the dataset. Type 'exit' to stop.")
    while True:
        question = input("> ")
        if question == "exit":
            break
        response = await client.conversations.turn(
            conversation_id=conv.conversation_id,
            question=question,
        )
        print(response.answer)
        print(f"(SQL: {response.executed_sql})")
```

### Recipe F: Query history + re-download (new in 26.5.10)

The v1 history endpoints surface previously executed queries — useful
for "show me my last 10 questions" UIs, audit dashboards, and
re-download flows that don't want to re-run the LLM pipeline.

```bash
# Curl: list history (filter to failures over the last week)
curl -sS 'http://localhost:8520/api/v1/queries?execution_status=FAILED&date_from=2026-05-17' \
  -H 'X-Tenant-Id: acme' -H 'X-Workspace-Id: analytics' | jq

# Curl: full detail
curl -sS 'http://localhost:8520/api/v1/queries/01906f40-.../' \
  -H 'X-Tenant-Id: acme' -H 'X-Workspace-Id: analytics' | jq

# Curl: re-download presigned URL
curl -sS 'http://localhost:8520/api/v1/queries/01906f40-.../result' \
  -H 'X-Tenant-Id: acme' -H 'X-Workspace-Id: analytics' | jq .parquet_presigned_url
# null means the TTL elapsed; rerun the query.
```

```python
# Python SDK
async def recent_failures(client):
    page = await client.get(
        "/api/v1/queries",
        params={"execution_status": "FAILED", "limit": 50},
    )
    for q in page["items"]:
        print(q["created_at"], q["question"], q["row_count"])
        detail = await client.get(f"/api/v1/queries/{q['id']}")
        print("  error:", detail.get("error_json"))
```

```java
// Java SDK -- header args come first in the generated signature
QueriesApi q = client.getQueriesApi();
PaginatedQueryHistoryItem page = q.listQueries(
    /* xTenantId */ "acme",
    /* xWorkspaceId */ "analytics",
    /* datasetId */ null,
    /* executionStatus */ "FAILED",
    /* semanticPathTaken */ null,
    /* dateFrom */ null,
    /* dateTo */ null,
    /* limit */ 50,
    /* offset */ 0,
    /* xCorrelationId */ null
).block();
page.getItems().forEach(i -> System.out.println(i.getQuestion()));
```

### Recipe G: Billing rollup + workspace stats (new in 26.5.10)

```bash
# Daily breakdown for the month so far
curl -sS 'http://localhost:8520/api/v1/billing?period=day&date_from=2026-05-01' \
  -H 'X-Tenant-Id: acme' -H 'X-Workspace-Id: analytics' | jq

# Compact workspace summary
curl -sS http://localhost:8520/api/v1/stats \
  -H 'X-Tenant-Id: acme' -H 'X-Workspace-Id: analytics' | jq
```

```python
# Python: render a workspace dashboard tile
stats = await client.get("/api/v1/stats")
billing = await client.get("/api/v1/billing?period=month")
print(f"Storage: {stats['storage_used_bytes'] / 1024**3:.2f} GB")
print(f"Datasets / Tables: {stats['dataset_count']} / {stats['table_count']}")
print(f"Queries (30d): {stats['query_count_last_30d']}")
print(f"This month: ${billing['total_cost_cents'] / 100:.2f}")
```

```java
// Java: pull the rollup for a finance dashboard
BillingRollup rollup = client.getBillingApi()
    .rollup(
        /* xTenantId */ "acme",
        /* xWorkspaceId */ "analytics",
        /* period */ "month",
        /* dateFrom */ null,
        /* dateTo */ null,
        /* xCorrelationId */ null
    )
    .block();
System.out.printf("Total: $%.2f over %d bucket(s)%n",
    rollup.getTotalCostCents().doubleValue() / 100.0,
    rollup.getBreakdown().size());
```
