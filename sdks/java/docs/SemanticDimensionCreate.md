

# SemanticDimensionCreate

Payload for creating a new semantic dimension.  The dimension's ``type`` (categorical|time) is taken from the ``definition_yaml`` body, not a separate request field.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**datasetId** | **UUID** |  |  |
|**definitionYaml** | **String** |  |  |
|**description** | **String** |  |  [optional] |
|**label** | **String** |  |  [optional] |
|**name** | **String** |  |  |



