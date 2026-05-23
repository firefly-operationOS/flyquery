# SchemaChangesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**confirm**](SchemaChangesApi.md#confirm) | **POST** /api/v1/schema-changes/{change_id}:confirm | Flip a RENAMED_CANDIDATE row to RENAMED. |



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
import com.firefly.flyquery.api.SchemaChangesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SchemaChangesApi apiInstance = new SchemaChangesApi(defaultClient);
        String changeId = "changeId_example"; // String | 
        try {
            SchemaChangeRead result = apiInstance.confirm(changeId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SchemaChangesApi#confirm");
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

