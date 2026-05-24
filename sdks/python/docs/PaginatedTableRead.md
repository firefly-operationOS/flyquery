# PaginatedTableRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[TableRead]**](TableRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_table_read import PaginatedTableRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedTableRead from a JSON string
paginated_table_read_instance = PaginatedTableRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedTableRead.to_json())

# convert the object into a dict
paginated_table_read_dict = paginated_table_read_instance.to_dict()
# create an instance of PaginatedTableRead from a dict
paginated_table_read_from_dict = PaginatedTableRead.from_dict(paginated_table_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


