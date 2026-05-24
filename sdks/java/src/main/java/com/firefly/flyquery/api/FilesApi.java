package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.BulkFileUploadResponse;
import com.firefly.flyquery.model.FileUploadResponse;
import com.firefly.flyquery.model.ReuploadResponse;
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
public class FilesApi {
    private ApiClient apiClient;

    public FilesApi() {
        this(new ApiClient());
    }

    public FilesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ReuploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec reuploadFileRequestCreation(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String tableId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling reuploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'tableId' is set
        if (tableId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tableId' when calling reuploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling reuploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling reuploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);
        pathParams.put("table_id", tableId);

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

        ParameterizedTypeReference<ReuploadResponse> localVarReturnType = new ParameterizedTypeReference<ReuploadResponse>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/tables/{table_id}:upload", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ReuploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ReuploadResponse> reuploadFile(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String tableId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ReuploadResponse> localVarReturnType = new ParameterizedTypeReference<ReuploadResponse>() {};
        return reuploadFileRequestCreation(datasetId, tableId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;ReuploadResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ReuploadResponse>> reuploadFileWithHttpInfo(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String tableId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ReuploadResponse> localVarReturnType = new ParameterizedTypeReference<ReuploadResponse>() {};
        return reuploadFileRequestCreation(datasetId, tableId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec reuploadFileWithResponseSpec(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String tableId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return reuploadFileRequestCreation(datasetId, tableId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return FileUploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec uploadFileRequestCreation(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling uploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling uploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling uploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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

        ParameterizedTypeReference<FileUploadResponse> localVarReturnType = new ParameterizedTypeReference<FileUploadResponse>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/files", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return FileUploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<FileUploadResponse> uploadFile(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<FileUploadResponse> localVarReturnType = new ParameterizedTypeReference<FileUploadResponse>() {};
        return uploadFileRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;FileUploadResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<FileUploadResponse>> uploadFileWithHttpInfo(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<FileUploadResponse> localVarReturnType = new ParameterizedTypeReference<FileUploadResponse>() {};
        return uploadFileRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec uploadFileWithResponseSpec(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return uploadFileRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Async alternative to &#x60;&#x60;POST /datasets/{ds}/files&#x60;&#x60;.
     * Stage 1 (receive: caps check, hash, format detect, store bytes, write &#x60;&#x60;flyquery_files&#x60;&#x60; row, track workspace storage) runs *synchronously* -- it&#39;s bounded by IO + a single Postgres insert, not by parse/profile/describe cost. Stages 2-10 are queued as a &#x60;&#x60;PARSE_AND_INGEST&#x60;&#x60; ingest job that the worker consumes; the response 202 carries the &#x60;&#x60;job_id&#x60;&#x60; plus a &#x60;&#x60;Location&#x60;&#x60; header so clients can poll &#x60;&#x60;GET /ingest-jobs/{job_id}&#x60;&#x60; or stream &#x60;&#x60;GET /ingest-jobs/{job_id}/stream&#x60;&#x60;.  Use this in place of the synchronous endpoint when a single file exceeds the request-timeout budget of the deployment (typically anything above a few MB with cold-cache LLM describe calls).  Stage 1&#39;s SHA-256 content hash provides natural dedup at the file level -- re-uploading the same bytes is detected at &#x60;&#x60;flyquery_files&#x60;&#x60; UNIQUE-on-(tenant, dataset, content_hash) -- so we do NOT layer Idempotency-Key replay caching here; the underlying &#x60;&#x60;IngestJobService&#x60;&#x60; is also idempotent by construction.
     * <p><b>202</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec uploadFileAsyncRequestCreation(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling uploadFileAsync", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling uploadFileAsync", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling uploadFileAsync", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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
        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/files:async", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Async alternative to &#x60;&#x60;POST /datasets/{ds}/files&#x60;&#x60;.
     * Stage 1 (receive: caps check, hash, format detect, store bytes, write &#x60;&#x60;flyquery_files&#x60;&#x60; row, track workspace storage) runs *synchronously* -- it&#39;s bounded by IO + a single Postgres insert, not by parse/profile/describe cost. Stages 2-10 are queued as a &#x60;&#x60;PARSE_AND_INGEST&#x60;&#x60; ingest job that the worker consumes; the response 202 carries the &#x60;&#x60;job_id&#x60;&#x60; plus a &#x60;&#x60;Location&#x60;&#x60; header so clients can poll &#x60;&#x60;GET /ingest-jobs/{job_id}&#x60;&#x60; or stream &#x60;&#x60;GET /ingest-jobs/{job_id}/stream&#x60;&#x60;.  Use this in place of the synchronous endpoint when a single file exceeds the request-timeout budget of the deployment (typically anything above a few MB with cold-cache LLM describe calls).  Stage 1&#39;s SHA-256 content hash provides natural dedup at the file level -- re-uploading the same bytes is detected at &#x60;&#x60;flyquery_files&#x60;&#x60; UNIQUE-on-(tenant, dataset, content_hash) -- so we do NOT layer Idempotency-Key replay caching here; the underlying &#x60;&#x60;IngestJobService&#x60;&#x60; is also idempotent by construction.
     * <p><b>202</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> uploadFileAsync(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return uploadFileAsyncRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Async alternative to &#x60;&#x60;POST /datasets/{ds}/files&#x60;&#x60;.
     * Stage 1 (receive: caps check, hash, format detect, store bytes, write &#x60;&#x60;flyquery_files&#x60;&#x60; row, track workspace storage) runs *synchronously* -- it&#39;s bounded by IO + a single Postgres insert, not by parse/profile/describe cost. Stages 2-10 are queued as a &#x60;&#x60;PARSE_AND_INGEST&#x60;&#x60; ingest job that the worker consumes; the response 202 carries the &#x60;&#x60;job_id&#x60;&#x60; plus a &#x60;&#x60;Location&#x60;&#x60; header so clients can poll &#x60;&#x60;GET /ingest-jobs/{job_id}&#x60;&#x60; or stream &#x60;&#x60;GET /ingest-jobs/{job_id}/stream&#x60;&#x60;.  Use this in place of the synchronous endpoint when a single file exceeds the request-timeout budget of the deployment (typically anything above a few MB with cold-cache LLM describe calls).  Stage 1&#39;s SHA-256 content hash provides natural dedup at the file level -- re-uploading the same bytes is detected at &#x60;&#x60;flyquery_files&#x60;&#x60; UNIQUE-on-(tenant, dataset, content_hash) -- so we do NOT layer Idempotency-Key replay caching here; the underlying &#x60;&#x60;IngestJobService&#x60;&#x60; is also idempotent by construction.
     * <p><b>202</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> uploadFileAsyncWithHttpInfo(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return uploadFileAsyncRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Async alternative to &#x60;&#x60;POST /datasets/{ds}/files&#x60;&#x60;.
     * Stage 1 (receive: caps check, hash, format detect, store bytes, write &#x60;&#x60;flyquery_files&#x60;&#x60; row, track workspace storage) runs *synchronously* -- it&#39;s bounded by IO + a single Postgres insert, not by parse/profile/describe cost. Stages 2-10 are queued as a &#x60;&#x60;PARSE_AND_INGEST&#x60;&#x60; ingest job that the worker consumes; the response 202 carries the &#x60;&#x60;job_id&#x60;&#x60; plus a &#x60;&#x60;Location&#x60;&#x60; header so clients can poll &#x60;&#x60;GET /ingest-jobs/{job_id}&#x60;&#x60; or stream &#x60;&#x60;GET /ingest-jobs/{job_id}/stream&#x60;&#x60;.  Use this in place of the synchronous endpoint when a single file exceeds the request-timeout budget of the deployment (typically anything above a few MB with cold-cache LLM describe calls).  Stage 1&#39;s SHA-256 content hash provides natural dedup at the file level -- re-uploading the same bytes is detected at &#x60;&#x60;flyquery_files&#x60;&#x60; UNIQUE-on-(tenant, dataset, content_hash) -- so we do NOT layer Idempotency-Key replay caching here; the underlying &#x60;&#x60;IngestJobService&#x60;&#x60; is also idempotent by construction.
     * <p><b>202</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec uploadFileAsyncWithResponseSpec(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return uploadFileAsyncRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Accept multiple files in one multipart request and ingest each.
     * Each &#x60;&#x60;files&#x60;&#x60; part is processed through the same per-file pipeline as &#x60;&#x60;POST /files&#x60;&#x60; (receive -&gt; parse -&gt; reconcile -&gt; sample -&gt; profile -&gt; describe -&gt; embed -&gt; publish), and the per-file results run **in parallel** through &#x60;&#x60;asyncio.gather&#x60;&#x60; -- a 5-file upload finishes in roughly the time of a single file.  Per-file failures do NOT abort the bulk. The response carries one &#x60;&#x60;BulkFileResult&#x60;&#x60; per submitted file with either &#x60;&#x60;status&#x3D;\&quot;OK\&quot;&#x60;&#x60; + &#x60;&#x60;file_id&#x60;&#x60; + &#x60;&#x60;tables&#x60;&#x60; or &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60;. Aggregate &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts let a UI render progress without scanning the list.  Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; when present (optional on user tier). A retried bulk upload with the same key returns the cached envelope without re-ingesting -- important because the pipeline is heavy (parse + profile + describe + embed per file) and a duplicate run would double-write Parquet snapshots.
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return BulkFileUploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec uploadFilesBulkRequestCreation(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling uploadFilesBulk", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling uploadFilesBulk", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling uploadFilesBulk", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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

        ParameterizedTypeReference<BulkFileUploadResponse> localVarReturnType = new ParameterizedTypeReference<BulkFileUploadResponse>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/files:bulk", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Accept multiple files in one multipart request and ingest each.
     * Each &#x60;&#x60;files&#x60;&#x60; part is processed through the same per-file pipeline as &#x60;&#x60;POST /files&#x60;&#x60; (receive -&gt; parse -&gt; reconcile -&gt; sample -&gt; profile -&gt; describe -&gt; embed -&gt; publish), and the per-file results run **in parallel** through &#x60;&#x60;asyncio.gather&#x60;&#x60; -- a 5-file upload finishes in roughly the time of a single file.  Per-file failures do NOT abort the bulk. The response carries one &#x60;&#x60;BulkFileResult&#x60;&#x60; per submitted file with either &#x60;&#x60;status&#x3D;\&quot;OK\&quot;&#x60;&#x60; + &#x60;&#x60;file_id&#x60;&#x60; + &#x60;&#x60;tables&#x60;&#x60; or &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60;. Aggregate &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts let a UI render progress without scanning the list.  Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; when present (optional on user tier). A retried bulk upload with the same key returns the cached envelope without re-ingesting -- important because the pipeline is heavy (parse + profile + describe + embed per file) and a duplicate run would double-write Parquet snapshots.
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return BulkFileUploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<BulkFileUploadResponse> uploadFilesBulk(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<BulkFileUploadResponse> localVarReturnType = new ParameterizedTypeReference<BulkFileUploadResponse>() {};
        return uploadFilesBulkRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Accept multiple files in one multipart request and ingest each.
     * Each &#x60;&#x60;files&#x60;&#x60; part is processed through the same per-file pipeline as &#x60;&#x60;POST /files&#x60;&#x60; (receive -&gt; parse -&gt; reconcile -&gt; sample -&gt; profile -&gt; describe -&gt; embed -&gt; publish), and the per-file results run **in parallel** through &#x60;&#x60;asyncio.gather&#x60;&#x60; -- a 5-file upload finishes in roughly the time of a single file.  Per-file failures do NOT abort the bulk. The response carries one &#x60;&#x60;BulkFileResult&#x60;&#x60; per submitted file with either &#x60;&#x60;status&#x3D;\&quot;OK\&quot;&#x60;&#x60; + &#x60;&#x60;file_id&#x60;&#x60; + &#x60;&#x60;tables&#x60;&#x60; or &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60;. Aggregate &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts let a UI render progress without scanning the list.  Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; when present (optional on user tier). A retried bulk upload with the same key returns the cached envelope without re-ingesting -- important because the pipeline is heavy (parse + profile + describe + embed per file) and a duplicate run would double-write Parquet snapshots.
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;BulkFileUploadResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<BulkFileUploadResponse>> uploadFilesBulkWithHttpInfo(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<BulkFileUploadResponse> localVarReturnType = new ParameterizedTypeReference<BulkFileUploadResponse>() {};
        return uploadFilesBulkRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Accept multiple files in one multipart request and ingest each.
     * Each &#x60;&#x60;files&#x60;&#x60; part is processed through the same per-file pipeline as &#x60;&#x60;POST /files&#x60;&#x60; (receive -&gt; parse -&gt; reconcile -&gt; sample -&gt; profile -&gt; describe -&gt; embed -&gt; publish), and the per-file results run **in parallel** through &#x60;&#x60;asyncio.gather&#x60;&#x60; -- a 5-file upload finishes in roughly the time of a single file.  Per-file failures do NOT abort the bulk. The response carries one &#x60;&#x60;BulkFileResult&#x60;&#x60; per submitted file with either &#x60;&#x60;status&#x3D;\&quot;OK\&quot;&#x60;&#x60; + &#x60;&#x60;file_id&#x60;&#x60; + &#x60;&#x60;tables&#x60;&#x60; or &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60;. Aggregate &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts let a UI render progress without scanning the list.  Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; when present (optional on user tier). A retried bulk upload with the same key returns the cached envelope without re-ingesting -- important because the pipeline is heavy (parse + profile + describe + embed per file) and a duplicate run would double-write Parquet snapshots.
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec uploadFilesBulkWithResponseSpec(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return uploadFilesBulkRequestCreation(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }
}
