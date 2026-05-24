# PaginatedSemanticMetricRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[SemanticMetricRead]**](SemanticMetricRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_semantic_metric_read import PaginatedSemanticMetricRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedSemanticMetricRead from a JSON string
paginated_semantic_metric_read_instance = PaginatedSemanticMetricRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedSemanticMetricRead.to_json())

# convert the object into a dict
paginated_semantic_metric_read_dict = paginated_semantic_metric_read_instance.to_dict()
# create an instance of PaginatedSemanticMetricRead from a dict
paginated_semantic_metric_read_from_dict = PaginatedSemanticMetricRead.from_dict(paginated_semantic_metric_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


