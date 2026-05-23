package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.DeriveTableRequest;
import com.firefly.flyquery.model.DeriveTableResponse;
import com.firefly.flyquery.model.HTTPValidationError;
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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-23T20:36:34.703085+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
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
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return DeriveTableResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec deriveRequestCreation(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        Object postBody = deriveTableRequest;
        // verify the required parameter 'deriveTableRequest' is set
        if (deriveTableRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'deriveTableRequest' when calling derive", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<DeriveTableResponse> localVarReturnType = new ParameterizedTypeReference<DeriveTableResponse>() {};
        return apiClient.invokeAPI("/api/v1/tables:derive", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return DeriveTableResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DeriveTableResponse> derive(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        ParameterizedTypeReference<DeriveTableResponse> localVarReturnType = new ParameterizedTypeReference<DeriveTableResponse>() {};
        return deriveRequestCreation(deriveTableRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return ResponseEntity&lt;DeriveTableResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DeriveTableResponse>> deriveWithHttpInfo(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        ParameterizedTypeReference<DeriveTableResponse> localVarReturnType = new ParameterizedTypeReference<DeriveTableResponse>() {};
        return deriveRequestCreation(deriveTableRequest).toEntity(localVarReturnType);
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec deriveWithResponseSpec(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        return deriveRequestCreation(deriveTableRequest);
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
}
