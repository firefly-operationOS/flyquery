# PaginatedSchemaObjectRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[SchemaObjectRead]**](SchemaObjectRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_schema_object_read import PaginatedSchemaObjectRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedSchemaObjectRead from a JSON string
paginated_schema_object_read_instance = PaginatedSchemaObjectRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedSchemaObjectRead.to_json())

# convert the object into a dict
paginated_schema_object_read_dict = paginated_schema_object_read_instance.to_dict()
# create an instance of PaginatedSchemaObjectRead from a dict
paginated_schema_object_read_from_dict = PaginatedSchemaObjectRead.from_dict(paginated_schema_object_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


