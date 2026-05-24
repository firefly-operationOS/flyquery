# PaginatedSemanticDimensionRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[SemanticDimensionRead]**](SemanticDimensionRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_semantic_dimension_read import PaginatedSemanticDimensionRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedSemanticDimensionRead from a JSON string
paginated_semantic_dimension_read_instance = PaginatedSemanticDimensionRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedSemanticDimensionRead.to_json())

# convert the object into a dict
paginated_semantic_dimension_read_dict = paginated_semantic_dimension_read_instance.to_dict()
# create an instance of PaginatedSemanticDimensionRead from a dict
paginated_semantic_dimension_read_from_dict = PaginatedSemanticDimensionRead.from_dict(paginated_semantic_dimension_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


