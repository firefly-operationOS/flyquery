# AgentRelationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listRelations**](AgentRelationsApi.md#listRelations) | **GET** /api/v1/agent/datasets/{dataset_id}/relations |  |



## listRelations

> PaginatedRelationRead listRelations(datasetId, xAgentToken, status, xCorrelationId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentRelationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentRelationsApi apiInstance = new AgentRelationsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        String status = "status_example"; // String | 
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            PaginatedRelationRead result = apiInstance.listRelations(datasetId, xAgentToken, status, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentRelationsApi#listRelations");
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
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **status** | **String**|  | [optional] |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**PaginatedRelationRead**](PaginatedRelationRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

