# SchemaApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**confirm**](SchemaApi.md#confirm) | **POST** /api/v1/schema-changes/{change_id}:confirm | Flip a RENAMED_CANDIDATE row to RENAMED. |
| [**getObject**](SchemaApi.md#getObject) | **GET** /api/v1/schema-objects/{object_id} | Get a single schema object by ID. |
| [**updateObject**](SchemaApi.md#updateObject) | **PUT** /api/v1/schema-objects/{object_id} | Update human-set fields on a schema object. |



## confirm

> SchemaChangeRead confirm(changeId)

Flip a RENAMED_CANDIDATE row to RENAMED.

Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SchemaApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SchemaApi apiInstance = new SchemaApi(defaultClient);
        String changeId = "changeId_example"; // String | 
        try {
            SchemaChangeRead result = apiInstance.confirm(changeId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SchemaApi#confirm");
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
| **changeId** | **String**|  | |

### Return type

[**SchemaChangeRead**](SchemaChangeRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## getObject

> SchemaObjectRead getObject(objectId)

Get a single schema object by ID.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SchemaApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SchemaApi apiInstance = new SchemaApi(defaultClient);
        String objectId = "objectId_example"; // String | 
        try {
            SchemaObjectRead result = apiInstance.getObject(objectId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SchemaApi#getObject");
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
| **objectId** | **String**|  | |

### Return type

[**SchemaObjectRead**](SchemaObjectRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## updateObject

> SchemaObjectRead updateObject(objectId, schemaObjectUpdate)

Update human-set fields on a schema object.

Sets description_source&#x3D;&#39;HUMAN&#39; when description is provided. Sets pii_source&#x3D;&#39;HUMAN&#39; when pii_tag is provided.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SchemaApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SchemaApi apiInstance = new SchemaApi(defaultClient);
        String objectId = "objectId_example"; // String | 
        SchemaObjectUpdate schemaObjectUpdate = new SchemaObjectUpdate(); // SchemaObjectUpdate | 
        try {
            SchemaObjectRead result = apiInstance.updateObject(objectId, schemaObjectUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SchemaApi#updateObject");
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
| **objectId** | **String**|  | |
| **schemaObjectUpdate** | [**SchemaObjectUpdate**](SchemaObjectUpdate.md)|  | |

### Return type

[**SchemaObjectRead**](SchemaObjectRead.md)

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

