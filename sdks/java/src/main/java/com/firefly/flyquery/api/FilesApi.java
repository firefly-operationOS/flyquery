package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.FileUploadResponse;
import com.firefly.flyquery.model.ReuploadResponse;

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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-23T20:01:27.049906+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
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
     * @return ReuploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec reuploadFileRequestCreation(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nullable String tableId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling reuploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'tableId' is set
        if (tableId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tableId' when calling reuploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);
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

        ParameterizedTypeReference<ReuploadResponse> localVarReturnType = new ParameterizedTypeReference<ReuploadResponse>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/tables/{table_id}:upload", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @return ReuploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ReuploadResponse> reuploadFile(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nullable String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<ReuploadResponse> localVarReturnType = new ParameterizedTypeReference<ReuploadResponse>() {};
        return reuploadFileRequestCreation(datasetId, tableId).bodyToMono(localVarReturnType);
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @return ResponseEntity&lt;ReuploadResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ReuploadResponse>> reuploadFileWithHttpInfo(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nullable String tableId) throws WebClientResponseException {
        ParameterizedTypeReference<ReuploadResponse> localVarReturnType = new ParameterizedTypeReference<ReuploadResponse>() {};
        return reuploadFileRequestCreation(datasetId, tableId).toEntity(localVarReturnType);
    }

    /**
     * Re-upload into an existing table slot; creates a new snapshot.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param tableId The tableId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec reuploadFileWithResponseSpec(@javax.annotation.Nonnull String datasetId, @javax.annotation.Nullable String tableId) throws WebClientResponseException {
        return reuploadFileRequestCreation(datasetId, tableId);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return FileUploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec uploadFileRequestCreation(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling uploadFile", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<FileUploadResponse> localVarReturnType = new ParameterizedTypeReference<FileUploadResponse>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/files", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return FileUploadResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<FileUploadResponse> uploadFile(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<FileUploadResponse> localVarReturnType = new ParameterizedTypeReference<FileUploadResponse>() {};
        return uploadFileRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseEntity&lt;FileUploadResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<FileUploadResponse>> uploadFileWithHttpInfo(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<FileUploadResponse> localVarReturnType = new ParameterizedTypeReference<FileUploadResponse>() {};
        return uploadFileRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * Accept a multipart file upload and run the synchronous ingestion pipeline.
     * 
     * <p><b>201</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec uploadFileWithResponseSpec(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        return uploadFileRequestCreation(datasetId);
    }
}
