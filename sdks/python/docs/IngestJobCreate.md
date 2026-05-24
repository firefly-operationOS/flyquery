# IngestJobCreate

Request body for POST /api/v1/ingest-jobs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**callback** | [**CallbackConfig**](CallbackConfig.md) | Optional webhook delivered after the job reaches a terminal status (SUCCEEDED, FAILED, or CANCELLED). See :class:&#x60;CallbackConfig&#x60; for the at-least-once delivery contract. | [optional] 
**dataset_id** | **UUID** |  | 
**file_id** | **UUID** |  | [optional] 
**job_kind** | **str** |  | 
**request_json** | **Dict[str, object]** |  | [optional] 
**table_id** | **UUID** |  | [optional] 

## Example

```python
from flyquery_sdk.models.ingest_job_create import IngestJobCreate

# TODO update the JSON string below
json = "{}"
# create an instance of IngestJobCreate from a JSON string
ingest_job_create_instance = IngestJobCreate.from_json(json)
# print the JSON string representation of the object
print(IngestJobCreate.to_json())

# convert the object into a dict
ingest_job_create_dict = ingest_job_create_instance.to_dict()
# create an instance of IngestJobCreate from a dict
ingest_job_create_from_dict = IngestJobCreate.from_dict(ingest_job_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


