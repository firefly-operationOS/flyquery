# WorkspacesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](WorkspacesApi.md#create) | **POST** /api/v1/workspaces | Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header. |
| [**listWorkspaces**](WorkspacesApi.md#listWorkspaces) | **GET** /api/v1/workspaces | Search/filter workspaces for the caller&#39;s tenant. |
| [**purge**](WorkspacesApi.md#purge) | **DELETE** /api/v1/workspaces/{workspace_id}:purge | Purge a workspace: mark PURGING + walk + delete all blobs. |
| [**read**](WorkspacesApi.md#read) | **GET** /api/v1/workspaces/{workspace_id} | Fetch a single workspace by id. Returns 404 if not found. |
| [**readBySlug**](WorkspacesApi.md#readBySlug) | **GET** /api/v1/workspaces/by-slug/{slug} | Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key. |
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

> listWorkspaces(q, slug, status, limit, offset)

Search/filter workspaces for the caller&#39;s tenant.

Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;      -- free-text substring match against &#x60;&#x60;slug&#x60;&#x60; or &#x60;&#x60;name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;slug&#x60;&#x60;   -- exact match on &#x60;&#x60;slug&#x60;&#x60; -- gives you slug-based lookup with zero extra round trips. * &#x60;&#x60;status&#x60;&#x60; -- exact match (&#x60;&#x60;ACTIVE&#x60;&#x60;, &#x60;&#x60;ARCHIVED&#x60;&#x60;, &#x60;&#x60;PURGING&#x60;&#x60;). * &#x60;&#x60;limit&#x60;&#x60;  -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60; -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60; where &#x60;&#x60;total&#x60;&#x60; is the un-paginated match count.

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
        String q = "q_example"; // String | 
        String slug = "slug_example"; // String | 
        String status = "status_example"; // String | 
        Integer limit = 100; // Integer | 
        Integer offset = 0; // Integer | 
        try {
            apiInstance.listWorkspaces(q, slug, status, limit, offset);
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


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **q** | **String**|  | [optional] |
| **slug** | **String**|  | [optional] |
| **status** | **String**|  | [optional] |
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


## readBySlug

> WorkspaceRead readBySlug(slug)

Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key.

Lets SDKs and CLIs resolve a workspace from a memorable identifier instead of carrying around a UUID. Returns 404 if no match.

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
        String slug = "slug_example"; // String | 
        try {
            WorkspaceRead result = apiInstance.readBySlug(slug);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkspacesApi#readBySlug");
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
| **slug** | **String**|  | |

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

