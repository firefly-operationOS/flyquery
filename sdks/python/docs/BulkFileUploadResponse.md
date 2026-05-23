# BulkFileUploadResponse

Response from POST /datasets/{id}/files:bulk.  Returns one ``results`` entry per uploaded file. Per-file failures do NOT abort the bulk -- the caller sees which files succeeded and which didn't, with the error message inline. Aggregate counts let a UI render \"4/5 uploaded successfully\" without scanning the list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**failed** | **int** |  | 
**results** | [**List[BulkFileResult]**](BulkFileResult.md) |  | 
**succeeded** | **int** |  | 
**total_files** | **int** |  | 

## Example

```python
from flyquery_sdk.models.bulk_file_upload_response import BulkFileUploadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkFileUploadResponse from a JSON string
bulk_file_upload_response_instance = BulkFileUploadResponse.from_json(json)
# print the JSON string representation of the object
print(BulkFileUploadResponse.to_json())

# convert the object into a dict
bulk_file_upload_response_dict = bulk_file_upload_response_instance.to_dict()
# create an instance of BulkFileUploadResponse from a dict
bulk_file_upload_response_from_dict = BulkFileUploadResponse.from_dict(bulk_file_upload_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


