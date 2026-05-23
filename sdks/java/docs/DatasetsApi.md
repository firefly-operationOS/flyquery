# DatasetsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**archive**](DatasetsApi.md#archive) | **DELETE** /api/v1/datasets/{dataset_id} | Archive a dataset (set status&#x3D;ARCHIVED). |
| [**create**](DatasetsApi.md#create) | **POST** /api/v1/datasets | Create a dataset; tenant + workspace come from request headers. |
| [**listDatasets**](DatasetsApi.md#listDatasets) | **GET** /api/v1/datasets | Search/filter datasets for the caller&#39;s tenant. |
| [**read**](DatasetsApi.md#read) | **GET** /api/v1/datasets/{dataset_id} | Fetch a single dataset by id. Returns 404 if not found. |
| [**readByName**](DatasetsApi.md#readByName) | **GET** /api/v1/datasets/by-name/{name} | Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;. |
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

> listDatasets(q, name, status, workspaceId, limit, offset)

Search/filter datasets for the caller&#39;s tenant.

Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;            -- free-text substring against &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;description&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;         -- exact match -- gives you name-based lookup with zero extra round-trips. * &#x60;&#x60;status&#x60;&#x60;       -- &#x60;&#x60;ACTIVE&#x60;&#x60; / &#x60;&#x60;ARCHIVED&#x60;&#x60; / &#x60;&#x60;PURGING&#x60;&#x60;. * &#x60;&#x60;workspace_id&#x60;&#x60; -- restrict to a single workspace; defaults to &#x60;&#x60;X-Workspace-Id&#x60;&#x60; header. Pass another UUID explicitly to override the header. * &#x60;&#x60;limit&#x60;&#x60;        -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;       -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.

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
        String q = "q_example"; // String | 
        String name = "name_example"; // String | 
        String status = "status_example"; // String | 
        String workspaceId = "workspaceId_example"; // String | 
        Integer limit = 100; // Integer | 
        Integer offset = 0; // Integer | 
        try {
            apiInstance.listDatasets(q, name, status, workspaceId, limit, offset);
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


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **q** | **String**|  | [optional] |
| **name** | **String**|  | [optional] |
| **status** | **String**|  | [optional] |
| **workspaceId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **offset** | **Integer**|  | [optional] [default to 0] |

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


## readByName

> DatasetRead readByName(name)

Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;.

Reads the workspace scope from &#x60;&#x60;X-Workspace-Id&#x60;&#x60;. Datasets enforce &#x60;&#x60;UNIQUE(workspace_id, name)&#x60;&#x60; so the lookup always returns 0 or 1.

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
        String name = "name_example"; // String | 
        try {
            DatasetRead result = apiInstance.readByName(name);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DatasetsApi#readByName");
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
| **name** | **String**|  | |

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

