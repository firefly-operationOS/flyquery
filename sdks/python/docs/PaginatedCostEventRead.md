# PaginatedCostEventRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[CostEventRead]**](CostEventRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_cost_event_read import PaginatedCostEventRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedCostEventRead from a JSON string
paginated_cost_event_read_instance = PaginatedCostEventRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedCostEventRead.to_json())

# convert the object into a dict
paginated_cost_event_read_dict = paginated_cost_event_read_instance.to_dict()
# create an instance of PaginatedCostEventRead from a dict
paginated_cost_event_read_from_dict = PaginatedCostEventRead.from_dict(paginated_cost_event_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


