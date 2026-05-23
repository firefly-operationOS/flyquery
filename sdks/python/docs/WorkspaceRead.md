# WorkspaceRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_direct_sql** | **bool** |  | 
**created_at** | **datetime** |  | 
**default_locale** | **str** |  | 
**id** | **UUID** |  | 
**kms_key_uri** | **str** |  | 
**metadata_json** | **Dict[str, object]** |  | 
**name** | **str** |  | 
**retention_days** | **int** |  | 
**slug** | **str** |  | 
**status** | **str** |  | 
**storage_used_bytes** | **int** |  | 
**tenant_id** | **str** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from flyquery_sdk.models.workspace_read import WorkspaceRead

# TODO update the JSON string below
json = "{}"
# create an instance of WorkspaceRead from a JSON string
workspace_read_instance = WorkspaceRead.from_json(json)
# print the JSON string representation of the object
print(WorkspaceRead.to_json())

# convert the object into a dict
workspace_read_dict = workspace_read_instance.to_dict()
# create an instance of WorkspaceRead from a dict
workspace_read_from_dict = WorkspaceRead.from_dict(workspace_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


