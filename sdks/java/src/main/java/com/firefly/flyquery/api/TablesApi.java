package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.TableRead;

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
public class TablesApi {
    private ApiClient apiClient;

    public TablesApi() {
        this(new ApiClient());
    }

    public TablesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return TableRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getTableRequestCreation(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'tableId' is set
        if (tableId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tableId' when calling getTable", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("table_id", tableId);

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

        ParameterizedTypeReference<TableRead> localVarReturnType = new ParameterizedTypeReference<TableRead>() {};
        return apiClient.invokeAPI("/api/v1/tables/{table_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return TableRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<TableRead> getTable(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<TableRead> localVarReturnType = new ParameterizedTypeReference<TableRead>() {};
        return getTableRequestCreation(tableId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return ResponseEntity&lt;TableRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<TableRead>> getTableWithHttpInfo(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<TableRead> localVarReturnType = new ParameterizedTypeReference<TableRead>() {};
        return getTableRequestCreation(tableId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getTableWithResponseSpec(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        return getTableRequestCreation(tableId);
    }

    /**
     * Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace.
     * Pass &#x60;&#x60;?dataset_id&#x3D;...&#x60;&#x60; to scope the lookup to a single dataset. Returns 404 if the name is not unique within the scope or no match is found.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @return TableRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getTableByNameRequestCreation(@javax.annotation.Nonnull String name, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'name' is set
        if (name == null) {
            throw new WebClientResponseException("Missing the required parameter 'name' when calling getTableByName", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("name", name);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<TableRead> localVarReturnType = new ParameterizedTypeReference<TableRead>() {};
        return apiClient.invokeAPI("/api/v1/tables/by-name/{name}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace.
     * Pass &#x60;&#x60;?dataset_id&#x3D;...&#x60;&#x60; to scope the lookup to a single dataset. Returns 404 if the name is not unique within the scope or no match is found.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @return TableRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<TableRead> getTableByName(@javax.annotation.Nonnull String name, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<TableRead> localVarReturnType = new ParameterizedTypeReference<TableRead>() {};
        return getTableByNameRequestCreation(name, datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace.
     * Pass &#x60;&#x60;?dataset_id&#x3D;...&#x60;&#x60; to scope the lookup to a single dataset. Returns 404 if the name is not unique within the scope or no match is found.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @return ResponseEntity&lt;TableRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<TableRead>> getTableByNameWithHttpInfo(@javax.annotation.Nonnull String name, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<TableRead> localVarReturnType = new ParameterizedTypeReference<TableRead>() {};
        return getTableByNameRequestCreation(name, datasetId).toEntity(localVarReturnType);
    }

    /**
     * Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace.
     * Pass &#x60;&#x60;?dataset_id&#x3D;...&#x60;&#x60; to scope the lookup to a single dataset. Returns 404 if the name is not unique within the scope or no match is found.
     * <p><b>200</b> - Successful response
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getTableByNameWithResponseSpec(@javax.annotation.Nonnull String name, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        return getTableByNameRequestCreation(name, datasetId);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listChangesRequestCreation(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'tableId' is set
        if (tableId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tableId' when calling listChanges", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("table_id", tableId);

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
        return apiClient.invokeAPI("/api/v1/tables/{table_id}/changes", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listChanges(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listChangesRequestCreation(tableId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listChangesWithHttpInfo(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listChangesRequestCreation(tableId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listChangesWithResponseSpec(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        return listChangesRequestCreation(tableId);
    }

    /**
     * List schema_objects for the table&#39;s current snapshot.
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listObjectsRequestCreation(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'tableId' is set
        if (tableId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tableId' when calling listObjects", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("table_id", tableId);

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
        return apiClient.invokeAPI("/api/v1/tables/{table_id}/objects", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List schema_objects for the table&#39;s current snapshot.
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listObjects(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listObjectsRequestCreation(tableId).bodyToMono(localVarReturnType);
    }

    /**
     * List schema_objects for the table&#39;s current snapshot.
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listObjectsWithHttpInfo(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listObjectsRequestCreation(tableId).toEntity(localVarReturnType);
    }

    /**
     * List schema_objects for the table&#39;s current snapshot.
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listObjectsWithResponseSpec(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        return listObjectsRequestCreation(tableId);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listSnapshotsRequestCreation(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'tableId' is set
        if (tableId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tableId' when calling listSnapshots", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("table_id", tableId);

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
        return apiClient.invokeAPI("/api/v1/tables/{table_id}/snapshots", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listSnapshots(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listSnapshotsRequestCreation(tableId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listSnapshotsWithHttpInfo(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listSnapshotsRequestCreation(tableId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param tableId The tableId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listSnapshotsWithResponseSpec(@javax.annotation.Nonnull String tableId) throws WebClientResponseException {
        return listSnapshotsRequestCreation(tableId);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listTablesRequestCreation(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling listTables", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

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
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/tables", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listTables(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listTablesRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listTablesWithHttpInfo(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listTablesRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * 
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listTablesWithResponseSpec(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        return listTablesRequestCreation(datasetId);
    }

    /**
     * Search/filter tables across the caller&#39;s workspace.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;          -- substring match on &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;qualified_name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;       -- exact match on &#x60;&#x60;name&#x60;&#x60;. * &#x60;&#x60;dataset_id&#x60;&#x60; -- restrict to a single dataset. * &#x60;&#x60;kind&#x60;&#x60;       -- &#x60;&#x60;UPLOADED&#x60;&#x60; / &#x60;&#x60;VIEW&#x60;&#x60; / &#x60;&#x60;DERIVED&#x60;&#x60;. * &#x60;&#x60;is_active&#x60;&#x60;  -- default &#x60;&#x60;true&#x60;&#x60;; pass &#x60;&#x60;false&#x60;&#x60; to include archived tables. * &#x60;&#x60;limit&#x60;&#x60;      -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;     -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @param kind The kind parameter
     * @param isActive The isActive parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec searchTablesRequestCreation(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String datasetId, @javax.annotation.Nullable String kind, @javax.annotation.Nullable String isActive, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "q", q));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "name", name));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "kind", kind));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "is_active", isActive));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/tables", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Search/filter tables across the caller&#39;s workspace.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;          -- substring match on &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;qualified_name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;       -- exact match on &#x60;&#x60;name&#x60;&#x60;. * &#x60;&#x60;dataset_id&#x60;&#x60; -- restrict to a single dataset. * &#x60;&#x60;kind&#x60;&#x60;       -- &#x60;&#x60;UPLOADED&#x60;&#x60; / &#x60;&#x60;VIEW&#x60;&#x60; / &#x60;&#x60;DERIVED&#x60;&#x60;. * &#x60;&#x60;is_active&#x60;&#x60;  -- default &#x60;&#x60;true&#x60;&#x60;; pass &#x60;&#x60;false&#x60;&#x60; to include archived tables. * &#x60;&#x60;limit&#x60;&#x60;      -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;     -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @param kind The kind parameter
     * @param isActive The isActive parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> searchTables(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String datasetId, @javax.annotation.Nullable String kind, @javax.annotation.Nullable String isActive, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return searchTablesRequestCreation(q, name, datasetId, kind, isActive, limit, offset).bodyToMono(localVarReturnType);
    }

    /**
     * Search/filter tables across the caller&#39;s workspace.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;          -- substring match on &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;qualified_name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;       -- exact match on &#x60;&#x60;name&#x60;&#x60;. * &#x60;&#x60;dataset_id&#x60;&#x60; -- restrict to a single dataset. * &#x60;&#x60;kind&#x60;&#x60;       -- &#x60;&#x60;UPLOADED&#x60;&#x60; / &#x60;&#x60;VIEW&#x60;&#x60; / &#x60;&#x60;DERIVED&#x60;&#x60;. * &#x60;&#x60;is_active&#x60;&#x60;  -- default &#x60;&#x60;true&#x60;&#x60;; pass &#x60;&#x60;false&#x60;&#x60; to include archived tables. * &#x60;&#x60;limit&#x60;&#x60;      -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;     -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @param kind The kind parameter
     * @param isActive The isActive parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> searchTablesWithHttpInfo(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String datasetId, @javax.annotation.Nullable String kind, @javax.annotation.Nullable String isActive, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return searchTablesRequestCreation(q, name, datasetId, kind, isActive, limit, offset).toEntity(localVarReturnType);
    }

    /**
     * Search/filter tables across the caller&#39;s workspace.
     * Query parameters ---------------- * &#x60;&#x60;q&#x60;&#x60;          -- substring match on &#x60;&#x60;name&#x60;&#x60; or &#x60;&#x60;qualified_name&#x60;&#x60; (case-insensitive &#x60;&#x60;ILIKE&#x60;&#x60;). * &#x60;&#x60;name&#x60;&#x60;       -- exact match on &#x60;&#x60;name&#x60;&#x60;. * &#x60;&#x60;dataset_id&#x60;&#x60; -- restrict to a single dataset. * &#x60;&#x60;kind&#x60;&#x60;       -- &#x60;&#x60;UPLOADED&#x60;&#x60; / &#x60;&#x60;VIEW&#x60;&#x60; / &#x60;&#x60;DERIVED&#x60;&#x60;. * &#x60;&#x60;is_active&#x60;&#x60;  -- default &#x60;&#x60;true&#x60;&#x60;; pass &#x60;&#x60;false&#x60;&#x60; to include archived tables. * &#x60;&#x60;limit&#x60;&#x60;      -- page size, clamped to [1, 1000]. Default 100. * &#x60;&#x60;offset&#x60;&#x60;     -- starting offset. Default 0.  Response envelope: &#x60;&#x60;{items, total, limit, offset, has_more}&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param q The q parameter
     * @param name The name parameter
     * @param datasetId The datasetId parameter
     * @param kind The kind parameter
     * @param isActive The isActive parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec searchTablesWithResponseSpec(@javax.annotation.Nullable String q, @javax.annotation.Nullable String name, @javax.annotation.Nullable String datasetId, @javax.annotation.Nullable String kind, @javax.annotation.Nullable String isActive, @javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        return searchTablesRequestCreation(q, name, datasetId, kind, isActive, limit, offset);
    }
}
