// Copyright 2024-2026 Firefly Software Foundation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.CallbackDeliveryListResponse;
import com.firefly.flyquery.model.CancelResponse;
import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.IngestEventListResponse;
import com.firefly.flyquery.model.IngestJobCreate;
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

@jakarta.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-24T17:01:34.733622+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class IngestJobsApi {
    private ApiClient apiClient;

    public IngestJobsApi() {
        this(new ApiClient());
    }

    public IngestJobsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return CancelResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec cancelJobRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling cancelJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling cancelJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling cancelJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
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

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}:cancel", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return CancelResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<CancelResponse> cancelJob(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return cancelJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;CancelResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<CancelResponse>> cancelJobWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return cancelJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec cancelJobWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return cancelJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * &#x60;&#x60;body&#x60;&#x60; is declared as &#x60;&#x60;Valid[Body[IngestJobCreate]]&#x60;&#x60; (not read from &#x60;&#x60;http_request.json()&#x60;&#x60;) so FastAPI / pyfly publish the request schema into &#x60;&#x60;openapi.json&#x60;&#x60; -- the older manual decode kept &#x60;&#x60;IngestJobCreate&#x60;&#x60; (and now the nested &#x60;&#x60;CallbackConfig&#x60;&#x60; field) invisible to SDK generators.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param ingestJobCreate The ingestJobCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createJobRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull IngestJobCreate ingestJobCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = ingestJobCreate;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling createJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling createJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'ingestJobCreate' is set
        if (ingestJobCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'ingestJobCreate' when calling createJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
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

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * &#x60;&#x60;body&#x60;&#x60; is declared as &#x60;&#x60;Valid[Body[IngestJobCreate]]&#x60;&#x60; (not read from &#x60;&#x60;http_request.json()&#x60;&#x60;) so FastAPI / pyfly publish the request schema into &#x60;&#x60;openapi.json&#x60;&#x60; -- the older manual decode kept &#x60;&#x60;IngestJobCreate&#x60;&#x60; (and now the nested &#x60;&#x60;CallbackConfig&#x60;&#x60; field) invisible to SDK generators.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param ingestJobCreate The ingestJobCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobRead> createJob(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull IngestJobCreate ingestJobCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return createJobRequestCreation(xTenantId, xWorkspaceId, ingestJobCreate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * &#x60;&#x60;body&#x60;&#x60; is declared as &#x60;&#x60;Valid[Body[IngestJobCreate]]&#x60;&#x60; (not read from &#x60;&#x60;http_request.json()&#x60;&#x60;) so FastAPI / pyfly publish the request schema into &#x60;&#x60;openapi.json&#x60;&#x60; -- the older manual decode kept &#x60;&#x60;IngestJobCreate&#x60;&#x60; (and now the nested &#x60;&#x60;CallbackConfig&#x60;&#x60; field) invisible to SDK generators.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param ingestJobCreate The ingestJobCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;IngestJobRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobRead>> createJobWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull IngestJobCreate ingestJobCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return createJobRequestCreation(xTenantId, xWorkspaceId, ingestJobCreate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * &#x60;&#x60;body&#x60;&#x60; is declared as &#x60;&#x60;Valid[Body[IngestJobCreate]]&#x60;&#x60; (not read from &#x60;&#x60;http_request.json()&#x60;&#x60;) so FastAPI / pyfly publish the request schema into &#x60;&#x60;openapi.json&#x60;&#x60; -- the older manual decode kept &#x60;&#x60;IngestJobCreate&#x60;&#x60; (and now the nested &#x60;&#x60;CallbackConfig&#x60;&#x60; field) invisible to SDK generators.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param ingestJobCreate The ingestJobCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createJobWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull IngestJobCreate ingestJobCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createJobRequestCreation(xTenantId, xWorkspaceId, ingestJobCreate, xCorrelationId, idempotencyKey);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getJobRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling getJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling getJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling getJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobRead> getJob(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return getJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;IngestJobRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobRead>> getJobWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return getJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getJobWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * Audit log of webhook delivery attempts for this job.
     * Returns one row per outbox entry: the URL we posted to, the terminal event we tried to deliver (&#x60;&#x60;ingest.succeeded&#x60;&#x60; or &#x60;&#x60;ingest.failed&#x60;&#x60;), the current status (&#x60;&#x60;PENDING&#x60;&#x60;, &#x60;&#x60;DELIVERED&#x60;&#x60;, &#x60;&#x60;FAILED&#x60;&#x60;, &#x60;&#x60;DEAD&#x60;&#x60;), the attempt count + the last HTTP status code / error, and the next scheduled retry.  Callers SHOULD poll this endpoint after a webhook outage to confirm that the in-flight retry storm has cleared (DEAD rows require manual replay or a follow-up REPARSE job).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return CallbackDeliveryListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listCallbacksRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling listCallbacks", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listCallbacks", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listCallbacks", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<CallbackDeliveryListResponse> localVarReturnType = new ParameterizedTypeReference<CallbackDeliveryListResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}/callbacks", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Audit log of webhook delivery attempts for this job.
     * Returns one row per outbox entry: the URL we posted to, the terminal event we tried to deliver (&#x60;&#x60;ingest.succeeded&#x60;&#x60; or &#x60;&#x60;ingest.failed&#x60;&#x60;), the current status (&#x60;&#x60;PENDING&#x60;&#x60;, &#x60;&#x60;DELIVERED&#x60;&#x60;, &#x60;&#x60;FAILED&#x60;&#x60;, &#x60;&#x60;DEAD&#x60;&#x60;), the attempt count + the last HTTP status code / error, and the next scheduled retry.  Callers SHOULD poll this endpoint after a webhook outage to confirm that the in-flight retry storm has cleared (DEAD rows require manual replay or a follow-up REPARSE job).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return CallbackDeliveryListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<CallbackDeliveryListResponse> listCallbacks(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<CallbackDeliveryListResponse> localVarReturnType = new ParameterizedTypeReference<CallbackDeliveryListResponse>() {};
        return listCallbacksRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Audit log of webhook delivery attempts for this job.
     * Returns one row per outbox entry: the URL we posted to, the terminal event we tried to deliver (&#x60;&#x60;ingest.succeeded&#x60;&#x60; or &#x60;&#x60;ingest.failed&#x60;&#x60;), the current status (&#x60;&#x60;PENDING&#x60;&#x60;, &#x60;&#x60;DELIVERED&#x60;&#x60;, &#x60;&#x60;FAILED&#x60;&#x60;, &#x60;&#x60;DEAD&#x60;&#x60;), the attempt count + the last HTTP status code / error, and the next scheduled retry.  Callers SHOULD poll this endpoint after a webhook outage to confirm that the in-flight retry storm has cleared (DEAD rows require manual replay or a follow-up REPARSE job).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;CallbackDeliveryListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<CallbackDeliveryListResponse>> listCallbacksWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<CallbackDeliveryListResponse> localVarReturnType = new ParameterizedTypeReference<CallbackDeliveryListResponse>() {};
        return listCallbacksRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Audit log of webhook delivery attempts for this job.
     * Returns one row per outbox entry: the URL we posted to, the terminal event we tried to deliver (&#x60;&#x60;ingest.succeeded&#x60;&#x60; or &#x60;&#x60;ingest.failed&#x60;&#x60;), the current status (&#x60;&#x60;PENDING&#x60;&#x60;, &#x60;&#x60;DELIVERED&#x60;&#x60;, &#x60;&#x60;FAILED&#x60;&#x60;, &#x60;&#x60;DEAD&#x60;&#x60;), the attempt count + the last HTTP status code / error, and the next scheduled retry.  Callers SHOULD poll this endpoint after a webhook outage to confirm that the in-flight retry storm has cleared (DEAD rows require manual replay or a follow-up REPARSE job).
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listCallbacksWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listCallbacksRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestEventListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listEventsRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}/events", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestEventListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestEventListResponse> listEvents(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return listEventsRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;IngestEventListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestEventListResponse>> listEventsWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return listEventsRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listEventsWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listEventsRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listJobsRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listJobs", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listJobs", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return IngestJobListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobListResponse> listJobs(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return listJobsRequestCreation(xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;IngestJobListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobListResponse>> listJobsWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return listJobsRequestCreation(xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listJobsWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listJobsRequestCreation(xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return String
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec streamJobRequestCreation(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling streamJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling streamJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling streamJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "text/event-stream"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<String> localVarReturnType = new ParameterizedTypeReference<String>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}/stream", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return String
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<String> streamJob(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<String> localVarReturnType = new ParameterizedTypeReference<String>() {};
        return streamJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;String&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<String>> streamJobWithHttpInfo(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<String> localVarReturnType = new ParameterizedTypeReference<String>() {};
        return streamJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * @param jobId The jobId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec streamJobWithResponseSpec(@jakarta.annotation.Nonnull String jobId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return streamJobRequestCreation(jobId, xTenantId, xWorkspaceId, xCorrelationId);
    }
}
