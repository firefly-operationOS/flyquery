# BatchQueryRequest

Request body for ``POST /api/v1/query:batch``.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**queries** | [**List[BatchQueryItem]**](BatchQueryItem.md) |  | 

## Example

```python
from flyquery_sdk.models.batch_query_request import BatchQueryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BatchQueryRequest from a JSON string
batch_query_request_instance = BatchQueryRequest.from_json(json)
# print the JSON string representation of the object
print(BatchQueryRequest.to_json())

# convert the object into a dict
batch_query_request_dict = batch_query_request_instance.to_dict()
# create an instance of BatchQueryRequest from a dict
batch_query_request_from_dict = BatchQueryRequest.from_dict(batch_query_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


