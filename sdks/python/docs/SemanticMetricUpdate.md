# SemanticMetricUpdate

Sparse-update payload for an existing semantic metric.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**definition_yaml** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**label** | **str** |  | [optional] 
**metric_type** | **str** |  | [optional] 

## Example

```python
from flyquery_sdk.models.semantic_metric_update import SemanticMetricUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticMetricUpdate from a JSON string
semantic_metric_update_instance = SemanticMetricUpdate.from_json(json)
# print the JSON string representation of the object
print(SemanticMetricUpdate.to_json())

# convert the object into a dict
semantic_metric_update_dict = semantic_metric_update_instance.to_dict()
# create an instance of SemanticMetricUpdate from a dict
semantic_metric_update_from_dict = SemanticMetricUpdate.from_dict(semantic_metric_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


