# WorkspaceStats

Response from GET /api/v1/stats -- compact workspace summary.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_count** | **int** |  | 
**ingest_job_count_pending** | **int** |  | 
**query_count_last_30d** | **int** |  | 
**storage_used_bytes** | **int** |  | 
**table_count** | **int** |  | 
**token_count_last_30d** | **int** |  | 

## Example

```python
from flyquery_sdk.models.workspace_stats import WorkspaceStats

# TODO update the JSON string below
json = "{}"
# create an instance of WorkspaceStats from a JSON string
workspace_stats_instance = WorkspaceStats.from_json(json)
# print the JSON string representation of the object
print(WorkspaceStats.to_json())

# convert the object into a dict
workspace_stats_dict = workspace_stats_instance.to_dict()
# create an instance of WorkspaceStats from a dict
workspace_stats_from_dict = WorkspaceStats.from_dict(workspace_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


