# DatasetRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**default_locale** | **str** |  | 
**description** | **str** |  | 
**drift_policy** | **str** |  | 
**id** | **UUID** |  | 
**ingest_policy_json** | **Dict[str, object]** |  | 
**metadata_json** | **Dict[str, object]** |  | 
**name** | **str** |  | 
**status** | **str** |  | 
**tenant_id** | **str** |  | 
**updated_at** | **datetime** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.dataset_read import DatasetRead

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetRead from a JSON string
dataset_read_instance = DatasetRead.from_json(json)
# print the JSON string representation of the object
print(DatasetRead.to_json())

# convert the object into a dict
dataset_read_dict = dataset_read_instance.to_dict()
# create an instance of DatasetRead from a dict
dataset_read_from_dict = DatasetRead.from_dict(dataset_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


