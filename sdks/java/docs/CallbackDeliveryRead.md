

# CallbackDeliveryRead

One row from flyquery_callback_outbox.  Returned by ``GET /api/v1/ingest-jobs/{id}/callbacks`` so the caller can audit webhook delivery without inspecting the DB.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**attempts** | **Integer** |  |  |
|**callbackUrl** | **String** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**eventType** | **String** |  |  |
|**finishedAt** | **OffsetDateTime** |  |  |
|**id** | **UUID** |  |  |
|**ingestJobId** | **UUID** |  |  |
|**lastAttemptAt** | **OffsetDateTime** |  |  |
|**lastError** | **String** |  |  |
|**lastStatusCode** | **Integer** |  |  |
|**nextAttemptAt** | **OffsetDateTime** |  |  |
|**status** | [**StatusEnum**](#StatusEnum) |  |  |



## Enum: StatusEnum

| Name | Value |
|---- | -----|
| PENDING | &quot;PENDING&quot; |
| DELIVERED | &quot;DELIVERED&quot; |
| FAILED | &quot;FAILED&quot; |
| DEAD | &quot;DEAD&quot; |



