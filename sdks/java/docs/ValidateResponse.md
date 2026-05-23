

# ValidateResponse

Response from POST /api/v1/query:validate — includes AST + scope check.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**astClassification** | **String** |  |  |
|**clarification** | [**ClarificationFrame**](ClarificationFrame.md) |  |  [optional] |
|**scopeError** | **String** |  |  [optional] |
|**singleStatement** | **Boolean** |  |  [optional] |
|**sql** | **String** |  |  |
|**tableRefs** | **List&lt;String&gt;** |  |  [optional] |



