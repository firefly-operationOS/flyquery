# flyquery_sdk.AgentIngestJobsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_job**](AgentIngestJobsApi.md#cancel_job) | **POST** /api/v1/agent/ingest-jobs/{job_id}:cancel | Cooperatively cancel a running job.
[**create_job**](AgentIngestJobsApi.md#create_job) | **POST** /api/v1/agent/ingest-jobs | Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).
[**get_job**](AgentIngestJobsApi.md#get_job) | **GET** /api/v1/agent/ingest-jobs/{job_id} | 
[**list_events**](AgentIngestJobsApi.md#list_events) | **GET** /api/v1/agent/ingest-jobs/{job_id}/events | 
[**list_jobs**](AgentIngestJobsApi.md#list_jobs) | **GET** /api/v1/agent/ingest-jobs | 
[**stream_job**](AgentIngestJobsApi.md#stream_job) | **GET** /api/v1/agent/ingest-jobs/{job_id}/stream | SSE progress stream. The underlying delegate handles framing,


# **cancel_job**
> CancelResponse cancel_job(job_id, x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Cooperatively cancel a running job.

Replay-dedup'd via ``Idempotency-Key`` (required). The
underlying service is itself idempotent on terminal jobs, but
we still cache the response so a retried cancel returns the
same wire envelope (same ``status`` field).

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentIngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Cooperatively cancel a running job.
        api_response = await api_instance.cancel_job(job_id, x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentIngestJobsApi->cancel_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentIngestJobsApi->cancel_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**CancelResponse**](CancelResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_job**
> create_job(x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentIngestJobsApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).
        await api_instance.create_job(x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
    except Exception as e:
        print("Exception when calling AgentIngestJobsApi->create_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

void (empty response body)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job**
> IngestJobRead get_job(job_id, x_agent_token, x_correlation_id=x_correlation_id)

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentIngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        api_response = await api_instance.get_job(job_id, x_agent_token, x_correlation_id=x_correlation_id)
        print("The response of AgentIngestJobsApi->get_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentIngestJobsApi->get_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**IngestJobRead**](IngestJobRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_events**
> IngestEventListResponse list_events(job_id, x_agent_token, x_correlation_id=x_correlation_id)

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentIngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        api_response = await api_instance.list_events(job_id, x_agent_token, x_correlation_id=x_correlation_id)
        print("The response of AgentIngestJobsApi->list_events:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentIngestJobsApi->list_events: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**IngestEventListResponse**](IngestEventListResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_jobs**
> IngestJobListResponse list_jobs(x_agent_token, x_correlation_id=x_correlation_id)

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentIngestJobsApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        api_response = await api_instance.list_jobs(x_agent_token, x_correlation_id=x_correlation_id)
        print("The response of AgentIngestJobsApi->list_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentIngestJobsApi->list_jobs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**IngestJobListResponse**](IngestJobListResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream_job**
> stream_job(job_id, x_agent_token, x_correlation_id=x_correlation_id)

SSE progress stream. The underlying delegate handles framing,

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentIngestJobsApi(api_client)
    job_id = 'job_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # SSE progress stream. The underlying delegate handles framing,
        await api_instance.stream_job(job_id, x_agent_token, x_correlation_id=x_correlation_id)
    except Exception as e:
        print("Exception when calling AgentIngestJobsApi->stream_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

void (empty response body)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

