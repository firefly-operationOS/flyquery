# IngestEventRead

One row from flyquery_ingest_events.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**id** | **int** |  | 
**ingest_job_id** | **UUID** |  | 
**message** | **str** |  | 
**payload_json** | **Dict[str, object]** |  | 
**stage** | **str** |  | 
**status** | **str** |  | 

## Example

```python
from flyquery_sdk.models.ingest_event_read import IngestEventRead

# TODO update the JSON string below
json = "{}"
# create an instance of IngestEventRead from a JSON string
ingest_event_read_instance = IngestEventRead.from_json(json)
# print the JSON string representation of the object
print(IngestEventRead.to_json())

# convert the object into a dict
ingest_event_read_dict = ingest_event_read_instance.to_dict()
# create an instance of IngestEventRead from a dict
ingest_event_read_from_dict = IngestEventRead.from_dict(ingest_event_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


