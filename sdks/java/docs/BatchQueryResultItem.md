

# BatchQueryResultItem

One outcome in a batch query response.  Mirrors ``AnswerResponse`` for OK results; carries ``error`` + ``status=\"FAILED\"`` on failure so the batch never aborts on one bad item.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**chartHint** | [**ChartHintEnum**](#ChartHintEnum) |  |  [optional] |
|**elapsedMs** | **Integer** |  |  [optional] |
|**error** | **String** |  |  [optional] |
|**executionStatus** | [**ExecutionStatusEnum**](#ExecutionStatusEnum) |  |  [optional] |
|**explanation** | **String** |  |  [optional] |
|**groundedSummary** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**index** | **Integer** |  |  |
|**preview** | **List&lt;Map&lt;String, Object&gt;&gt;** |  |  [optional] |
|**queryId** | **UUID** |  |  [optional] |
|**rowCount** | **Integer** |  |  [optional] |
|**sql** | **String** |  |  [optional] |
|**status** | **String** |  |  |



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



