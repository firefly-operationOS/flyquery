package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.CancelResponse;
import com.firefly.flyquery.model.IngestEventListResponse;
import com.firefly.flyquery.model.IngestJobListResponse;
import com.firefly.flyquery.model.IngestJobRead;

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
public class IngestJobsApi {
    private ApiClient apiClient;

    public IngestJobsApi() {
        this(new ApiClient());
    }

    public IngestJobsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return CancelResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec cancelJobRequestCreation(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling cancelJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

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

        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}:cancel", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return CancelResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<CancelResponse> cancelJob(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return cancelJobRequestCreation(jobId).bodyToMono(localVarReturnType);
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseEntity&lt;CancelResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<CancelResponse>> cancelJobWithHttpInfo(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<CancelResponse> localVarReturnType = new ParameterizedTypeReference<CancelResponse>() {};
        return cancelJobRequestCreation(jobId).toEntity(localVarReturnType);
    }

    /**
     * Cooperatively cancel a job (idempotent for terminal jobs).
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec cancelJobWithResponseSpec(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        return cancelJobRequestCreation(jobId);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * 
     * <p><b>201</b> - Successful response
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createJobRequestCreation() throws WebClientResponseException {
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

        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * 
     * <p><b>201</b> - Successful response
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobRead> createJob() throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return createJobRequestCreation().bodyToMono(localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * 
     * <p><b>201</b> - Successful response
     * @return ResponseEntity&lt;IngestJobRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobRead>> createJobWithHttpInfo() throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return createJobRequestCreation().toEntity(localVarReturnType);
    }

    /**
     * Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).
     * 
     * <p><b>201</b> - Successful response
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createJobWithResponseSpec() throws WebClientResponseException {
        return createJobRequestCreation();
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getJobRequestCreation(@javax.annotation.Nullable String jobId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling getJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

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

        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return IngestJobRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobRead> getJob(@javax.annotation.Nullable String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return getJobRequestCreation(jobId).bodyToMono(localVarReturnType);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseEntity&lt;IngestJobRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobRead>> getJobWithHttpInfo(@javax.annotation.Nullable String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobRead> localVarReturnType = new ParameterizedTypeReference<IngestJobRead>() {};
        return getJobRequestCreation(jobId).toEntity(localVarReturnType);
    }

    /**
     * Get a single ingest job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getJobWithResponseSpec(@javax.annotation.Nullable String jobId) throws WebClientResponseException {
        return getJobRequestCreation(jobId);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return IngestEventListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listEventsRequestCreation(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

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

        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}/events", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return IngestEventListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestEventListResponse> listEvents(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return listEventsRequestCreation(jobId).bodyToMono(localVarReturnType);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseEntity&lt;IngestEventListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestEventListResponse>> listEventsWithHttpInfo(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<IngestEventListResponse> localVarReturnType = new ParameterizedTypeReference<IngestEventListResponse>() {};
        return listEventsRequestCreation(jobId).toEntity(localVarReturnType);
    }

    /**
     * Paginated event ledger for a job.
     * 
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listEventsWithResponseSpec(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        return listEventsRequestCreation(jobId);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @return IngestJobListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listJobsRequestCreation() throws WebClientResponseException {
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

        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return apiClient.invokeAPI("/api/v1/ingest-jobs", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @return IngestJobListResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<IngestJobListResponse> listJobs() throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return listJobsRequestCreation().bodyToMono(localVarReturnType);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @return ResponseEntity&lt;IngestJobListResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<IngestJobListResponse>> listJobsWithHttpInfo() throws WebClientResponseException {
        ParameterizedTypeReference<IngestJobListResponse> localVarReturnType = new ParameterizedTypeReference<IngestJobListResponse>() {};
        return listJobsRequestCreation().toEntity(localVarReturnType);
    }

    /**
     * List ingest jobs with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listJobsWithResponseSpec() throws WebClientResponseException {
        return listJobsRequestCreation();
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec streamJobRequestCreation(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'jobId' is set
        if (jobId == null) {
            throw new WebClientResponseException("Missing the required parameter 'jobId' when calling streamJob", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("job_id", jobId);

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
        return apiClient.invokeAPI("/api/v1/ingest-jobs/{job_id}/stream", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> streamJob(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return streamJobRequestCreation(jobId).bodyToMono(localVarReturnType);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> streamJobWithHttpInfo(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return streamJobRequestCreation(jobId).toEntity(localVarReturnType);
    }

    /**
     * SSE stream for real-time job progress.
     * Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak
     * <p><b>200</b> - Successful response
     * @param jobId The jobId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec streamJobWithResponseSpec(@javax.annotation.Nonnull String jobId) throws WebClientResponseException {
        return streamJobRequestCreation(jobId);
    }
}
