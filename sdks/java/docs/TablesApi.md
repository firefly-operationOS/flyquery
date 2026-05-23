# TablesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getTable**](TablesApi.md#getTable) | **GET** /api/v1/tables/{table_id} |  |
| [**getTableByName**](TablesApi.md#getTableByName) | **GET** /api/v1/tables/by-name/{name} | Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace. |
| [**listChanges**](TablesApi.md#listChanges) | **GET** /api/v1/tables/{table_id}/changes |  |
| [**listObjects**](TablesApi.md#listObjects) | **GET** /api/v1/tables/{table_id}/objects | List schema_objects for the table&#39;s current snapshot. |
| [**listSnapshots**](TablesApi.md#listSnapshots) | **GET** /api/v1/tables/{table_id}/snapshots |  |
| [**listTables**](TablesApi.md#listTables) | **GET** /api/v1/datasets/{dataset_id}/tables |  |
| [**searchTables**](TablesApi.md#searchTables) | **GET** /api/v1/tables | Search/filter tables across the caller&#39;s workspace. |



## getTable

> TableRead getTable(tableId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String tableId = "tableId_example"; // String | 
        try {
            TableRead result = apiInstance.getTable(tableId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#getTable");
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
| **tableId** | **String**|  | |

### Return type

[**TableRead**](TableRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## getTableByName

> TableRead getTableByName(name, datasetId)

Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace.

Pass &#x60;&#x60;?dataset_id&#x3D;...&#x60;&#x60; to scope the lookup to a single dataset. Returns 404 if the name is not unique within the scope or no match is found.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String name = "name_example"; // String | 
        String datasetId = "datasetId_example"; // String | 
        try {
            TableRead result = apiInstance.getTableByName(name, datasetId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#getTableByName");
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
| **datasetId** | **String**|  | [optional] |

### Return type

[**TableRead**](TableRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## listChanges

> listChanges(tableId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String tableId = "tableId_example"; // String | 
        try {
            apiInstance.listChanges(tableId);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#listChanges");
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
| **tableId** | **String**|  | |

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


## listObjects

> listObjects(tableId)

List schema_objects for the table&#39;s current snapshot.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String tableId = "tableId_example"; // String | 
        try {
            apiInstance.listObjects(tableId);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#listObjects");
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
| **tableId** | **String**|  | |

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


## listSnapshots

> listSnapshots(tableId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String tableId = "tableId_example"; // String | 
        try {
            apiInstance.listSnapshots(tableId);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#listSnapshots");
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
| **tableId** | **String**|  | |

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


## listTables

> listTables(datasetId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            apiInstance.listTables(datasetId);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#listTables");
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


## searchTables

> searchTables(q, name, datasetId, kind, isActive, limit, offset)

Search/filter tables across the caller&#39;s workspace.

Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;          -- substring match on &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;qualified_name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;       -- exact match on &#x60;&#x60;name&#x60;&#x60;. * &#x60;&#x60;dataset_id&#x60;&#x60; -- restrict to a single dataset. * &#x60;&#x60;kind&#x60;&#x60;       -- &#x60;&#x60;UPLOADED&#x60;&#x60; / &#x60;&#x60;VIEW&#x60;&#x60; / &#x60;&#x60;DERIVED&#x60;&#x60;. * &#x60;&#x60;is_active&#x60;&#x60;  -- default &#x60;&#x60;true&#x60;&#x60;; pass &#x60;&#x60;false&#x60;&#x60; to include archived tables. * &#x60;&#x60;limit&#x60;&#x60;      -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;     -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesApi apiInstance = new TablesApi(defaultClient);
        String q = "q_example"; // String | 
        String name = "name_example"; // String | 
        String datasetId = "datasetId_example"; // String | 
        String kind = "kind_example"; // String | 
        String isActive = "isActive_example"; // String | 
        Integer limit = 100; // Integer | 
        Integer offset = 0; // Integer | 
        try {
            apiInstance.searchTables(q, name, datasetId, kind, isActive, limit, offset);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesApi#searchTables");
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
| **datasetId** | **String**|  | [optional] |
| **kind** | **String**|  | [optional] |
| **isActive** | **String**|  | [optional] |
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

