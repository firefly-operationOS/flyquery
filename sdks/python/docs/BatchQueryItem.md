# BatchQueryItem

One question in a batch -- matches ``AnswerRequest`` minus headers.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversation_id** | **UUID** |  | [optional] 
**dataset_id** | **UUID** |  | 
**question** | **str** |  | 

## Example

```python
from flyquery_sdk.models.batch_query_item import BatchQueryItem

# TODO update the JSON string below
json = "{}"
# create an instance of BatchQueryItem from a JSON string
batch_query_item_instance = BatchQueryItem.from_json(json)
# print the JSON string representation of the object
print(BatchQueryItem.to_json())

# convert the object into a dict
batch_query_item_dict = batch_query_item_instance.to_dict()
# create an instance of BatchQueryItem from a dict
batch_query_item_from_dict = BatchQueryItem.from_dict(batch_query_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


