# WorkspaceCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_direct_sql** | **bool** |  | [optional] [default to False]
**default_locale** | **str** |  | [optional] [default to 'en-US']
**kms_key_uri** | **str** |  | [optional] 
**metadata_json** | **Dict[str, object]** |  | [optional] 
**name** | **str** |  | 
**retention_days** | **int** |  | [optional] 
**slug** | **str** |  | 

## Example

```python
from flyquery_sdk.models.workspace_create import WorkspaceCreate

# TODO update the JSON string below
json = "{}"
# create an instance of WorkspaceCreate from a JSON string
workspace_create_instance = WorkspaceCreate.from_json(json)
# print the JSON string representation of the object
print(WorkspaceCreate.to_json())

# convert the object into a dict
workspace_create_dict = workspace_create_instance.to_dict()
# create an instance of WorkspaceCreate from a dict
workspace_create_from_dict = WorkspaceCreate.from_dict(workspace_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


