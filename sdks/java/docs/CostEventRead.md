

# CostEventRead

Append-only LLM cost ledger row.  ``cost_cents`` is a Decimal because partial cents are common at the per-call granularity (the cost tracker in fireflyframework-agentic rounds at aggregation time, not per row).

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**actor** | **String** |  |  |
|**correlationId** | **String** |  |  [optional] |
|**costCents** | [**CostCents**](CostCents.md) |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**id** | **UUID** |  |  |
|**ingestJobId** | **UUID** |  |  [optional] |
|**inputTokens** | **Integer** |  |  |
|**model** | **String** |  |  [optional] |
|**operation** | **String** |  |  |
|**outputTokens** | **Integer** |  |  |
|**queryId** | **UUID** |  |  [optional] |
|**tenantId** | **String** |  |  |
|**workspaceId** | **UUID** |  |  |



