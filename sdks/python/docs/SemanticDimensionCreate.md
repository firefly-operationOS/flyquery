# SemanticDimensionCreate

Payload for creating a new semantic dimension.  The dimension's ``type`` (categorical|time) is taken from the ``definition_yaml`` body, not a separate request field.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **UUID** |  | 
**definition_yaml** | **str** |  | 
**description** | **str** |  | [optional] 
**label** | **str** |  | [optional] 
**name** | **str** |  | 

## Example

```python
from flyquery_sdk.models.semantic_dimension_create import SemanticDimensionCreate

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticDimensionCreate from a JSON string
semantic_dimension_create_instance = SemanticDimensionCreate.from_json(json)
# print the JSON string representation of the object
print(SemanticDimensionCreate.to_json())

# convert the object into a dict
semantic_dimension_create_dict = semantic_dimension_create_instance.to_dict()
# create an instance of SemanticDimensionCreate from a dict
semantic_dimension_create_from_dict = SemanticDimensionCreate.from_dict(semantic_dimension_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


