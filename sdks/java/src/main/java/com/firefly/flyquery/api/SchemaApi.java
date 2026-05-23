package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.SchemaChangeRead;
import com.firefly.flyquery.model.SchemaObjectRead;
import com.firefly.flyquery.model.SchemaObjectUpdate;

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
public class SchemaApi {
    private ApiClient apiClient;

    public SchemaApi() {
        this(new ApiClient());
    }

    public SchemaApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @return SchemaChangeRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec confirmRequestCreation(@javax.annotation.Nullable String changeId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'changeId' is set
        if (changeId == null) {
            throw new WebClientResponseException("Missing the required parameter 'changeId' when calling confirm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("change_id", changeId);

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

        ParameterizedTypeReference<SchemaChangeRead> localVarReturnType = new ParameterizedTypeReference<SchemaChangeRead>() {};
        return apiClient.invokeAPI("/api/v1/schema-changes/{change_id}:confirm", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @return SchemaChangeRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SchemaChangeRead> confirm(@javax.annotation.Nullable String changeId) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaChangeRead> localVarReturnType = new ParameterizedTypeReference<SchemaChangeRead>() {};
        return confirmRequestCreation(changeId).bodyToMono(localVarReturnType);
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @return ResponseEntity&lt;SchemaChangeRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SchemaChangeRead>> confirmWithHttpInfo(@javax.annotation.Nullable String changeId) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaChangeRead> localVarReturnType = new ParameterizedTypeReference<SchemaChangeRead>() {};
        return confirmRequestCreation(changeId).toEntity(localVarReturnType);
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec confirmWithResponseSpec(@javax.annotation.Nullable String changeId) throws WebClientResponseException {
        return confirmRequestCreation(changeId);
    }

    /**
     * Get a single schema object by ID.
     * 
     * <p><b>200</b> - Successful response
     * @param objectId The objectId parameter
     * @return SchemaObjectRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getObjectRequestCreation(@javax.annotation.Nullable String objectId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'objectId' is set
        if (objectId == null) {
            throw new WebClientResponseException("Missing the required parameter 'objectId' when calling getObject", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("object_id", objectId);

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

        ParameterizedTypeReference<SchemaObjectRead> localVarReturnType = new ParameterizedTypeReference<SchemaObjectRead>() {};
        return apiClient.invokeAPI("/api/v1/schema-objects/{object_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Get a single schema object by ID.
     * 
     * <p><b>200</b> - Successful response
     * @param objectId The objectId parameter
     * @return SchemaObjectRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SchemaObjectRead> getObject(@javax.annotation.Nullable String objectId) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaObjectRead> localVarReturnType = new ParameterizedTypeReference<SchemaObjectRead>() {};
        return getObjectRequestCreation(objectId).bodyToMono(localVarReturnType);
    }

    /**
     * Get a single schema object by ID.
     * 
     * <p><b>200</b> - Successful response
     * @param objectId The objectId parameter
     * @return ResponseEntity&lt;SchemaObjectRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SchemaObjectRead>> getObjectWithHttpInfo(@javax.annotation.Nullable String objectId) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaObjectRead> localVarReturnType = new ParameterizedTypeReference<SchemaObjectRead>() {};
        return getObjectRequestCreation(objectId).toEntity(localVarReturnType);
    }

    /**
     * Get a single schema object by ID.
     * 
     * <p><b>200</b> - Successful response
     * @param objectId The objectId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getObjectWithResponseSpec(@javax.annotation.Nullable String objectId) throws WebClientResponseException {
        return getObjectRequestCreation(objectId);
    }

    /**
     * Update human-set fields on a schema object.
     * Sets description_source&#x3D;&#39;HUMAN&#39; when description is provided. Sets pii_source&#x3D;&#39;HUMAN&#39; when pii_tag is provided.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param objectId The objectId parameter
     * @param schemaObjectUpdate The schemaObjectUpdate parameter
     * @return SchemaObjectRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateObjectRequestCreation(@javax.annotation.Nonnull String objectId, @javax.annotation.Nonnull SchemaObjectUpdate schemaObjectUpdate) throws WebClientResponseException {
        Object postBody = schemaObjectUpdate;
        // verify the required parameter 'objectId' is set
        if (objectId == null) {
            throw new WebClientResponseException("Missing the required parameter 'objectId' when calling updateObject", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'schemaObjectUpdate' is set
        if (schemaObjectUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'schemaObjectUpdate' when calling updateObject", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("object_id", objectId);

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

        ParameterizedTypeReference<SchemaObjectRead> localVarReturnType = new ParameterizedTypeReference<SchemaObjectRead>() {};
        return apiClient.invokeAPI("/api/v1/schema-objects/{object_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Update human-set fields on a schema object.
     * Sets description_source&#x3D;&#39;HUMAN&#39; when description is provided. Sets pii_source&#x3D;&#39;HUMAN&#39; when pii_tag is provided.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param objectId The objectId parameter
     * @param schemaObjectUpdate The schemaObjectUpdate parameter
     * @return SchemaObjectRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SchemaObjectRead> updateObject(@javax.annotation.Nonnull String objectId, @javax.annotation.Nonnull SchemaObjectUpdate schemaObjectUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaObjectRead> localVarReturnType = new ParameterizedTypeReference<SchemaObjectRead>() {};
        return updateObjectRequestCreation(objectId, schemaObjectUpdate).bodyToMono(localVarReturnType);
    }

    /**
     * Update human-set fields on a schema object.
     * Sets description_source&#x3D;&#39;HUMAN&#39; when description is provided. Sets pii_source&#x3D;&#39;HUMAN&#39; when pii_tag is provided.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param objectId The objectId parameter
     * @param schemaObjectUpdate The schemaObjectUpdate parameter
     * @return ResponseEntity&lt;SchemaObjectRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SchemaObjectRead>> updateObjectWithHttpInfo(@javax.annotation.Nonnull String objectId, @javax.annotation.Nonnull SchemaObjectUpdate schemaObjectUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaObjectRead> localVarReturnType = new ParameterizedTypeReference<SchemaObjectRead>() {};
        return updateObjectRequestCreation(objectId, schemaObjectUpdate).toEntity(localVarReturnType);
    }

    /**
     * Update human-set fields on a schema object.
     * Sets description_source&#x3D;&#39;HUMAN&#39; when description is provided. Sets pii_source&#x3D;&#39;HUMAN&#39; when pii_tag is provided.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param objectId The objectId parameter
     * @param schemaObjectUpdate The schemaObjectUpdate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateObjectWithResponseSpec(@javax.annotation.Nonnull String objectId, @javax.annotation.Nonnull SchemaObjectUpdate schemaObjectUpdate) throws WebClientResponseException {
        return updateObjectRequestCreation(objectId, schemaObjectUpdate);
    }
}
