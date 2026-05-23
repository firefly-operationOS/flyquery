# DatasetsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**archive**](DatasetsApi.md#archive) | **DELETE** /api/v1/datasets/{dataset_id} | Archive a dataset (set status&#x3D;ARCHIVED). |
| [**create**](DatasetsApi.md#create) | **POST** /api/v1/datasets | Create a dataset; tenant + workspace come from request headers. |
| [**listDatasets**](DatasetsApi.md#listDatasets) | **GET** /api/v1/datasets | Return all datasets for the caller&#39;s tenant+workspace. |
| [**read**](DatasetsApi.md#read) | **GET** /api/v1/datasets/{dataset_id} | Fetch a single dataset by id. Returns 404 if not found. |
| [**update**](DatasetsApi.md#update) | **PUT** /api/v1/datasets/{dataset_id} | Sparse-update a dataset. Only fields present in body are changed. |



## archive

> DatasetRead archive(datasetId)

Archive a dataset (set status&#x3D;ARCHIVED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.DatasetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DatasetsApi apiInstance = new DatasetsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            DatasetRead result = apiInstance.archive(datasetId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DatasetsApi#archive");
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

[**DatasetRead**](DatasetRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## create

> DatasetRead create(datasetCreate)

Create a dataset; tenant + workspace come from request headers.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.DatasetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DatasetsApi apiInstance = new DatasetsApi(defaultClient);
        DatasetCreate datasetCreate = new DatasetCreate(); // DatasetCreate | 
        try {
            DatasetRead result = apiInstance.create(datasetCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DatasetsApi#create");
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
| **datasetCreate** | [**DatasetCreate**](DatasetCreate.md)|  | |

### Return type

[**DatasetRead**](DatasetRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |
| **422** | Validation Error |  -  |


## listDatasets

> listDatasets()

Return all datasets for the caller&#39;s tenant+workspace.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.DatasetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DatasetsApi apiInstance = new DatasetsApi(defaultClient);
        try {
            apiInstance.listDatasets();
        } catch (ApiException e) {
            System.err.println("Exception when calling DatasetsApi#listDatasets");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## read

> DatasetRead read(datasetId)

Fetch a single dataset by id. Returns 404 if not found.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.DatasetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DatasetsApi apiInstance = new DatasetsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            DatasetRead result = apiInstance.read(datasetId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DatasetsApi#read");
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

[**DatasetRead**](DatasetRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## update

> DatasetRead update(datasetId, datasetUpdate)

Sparse-update a dataset. Only fields present in body are changed.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.DatasetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DatasetsApi apiInstance = new DatasetsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        DatasetUpdate datasetUpdate = new DatasetUpdate(); // DatasetUpdate | 
        try {
            DatasetRead result = apiInstance.update(datasetId, datasetUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DatasetsApi#update");
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
| **datasetUpdate** | [**DatasetUpdate**](DatasetUpdate.md)|  | |

### Return type

[**DatasetRead**](DatasetRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |
| **422** | Validation Error |  -  |

