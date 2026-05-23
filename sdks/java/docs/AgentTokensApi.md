# AgentTokensApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listTokens**](AgentTokensApi.md#listTokens) | **GET** /api/v1/agent-tokens | List tokens for the current tenant (newest first). |
| [**mint**](AgentTokensApi.md#mint) | **POST** /api/v1/agent-tokens | Mint a new agent token. |
| [**revoke**](AgentTokensApi.md#revoke) | **DELETE** /api/v1/agent-tokens/{token_id} | Revoke a token. Idempotent -- already-revoked is a no-op (204). |


<a id="listTokens"></a>
# **listTokens**
> List&lt;AgentTokenSummaryDto&gt; listTokens()

List tokens for the current tenant (newest first).

Returns the summary shape only -- the secret is never round-tripped on this endpoint.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentTokensApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentTokensApi apiInstance = new AgentTokensApi(defaultClient);
    try {
      List<AgentTokenSummaryDto> result = apiInstance.listTokens();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentTokensApi#listTokens");
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

[**List&lt;AgentTokenSummaryDto&gt;**](AgentTokenSummaryDto.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="mint"></a>
# **mint**
> AgentTokenCreated mint(agentTokenMintRequest)

Mint a new agent token.

Returns 201 with the full &#x60;&#x60;token&#x60;&#x60; populated. The token is only returned this once -- subsequent reads expose only &#x60;&#x60;prefix&#x60;&#x60;. Refuses agent-tier callers with &#x60;&#x60;403 agent_cannot_mint&#x60;&#x60;.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentTokensApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentTokensApi apiInstance = new AgentTokensApi(defaultClient);
    AgentTokenMintRequest agentTokenMintRequest = new AgentTokenMintRequest(); // AgentTokenMintRequest | 
    try {
      AgentTokenCreated result = apiInstance.mint(agentTokenMintRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentTokensApi#mint");
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
| **agentTokenMintRequest** | [**AgentTokenMintRequest**](AgentTokenMintRequest.md)|  | |

### Return type

[**AgentTokenCreated**](AgentTokenCreated.md)

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

<a id="revoke"></a>
# **revoke**
> revoke(tokenId)

Revoke a token. Idempotent -- already-revoked is a no-op (204).

Unknown &#x60;&#x60;token_id&#x60;&#x60; returns &#x60;&#x60;404 resource_not_found&#x60;&#x60;.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentTokensApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentTokensApi apiInstance = new AgentTokensApi(defaultClient);
    String tokenId = "tokenId_example"; // String | 
    try {
      apiInstance.revoke(tokenId);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentTokensApi#revoke");
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
| **tokenId** | **String**|  | |

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

