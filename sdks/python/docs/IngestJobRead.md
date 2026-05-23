# IngestJobRead

Response for GET /api/v1/ingest-jobs/{id} and list items.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attempts** | **int** |  | 
**cost_cents** | [**CostCents**](CostCents.md) |  | 
**dataset_id** | **UUID** |  | 
**elapsed_ms** | **int** |  | 
**file_id** | **UUID** |  | 
**finished_at** | **datetime** |  | 
**id** | **UUID** |  | 
**job_kind** | **str** |  | 
**request_json** | **Dict[str, object]** |  | 
**result_json** | **Dict[str, object]** |  | 
**snapshot_id** | **UUID** |  | 
**started_at** | **datetime** |  | 
**status** | **str** |  | 
**table_id** | **UUID** |  | 
**tenant_id** | **str** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.ingest_job_read import IngestJobRead

# TODO update the JSON string below
json = "{}"
# create an instance of IngestJobRead from a JSON string
ingest_job_read_instance = IngestJobRead.from_json(json)
# print the JSON string representation of the object
print(IngestJobRead.to_json())

# convert the object into a dict
ingest_job_read_dict = ingest_job_read_instance.to_dict()
# create an instance of IngestJobRead from a dict
ingest_job_read_from_dict = IngestJobRead.from_dict(ingest_job_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


