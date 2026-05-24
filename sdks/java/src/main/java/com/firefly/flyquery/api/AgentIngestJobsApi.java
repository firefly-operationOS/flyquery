package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.CancelResponse;
import com.firefly.flyquery.model.IngestEventListResponse;
import com.firefly.flyquery.model.IngestJobListResponse;
import com.firefly.flyquery.model.IngestJobRead;
import java.util.UUID;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Arrays;
import java.util.stream.Collectors;

import org.springframework.core.io.FileSystemResource;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.client.WebClient.ResponseSpec;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Flux;

@jakarta.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-24T14:41:07.623178+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class AgentIngestJobsApi {
    private ApiClient apiClient;

    public AgentIngestJobsApi() {
        this(new ApiClient());
    }

    public AgentIngestJobsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Cooperatively cancel a running job.
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). The underlying service is itself idempotent on terminal jobs, but we still cache the response so a retried cancel returns the same wire envelope (same &#x60;&#x60;status&#x60;&#x60; field).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return CancelResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec cancelJobRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling cancelJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling cancelJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/ingest-jobs/{job_id}:cancel", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Cooperatively cancel a running job.
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). The underlying service is itself idempotent on terminal jobs, but we still cache the response so a retried cancel returns the same wire envelope (same &#x60;&#x60;status&#x60;&#x60; field).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return CancelResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<CancelResponse> cancelJob(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return cancelJobRequestCreation(jobId, xAgentToken, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Cooperatively cancel a running job.
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). The underlying service is itself idempotent on terminal jobs, but we still cache the response so a retried cancel returns the same wire envelope (same &#x60;&#x60;status&#x60;&#x60; field).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;CancelResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<CancelResponse>> cancelJobWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return cancelJobRequestCreation(jobId, xAgentToken, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Cooperatively cancel a running job.
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). The underlying service is itself idempotent on terminal jobs, but we still cache the response so a retried cancel returns the same wire envelope (same &#x60;&#x60;status&#x60;&#x60; field).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec cancelJobWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return cancelJobRequestCreation(jobId, xAgentToken, xCorrelationId, idempotencyKey);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).
     * 
     * <p><b>201</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createJobRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling createJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/agent/ingest-jobs", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).
     * 
     * <p><b>201</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> createJob(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return createJobRequestCreation(xAgentToken, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).
     * 
     * <p><b>201</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> createJobWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return createJobRequestCreation(xAgentToken, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).
     * 
     * <p><b>201</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createJobWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createJobRequestCreation(xAgentToken, xCorrelationId, idempotencyKey);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getJobRequestCreation(@jakarta.annotation.Nullable String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling getJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling getJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/ingest-jobs/{job_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobRead> getJob(@jakarta.annotation.Nullable String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return getJobRequestCreation(jobId, xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;IngestJobRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobRead>> getJobWithHttpInfo(@jakarta.annotation.Nullable String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return getJobRequestCreation(jobId, xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getJobWithResponseSpec(@jakarta.annotation.Nullable String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getJobRequestCreation(jobId, xAgentToken, xCorrelationId);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestEventListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listEventsRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/ingest-jobs/{job_id}/events", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestEventListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestEventListResponse> listEvents(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return listEventsRequestCreation(jobId, xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;IngestEventListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestEventListResponse>> listEventsWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return listEventsRequestCreation(jobId, xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listEventsWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listEventsRequestCreation(jobId, xAgentToken, xCorrelationId);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listJobsRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling listJobs", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/ingest-jobs", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobListResponse> listJobs(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return listJobsRequestCreation(xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;IngestJobListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobListResponse>> listJobsWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return listJobsRequestCreation(xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listJobsWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listJobsRequestCreation(xAgentToken, xCorrelationId);
    }

    /**
     * SSE progress stream. The underlying delegate handles framing,
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec streamJobRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling streamJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling streamJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/agent/ingest-jobs/{job_id}/stream", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * SSE progress stream. The underlying delegate handles framing,
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> streamJob(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return streamJobRequestCreation(jobId, xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * SSE progress stream. The underlying delegate handles framing,
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> streamJobWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return streamJobRequestCreation(jobId, xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * SSE progress stream. The underlying delegate handles framing,
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec streamJobWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return streamJobRequestCreation(jobId, xAgentToken, xCorrelationId);
    }
}
