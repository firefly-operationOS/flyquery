# flyquery_sdk.IngestJobsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_job**](IngestJobsApi.md#cancel_job) | **POST** /api/v1/ingest-jobs/{job_id}:cancel | Cooperatively cancel a job (idempotent for terminal jobs).
[**create_job**](IngestJobsApi.md#create_job) | **POST** /api/v1/ingest-jobs | Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
[**get_job**](IngestJobsApi.md#get_job) | **GET** /api/v1/ingest-jobs/{job_id} | Get a single ingest job.
[**list_events**](IngestJobsApi.md#list_events) | **GET** /api/v1/ingest-jobs/{job_id}/events | Paginated event ledger for a job.
[**list_jobs**](IngestJobsApi.md#list_jobs) | **GET** /api/v1/ingest-jobs | List ingest jobs with optional filters.
[**stream_job**](IngestJobsApi.md#stream_job) | **GET** /api/v1/ingest-jobs/{job_id}/stream | SSE stream for real-time job progress.


# **cancel_job**
> CancelResponse cancel_job(job_id)

Cooperatively cancel a job (idempotent for terminal jobs).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.cancel_response import CancelResponse
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
    api_instance = flyquery_sdk.IngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Cooperatively cancel a job (idempotent for terminal jobs).
        api_response = await api_instance.cancel_job(job_id)
        print("The response of IngestJobsApi->cancel_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestJobsApi->cancel_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**CancelResponse**](CancelResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_job**
> IngestJobRead create_job()

Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.ingest_job_read import IngestJobRead
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
    api_instance = flyquery_sdk.IngestJobsApi(api_client)

    try:
        # Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
        api_response = await api_instance.create_job()
        print("The response of IngestJobsApi->create_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestJobsApi->create_job: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**IngestJobRead**](IngestJobRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job**
> IngestJobRead get_job(job_id)

Get a single ingest job.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.ingest_job_read import IngestJobRead
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
    api_instance = flyquery_sdk.IngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Get a single ingest job.
        api_response = await api_instance.get_job(job_id)
        print("The response of IngestJobsApi->get_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestJobsApi->get_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**IngestJobRead**](IngestJobRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_events**
> IngestEventListResponse list_events(job_id)

Paginated event ledger for a job.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.ingest_event_list_response import IngestEventListResponse
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
    api_instance = flyquery_sdk.IngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Paginated event ledger for a job.
        api_response = await api_instance.list_events(job_id)
        print("The response of IngestJobsApi->list_events:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestJobsApi->list_events: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**IngestEventListResponse**](IngestEventListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_jobs**
> IngestJobListResponse list_jobs()

List ingest jobs with optional filters.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.ingest_job_list_response import IngestJobListResponse
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
    api_instance = flyquery_sdk.IngestJobsApi(api_client)

    try:
        # List ingest jobs with optional filters.
        api_response = await api_instance.list_jobs()
        print("The response of IngestJobsApi->list_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestJobsApi->list_jobs: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**IngestJobListResponse**](IngestJobListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream_job**
> stream_job(job_id)

SSE stream for real-time job progress.

Mirrors canon's ingest_jobs_controller SSE pattern:
1. Emit all existing events for the job (catch-up replay)
2. Poll for new events every 250ms
3. Close stream when a ``final`` or ``error`` event is emitted
4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak

### Example


```python
import flyquery_sdk
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
    api_instance = flyquery_sdk.IngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # SSE stream for real-time job progress.
        await api_instance.stream_job(job_id)
    except Exception as e:
        print("Exception when calling IngestJobsApi->stream_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

