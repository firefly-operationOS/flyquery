# SnapshotRead

Response for GET /tables/{id}/snapshots items.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**n_columns** | **int** |  | 
**n_rows_actual** | **int** |  | 
**n_rows_estimate** | **int** |  | 
**parquet_byte_size** | **int** |  | 
**status** | **str** |  | 
**table_id** | **UUID** |  | 
**taken_at** | **datetime** |  | 
**triggered_by** | **str** |  | 

## Example

```python
from flyquery_sdk.models.snapshot_read import SnapshotRead

# TODO update the JSON string below
json = "{}"
# create an instance of SnapshotRead from a JSON string
snapshot_read_instance = SnapshotRead.from_json(json)
# print the JSON string representation of the object
print(SnapshotRead.to_json())

# convert the object into a dict
snapshot_read_dict = snapshot_read_instance.to_dict()
# create an instance of SnapshotRead from a dict
snapshot_read_from_dict = SnapshotRead.from_dict(snapshot_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


