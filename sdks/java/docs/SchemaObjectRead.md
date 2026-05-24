

# SchemaObjectRead

Response for GET /schema-objects/{id} or PUT /schema-objects/{id}.  See :class:`SchemaObjectUpdate` for shape contract. Reads always return canonical shapes; the validators forgive a legacy row that has not yet been touched by migration 0012.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**businessOwner** | **String** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**dataType** | **String** |  |  |
|**description** | **String** |  |  |
|**descriptionSource** | **String** |  |  |
|**governanceJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**id** | **UUID** |  |  |
|**isActive** | **Boolean** |  |  |
|**isNullable** | **Boolean** |  |  |
|**kind** | **String** |  |  |
|**lastChangedAt** | **OffsetDateTime** |  |  |
|**piiSource** | **String** |  |  |
|**piiTag** | **String** |  |  |
|**qualifiedName** | **String** |  |  |
|**snapshotId** | **UUID** |  |  |
|**synonymsJson** | **List&lt;String&gt;** |  |  [optional] |
|**tableId** | **UUID** |  |  |
|**tenantId** | **String** |  |  |
|**workspaceId** | **UUID** |  |  |



