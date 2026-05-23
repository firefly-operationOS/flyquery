# DatasetUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_locale** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**drift_policy** | **str** |  | [optional] 
**ingest_policy_json** | **Dict[str, object]** |  | [optional] 
**metadata_json** | **Dict[str, object]** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from flyquery_sdk.models.dataset_update import DatasetUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetUpdate from a JSON string
dataset_update_instance = DatasetUpdate.from_json(json)
# print the JSON string representation of the object
print(DatasetUpdate.to_json())

# convert the object into a dict
dataset_update_dict = dataset_update_instance.to_dict()
# create an instance of DatasetUpdate from a dict
dataset_update_from_dict = DatasetUpdate.from_dict(dataset_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


