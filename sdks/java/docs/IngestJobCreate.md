

# IngestJobCreate

Request body for POST /api/v1/ingest-jobs.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**callback** | [**CallbackConfig**](CallbackConfig.md) | Optional webhook delivered after the job reaches a terminal status (SUCCEEDED, FAILED, or CANCELLED). See :class:&#x60;CallbackConfig&#x60; for the at-least-once delivery contract. |  [optional] |
|**datasetId** | **UUID** |  |  |
|**fileId** | **UUID** |  |  [optional] |
|**jobKind** | [**JobKindEnum**](#JobKindEnum) |  |  |
|**requestJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**tableId** | **UUID** |  |  [optional] |



## Enum: JobKindEnum

| Name | Value |
|---- | -----|
| PARSE_AND_INGEST | &quot;PARSE_AND_INGEST&quot; |
| REPARSE | &quot;REPARSE&quot; |
| SAMPLE_REFRESH | &quot;SAMPLE_REFRESH&quot; |
| DESCRIBE_PASS | &quot;DESCRIBE_PASS&quot; |
| RELATION_PASS | &quot;RELATION_PASS&quot; |



