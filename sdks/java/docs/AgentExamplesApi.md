# AgentExamplesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](AgentExamplesApi.md#create) | **POST** /api/v1/agent/examples | Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED). |
| [**listExamples**](AgentExamplesApi.md#listExamples) | **GET** /api/v1/agent/examples | List examples for the caller&#39;s workspace (agent-tier). |


<a id="create"></a>
# **create**
> ExampleRead create(exampleCreate)

Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).

:param http_request: Starlette request :param body: validated ExampleCreate :return: ExampleRead with created fields

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentExamplesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentExamplesApi apiInstance = new AgentExamplesApi(defaultClient);
    ExampleCreate exampleCreate = new ExampleCreate(); // ExampleCreate | 
    try {
      ExampleRead result = apiInstance.create(exampleCreate);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentExamplesApi#create");
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
| **exampleCreate** | [**ExampleCreate**](ExampleCreate.md)|  | |

### Return type

[**ExampleRead**](ExampleRead.md)

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

<a id="listExamples"></a>
# **listExamples**
> listExamples(quality, datasetId)

List examples for the caller&#39;s workspace (agent-tier).

:param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentExamplesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentExamplesApi apiInstance = new AgentExamplesApi(defaultClient);
    String quality = "null"; // String | 
    String datasetId = "datasetId_example"; // String | 
    try {
      apiInstance.listExamples(quality, datasetId);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentExamplesApi#listExamples");
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
| **quality** | **String**|  | [optional] [default to null] |
| **datasetId** | **String**|  | [optional] |

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

