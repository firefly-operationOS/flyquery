package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;


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
public class RelationsApi {
    private ApiClient apiClient;

    public RelationsApi() {
        this(new ApiClient());
    }

    public RelationsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec approveRelationRequestCreation(@javax.annotation.Nullable String relationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'relationId' is set
        if (relationId == null) {
            throw new WebClientResponseException("Missing the required parameter 'relationId' when calling approveRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("relation_id", relationId);

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
        return apiClient.invokeAPI("/api/v1/relations/{relation_id}:approve", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> approveRelation(@javax.annotation.Nullable String relationId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return approveRelationRequestCreation(relationId).bodyToMono(localVarReturnType);
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> approveRelationWithHttpInfo(@javax.annotation.Nullable String relationId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return approveRelationRequestCreation(relationId).toEntity(localVarReturnType);
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec approveRelationWithResponseSpec(@javax.annotation.Nullable String relationId) throws WebClientResponseException {
        return approveRelationRequestCreation(relationId);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listRelationsRequestCreation(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling listRelations", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/relations", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listRelations(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listRelationsRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listRelationsWithHttpInfo(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listRelationsRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listRelationsWithResponseSpec(@javax.annotation.Nonnull String datasetId) throws WebClientResponseException {
        return listRelationsRequestCreation(datasetId);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec rejectRelationRequestCreation(@javax.annotation.Nonnull String relationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'relationId' is set
        if (relationId == null) {
            throw new WebClientResponseException("Missing the required parameter 'relationId' when calling rejectRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("relation_id", relationId);

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
        return apiClient.invokeAPI("/api/v1/relations/{relation_id}:reject", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> rejectRelation(@javax.annotation.Nonnull String relationId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return rejectRelationRequestCreation(relationId).bodyToMono(localVarReturnType);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> rejectRelationWithHttpInfo(@javax.annotation.Nonnull String relationId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return rejectRelationRequestCreation(relationId).toEntity(localVarReturnType);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec rejectRelationWithResponseSpec(@javax.annotation.Nonnull String relationId) throws WebClientResponseException {
        return rejectRelationRequestCreation(relationId);
    }
}
