

# SchemaChangeRead

Response for GET /tables/{id}/changes items.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**afterJson** | **Map&lt;String, Object&gt;** |  |  |
|**approvedAt** | **OffsetDateTime** |  |  [optional] |
|**approvedBy** | **String** |  |  [optional] |
|**beforeJson** | **Map&lt;String, Object&gt;** |  |  |
|**change** | **String** |  |  |
|**columnName** | **String** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**id** | **UUID** |  |  |
|**llmRationale** | **String** |  |  |
|**nextSnapshotId** | **UUID** |  |  |
|**prevSnapshotId** | **UUID** |  |  |
|**tableId** | **UUID** |  |  |



