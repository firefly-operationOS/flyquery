# flyquery_sdk.TablesDeriveApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**derive**](TablesDeriveApi.md#derive) | **POST** /api/v1/tables:derive | Materialise a SELECT result as a new DERIVED table.


# **derive**
> DeriveTableResponse derive(derive_table_request)

Materialise a SELECT result as a new DERIVED table.

:param http_request: Starlette request (tenant context headers)
:param body: dataset_id + name + sql (must be a SELECT)
:return: DeriveTableResponse with the new table_id
:raises DeriveTableForbidden: when sql is not a SELECT
:raises DeriveTableError: when DuckDB execution fails

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.derive_table_request import DeriveTableRequest
from flyquery_sdk.models.derive_table_response import DeriveTableResponse
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.TablesDeriveApi(api_client)
    derive_table_request = flyquery_sdk.DeriveTableRequest() # DeriveTableRequest | 

    try:
        # Materialise a SELECT result as a new DERIVED table.
        api_response = await api_instance.derive(derive_table_request)
        print("The response of TablesDeriveApi->derive:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TablesDeriveApi->derive: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **derive_table_request** | [**DeriveTableRequest**](DeriveTableRequest.md)|  | 

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
**201** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

