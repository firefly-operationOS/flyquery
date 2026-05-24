# PaginatedSemanticVersionRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[SemanticVersionRead]**](SemanticVersionRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_semantic_version_read import PaginatedSemanticVersionRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedSemanticVersionRead from a JSON string
paginated_semantic_version_read_instance = PaginatedSemanticVersionRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedSemanticVersionRead.to_json())

# convert the object into a dict
paginated_semantic_version_read_dict = paginated_semantic_version_read_instance.to_dict()
# create an instance of PaginatedSemanticVersionRead from a dict
paginated_semantic_version_read_from_dict = PaginatedSemanticVersionRead.from_dict(paginated_semantic_version_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


