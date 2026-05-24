# Cost Tracking and Usage Metrics

Every flyquery operation that hits a paid LLM provider tracks
token usage + dollar cost + latency per agent stage. The numbers
ride back on the API response so callers can show consumption to
end users and feed a billing pipeline.

> **Status — write path is live as of 26.5.10.** Both the in-response
> `usage` block AND the persistent `flyquery_cost_events` /
> `flyquery_audit_events` ledgers are populated by real callsites:
> dataset CRUD writes audit events
> ([`audit_event_service.record`](../src/flyquery/core/services/ops/audit_event_service.py)),
> and every LLM call in the `flyquery.core.agents.*` modules writes a
> cost event through
> [`cost_event_service.record`](../src/flyquery/core/services/ops/cost_event_service.py).
> The callsites surface is still expanding — every new authoring or
> action endpoint adds an `audit_events.record` call, every new agent
> adds a `cost_events.record` call. Read endpoints
> ([`GET /api/v1/cost-events`](api-reference.md#5.12-history-and-ops),
> [`GET /api/v1/audit-events`](api-reference.md#5.12-history-and-ops),
> [`GET /api/v1/billing`](billing.md)) are now part of the supported
> wire contract.

## What gets tracked

* **Per-agent stage** (grounding / generation / critic / explainer
  / describe / column-name-proposer / …):
  * `input_tokens`
  * `output_tokens`
  * `total_tokens`
  * `cost_usd` (computed by fireflyframework-agentic's per-model
    rate table)
  * `latency_ms`
  * `calls` (how many times the stage was invoked -- the critic
    can loop)

## API surface

### Query responses

`POST /api/v1/query` returns the
[`AnswerResponse`](../src/flyquery/interfaces/query.py) schema,
which now includes a `usage` block:

```json
{
  "query_id": "...",
  "sql": "...",
  "execution_status": "OK",
  "preview": [...],
  "elapsed_ms": 15429,
  "explanation": "...",
  "usage": {
    "total_input_tokens": 4321,
    "total_output_tokens": 312,
    "total_tokens": 4633,
    "total_cost_usd": 0.018345,
    "total_latency_ms": 14820.0,
    "by_agent": [
      {
        "agent": "grounding",
        "model": "anthropic:claude-sonnet-4-6",
        "input_tokens": 1572,
        "output_tokens": 232,
        "total_tokens": 1804,
        "cost_usd": 0.008196,
        "latency_ms": 4913.4,
        "calls": 1
      },
      {
        "agent": "generation",
        "model": "anthropic:claude-sonnet-4-6",
        "input_tokens": 1152,
        "output_tokens": 135,
        "total_tokens": 1287,
        "cost_usd": 0.005481,
        "latency_ms": 3235.1,
        "calls": 1
      },
      {
        "agent": "explainer",
        "model": "anthropic:claude-haiku-4-5",
        "input_tokens": 1597,
        "output_tokens": 176,
        "total_tokens": 1773,
        "cost_usd": 0.004668,
        "latency_ms": 6671.5,
        "calls": 1
      }
    ]
  }
}
```

When a query path doesn't hit an LLM (semantic-layer fast path,
direct SQL), the `usage` block is still returned but
`total_tokens` / `total_cost_usd` are zero and `by_agent` is
empty.

### Ingest responses

`POST /api/v1/datasets/{id}/files` returns an analogous block --
the describe stage + column-name-proposer dominate, and the
publish stage contributes only network latency (no LLM call).

### Streaming endpoints

`POST /api/v1/query/stream` emits a `usage` SSE event at the end
of the stream, just before `final`, so clients can render the
running total alongside the SQL + result.

## Persistence

* `flyquery_queries.tokens_in_total` / `tokens_out_total` /
  `cost_usd_total` columns capture the aggregate.
* `flyquery_queries.usage_by_agent_json` (JSONB) captures the
  per-stage breakdown for forensic / billing-audit use.
* `flyquery_ingest_events.metadata_json.usage` carries the same
  schema for ingest-side LLM calls.

## Rate table

fireflyframework-agentic ships a built-in rate table covering
every model declared in the `flyquery_*_model` settings; rates
match Anthropic / OpenAI / Bedrock published pricing as of the
fireflyframework-agentic release pinned in `pyproject.toml`.

To override a rate (e.g. for an enterprise contract), set
`FIREFLY_AGENT_MODEL_RATE_<model>=<usd_per_1k_in>:<usd_per_1k_out>`
in the runtime env -- see the fireflyframework-agentic docs.

## Observability

Every agent emits an `agent.completed` event with `cost_usd`,
`input_tokens`, `output_tokens`, `latency_ms` to the structured
log + OpenTelemetry tracer. Sample log line:

```
{'event_type': 'agent.completed', 'agent': 'flyquery-grounding',
 'detail': {'tokens': 1804, 'latency_ms': 4913.4,
            'model': 'anthropic:claude-sonnet-4-6',
            'cost_usd': 0.008196,
            'input_tokens': 1572,
            'output_tokens': 232}}
```

Wire this into Grafana / Datadog by parsing the JSON line and
graphing `cost_usd` per `agent` per tenant.
