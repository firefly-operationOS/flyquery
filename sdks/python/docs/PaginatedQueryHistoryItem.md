# PaginatedQueryHistoryItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[QueryHistoryItem]**](QueryHistoryItem.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_query_history_item import PaginatedQueryHistoryItem

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedQueryHistoryItem from a JSON string
paginated_query_history_item_instance = PaginatedQueryHistoryItem.from_json(json)
# print the JSON string representation of the object
print(PaginatedQueryHistoryItem.to_json())

# convert the object into a dict
paginated_query_history_item_dict = paginated_query_history_item_instance.to_dict()
# create an instance of PaginatedQueryHistoryItem from a dict
paginated_query_history_item_from_dict = PaginatedQueryHistoryItem.from_dict(paginated_query_history_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


