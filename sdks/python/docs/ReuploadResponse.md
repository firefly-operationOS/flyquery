# ReuploadResponse

Response from PUT /datasets/{ds}/tables/{id}:upload.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** |  | 
**n_columns** | **int** |  | 
**n_rows_actual** | **int** |  | 
**snapshot_id** | **str** |  | 

## Example

```python
from flyquery_sdk.models.reupload_response import ReuploadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReuploadResponse from a JSON string
reupload_response_instance = ReuploadResponse.from_json(json)
# print the JSON string representation of the object
print(ReuploadResponse.to_json())

# convert the object into a dict
reupload_response_dict = reupload_response_instance.to_dict()
# create an instance of ReuploadResponse from a dict
reupload_response_from_dict = ReuploadResponse.from_dict(reupload_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


