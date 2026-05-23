# FilesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**reuploadFile**](FilesApi.md#reuploadFile) | **PUT** /api/v1/datasets/{dataset_id}/tables/{table_id}:upload | Re-upload into an existing table slot; creates a new snapshot. |
| [**uploadFile**](FilesApi.md#uploadFile) | **POST** /api/v1/datasets/{dataset_id}/files | Accept a multipart file upload and run the synchronous ingestion pipeline. |
| [**uploadFilesBulk**](FilesApi.md#uploadFilesBulk) | **POST** /api/v1/datasets/{dataset_id}/files:bulk | Accept multiple files in one multipart request and ingest each. |



## reuploadFile

> ReuploadResponse reuploadFile(datasetId, tableId)

Re-upload into an existing table slot; creates a new snapshot.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

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


## uploadFile

> FileUploadResponse uploadFile(datasetId)

Accept a multipart file upload and run the synchronous ingestion pipeline.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

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


## uploadFilesBulk

> BulkFileUploadResponse uploadFilesBulk(datasetId)

Accept multiple files in one multipart request and ingest each.

Each &#x60;&#x60;files&#x60;&#x60; part is processed through the same per-file pipeline as &#x60;&#x60;POST /files&#x60;&#x60; (receive -&gt; parse -&gt; reconcile -&gt; sample -&gt; profile -&gt; describe -&gt; embed -&gt; publish), and the per-file results run **in parallel** through &#x60;&#x60;asyncio.gather&#x60;&#x60; -- a 5-file upload finishes in roughly the time of a single file.  Per-file failures do NOT abort the bulk. The response carries one &#x60;&#x60;BulkFileResult&#x60;&#x60; per submitted file with either &#x60;&#x60;status&#x3D;\&quot;OK\&quot;&#x60;&#x60; + &#x60;&#x60;file_id&#x60;&#x60; + &#x60;&#x60;tables&#x60;&#x60; or &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60;. Aggregate &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts let a UI render progress without scanning the list.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FilesApi apiInstance = new FilesApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            BulkFileUploadResponse result = apiInstance.uploadFilesBulk(datasetId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FilesApi#uploadFilesBulk");
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

[**BulkFileUploadResponse**](BulkFileUploadResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |

