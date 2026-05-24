# PaginatedSnapshotRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[SnapshotRead]**](SnapshotRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_snapshot_read import PaginatedSnapshotRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedSnapshotRead from a JSON string
paginated_snapshot_read_instance = PaginatedSnapshotRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedSnapshotRead.to_json())

# convert the object into a dict
paginated_snapshot_read_dict = paginated_snapshot_read_instance.to_dict()
# create an instance of PaginatedSnapshotRead from a dict
paginated_snapshot_read_from_dict = PaginatedSnapshotRead.from_dict(paginated_snapshot_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


