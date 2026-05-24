# QueryHistoryItem

Compact row for `GET /api/v1/queries` (history list).  Heavy JSONB columns (candidates, clarification, pii_findings) are omitted here so a 50-item page stays under a few KB; the detail endpoint exposes them via :class:`QueryDetailRead`.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ast_classification** | **str** |  | [optional] 
**clarification_emitted** | **bool** |  | [optional] [default to False]
**created_at** | **datetime** |  | 
**dataset_id** | **UUID** |  | [optional] 
**elapsed_ms** | **int** |  | [optional] 
**executed_sql** | **str** |  | [optional] 
**execution_status** | **str** |  | [optional] 
**finalised_at** | **datetime** |  | [optional] 
**id** | **UUID** |  | 
**question** | **str** |  | 
**retries** | **int** |  | [optional] [default to 0]
**row_count** | **int** |  | [optional] 
**semantic_path_taken** | **str** |  | [optional] 
**tenant_id** | **str** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.query_history_item import QueryHistoryItem

# TODO update the JSON string below
json = "{}"
# create an instance of QueryHistoryItem from a JSON string
query_history_item_instance = QueryHistoryItem.from_json(json)
# print the JSON string representation of the object
print(QueryHistoryItem.to_json())

# convert the object into a dict
query_history_item_dict = query_history_item_instance.to_dict()
# create an instance of QueryHistoryItem from a dict
query_history_item_from_dict = QueryHistoryItem.from_dict(query_history_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


