

# SemanticDimensionCreate

Payload for creating a new semantic dimension.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**datasetId** | **UUID** |  |  |
|**definitionYaml** | **String** |  |  |
|**description** | **String** |  |  [optional] |
|**label** | **String** |  |  [optional] |
|**metricType** | [**MetricTypeEnum**](#MetricTypeEnum) |  |  [optional] |
|**name** | **String** |  |  |



## Enum: MetricTypeEnum

| Name | Value |
|---- | -----|
| SIMPLE | &quot;SIMPLE&quot; |
| RATIO | &quot;RATIO&quot; |
| DERIVED | &quot;DERIVED&quot; |
| CUMULATIVE | &quot;CUMULATIVE&quot; |



