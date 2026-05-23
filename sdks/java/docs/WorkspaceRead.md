

# WorkspaceRead


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**allowDirectSql** | **Boolean** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**defaultLocale** | **String** |  |  |
|**id** | **UUID** |  |  |
|**kmsKeyUri** | **String** |  |  |
|**metadataJson** | **Map&lt;String, Object&gt;** |  |  |
|**name** | **String** |  |  |
|**retentionDays** | **Integer** |  |  |
|**slug** | **String** |  |  |
|**status** | [**StatusEnum**](#StatusEnum) |  |  |
|**storageUsedBytes** | **Integer** |  |  |
|**tenantId** | **String** |  |  |
|**updatedAt** | **OffsetDateTime** |  |  |



## Enum: StatusEnum

| Name | Value |
|---- | -----|
| ACTIVE | &quot;ACTIVE&quot; |
| ARCHIVED | &quot;ARCHIVED&quot; |
| PURGING | &quot;PURGING&quot; |



