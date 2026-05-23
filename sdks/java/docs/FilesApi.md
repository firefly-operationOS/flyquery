# FilesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**reuploadFile**](FilesApi.md#reuploadFile) | **PUT** /api/v1/datasets/{dataset_id}/tables/{table_id}:upload | Re-upload into an existing table slot; creates a new snapshot. |
| [**uploadFile**](FilesApi.md#uploadFile) | **POST** /api/v1/datasets/{dataset_id}/files | Accept a multipart file upload and run the synchronous ingestion pipeline. |


<a id="reuploadFile"></a>
# **reuploadFile**
> ReuploadResponse reuploadFile(datasetId, tableId)

Re-upload into an existing table slot; creates a new snapshot.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.FilesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    FilesApi apiInstance = new FilesApi(defaultClient);
    String datasetId = "datasetId_example"; // String | 
    String tableId = "tableId_example"; // String | 
    try {
      ReuploadResponse result = apiInstance.reuploadFile(datasetId, tableId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling FilesApi#reuploadFile");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **datasetId** | **String**|  | |
| **tableId** | **String**|  | |

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
| **201** | Successful response |  -  |

<a id="uploadFile"></a>
# **uploadFile**
> FileUploadResponse uploadFile(datasetId)

Accept a multipart file upload and run the synchronous ingestion pipeline.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.FilesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    FilesApi apiInstance = new FilesApi(defaultClient);
    String datasetId = "datasetId_example"; // String | 
    try {
      FileUploadResponse result = apiInstance.uploadFile(datasetId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling FilesApi#uploadFile");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **datasetId** | **String**|  | |

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
| **201** | Successful response |  -  |

