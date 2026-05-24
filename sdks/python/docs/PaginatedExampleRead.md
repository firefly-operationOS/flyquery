# PaginatedExampleRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[ExampleRead]**](ExampleRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_example_read import PaginatedExampleRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedExampleRead from a JSON string
paginated_example_read_instance = PaginatedExampleRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedExampleRead.to_json())

# convert the object into a dict
paginated_example_read_dict = paginated_example_read_instance.to_dict()
# create an instance of PaginatedExampleRead from a dict
paginated_example_read_from_dict = PaginatedExampleRead.from_dict(paginated_example_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


