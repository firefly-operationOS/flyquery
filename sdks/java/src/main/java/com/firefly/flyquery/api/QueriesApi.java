package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.PaginatedQueryHistoryItem;
import com.firefly.flyquery.model.QueryDetailRead;
import com.firefly.flyquery.model.QueryResultRead;
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
public class QueriesApi {
    private ApiClient apiClient;

    public QueriesApi() {
        this(new ApiClient());
    }

    public QueriesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Fetch a single query with every candidate, retry, and model id.
     * Returns 404 if the query doesn&#39;t belong to the caller&#39;s &#x60;&#x60;(tenant, workspace)&#x60;&#x60; -- not just \&quot;not found\&quot;, but also \&quot;exists but wrong tenant\&quot; (cross-tenant probing is the same 404 as missing).
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return QueryDetailRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getQueryRequestCreation(@jakarta.annotation.Nullable String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'queryId' is set
        if (queryId == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryId' when calling getQuery", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling getQuery", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling getQuery", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("query_id", queryId);

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

        ParameterizedTypeReference<QueryDetailRead> localVarReturnType = new ParameterizedTypeReference<QueryDetailRead>() {};
        return apiClient.invokeAPI("/api/v1/queries/{query_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single query with every candidate, retry, and model id.
     * Returns 404 if the query doesn&#39;t belong to the caller&#39;s &#x60;&#x60;(tenant, workspace)&#x60;&#x60; -- not just \&quot;not found\&quot;, but also \&quot;exists but wrong tenant\&quot; (cross-tenant probing is the same 404 as missing).
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return QueryDetailRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<QueryDetailRead> getQuery(@jakarta.annotation.Nullable String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<QueryDetailRead> localVarReturnType = new ParameterizedTypeReference<QueryDetailRead>() {};
        return getQueryRequestCreation(queryId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single query with every candidate, retry, and model id.
     * Returns 404 if the query doesn&#39;t belong to the caller&#39;s &#x60;&#x60;(tenant, workspace)&#x60;&#x60; -- not just \&quot;not found\&quot;, but also \&quot;exists but wrong tenant\&quot; (cross-tenant probing is the same 404 as missing).
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;QueryDetailRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<QueryDetailRead>> getQueryWithHttpInfo(@jakarta.annotation.Nullable String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<QueryDetailRead> localVarReturnType = new ParameterizedTypeReference<QueryDetailRead>() {};
        return getQueryRequestCreation(queryId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single query with every candidate, retry, and model id.
     * Returns 404 if the query doesn&#39;t belong to the caller&#39;s &#x60;&#x60;(tenant, workspace)&#x60;&#x60; -- not just \&quot;not found\&quot;, but also \&quot;exists but wrong tenant\&quot; (cross-tenant probing is the same 404 as missing).
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getQueryWithResponseSpec(@jakarta.annotation.Nullable String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getQueryRequestCreation(queryId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * Re-download a previously-executed query&#39;s preview + parquet.
     * The preview is always inlined. The presigned Parquet URL is &#x60;&#x60;None&#x60;&#x60; when the TTL has elapsed (default 24h) -- consumers must rerun the query in that case. The presign TTL itself is bounded by &#x60;&#x60;object_store_presign_ttl_s&#x60;&#x60; (default 24h).  Returns 404 if either the query OR its result row doesn&#39;t exist for this tenant.
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return QueryResultRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getQueryResultRequestCreation(@jakarta.annotation.Nonnull String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'queryId' is set
        if (queryId == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryId' when calling getQueryResult", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling getQueryResult", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling getQueryResult", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("query_id", queryId);

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

        ParameterizedTypeReference<QueryResultRead> localVarReturnType = new ParameterizedTypeReference<QueryResultRead>() {};
        return apiClient.invokeAPI("/api/v1/queries/{query_id}/result", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Re-download a previously-executed query&#39;s preview + parquet.
     * The preview is always inlined. The presigned Parquet URL is &#x60;&#x60;None&#x60;&#x60; when the TTL has elapsed (default 24h) -- consumers must rerun the query in that case. The presign TTL itself is bounded by &#x60;&#x60;object_store_presign_ttl_s&#x60;&#x60; (default 24h).  Returns 404 if either the query OR its result row doesn&#39;t exist for this tenant.
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return QueryResultRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<QueryResultRead> getQueryResult(@jakarta.annotation.Nonnull String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<QueryResultRead> localVarReturnType = new ParameterizedTypeReference<QueryResultRead>() {};
        return getQueryResultRequestCreation(queryId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Re-download a previously-executed query&#39;s preview + parquet.
     * The preview is always inlined. The presigned Parquet URL is &#x60;&#x60;None&#x60;&#x60; when the TTL has elapsed (default 24h) -- consumers must rerun the query in that case. The presign TTL itself is bounded by &#x60;&#x60;object_store_presign_ttl_s&#x60;&#x60; (default 24h).  Returns 404 if either the query OR its result row doesn&#39;t exist for this tenant.
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;QueryResultRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<QueryResultRead>> getQueryResultWithHttpInfo(@jakarta.annotation.Nonnull String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<QueryResultRead> localVarReturnType = new ParameterizedTypeReference<QueryResultRead>() {};
        return getQueryResultRequestCreation(queryId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Re-download a previously-executed query&#39;s preview + parquet.
     * The preview is always inlined. The presigned Parquet URL is &#x60;&#x60;None&#x60;&#x60; when the TTL has elapsed (default 24h) -- consumers must rerun the query in that case. The presign TTL itself is bounded by &#x60;&#x60;object_store_presign_ttl_s&#x60;&#x60; (default 24h).  Returns 404 if either the query OR its result row doesn&#39;t exist for this tenant.
     * <p><b>200</b> - Successful response
     * @param queryId The queryId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getQueryResultWithResponseSpec(@jakarta.annotation.Nonnull String queryId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getQueryResultRequestCreation(queryId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * List queries for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;dataset_id&#x60;&#x60;           -- restrict to one dataset * &#x60;&#x60;execution_status&#x60;&#x60;     -- &#x60;&#x60;OK&#x60;&#x60; / &#x60;&#x60;REJECTED_BY_FIREWALL&#x60;&#x60; / &#x60;&#x60;FAILED&#x60;&#x60; / ... * &#x60;&#x60;semantic_path_taken&#x60;&#x60;  -- e.g. &#x60;&#x60;\&quot;sql\&quot;&#x60;&#x60; vs &#x60;&#x60;\&quot;semantic-layer\&quot;&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60;            -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;              -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Page size is clamped to &#x60;&#x60;[1, 200]&#x60;&#x60;. Each item is the compact history shape (no heavy JSONB columns). Use &#x60;&#x60;GET /queries/{id}&#x60;&#x60; for the full row.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param executionStatus The executionStatus parameter
     * @param semanticPathTaken The semanticPathTaken parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedQueryHistoryItem
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listQueriesRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String executionStatus, @jakarta.annotation.Nullable String semanticPathTaken, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listQueries", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listQueries", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "execution_status", executionStatus));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "semantic_path_taken", semanticPathTaken));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "date_from", dateFrom));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "date_to", dateTo));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

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

        ParameterizedTypeReference<PaginatedQueryHistoryItem> localVarReturnType = new ParameterizedTypeReference<PaginatedQueryHistoryItem>() {};
        return apiClient.invokeAPI("/api/v1/queries", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List queries for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;dataset_id&#x60;&#x60;           -- restrict to one dataset * &#x60;&#x60;execution_status&#x60;&#x60;     -- &#x60;&#x60;OK&#x60;&#x60; / &#x60;&#x60;REJECTED_BY_FIREWALL&#x60;&#x60; / &#x60;&#x60;FAILED&#x60;&#x60; / ... * &#x60;&#x60;semantic_path_taken&#x60;&#x60;  -- e.g. &#x60;&#x60;\&quot;sql\&quot;&#x60;&#x60; vs &#x60;&#x60;\&quot;semantic-layer\&quot;&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60;            -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;              -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Page size is clamped to &#x60;&#x60;[1, 200]&#x60;&#x60;. Each item is the compact history shape (no heavy JSONB columns). Use &#x60;&#x60;GET /queries/{id}&#x60;&#x60; for the full row.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param executionStatus The executionStatus parameter
     * @param semanticPathTaken The semanticPathTaken parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedQueryHistoryItem
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedQueryHistoryItem> listQueries(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String executionStatus, @jakarta.annotation.Nullable String semanticPathTaken, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedQueryHistoryItem> localVarReturnType = new ParameterizedTypeReference<PaginatedQueryHistoryItem>() {};
        return listQueriesRequestCreation(xTenantId, xWorkspaceId, datasetId, executionStatus, semanticPathTaken, dateFrom, dateTo, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List queries for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;dataset_id&#x60;&#x60;           -- restrict to one dataset * &#x60;&#x60;execution_status&#x60;&#x60;     -- &#x60;&#x60;OK&#x60;&#x60; / &#x60;&#x60;REJECTED_BY_FIREWALL&#x60;&#x60; / &#x60;&#x60;FAILED&#x60;&#x60; / ... * &#x60;&#x60;semantic_path_taken&#x60;&#x60;  -- e.g. &#x60;&#x60;\&quot;sql\&quot;&#x60;&#x60; vs &#x60;&#x60;\&quot;semantic-layer\&quot;&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60;            -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;              -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Page size is clamped to &#x60;&#x60;[1, 200]&#x60;&#x60;. Each item is the compact history shape (no heavy JSONB columns). Use &#x60;&#x60;GET /queries/{id}&#x60;&#x60; for the full row.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param executionStatus The executionStatus parameter
     * @param semanticPathTaken The semanticPathTaken parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedQueryHistoryItem&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedQueryHistoryItem>> listQueriesWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String executionStatus, @jakarta.annotation.Nullable String semanticPathTaken, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedQueryHistoryItem> localVarReturnType = new ParameterizedTypeReference<PaginatedQueryHistoryItem>() {};
        return listQueriesRequestCreation(xTenantId, xWorkspaceId, datasetId, executionStatus, semanticPathTaken, dateFrom, dateTo, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List queries for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;dataset_id&#x60;&#x60;           -- restrict to one dataset * &#x60;&#x60;execution_status&#x60;&#x60;     -- &#x60;&#x60;OK&#x60;&#x60; / &#x60;&#x60;REJECTED_BY_FIREWALL&#x60;&#x60; / &#x60;&#x60;FAILED&#x60;&#x60; / ... * &#x60;&#x60;semantic_path_taken&#x60;&#x60;  -- e.g. &#x60;&#x60;\&quot;sql\&quot;&#x60;&#x60; vs &#x60;&#x60;\&quot;semantic-layer\&quot;&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60;            -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;              -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Page size is clamped to &#x60;&#x60;[1, 200]&#x60;&#x60;. Each item is the compact history shape (no heavy JSONB columns). Use &#x60;&#x60;GET /queries/{id}&#x60;&#x60; for the full row.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param executionStatus The executionStatus parameter
     * @param semanticPathTaken The semanticPathTaken parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listQueriesWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String executionStatus, @jakarta.annotation.Nullable String semanticPathTaken, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listQueriesRequestCreation(xTenantId, xWorkspaceId, datasetId, executionStatus, semanticPathTaken, dateFrom, dateTo, limit, offset, xCorrelationId);
    }
}
