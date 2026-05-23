# flyquery_sdk.FilesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**reupload_file**](FilesApi.md#reupload_file) | **PUT** /api/v1/datasets/{dataset_id}/tables/{table_id}:upload | Re-upload into an existing table slot; creates a new snapshot.
[**upload_file**](FilesApi.md#upload_file) | **POST** /api/v1/datasets/{dataset_id}/files | Accept a multipart file upload and run the synchronous ingestion pipeline.


# **reupload_file**
> ReuploadResponse reupload_file(dataset_id, table_id)

Re-upload into an existing table slot; creates a new snapshot.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.reupload_response import ReuploadResponse
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.FilesApi(api_client)
    dataset_id = 'dataset_id_example' # str | 
    table_id = 'table_id_example' # str | 

    try:
        # Re-upload into an existing table slot; creates a new snapshot.
        api_response = await api_instance.reupload_file(dataset_id, table_id)
        print("The response of FilesApi->reupload_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->reupload_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 
 **table_id** | **str**|  | 

### Return type

[**ReuploadResponse**](ReuploadResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file**
> FileUploadResponse upload_file(dataset_id)

Accept a multipart file upload and run the synchronous ingestion pipeline.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.file_upload_response import FileUploadResponse
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.FilesApi(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Accept a multipart file upload and run the synchronous ingestion pipeline.
        api_response = await api_instance.upload_file(dataset_id)
        print("The response of FilesApi->upload_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->upload_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 

### Return type

[**FileUploadResponse**](FileUploadResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

