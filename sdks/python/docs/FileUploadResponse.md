# FileUploadResponse

Response from POST /datasets/{id}/files.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** |  | 
**tables** | [**List[TableSummary]**](TableSummary.md) |  | 

## Example

```python
from flyquery_sdk.models.file_upload_response import FileUploadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FileUploadResponse from a JSON string
file_upload_response_instance = FileUploadResponse.from_json(json)
# print the JSON string representation of the object
print(FileUploadResponse.to_json())

# convert the object into a dict
file_upload_response_dict = file_upload_response_instance.to_dict()
# create an instance of FileUploadResponse from a dict
file_upload_response_from_dict = FileUploadResponse.from_dict(file_upload_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


