# WorkspacesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](WorkspacesApi.md#create) | **POST** /api/v1/workspaces | Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header. |
| [**listWorkspaces**](WorkspacesApi.md#listWorkspaces) | **GET** /api/v1/workspaces | Return all workspaces for the caller&#39;s tenant. |
| [**purge**](WorkspacesApi.md#purge) | **DELETE** /api/v1/workspaces/{workspace_id}:purge | Purge a workspace: mark PURGING + walk + delete all blobs. |
| [**read**](WorkspacesApi.md#read) | **GET** /api/v1/workspaces/{workspace_id} | Fetch a single workspace by id. Returns 404 if not found. |
| [**update**](WorkspacesApi.md#update) | **PUT** /api/v1/workspaces/{workspace_id} | Sparse-update a workspace. Only fields present in body are changed. |



## create

> WorkspaceRead create(workspaceCreate)

Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.WorkspacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkspacesApi apiInstance = new WorkspacesApi(defaultClient);
        WorkspaceCreate workspaceCreate = new WorkspaceCreate(); // WorkspaceCreate | 
        try {
            WorkspaceRead result = apiInstance.create(workspaceCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkspacesApi#create");
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
| **workspaceCreate** | [**WorkspaceCreate**](WorkspaceCreate.md)|  | |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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


## listWorkspaces

> listWorkspaces()

Return all workspaces for the caller&#39;s tenant.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.WorkspacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkspacesApi apiInstance = new WorkspacesApi(defaultClient);
        try {
            apiInstance.listWorkspaces();
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkspacesApi#listWorkspaces");
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


## purge

> purge(workspaceId)

Purge a workspace: mark PURGING + walk + delete all blobs.

Returns 202 Accepted with a tombstone placeholder.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.WorkspacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkspacesApi apiInstance = new WorkspacesApi(defaultClient);
        String workspaceId = "workspaceId_example"; // String | 
        try {
            apiInstance.purge(workspaceId);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkspacesApi#purge");
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
| **workspaceId** | **String**|  | |

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
| **202** | Successful response |  -  |


## read

> WorkspaceRead read(workspaceId)

Fetch a single workspace by id. Returns 404 if not found.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.WorkspacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkspacesApi apiInstance = new WorkspacesApi(defaultClient);
        String workspaceId = "workspaceId_example"; // String | 
        try {
            WorkspaceRead result = apiInstance.read(workspaceId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkspacesApi#read");
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
| **workspaceId** | **String**|  | |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

> WorkspaceRead update(workspaceId, workspaceUpdate)

Sparse-update a workspace. Only fields present in body are changed.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.WorkspacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkspacesApi apiInstance = new WorkspacesApi(defaultClient);
        String workspaceId = "workspaceId_example"; // String | 
        WorkspaceUpdate workspaceUpdate = new WorkspaceUpdate(); // WorkspaceUpdate | 
        try {
            WorkspaceRead result = apiInstance.update(workspaceId, workspaceUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkspacesApi#update");
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
| **workspaceId** | **String**|  | |
| **workspaceUpdate** | [**WorkspaceUpdate**](WorkspaceUpdate.md)|  | |

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

