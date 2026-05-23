# GlossaryApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](GlossaryApi.md#create) | **POST** /api/v1/glossary | Create a glossary term; (workspace_id, term) must be unique. |
| [**delete**](GlossaryApi.md#delete) | **DELETE** /api/v1/glossary/{term_id} | Hard-delete a glossary term. |
| [**listTerms**](GlossaryApi.md#listTerms) | **GET** /api/v1/glossary | Return paginated glossary terms for the caller&#39;s workspace. |
| [**update**](GlossaryApi.md#update) | **PUT** /api/v1/glossary/{term_id} | Sparse-update a glossary term. |



## create

> GlossaryTermRead create(glossaryTermCreate)

Create a glossary term; (workspace_id, term) must be unique.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.GlossaryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        GlossaryApi apiInstance = new GlossaryApi(defaultClient);
        GlossaryTermCreate glossaryTermCreate = new GlossaryTermCreate(); // GlossaryTermCreate | 
        try {
            GlossaryTermRead result = apiInstance.create(glossaryTermCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling GlossaryApi#create");
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
| **glossaryTermCreate** | [**GlossaryTermCreate**](GlossaryTermCreate.md)|  | |

### Return type

[**GlossaryTermRead**](GlossaryTermRead.md)

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


## delete

> delete(termId)

Hard-delete a glossary term.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.GlossaryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        GlossaryApi apiInstance = new GlossaryApi(defaultClient);
        String termId = "termId_example"; // String | 
        try {
            apiInstance.delete(termId);
        } catch (ApiException e) {
            System.err.println("Exception when calling GlossaryApi#delete");
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
| **termId** | **String**|  | |

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
| **204** | No Content |  -  |


## listTerms

> listTerms(limit, offset)

Return paginated glossary terms for the caller&#39;s workspace.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.GlossaryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        GlossaryApi apiInstance = new GlossaryApi(defaultClient);
        Integer limit = 100; // Integer | 
        Integer offset = 0; // Integer | 
        try {
            apiInstance.listTerms(limit, offset);
        } catch (ApiException e) {
            System.err.println("Exception when calling GlossaryApi#listTerms");
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


## update

> GlossaryTermRead update(termId, glossaryTermUpdate)

Sparse-update a glossary term.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.GlossaryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        GlossaryApi apiInstance = new GlossaryApi(defaultClient);
        String termId = "termId_example"; // String | 
        GlossaryTermUpdate glossaryTermUpdate = new GlossaryTermUpdate(); // GlossaryTermUpdate | 
        try {
            GlossaryTermRead result = apiInstance.update(termId, glossaryTermUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling GlossaryApi#update");
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
| **termId** | **String**|  | |
| **glossaryTermUpdate** | [**GlossaryTermUpdate**](GlossaryTermUpdate.md)|  | |

### Return type

[**GlossaryTermRead**](GlossaryTermRead.md)

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

