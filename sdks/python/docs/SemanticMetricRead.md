# SemanticMetricRead

Full read representation of a flyquery_semantic_metrics row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**compiled_sql_template** | **str** |  | 
**created_at** | **datetime** |  | 
**current_version** | **int** |  | 
**dataset_id** | **UUID** |  | 
**definition_yaml** | **str** |  | 
**description** | **str** |  | 
**id** | **UUID** |  | 
**label** | **str** |  | 
**metric_type** | **str** |  | 
**name** | **str** |  | 
**status** | **str** |  | 
**tenant_id** | **str** |  | 
**updated_at** | **datetime** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.semantic_metric_read import SemanticMetricRead

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticMetricRead from a JSON string
semantic_metric_read_instance = SemanticMetricRead.from_json(json)
# print the JSON string representation of the object
print(SemanticMetricRead.to_json())

# convert the object into a dict
semantic_metric_read_dict = semantic_metric_read_instance.to_dict()
# create an instance of SemanticMetricRead from a dict
semantic_metric_read_from_dict = SemanticMetricRead.from_dict(semantic_metric_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


