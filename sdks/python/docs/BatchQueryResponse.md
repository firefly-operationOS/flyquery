# BatchQueryResponse

Response from ``POST /api/v1/query:batch``.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**failed** | **int** |  | 
**results** | [**List[BatchQueryResultItem]**](BatchQueryResultItem.md) |  | 
**succeeded** | **int** |  | 
**total_queries** | **int** |  | 

## Example

```python
from flyquery_sdk.models.batch_query_response import BatchQueryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BatchQueryResponse from a JSON string
batch_query_response_instance = BatchQueryResponse.from_json(json)
# print the JSON string representation of the object
print(BatchQueryResponse.to_json())

# convert the object into a dict
batch_query_response_dict = batch_query_response_instance.to_dict()
# create an instance of BatchQueryResponse from a dict
batch_query_response_from_dict = BatchQueryResponse.from_dict(batch_query_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


