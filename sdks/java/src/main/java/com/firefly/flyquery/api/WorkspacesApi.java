package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.WorkspaceCreate;
import com.firefly.flyquery.model.WorkspaceRead;
import com.firefly.flyquery.model.WorkspaceUpdate;

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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-24T00:36:39.059958+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class WorkspacesApi {
    private ApiClient apiClient;

    public WorkspacesApi() {
        this(new ApiClient());
    }

    public WorkspacesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceCreate The workspaceCreate parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull WorkspaceCreate workspaceCreate) throws WebClientResponseException {
        Object postBody = workspaceCreate;
        // verify the required parameter 'workspaceCreate' is set
        if (workspaceCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'workspaceCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return apiClient.invokeAPI("/api/v1/workspaces", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceCreate The workspaceCreate parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<WorkspaceRead> create(@javax.annotation.Nonnull WorkspaceCreate workspaceCreate) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return createRequestCreation(workspaceCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceCreate The workspaceCreate parameter
     * @return ResponseEntity&lt;WorkspaceRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<WorkspaceRead>> createWithHttpInfo(@javax.annotation.Nonnull WorkspaceCreate workspaceCreate) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return createRequestCreation(workspaceCreate).toEntity(localVarReturnType);
    }

    /**
     * Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceCreate The workspaceCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull WorkspaceCreate workspaceCreate) throws WebClientResponseException {
        return createRequestCreation(workspaceCreate);
    }

    /**
     * Search/filter workspaces for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;      -- free-text substring match against &#x60;&#x60;slug&#x60;&#x60; or &#x60;&#x60;name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;slug&#x60;&#x60;   -- exact match on &#x60;&#x60;slug&#x60;&#x60; -- gives you slug-based lookup with zero extra round trips. * &#x60;&#x60;status&#x60;&#x60; -- exact match (&#x60;&#x60;ACTIVE&#x60;&#x60;, &#x60;&#x60;ARCHIVED&#x60;&#x60;, &#x60;&#x60;PURGING&#x60;&#x60;). * &#x60;&#x60;limit&#x60;&#x60;  -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60; -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60; where &#x60;&#x60;total&#x60;&#x60; is the un-paginated match count.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param slug The slug parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listWorkspacesRequestCreation(@javax.annotation.Nullable String q, @javax.annotation.Nullable String slug, @javax.annotation.Nullable String status, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "q", q));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "slug", slug));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "status", status));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/workspaces", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Search/filter workspaces for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;      -- free-text substring match against &#x60;&#x60;slug&#x60;&#x60; or &#x60;&#x60;name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;slug&#x60;&#x60;   -- exact match on &#x60;&#x60;slug&#x60;&#x60; -- gives you slug-based lookup with zero extra round trips. * &#x60;&#x60;status&#x60;&#x60; -- exact match (&#x60;&#x60;ACTIVE&#x60;&#x60;, &#x60;&#x60;ARCHIVED&#x60;&#x60;, &#x60;&#x60;PURGING&#x60;&#x60;). * &#x60;&#x60;limit&#x60;&#x60;  -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60; -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60; where &#x60;&#x60;total&#x60;&#x60; is the un-paginated match count.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param slug The slug parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listWorkspaces(@javax.annotation.Nullable String q, @javax.annotation.Nullable String slug, @javax.annotation.Nullable String status, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listWorkspacesRequestCreation(q, slug, status, limit, offset).bodyToMono(localVarReturnType);
    }

    /**
     * Search/filter workspaces for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;      -- free-text substring match against &#x60;&#x60;slug&#x60;&#x60; or &#x60;&#x60;name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;slug&#x60;&#x60;   -- exact match on &#x60;&#x60;slug&#x60;&#x60; -- gives you slug-based lookup with zero extra round trips. * &#x60;&#x60;status&#x60;&#x60; -- exact match (&#x60;&#x60;ACTIVE&#x60;&#x60;, &#x60;&#x60;ARCHIVED&#x60;&#x60;, &#x60;&#x60;PURGING&#x60;&#x60;). * &#x60;&#x60;limit&#x60;&#x60;  -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60; -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60; where &#x60;&#x60;total&#x60;&#x60; is the un-paginated match count.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param slug The slug parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listWorkspacesWithHttpInfo(@javax.annotation.Nullable String q, @javax.annotation.Nullable String slug, @javax.annotation.Nullable String status, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listWorkspacesRequestCreation(q, slug, status, limit, offset).toEntity(localVarReturnType);
    }

    /**
     * Search/filter workspaces for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;      -- free-text substring match against &#x60;&#x60;slug&#x60;&#x60; or &#x60;&#x60;name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;slug&#x60;&#x60;   -- exact match on &#x60;&#x60;slug&#x60;&#x60; -- gives you slug-based lookup with zero extra round trips. * &#x60;&#x60;status&#x60;&#x60; -- exact match (&#x60;&#x60;ACTIVE&#x60;&#x60;, &#x60;&#x60;ARCHIVED&#x60;&#x60;, &#x60;&#x60;PURGING&#x60;&#x60;). * &#x60;&#x60;limit&#x60;&#x60;  -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60; -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60; where &#x60;&#x60;total&#x60;&#x60; is the un-paginated match count.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param slug The slug parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listWorkspacesWithResponseSpec(@javax.annotation.Nullable String q, @javax.annotation.Nullable String slug, @javax.annotation.Nullable String status, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        return listWorkspacesRequestCreation(q, slug, status, limit, offset);
    }

    /**
     * Purge a workspace: mark PURGING + walk + delete all blobs.
     * Returns 202 Accepted with a tombstone placeholder.
     * <p><b>202</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec purgeRequestCreation(@javax.annotation.Nonnull String workspaceId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'workspaceId' is set
        if (workspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'workspaceId' when calling purge", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("workspace_id", workspaceId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/workspaces/{workspace_id}:purge", HttpMethod.DELETE, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Purge a workspace: mark PURGING + walk + delete all blobs.
     * Returns 202 Accepted with a tombstone placeholder.
     * <p><b>202</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> purge(@javax.annotation.Nonnull String workspaceId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return purgeRequestCreation(workspaceId).bodyToMono(localVarReturnType);
    }

    /**
     * Purge a workspace: mark PURGING + walk + delete all blobs.
     * Returns 202 Accepted with a tombstone placeholder.
     * <p><b>202</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> purgeWithHttpInfo(@javax.annotation.Nonnull String workspaceId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return purgeRequestCreation(workspaceId).toEntity(localVarReturnType);
    }

    /**
     * Purge a workspace: mark PURGING + walk + delete all blobs.
     * Returns 202 Accepted with a tombstone placeholder.
     * <p><b>202</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec purgeWithResponseSpec(@javax.annotation.Nonnull String workspaceId) throws WebClientResponseException {
        return purgeRequestCreation(workspaceId);
    }

    /**
     * Fetch a single workspace by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec readRequestCreation(@javax.annotation.Nullable String workspaceId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'workspaceId' is set
        if (workspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'workspaceId' when calling read", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("workspace_id", workspaceId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return apiClient.invokeAPI("/api/v1/workspaces/{workspace_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single workspace by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<WorkspaceRead> read(@javax.annotation.Nullable String workspaceId) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return readRequestCreation(workspaceId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single workspace by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @return ResponseEntity&lt;WorkspaceRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<WorkspaceRead>> readWithHttpInfo(@javax.annotation.Nullable String workspaceId) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return readRequestCreation(workspaceId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single workspace by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param workspaceId The workspaceId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec readWithResponseSpec(@javax.annotation.Nullable String workspaceId) throws WebClientResponseException {
        return readRequestCreation(workspaceId);
    }

    /**
     * Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key.
     * Lets SDKs and CLIs resolve a workspace from a memorable identifier instead of carrying around a UUID. Returns 404 if no match.
     * <p><b>200</b> - Successful response
     * @param slug The slug parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec readBySlugRequestCreation(@javax.annotation.Nullable String slug) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'slug' is set
        if (slug == null) {
            throw new WebClientResponseException("Missing the required parameter 'slug' when calling readBySlug", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("slug", slug);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return apiClient.invokeAPI("/api/v1/workspaces/by-slug/{slug}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key.
     * Lets SDKs and CLIs resolve a workspace from a memorable identifier instead of carrying around a UUID. Returns 404 if no match.
     * <p><b>200</b> - Successful response
     * @param slug The slug parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<WorkspaceRead> readBySlug(@javax.annotation.Nullable String slug) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return readBySlugRequestCreation(slug).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key.
     * Lets SDKs and CLIs resolve a workspace from a memorable identifier instead of carrying around a UUID. Returns 404 if no match.
     * <p><b>200</b> - Successful response
     * @param slug The slug parameter
     * @return ResponseEntity&lt;WorkspaceRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<WorkspaceRead>> readBySlugWithHttpInfo(@javax.annotation.Nullable String slug) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return readBySlugRequestCreation(slug).toEntity(localVarReturnType);
    }

    /**
     * Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key.
     * Lets SDKs and CLIs resolve a workspace from a memorable identifier instead of carrying around a UUID. Returns 404 if no match.
     * <p><b>200</b> - Successful response
     * @param slug The slug parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec readBySlugWithResponseSpec(@javax.annotation.Nullable String slug) throws WebClientResponseException {
        return readBySlugRequestCreation(slug);
    }

    /**
     * Sparse-update a workspace. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceId The workspaceId parameter
     * @param workspaceUpdate The workspaceUpdate parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@javax.annotation.Nonnull String workspaceId, @javax.annotation.Nonnull WorkspaceUpdate workspaceUpdate) throws WebClientResponseException {
        Object postBody = workspaceUpdate;
        // verify the required parameter 'workspaceId' is set
        if (workspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'workspaceId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'workspaceUpdate' is set
        if (workspaceUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'workspaceUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("workspace_id", workspaceId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return apiClient.invokeAPI("/api/v1/workspaces/{workspace_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a workspace. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceId The workspaceId parameter
     * @param workspaceUpdate The workspaceUpdate parameter
     * @return WorkspaceRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<WorkspaceRead> update(@javax.annotation.Nonnull String workspaceId, @javax.annotation.Nonnull WorkspaceUpdate workspaceUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return updateRequestCreation(workspaceId, workspaceUpdate).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a workspace. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceId The workspaceId parameter
     * @param workspaceUpdate The workspaceUpdate parameter
     * @return ResponseEntity&lt;WorkspaceRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<WorkspaceRead>> updateWithHttpInfo(@javax.annotation.Nonnull String workspaceId, @javax.annotation.Nonnull WorkspaceUpdate workspaceUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<WorkspaceRead> localVarReturnType = new ParameterizedTypeReference<WorkspaceRead>() {};
        return updateRequestCreation(workspaceId, workspaceUpdate).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a workspace. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param workspaceId The workspaceId parameter
     * @param workspaceUpdate The workspaceUpdate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@javax.annotation.Nonnull String workspaceId, @javax.annotation.Nonnull WorkspaceUpdate workspaceUpdate) throws WebClientResponseException {
        return updateRequestCreation(workspaceId, workspaceUpdate);
    }
}
