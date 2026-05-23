# TablesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**derive**](TablesApi.md#derive) | **POST** /api/v1/tables:derive | Materialise a SELECT result as a new DERIVED table. |
| [**getTable**](TablesApi.md#getTable) | **GET** /api/v1/tables/{table_id} |  |
| [**listChanges**](TablesApi.md#listChanges) | **GET** /api/v1/tables/{table_id}/changes |  |
| [**listObjects**](TablesApi.md#listObjects) | **GET** /api/v1/tables/{table_id}/objects | List schema_objects for the table&#39;s current snapshot. |
| [**listSnapshots**](TablesApi.md#listSnapshots) | **GET** /api/v1/tables/{table_id}/snapshots |  |
| [**listTables**](TablesApi.md#listTables) | **GET** /api/v1/datasets/{dataset_id}/tables |  |


<a id="derive"></a>
# **derive**
> DeriveTableResponse derive(deriveTableRequest)

Materialise a SELECT result as a new DERIVED table.

:param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.TablesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    TablesApi apiInstance = new TablesApi(defaultClient);
    DeriveTableRequest deriveTableRequest = new DeriveTableRequest(); // DeriveTableRequest | 
    try {
      DeriveTableResponse result = apiInstance.derive(deriveTableRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling TablesApi#derive");
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
| **deriveTableRequest** | [**DeriveTableRequest**](DeriveTableRequest.md)|  | |

### Return type

[**DeriveTableResponse**](DeriveTableResponse.md)

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

<a id="getTable"></a>
# **getTable**
> TableRead getTable(tableId)



### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.TablesApi;

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

<a id="listChanges"></a>
# **listChanges**
> listChanges(tableId)



### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.TablesApi;

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

<a id="listObjects"></a>
# **listObjects**
> listObjects(tableId)

List schema_objects for the table&#39;s current snapshot.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.TablesApi;

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

<a id="listSnapshots"></a>
# **listSnapshots**
> listSnapshots(tableId)



### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.TablesApi;

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

<a id="listTables"></a>
# **listTables**
> listTables(datasetId)



### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.TablesApi;

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

