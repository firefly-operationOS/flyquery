

# AgentUsage

LLM usage + cost for a single pipeline stage.  Surfaced inside :class:`UsageSummary` so callers see exactly where the tokens went. ``cost_usd`` is computed by the fireflyframework-agentic cost tracker (per-model rate table).

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**agent** | **String** |  |  |
|**calls** | **Integer** |  |  [optional] |
|**costUsd** | **BigDecimal** |  |  [optional] |
|**inputTokens** | **Integer** |  |  [optional] |
|**latencyMs** | **BigDecimal** |  |  [optional] |
|**model** | **String** |  |  [optional] |
|**outputTokens** | **Integer** |  |  [optional] |
|**totalTokens** | **Integer** |  |  [optional] |



