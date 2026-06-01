package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.PaginatedSemanticMetricRead;
import com.firefly.flyquery.model.PaginatedSemanticVersionRead;
import com.firefly.flyquery.model.SemanticMetricCreate;
import com.firefly.flyquery.model.SemanticMetricRead;
import com.firefly.flyquery.model.SemanticMetricUpdate;
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

@jakarta.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-06-01T11:28:27.907207+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class AgentSemanticMetricsApi {
    private ApiClient apiClient;

    public AgentSemanticMetricsApi() {
        this(new ApiClient());
    }

    public AgentSemanticMetricsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a metric in DRAFT (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricCreate semanticMetricCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = semanticMetricCreate;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'semanticMetricCreate' is set
        if (semanticMetricCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'semanticMetricCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a metric in DRAFT (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> create(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricCreate semanticMetricCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return createRequestCreation(xAgentToken, semanticMetricCreate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Create a metric in DRAFT (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> createWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricCreate semanticMetricCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return createRequestCreation(xAgentToken, semanticMetricCreate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Create a metric in DRAFT (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricCreate semanticMetricCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createRequestCreation(xAgentToken, semanticMetricCreate, xCorrelationId, idempotencyKey);
    }

    /**
     * Fetch a single metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getMetricRequestCreation(@jakarta.annotation.Nullable String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling getMetric", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling getMetric", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics/{metric_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> getMetric(@jakarta.annotation.Nullable String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return getMetricRequestCreation(metricId, xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> getMetricWithHttpInfo(@jakarta.annotation.Nullable String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return getMetricRequestCreation(metricId, xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getMetricWithResponseSpec(@jakarta.annotation.Nullable String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getMetricRequestCreation(metricId, xAgentToken, xCorrelationId);
    }

    /**
     * Return version history for a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticVersionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec historyRequestCreation(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<PaginatedSemanticVersionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticVersionRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics/{metric_id}/history", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return version history for a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticVersionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedSemanticVersionRead> history(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticVersionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticVersionRead>() {};
        return historyRequestCreation(metricId, xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Return version history for a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedSemanticVersionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedSemanticVersionRead>> historyWithHttpInfo(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticVersionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticVersionRead>() {};
        return historyRequestCreation(metricId, xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Return version history for a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec historyWithResponseSpec(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return historyRequestCreation(metricId, xAgentToken, xCorrelationId);
    }

    /**
     * List metrics for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listMetricsRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling listMetrics", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "status", status));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

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

        ParameterizedTypeReference<PaginatedSemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List metrics for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedSemanticMetricRead> listMetrics(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticMetricRead>() {};
        return listMetricsRequestCreation(xAgentToken, datasetId, status, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List metrics for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedSemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedSemanticMetricRead>> listMetricsWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticMetricRead>() {};
        return listMetricsRequestCreation(xAgentToken, datasetId, status, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List metrics for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listMetricsWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listMetricsRequestCreation(xAgentToken, datasetId, status, limit, offset, xCorrelationId);
    }

    /**
     * Publish a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec publishRequestCreation(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics/{metric_id}:publish", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Publish a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> publish(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return publishRequestCreation(metricId, xAgentToken, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Publish a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> publishWithHttpInfo(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return publishRequestCreation(metricId, xAgentToken, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Publish a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec publishWithResponseSpec(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return publishRequestCreation(metricId, xAgentToken, xCorrelationId, idempotencyKey);
    }

    /**
     * Retire a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec retireRequestCreation(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics/{metric_id}:retire", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Retire a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> retire(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return retireRequestCreation(metricId, xAgentToken, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Retire a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> retireWithHttpInfo(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return retireRequestCreation(metricId, xAgentToken, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Retire a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec retireWithResponseSpec(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return retireRequestCreation(metricId, xAgentToken, xCorrelationId, idempotencyKey);
    }

    /**
     * Sparse-update a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = semanticMetricUpdate;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'semanticMetricUpdate' is set
        if (semanticMetricUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'semanticMetricUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/semantic/metrics/{metric_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> update(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return updateRequestCreation(metricId, xAgentToken, semanticMetricUpdate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> updateWithHttpInfo(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return updateRequestCreation(metricId, xAgentToken, semanticMetricUpdate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a metric (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@jakarta.annotation.Nonnull String metricId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return updateRequestCreation(metricId, xAgentToken, semanticMetricUpdate, xCorrelationId, idempotencyKey);
    }
}
