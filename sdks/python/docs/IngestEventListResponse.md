# IngestEventListResponse

Paginated event ledger for GET /ingest-jobs/{id}/events.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[IngestEventRead]**](IngestEventRead.md) |  | 
**limit** | **int** |  | 
**offset** | **int** |  | 
**total** | **int** |  | 

## Example

```python
from flyquery_sdk.models.ingest_event_list_response import IngestEventListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of IngestEventListResponse from a JSON string
ingest_event_list_response_instance = IngestEventListResponse.from_json(json)
# print the JSON string representation of the object
print(IngestEventListResponse.to_json())

# convert the object into a dict
ingest_event_list_response_dict = ingest_event_list_response_instance.to_dict()
# create an instance of IngestEventListResponse from a dict
ingest_event_list_response_from_dict = IngestEventListResponse.from_dict(ingest_event_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


