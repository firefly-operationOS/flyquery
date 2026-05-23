# ExampleRead

Full read representation of a flyquery_examples row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**citations_json** | **Dict[str, object]** |  | 
**created_at** | **datetime** |  | 
**created_by** | **str** |  | 
**dataset_id** | **UUID** |  | 
**generated_sql** | **str** |  | 
**id** | **UUID** |  | 
**last_used_at** | **datetime** |  | 
**normalised_sql** | **str** |  | 
**quality** | **str** |  | 
**question** | **str** |  | 
**source** | **str** |  | 
**tenant_id** | **str** |  | 
**usage_count** | **int** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.example_read import ExampleRead

# TODO update the JSON string below
json = "{}"
# create an instance of ExampleRead from a JSON string
example_read_instance = ExampleRead.from_json(json)
# print the JSON string representation of the object
print(ExampleRead.to_json())

# convert the object into a dict
example_read_dict = example_read_instance.to_dict()
# create an instance of ExampleRead from a dict
example_read_from_dict = ExampleRead.from_dict(example_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


