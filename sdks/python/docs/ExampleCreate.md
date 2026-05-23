# ExampleCreate

Payload for creating a new example (question + SQL pair).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**citations_json** | **Dict[str, object]** |  | [optional] 
**dataset_id** | **UUID** |  | [optional] 
**generated_sql** | **str** |  | 
**question** | **str** |  | 

## Example

```python
from flyquery_sdk.models.example_create import ExampleCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ExampleCreate from a JSON string
example_create_instance = ExampleCreate.from_json(json)
# print the JSON string representation of the object
print(ExampleCreate.to_json())

# convert the object into a dict
example_create_dict = example_create_instance.to_dict()
# create an instance of ExampleCreate from a dict
example_create_from_dict = ExampleCreate.from_dict(example_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


