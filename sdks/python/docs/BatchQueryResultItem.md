# BatchQueryResultItem

One outcome in a batch query response.  Mirrors ``AnswerResponse`` for OK results; carries ``error`` + ``status=\"FAILED\"`` on failure so the batch never aborts on one bad item.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chart_hint** | **str** |  | [optional] 
**elapsed_ms** | **int** |  | [optional] 
**error** | **str** |  | [optional] 
**execution_status** | **str** |  | [optional] 
**explanation** | **str** |  | [optional] 
**grounded_summary** | **Dict[str, object]** |  | [optional] 
**index** | **int** |  | 
**preview** | **List[Dict[str, object]]** |  | [optional] 
**query_id** | **UUID** |  | [optional] 
**row_count** | **int** |  | [optional] 
**sql** | **str** |  | [optional] 
**status** | **str** |  | 

## Example

```python
from flyquery_sdk.models.batch_query_result_item import BatchQueryResultItem

# TODO update the JSON string below
json = "{}"
# create an instance of BatchQueryResultItem from a JSON string
batch_query_result_item_instance = BatchQueryResultItem.from_json(json)
# print the JSON string representation of the object
print(BatchQueryResultItem.to_json())

# convert the object into a dict
batch_query_result_item_dict = batch_query_result_item_instance.to_dict()
# create an instance of BatchQueryResultItem from a dict
batch_query_result_item_from_dict = BatchQueryResultItem.from_dict(batch_query_result_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


