package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.AgentTokenCreated;
import com.firefly.flyquery.model.AgentTokenMintRequest;
import com.firefly.flyquery.model.AgentTokenSummaryDto;
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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-23T20:01:27.049906+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class AgentTokensApi {
    private ApiClient apiClient;

    public AgentTokensApi() {
        this(new ApiClient());
    }

    public AgentTokensApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * List tokens for the current tenant (newest first).
     * Returns the summary shape only -- the secret is never round-tripped on this endpoint.
     * <p><b>200</b> - Successful response
     * @return List&lt;AgentTokenSummaryDto&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listTokensRequestCreation() throws WebClientResponseException {
        Object postBody = null;
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
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<AgentTokenSummaryDto> localVarReturnType = new ParameterizedTypeReference<AgentTokenSummaryDto>() {};
        return apiClient.invokeAPI("/api/v1/agent-tokens", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List tokens for the current tenant (newest first).
     * Returns the summary shape only -- the secret is never round-tripped on this endpoint.
     * <p><b>200</b> - Successful response
     * @return List&lt;AgentTokenSummaryDto&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Flux<AgentTokenSummaryDto> listTokens() throws WebClientResponseException {
        ParameterizedTypeReference<AgentTokenSummaryDto> localVarReturnType = new ParameterizedTypeReference<AgentTokenSummaryDto>() {};
        return listTokensRequestCreation().bodyToFlux(localVarReturnType);
    }

    /**
     * List tokens for the current tenant (newest first).
     * Returns the summary shape only -- the secret is never round-tripped on this endpoint.
     * <p><b>200</b> - Successful response
     * @return ResponseEntity&lt;List&lt;AgentTokenSummaryDto&gt;&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<List<AgentTokenSummaryDto>>> listTokensWithHttpInfo() throws WebClientResponseException {
        ParameterizedTypeReference<AgentTokenSummaryDto> localVarReturnType = new ParameterizedTypeReference<AgentTokenSummaryDto>() {};
        return listTokensRequestCreation().toEntityList(localVarReturnType);
    }

    /**
     * List tokens for the current tenant (newest first).
     * Returns the summary shape only -- the secret is never round-tripped on this endpoint.
     * <p><b>200</b> - Successful response
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listTokensWithResponseSpec() throws WebClientResponseException {
        return listTokensRequestCreation();
    }

    /**
     * Mint a new agent token.
     * Returns 201 with the full &#x60;&#x60;token&#x60;&#x60; populated. The token is only returned this once -- subsequent reads expose only &#x60;&#x60;prefix&#x60;&#x60;. Refuses agent-tier callers with &#x60;&#x60;403 agent_cannot_mint&#x60;&#x60;.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param agentTokenMintRequest The agentTokenMintRequest parameter
     * @return AgentTokenCreated
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec mintRequestCreation(@javax.annotation.Nonnull AgentTokenMintRequest agentTokenMintRequest) throws WebClientResponseException {
        Object postBody = agentTokenMintRequest;
        // verify the required parameter 'agentTokenMintRequest' is set
        if (agentTokenMintRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'agentTokenMintRequest' when calling mint", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<AgentTokenCreated> localVarReturnType = new ParameterizedTypeReference<AgentTokenCreated>() {};
        return apiClient.invokeAPI("/api/v1/agent-tokens", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Mint a new agent token.
     * Returns 201 with the full &#x60;&#x60;token&#x60;&#x60; populated. The token is only returned this once -- subsequent reads expose only &#x60;&#x60;prefix&#x60;&#x60;. Refuses agent-tier callers with &#x60;&#x60;403 agent_cannot_mint&#x60;&#x60;.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param agentTokenMintRequest The agentTokenMintRequest parameter
     * @return AgentTokenCreated
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<AgentTokenCreated> mint(@javax.annotation.Nonnull AgentTokenMintRequest agentTokenMintRequest) throws WebClientResponseException {
        ParameterizedTypeReference<AgentTokenCreated> localVarReturnType = new ParameterizedTypeReference<AgentTokenCreated>() {};
        return mintRequestCreation(agentTokenMintRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Mint a new agent token.
     * Returns 201 with the full &#x60;&#x60;token&#x60;&#x60; populated. The token is only returned this once -- subsequent reads expose only &#x60;&#x60;prefix&#x60;&#x60;. Refuses agent-tier callers with &#x60;&#x60;403 agent_cannot_mint&#x60;&#x60;.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param agentTokenMintRequest The agentTokenMintRequest parameter
     * @return ResponseEntity&lt;AgentTokenCreated&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<AgentTokenCreated>> mintWithHttpInfo(@javax.annotation.Nonnull AgentTokenMintRequest agentTokenMintRequest) throws WebClientResponseException {
        ParameterizedTypeReference<AgentTokenCreated> localVarReturnType = new ParameterizedTypeReference<AgentTokenCreated>() {};
        return mintRequestCreation(agentTokenMintRequest).toEntity(localVarReturnType);
    }

    /**
     * Mint a new agent token.
     * Returns 201 with the full &#x60;&#x60;token&#x60;&#x60; populated. The token is only returned this once -- subsequent reads expose only &#x60;&#x60;prefix&#x60;&#x60;. Refuses agent-tier callers with &#x60;&#x60;403 agent_cannot_mint&#x60;&#x60;.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param agentTokenMintRequest The agentTokenMintRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec mintWithResponseSpec(@javax.annotation.Nonnull AgentTokenMintRequest agentTokenMintRequest) throws WebClientResponseException {
        return mintRequestCreation(agentTokenMintRequest);
    }

    /**
     * Revoke a token. Idempotent -- already-revoked is a no-op (204).
     * Unknown &#x60;&#x60;token_id&#x60;&#x60; returns &#x60;&#x60;404 resource_not_found&#x60;&#x60;.
     * <p><b>204</b> - No Content
     * @param tokenId The tokenId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec revokeRequestCreation(@javax.annotation.Nullable String tokenId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'tokenId' is set
        if (tokenId == null) {
            throw new WebClientResponseException("Missing the required parameter 'tokenId' when calling revoke", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("token_id", tokenId);

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
        return apiClient.invokeAPI("/api/v1/agent-tokens/{token_id}", HttpMethod.DELETE, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Revoke a token. Idempotent -- already-revoked is a no-op (204).
     * Unknown &#x60;&#x60;token_id&#x60;&#x60; returns &#x60;&#x60;404 resource_not_found&#x60;&#x60;.
     * <p><b>204</b> - No Content
     * @param tokenId The tokenId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> revoke(@javax.annotation.Nullable String tokenId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return revokeRequestCreation(tokenId).bodyToMono(localVarReturnType);
    }

    /**
     * Revoke a token. Idempotent -- already-revoked is a no-op (204).
     * Unknown &#x60;&#x60;token_id&#x60;&#x60; returns &#x60;&#x60;404 resource_not_found&#x60;&#x60;.
     * <p><b>204</b> - No Content
     * @param tokenId The tokenId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> revokeWithHttpInfo(@javax.annotation.Nullable String tokenId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return revokeRequestCreation(tokenId).toEntity(localVarReturnType);
    }

    /**
     * Revoke a token. Idempotent -- already-revoked is a no-op (204).
     * Unknown &#x60;&#x60;token_id&#x60;&#x60; returns &#x60;&#x60;404 resource_not_found&#x60;&#x60;.
     * <p><b>204</b> - No Content
     * @param tokenId The tokenId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec revokeWithResponseSpec(@javax.annotation.Nullable String tokenId) throws WebClientResponseException {
        return revokeRequestCreation(tokenId);
    }
}
