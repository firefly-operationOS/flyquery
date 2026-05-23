

# ExplainResponse

Response from POST /api/v1/query:explain — Grounding + Generation only.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**clarification** | [**ClarificationFrame**](ClarificationFrame.md) |  |  [optional] |
|**confidence** | **BigDecimal** |  |  |
|**groundedSummary** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**reasoning** | **String** |  |  |
|**sql** | **String** |  |  |



