

# SqlExecuteResponse

Response from POST /api/v1/sql:execute (sync).

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**astClassification** | **String** |  |  |
|**elapsedMs** | **Integer** |  |  |
|**executionStatus** | [**ExecutionStatusEnum**](#ExecutionStatusEnum) |  |  |
|**preview** | **List&lt;Map&lt;String, Object&gt;&gt;** |  |  |
|**queryId** | **UUID** |  |  |
|**rowCount** | **Integer** |  |  |
|**sql** | **String** |  |  |
|**truncated** | **Boolean** |  |  [optional] |



## Enum: ExecutionStatusEnum

| Name | Value |
|---- | -----|
| OK | &quot;OK&quot; |
| FAILED | &quot;FAILED&quot; |
| REJECTED_BY_FIREWALL | &quot;REJECTED_BY_FIREWALL&quot; |



