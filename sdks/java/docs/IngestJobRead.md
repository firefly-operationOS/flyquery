

# IngestJobRead

Response for GET /api/v1/ingest-jobs/{id} and list items.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**attempts** | **Integer** |  |  |
|**costCents** | [**CostCents**](CostCents.md) |  |  |
|**datasetId** | **UUID** |  |  |
|**elapsedMs** | **Integer** |  |  |
|**fileId** | **UUID** |  |  |
|**finishedAt** | **OffsetDateTime** |  |  |
|**id** | **UUID** |  |  |
|**jobKind** | **String** |  |  |
|**requestJson** | **Map&lt;String, Object&gt;** |  |  |
|**resultJson** | **Map&lt;String, Object&gt;** |  |  |
|**snapshotId** | **UUID** |  |  |
|**startedAt** | **OffsetDateTime** |  |  |
|**status** | **String** |  |  |
|**tableId** | **UUID** |  |  |
|**tenantId** | **String** |  |  |
|**workspaceId** | **UUID** |  |  |



