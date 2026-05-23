# TablesDeriveApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**derive**](TablesDeriveApi.md#derive) | **POST** /api/v1/tables:derive | Materialise a SELECT result as a new DERIVED table. |



## derive

> DeriveTableResponse derive(deriveTableRequest)

Materialise a SELECT result as a new DERIVED table.

:param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.TablesDeriveApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TablesDeriveApi apiInstance = new TablesDeriveApi(defaultClient);
        DeriveTableRequest deriveTableRequest = new DeriveTableRequest(); // DeriveTableRequest | 
        try {
            DeriveTableResponse result = apiInstance.derive(deriveTableRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TablesDeriveApi#derive");
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

