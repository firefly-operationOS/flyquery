# PaginatedWorkspaceRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[WorkspaceRead]**](WorkspaceRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_workspace_read import PaginatedWorkspaceRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedWorkspaceRead from a JSON string
paginated_workspace_read_instance = PaginatedWorkspaceRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedWorkspaceRead.to_json())

# convert the object into a dict
paginated_workspace_read_dict = paginated_workspace_read_instance.to_dict()
# create an instance of PaginatedWorkspaceRead from a dict
paginated_workspace_read_from_dict = PaginatedWorkspaceRead.from_dict(paginated_workspace_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


