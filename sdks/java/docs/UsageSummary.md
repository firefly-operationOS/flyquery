

# UsageSummary

Aggregated cost + latency across the whole pipeline.  Returned on every query / ingest response so clients can show consumption to end users and stream into a billing pipeline. The per-stage breakdown stays in ``by_agent`` for debugging.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**byAgent** | [**List&lt;AgentUsage&gt;**](AgentUsage.md) |  |  [optional] |
|**totalCostUsd** | **BigDecimal** |  |  [optional] |
|**totalInputTokens** | **Integer** |  |  [optional] |
|**totalLatencyMs** | **BigDecimal** |  |  [optional] |
|**totalOutputTokens** | **Integer** |  |  [optional] |
|**totalTokens** | **Integer** |  |  [optional] |



