# SemanticMetricCreate

Payload for creating a new semantic metric.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **UUID** |  | 
**definition_yaml** | **str** |  | 
**description** | **str** |  | [optional] 
**label** | **str** |  | [optional] 
**metric_type** | **str** |  | [optional] [default to 'SIMPLE']
**name** | **str** |  | 

## Example

```python
from flyquery_sdk.models.semantic_metric_create import SemanticMetricCreate

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticMetricCreate from a JSON string
semantic_metric_create_instance = SemanticMetricCreate.from_json(json)
# print the JSON string representation of the object
print(SemanticMetricCreate.to_json())

# convert the object into a dict
semantic_metric_create_dict = semantic_metric_create_instance.to_dict()
# create an instance of SemanticMetricCreate from a dict
semantic_metric_create_from_dict = SemanticMetricCreate.from_dict(semantic_metric_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


