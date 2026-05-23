

# DatasetRead


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**createdAt** | **OffsetDateTime** |  |  |
|**defaultLocale** | **String** |  |  |
|**description** | **String** |  |  |
|**driftPolicy** | [**DriftPolicyEnum**](#DriftPolicyEnum) |  |  |
|**id** | **UUID** |  |  |
|**ingestPolicyJson** | **Map&lt;String, Object&gt;** |  |  |
|**metadataJson** | **Map&lt;String, Object&gt;** |  |  |
|**name** | **String** |  |  |
|**status** | [**StatusEnum**](#StatusEnum) |  |  |
|**tenantId** | **String** |  |  |
|**updatedAt** | **OffsetDateTime** |  |  |
|**workspaceId** | **UUID** |  |  |



## Enum: DriftPolicyEnum

| Name | Value |
|---- | -----|
| AUTO | &quot;AUTO&quot; |
| MANUAL | &quot;MANUAL&quot; |



## Enum: StatusEnum

| Name | Value |
|---- | -----|
| ACTIVE | &quot;ACTIVE&quot; |
| ARCHIVED | &quot;ARCHIVED&quot; |



