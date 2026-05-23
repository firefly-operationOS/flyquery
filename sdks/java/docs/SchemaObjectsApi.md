# SchemaObjectsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getObject**](SchemaObjectsApi.md#getObject) | **GET** /api/v1/schema-objects/{object_id} | Get a single schema object by ID. |
| [**updateObject**](SchemaObjectsApi.md#updateObject) | **PUT** /api/v1/schema-objects/{object_id} | Update human-set fields on a schema object. |



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
import com.firefly.flyquery.api.SchemaObjectsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SchemaObjectsApi apiInstance = new SchemaObjectsApi(defaultClient);
        String objectId = "objectId_example"; // String | 
        try {
            SchemaObjectRead result = apiInstance.getObject(objectId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SchemaObjectsApi#getObject");
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
import com.firefly.flyquery.api.SchemaObjectsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SchemaObjectsApi apiInstance = new SchemaObjectsApi(defaultClient);
        String objectId = "objectId_example"; // String | 
        SchemaObjectUpdate schemaObjectUpdate = new SchemaObjectUpdate(); // SchemaObjectUpdate | 
        try {
            SchemaObjectRead result = apiInstance.updateObject(objectId, schemaObjectUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SchemaObjectsApi#updateObject");
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

