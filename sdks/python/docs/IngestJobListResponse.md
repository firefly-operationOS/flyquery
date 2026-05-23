# IngestJobListResponse

Paginated list of ingest jobs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[IngestJobRead]**](IngestJobRead.md) |  | 
**limit** | **int** |  | 
**offset** | **int** |  | 
**total** | **int** |  | 

## Example

```python
from flyquery_sdk.models.ingest_job_list_response import IngestJobListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of IngestJobListResponse from a JSON string
ingest_job_list_response_instance = IngestJobListResponse.from_json(json)
# print the JSON string representation of the object
print(IngestJobListResponse.to_json())

# convert the object into a dict
ingest_job_list_response_dict = ingest_job_list_response_instance.to_dict()
# create an instance of IngestJobListResponse from a dict
ingest_job_list_response_from_dict = IngestJobListResponse.from_dict(ingest_job_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


