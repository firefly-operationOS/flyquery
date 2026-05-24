# PaginatedSchemaChangeRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[SchemaChangeRead]**](SchemaChangeRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_schema_change_read import PaginatedSchemaChangeRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedSchemaChangeRead from a JSON string
paginated_schema_change_read_instance = PaginatedSchemaChangeRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedSchemaChangeRead.to_json())

# convert the object into a dict
paginated_schema_change_read_dict = paginated_schema_change_read_instance.to_dict()
# create an instance of PaginatedSchemaChangeRead from a dict
paginated_schema_change_read_from_dict = PaginatedSchemaChangeRead.from_dict(paginated_schema_change_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


