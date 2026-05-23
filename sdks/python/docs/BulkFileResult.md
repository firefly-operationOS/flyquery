# BulkFileResult

Per-file outcome from POST /datasets/{id}/files:bulk.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **str** |  | [optional] 
**file_id** | **str** |  | [optional] 
**index** | **int** |  | 
**original_filename** | **str** |  | 
**status** | **str** |  | 
**tables** | [**List[TableSummary]**](TableSummary.md) |  | [optional] [default to []]

## Example

```python
from flyquery_sdk.models.bulk_file_result import BulkFileResult

# TODO update the JSON string below
json = "{}"
# create an instance of BulkFileResult from a JSON string
bulk_file_result_instance = BulkFileResult.from_json(json)
# print the JSON string representation of the object
print(BulkFileResult.to_json())

# convert the object into a dict
bulk_file_result_dict = bulk_file_result_instance.to_dict()
# create an instance of BulkFileResult from a dict
bulk_file_result_from_dict = BulkFileResult.from_dict(bulk_file_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


