package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.GlossaryTermCreate;
import com.firefly.flyquery.model.GlossaryTermRead;
import com.firefly.flyquery.model.GlossaryTermUpdate;
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
public class GlossaryApi {
    private ApiClient apiClient;

    public GlossaryApi() {
        this(new ApiClient());
    }

    public GlossaryApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull GlossaryTermCreate glossaryTermCreate) throws WebClientResponseException {
        Object postBody = glossaryTermCreate;
        // verify the required parameter 'glossaryTermCreate' is set
        if (glossaryTermCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'glossaryTermCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/glossary", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> create(@javax.annotation.Nonnull GlossaryTermCreate glossaryTermCreate) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return createRequestCreation(glossaryTermCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> createWithHttpInfo(@javax.annotation.Nonnull GlossaryTermCreate glossaryTermCreate) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return createRequestCreation(glossaryTermCreate).toEntity(localVarReturnType);
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull GlossaryTermCreate glossaryTermCreate) throws WebClientResponseException {
        return createRequestCreation(glossaryTermCreate);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec deleteRequestCreation(@javax.annotation.Nonnull String termId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling delete", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

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
        return apiClient.invokeAPI("/api/v1/glossary/{term_id}", HttpMethod.DELETE, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> delete(@javax.annotation.Nonnull String termId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return deleteRequestCreation(termId).bodyToMono(localVarReturnType);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> deleteWithHttpInfo(@javax.annotation.Nonnull String termId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return deleteRequestCreation(termId).toEntity(localVarReturnType);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec deleteWithResponseSpec(@javax.annotation.Nonnull String termId) throws WebClientResponseException {
        return deleteRequestCreation(termId);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listTermsRequestCreation(@javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/glossary", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listTerms(@javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listTermsRequestCreation(limit, offset).bodyToMono(localVarReturnType);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listTermsWithHttpInfo(@javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listTermsRequestCreation(limit, offset).toEntity(localVarReturnType);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listTermsWithResponseSpec(@javax.annotation.Nullable Integer limit, @javax.annotation.Nullable Integer offset) throws WebClientResponseException {
        return listTermsRequestCreation(limit, offset);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@javax.annotation.Nullable String termId, @javax.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate) throws WebClientResponseException {
        Object postBody = glossaryTermUpdate;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'glossaryTermUpdate' is set
        if (glossaryTermUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'glossaryTermUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

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

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/glossary/{term_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> update(@javax.annotation.Nullable String termId, @javax.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return updateRequestCreation(termId, glossaryTermUpdate).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> updateWithHttpInfo(@javax.annotation.Nullable String termId, @javax.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return updateRequestCreation(termId, glossaryTermUpdate).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@javax.annotation.Nullable String termId, @javax.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate) throws WebClientResponseException {
        return updateRequestCreation(termId, glossaryTermUpdate);
    }
}
