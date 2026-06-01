

# SemanticDimensionRead

Full read representation of a flyquery_semantic_dimensions row.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**compiledSqlTemplate** | **String** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**currentVersion** | **Integer** |  |  |
|**datasetId** | **UUID** |  |  |
|**definitionYaml** | **String** |  |  |
|**description** | **String** |  |  |
|**dimensionType** | [**DimensionTypeEnum**](#DimensionTypeEnum) |  |  |
|**id** | **UUID** |  |  |
|**label** | **String** |  |  |
|**metadataJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**name** | **String** |  |  |
|**status** | [**StatusEnum**](#StatusEnum) |  |  |
|**tenantId** | **String** |  |  |
|**updatedAt** | **OffsetDateTime** |  |  |
|**workspaceId** | **UUID** |  |  |



## Enum: DimensionTypeEnum

| Name | Value |
|---- | -----|
| CATEGORICAL | &quot;categorical&quot; |
| TIME | &quot;time&quot; |



## Enum: StatusEnum

| Name | Value |
|---- | -----|
| DRAFT | &quot;DRAFT&quot; |
| PUBLISHED | &quot;PUBLISHED&quot; |
| RETIRED | &quot;RETIRED&quot; |



