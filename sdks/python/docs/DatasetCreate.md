# DatasetCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_locale** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**drift_policy** | **str** |  | [optional] [default to 'AUTO']
**ingest_policy_json** | **Dict[str, object]** |  | [optional] 
**metadata_json** | **Dict[str, object]** |  | [optional] 
**name** | **str** |  | 

## Example

```python
from flyquery_sdk.models.dataset_create import DatasetCreate

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetCreate from a JSON string
dataset_create_instance = DatasetCreate.from_json(json)
# print the JSON string representation of the object
print(DatasetCreate.to_json())

# convert the object into a dict
dataset_create_dict = dataset_create_instance.to_dict()
# create an instance of DatasetCreate from a dict
dataset_create_from_dict = DatasetCreate.from_dict(dataset_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


