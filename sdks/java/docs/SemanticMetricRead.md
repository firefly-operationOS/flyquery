

# SemanticMetricRead

Full read representation of a flyquery_semantic_metrics row.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**compiledSqlTemplate** | **String** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**currentVersion** | **Integer** |  |  |
|**datasetId** | **UUID** |  |  |
|**definitionYaml** | **String** |  |  |
|**description** | **String** |  |  |
|**id** | **UUID** |  |  |
|**label** | **String** |  |  |
|**metricType** | [**MetricTypeEnum**](#MetricTypeEnum) |  |  |
|**name** | **String** |  |  |
|**status** | [**StatusEnum**](#StatusEnum) |  |  |
|**tenantId** | **String** |  |  |
|**updatedAt** | **OffsetDateTime** |  |  |
|**workspaceId** | **UUID** |  |  |



## Enum: MetricTypeEnum

| Name | Value |
|---- | -----|
| SIMPLE | &quot;SIMPLE&quot; |
| RATIO | &quot;RATIO&quot; |
| DERIVED | &quot;DERIVED&quot; |
| CUMULATIVE | &quot;CUMULATIVE&quot; |



## Enum: StatusEnum

| Name | Value |
|---- | -----|
| DRAFT | &quot;DRAFT&quot; |
| PUBLISHED | &quot;PUBLISHED&quot; |
| RETIRED | &quot;RETIRED&quot; |



