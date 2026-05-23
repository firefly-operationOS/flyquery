package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.DatasetCreate;
import com.firefly.flyquery.model.DatasetRead;
import com.firefly.flyquery.model.DatasetUpdate;
import com.firefly.flyquery.model.HTTPValidationError;

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
public class DatasetsApi {
    private ApiClient apiClient;

    public DatasetsApi() {
        this(new ApiClient());
    }

    public DatasetsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Archive a dataset (set status&#x3D;ARCHIVED).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec archiveRequestCreation(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling archive", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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

        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}", HttpMethod.DELETE, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Archive a dataset (set status&#x3D;ARCHIVED).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DatasetRead> archive(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return archiveRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * Archive a dataset (set status&#x3D;ARCHIVED).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseEntity&lt;DatasetRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DatasetRead>> archiveWithHttpInfo(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return archiveRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * Archive a dataset (set status&#x3D;ARCHIVED).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec archiveWithResponseSpec(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        return archiveRequestCreation(datasetId);
    }

    /**
     * Create a dataset; tenant + workspace come from request headers.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetCreate The datasetCreate parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull DatasetCreate datasetCreate) throws WebClientResponseException {
        Object postBody = datasetCreate;
        // verify the required parameter 'datasetCreate' is set
        if (datasetCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return apiClient.invokeAPI("/api/v1/datasets", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a dataset; tenant + workspace come from request headers.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetCreate The datasetCreate parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DatasetRead> create(@javax.annotation.Nonnull DatasetCreate datasetCreate) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return createRequestCreation(datasetCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create a dataset; tenant + workspace come from request headers.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetCreate The datasetCreate parameter
     * @return ResponseEntity&lt;DatasetRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DatasetRead>> createWithHttpInfo(@javax.annotation.Nonnull DatasetCreate datasetCreate) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return createRequestCreation(datasetCreate).toEntity(localVarReturnType);
    }

    /**
     * Create a dataset; tenant + workspace come from request headers.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetCreate The datasetCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull DatasetCreate datasetCreate) throws WebClientResponseException {
        return createRequestCreation(datasetCreate);
    }

    /**
     * Search/filter datasets for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;            -- free-text substring against &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;description&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;         -- exact match -- gives you name-based lookup with zero extra round-trips. * &#x60;&#x60;status&#x60;&#x60;       -- &#x60;&#x60;ACTIVE&#x60;&#x60; / &#x60;&#x60;ARCHIVED&#x60;&#x60; / &#x60;&#x60;PURGING&#x60;&#x60;. * &#x60;&#x60;workspace_id&#x60;&#x60; -- restrict to a single workspace; defaults to &#x60;&#x60;X-Workspace-Id&#x60;&#x60; header. Pass another UUID explicitly to override the header. * &#x60;&#x60;limit&#x60;&#x60;        -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;       -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param status The status parameter
     * @param workspaceId The workspaceId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listDatasetsRequestCreation(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String status, @javax.annotation.Nullable String workspaceId, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "q", q));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "name", name));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "status", status));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "workspace_id", workspaceId));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/datasets", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Search/filter datasets for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;            -- free-text substring against &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;description&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;         -- exact match -- gives you name-based lookup with zero extra round-trips. * &#x60;&#x60;status&#x60;&#x60;       -- &#x60;&#x60;ACTIVE&#x60;&#x60; / &#x60;&#x60;ARCHIVED&#x60;&#x60; / &#x60;&#x60;PURGING&#x60;&#x60;. * &#x60;&#x60;workspace_id&#x60;&#x60; -- restrict to a single workspace; defaults to &#x60;&#x60;X-Workspace-Id&#x60;&#x60; header. Pass another UUID explicitly to override the header. * &#x60;&#x60;limit&#x60;&#x60;        -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;       -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param status The status parameter
     * @param workspaceId The workspaceId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listDatasets(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String status, @javax.annotation.Nullable String workspaceId, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listDatasetsRequestCreation(q, name, status, workspaceId, limit, offset).bodyToMono(localVarReturnType);
    }

    /**
     * Search/filter datasets for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;            -- free-text substring against &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;description&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;         -- exact match -- gives you name-based lookup with zero extra round-trips. * &#x60;&#x60;status&#x60;&#x60;       -- &#x60;&#x60;ACTIVE&#x60;&#x60; / &#x60;&#x60;ARCHIVED&#x60;&#x60; / &#x60;&#x60;PURGING&#x60;&#x60;. * &#x60;&#x60;workspace_id&#x60;&#x60; -- restrict to a single workspace; defaults to &#x60;&#x60;X-Workspace-Id&#x60;&#x60; header. Pass another UUID explicitly to override the header. * &#x60;&#x60;limit&#x60;&#x60;        -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;       -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param status The status parameter
     * @param workspaceId The workspaceId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listDatasetsWithHttpInfo(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String status, @javax.annotation.Nullable String workspaceId, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listDatasetsRequestCreation(q, name, status, workspaceId, limit, offset).toEntity(localVarReturnType);
    }

    /**
     * Search/filter datasets for the caller&#39;s tenant.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;            -- free-text substring against &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;description&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;         -- exact match -- gives you name-based lookup with zero extra round-trips. * &#x60;&#x60;status&#x60;&#x60;       -- &#x60;&#x60;ACTIVE&#x60;&#x60; / &#x60;&#x60;ARCHIVED&#x60;&#x60; / &#x60;&#x60;PURGING&#x60;&#x60;. * &#x60;&#x60;workspace_id&#x60;&#x60; -- restrict to a single workspace; defaults to &#x60;&#x60;X-Workspace-Id&#x60;&#x60; header. Pass another UUID explicitly to override the header. * &#x60;&#x60;limit&#x60;&#x60;        -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;       -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param status The status parameter
     * @param workspaceId The workspaceId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listDatasetsWithResponseSpec(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String status, @javax.annotation.Nullable String workspaceId, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        return listDatasetsRequestCreation(q, name, status, workspaceId, limit, offset);
    }

    /**
     * Fetch a single dataset by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec readRequestCreation(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling read", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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

        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single dataset by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DatasetRead> read(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return readRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single dataset by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseEntity&lt;DatasetRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DatasetRead>> readWithHttpInfo(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return readRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single dataset by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec readWithResponseSpec(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        return readRequestCreation(datasetId);
    }

    /**
     * Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;.
     * Reads the workspace scope from &#x60;&#x60;X-Workspace-Id&#x60;&#x60;. Datasets enforce &#x60;&#x60;UNIQUE(workspace_id, name)&#x60;&#x60; so the lookup always returns 0 or 1.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec readByNameRequestCreation(@javax.annotation.Nullable String name) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'name' is set
        if (name == null) {
            throw new WebClientResponseException("Missing the required parameter 'name' when calling readByName", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("name", name);

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

        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return apiClient.invokeAPI("/api/v1/datasets/by-name/{name}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;.
     * Reads the workspace scope from &#x60;&#x60;X-Workspace-Id&#x60;&#x60;. Datasets enforce &#x60;&#x60;UNIQUE(workspace_id, name)&#x60;&#x60; so the lookup always returns 0 or 1.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DatasetRead> readByName(@javax.annotation.Nullable String name) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return readByNameRequestCreation(name).bodyToMono(localVarReturnType);
    }

    /**
     * Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;.
     * Reads the workspace scope from &#x60;&#x60;X-Workspace-Id&#x60;&#x60;. Datasets enforce &#x60;&#x60;UNIQUE(workspace_id, name)&#x60;&#x60; so the lookup always returns 0 or 1.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @return ResponseEntity&lt;DatasetRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DatasetRead>> readByNameWithHttpInfo(@javax.annotation.Nullable String name) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return readByNameRequestCreation(name).toEntity(localVarReturnType);
    }

    /**
     * Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;.
     * Reads the workspace scope from &#x60;&#x60;X-Workspace-Id&#x60;&#x60;. Datasets enforce &#x60;&#x60;UNIQUE(workspace_id, name)&#x60;&#x60; so the lookup always returns 0 or 1.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec readByNameWithResponseSpec(@javax.annotation.Nullable String name) throws WebClientResponseException {
        return readByNameRequestCreation(name);
    }

    /**
     * Sparse-update a dataset. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetId The datasetId parameter
     * @param datasetUpdate The datasetUpdate parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nonnull DatasetUpdate datasetUpdate) throws WebClientResponseException {
        Object postBody = datasetUpdate;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'datasetUpdate' is set
        if (datasetUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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

        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a dataset. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetId The datasetId parameter
     * @param datasetUpdate The datasetUpdate parameter
     * @return DatasetRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DatasetRead> update(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nonnull DatasetUpdate datasetUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return updateRequestCreation(datasetId, datasetUpdate).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a dataset. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetId The datasetId parameter
     * @param datasetUpdate The datasetUpdate parameter
     * @return ResponseEntity&lt;DatasetRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DatasetRead>> updateWithHttpInfo(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nonnull DatasetUpdate datasetUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<DatasetRead> localVarReturnType = new ParameterizedTypeReference<DatasetRead>() {};
        return updateRequestCreation(datasetId, datasetUpdate).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a dataset. Only fields present in body are changed.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param datasetId The datasetId parameter
     * @param datasetUpdate The datasetUpdate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nonnull DatasetUpdate datasetUpdate) throws WebClientResponseException {
        return updateRequestCreation(datasetId, datasetUpdate);
    }
}
