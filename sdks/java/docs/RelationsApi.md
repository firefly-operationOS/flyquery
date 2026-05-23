# RelationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**approveRelation**](RelationsApi.md#approveRelation) | **POST** /api/v1/relations/{relation_id}:approve | Approve a PROPOSED relation. |
| [**listRelations**](RelationsApi.md#listRelations) | **GET** /api/v1/datasets/{dataset_id}/relations | List relations for a dataset (all statuses by default). |
| [**rejectRelation**](RelationsApi.md#rejectRelation) | **POST** /api/v1/relations/{relation_id}:reject | Reject a PROPOSED relation. |



## approveRelation

> approveRelation(relationId)

Approve a PROPOSED relation.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.RelationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RelationsApi apiInstance = new RelationsApi(defaultClient);
        String relationId = "relationId_example"; // String | 
        try {
            apiInstance.approveRelation(relationId);
        } catch (ApiException e) {
            System.err.println("Exception when calling RelationsApi#approveRelation");
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
| **relationId** | **String**|  | |

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


## listRelations

> listRelations(datasetId)

List relations for a dataset (all statuses by default).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.RelationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RelationsApi apiInstance = new RelationsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            apiInstance.listRelations(datasetId);
        } catch (ApiException e) {
            System.err.println("Exception when calling RelationsApi#listRelations");
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


## rejectRelation

> rejectRelation(relationId)

Reject a PROPOSED relation.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.RelationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RelationsApi apiInstance = new RelationsApi(defaultClient);
        String relationId = "relationId_example"; // String | 
        try {
            apiInstance.rejectRelation(relationId);
        } catch (ApiException e) {
            System.err.println("Exception when calling RelationsApi#rejectRelation");
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
| **relationId** | **String**|  | |

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

