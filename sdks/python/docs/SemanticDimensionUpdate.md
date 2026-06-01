# SemanticDimensionUpdate

Sparse-update payload for an existing semantic dimension.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**definition_yaml** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**label** | **str** |  | [optional] 

## Example

```python
from flyquery_sdk.models.semantic_dimension_update import SemanticDimensionUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticDimensionUpdate from a JSON string
semantic_dimension_update_instance = SemanticDimensionUpdate.from_json(json)
# print the JSON string representation of the object
print(SemanticDimensionUpdate.to_json())

# convert the object into a dict
semantic_dimension_update_dict = semantic_dimension_update_instance.to_dict()
# create an instance of SemanticDimensionUpdate from a dict
semantic_dimension_update_from_dict = SemanticDimensionUpdate.from_dict(semantic_dimension_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


