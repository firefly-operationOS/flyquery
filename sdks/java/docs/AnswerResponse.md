

# AnswerResponse

Response from POST /api/v1/query (sync).

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**chartHint** | [**ChartHintEnum**](#ChartHintEnum) |  |  [optional] |
|**clarification** | [**ClarificationFrame**](ClarificationFrame.md) |  |  [optional] |
|**elapsedMs** | **Integer** |  |  |
|**executionStatus** | [**ExecutionStatusEnum**](#ExecutionStatusEnum) |  |  |
|**explanation** | **String** |  |  [optional] |
|**groundedSummary** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**preview** | **List&lt;Map&lt;String, Object&gt;&gt;** |  |  |
|**queryId** | **UUID** |  |  |
|**rowCount** | **Integer** |  |  |
|**snapshotPins** | **Map&lt;String, String&gt;** |  |  [optional] |
|**sql** | **String** |  |  |
|**truncated** | **Boolean** |  |  [optional] |
|**usage** | [**UsageSummary**](UsageSummary.md) |  |  [optional] |



## Enum: ChartHintEnum

| Name | Value |
|---- | -----|
| LINE | &quot;line&quot; |
| BAR | &quot;bar&quot; |
| TABLE | &quot;table&quot; |
| PIE | &quot;pie&quot; |
| NONE | &quot;none&quot; |



## Enum: ExecutionStatusEnum

| Name | Value |
|---- | -----|
| OK | &quot;OK&quot; |
| REFINED_OK | &quot;REFINED_OK&quot; |
| FAILED | &quot;FAILED&quot; |
| REJECTED_BY_FIREWALL | &quot;REJECTED_BY_FIREWALL&quot; |



