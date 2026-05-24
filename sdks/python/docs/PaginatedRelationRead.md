# PaginatedRelationRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[RelationRead]**](RelationRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_relation_read import PaginatedRelationRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedRelationRead from a JSON string
paginated_relation_read_instance = PaginatedRelationRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedRelationRead.to_json())

# convert the object into a dict
paginated_relation_read_dict = paginated_relation_read_instance.to_dict()
# create an instance of PaginatedRelationRead from a dict
paginated_relation_read_from_dict = PaginatedRelationRead.from_dict(paginated_relation_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


