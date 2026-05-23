

# ExampleRead

Full read representation of a flyquery_examples row.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**citationsJson** | **Map&lt;String, Object&gt;** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**createdBy** | **String** |  |  |
|**datasetId** | **UUID** |  |  |
|**generatedSql** | **String** |  |  |
|**id** | **UUID** |  |  |
|**lastUsedAt** | **OffsetDateTime** |  |  |
|**normalisedSql** | **String** |  |  |
|**quality** | [**QualityEnum**](#QualityEnum) |  |  |
|**question** | **String** |  |  |
|**source** | [**SourceEnum**](#SourceEnum) |  |  |
|**tenantId** | **String** |  |  |
|**usageCount** | **Integer** |  |  |
|**workspaceId** | **UUID** |  |  |



## Enum: QualityEnum

| Name | Value |
|---- | -----|
| PROPOSED | &quot;PROPOSED&quot; |
| APPROVED | &quot;APPROVED&quot; |
| REJECTED | &quot;REJECTED&quot; |



## Enum: SourceEnum

| Name | Value |
|---- | -----|
| USER_CURATED | &quot;USER_CURATED&quot; |
| AGENT_LEARNED | &quot;AGENT_LEARNED&quot; |



