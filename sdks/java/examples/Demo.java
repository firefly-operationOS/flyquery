// Copyright 2024-2026 Firefly Software Foundation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//
// End-to-end Java demo: workspace + dataset + bulk upload + batch query.
//
// Run with the SDK on the classpath (mvn install in ../) against a
// local flyquery on http://127.0.0.1:8520.

package com.firefly.flyquery.examples;

import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.api.DatasetsApi;
import com.firefly.flyquery.api.QueryApi;
import com.firefly.flyquery.api.WorkspacesApi;
import com.firefly.flyquery.model.BatchQueryItem;
import com.firefly.flyquery.model.BatchQueryRequest;
import com.firefly.flyquery.model.BatchQueryResponse;
import com.firefly.flyquery.model.BulkFileUploadResponse;
import com.firefly.flyquery.model.DatasetCreate;
import com.firefly.flyquery.model.DatasetRead;
import com.firefly.flyquery.model.WorkspaceCreate;
import com.firefly.flyquery.model.WorkspaceRead;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.List;

public class Demo {
    public static void main(String[] args) {
        ApiClient client = new ApiClient();
        client.setBasePath("http://127.0.0.1:8520");
        client.addDefaultHeader("X-Tenant-Id", "java-quickstart");
        client.addDefaultHeader("X-Workspace-Id", "jq1");

        WorkspacesApi workspaces = new WorkspacesApi(client);
        DatasetsApi datasets = new DatasetsApi(client);
        QueryApi query = new QueryApi(client);

        // 1) Idempotent workspace + dataset
        WorkspaceRead ws = workspaces.readBySlug("jq1")
            .onErrorResume(err -> workspaces.create(
                new WorkspaceCreate().slug("jq1").name("Java Quickstart")))
            .block();
        client.addDefaultHeader("X-Workspace-Id", ws.getId().toString());

        DatasetRead ds = datasets.readByName("java_demo")
            .onErrorResume(err -> datasets.create(
                new DatasetCreate().name("java_demo")
                    .description("Java SDK quickstart demo")))
            .block();

        System.out.printf("workspace=%s dataset=%s%n", ws.getId(), ds.getId());

        // 2) Bulk upload through the FilesApi:bulk endpoint
        WebClient web = WebClient.builder()
            .baseUrl(client.getBasePath())
            .defaultHeader("X-Tenant-Id", "java-quickstart")
            .defaultHeader("X-Workspace-Id", ws.getId().toString())
            .build();

        MultipartBodyBuilder mp = new MultipartBodyBuilder();
        mp.part("files", new FileSystemResource("../../examples/csv/customers.csv"));
        mp.part("files", new FileSystemResource("../../examples/csv/sales_orders.csv"));
        mp.part("files", new FileSystemResource("../../examples/parquet/transactions.parquet"));

        BulkFileUploadResponse upload = web.post()
            .uri("/api/v1/datasets/{id}/files:bulk", ds.getId())
            .body(BodyInserters.fromMultipartData(mp.build()))
            .retrieve()
            .bodyToMono(BulkFileUploadResponse.class)
            .block();
        System.out.printf("bulk-upload: %d/%d succeeded%n",
            upload.getSucceeded(), upload.getTotalFiles());
        upload.getResults().forEach(r ->
            System.out.printf("  %s %s (%d tables)%n",
                "OK".equals(r.getStatus()) ? "✓" : "✗",
                r.getOriginalFilename(),
                r.getTables() == null ? 0 : r.getTables().size()));

        // 3) Batch query: N questions in one round-trip
        BatchQueryResponse batch = query.batch(new BatchQueryRequest()
            .queries(List.of(
                new BatchQueryItem().question("How many customers do we have?").datasetId(ds.getId()),
                new BatchQueryItem().question("What is the total revenue across all orders?").datasetId(ds.getId()),
                new BatchQueryItem().question("Top 3 customers by lifetime value?").datasetId(ds.getId())
            ))).block();
        System.out.printf("%nbatch-query: %d/%d succeeded%n",
            batch.getSucceeded(), batch.getTotalQueries());
        batch.getResults().forEach(r ->
            System.out.printf("  #%d %s: %s%n",
                r.getIndex(), r.getStatus(),
                r.getSql() == null ? "" : r.getSql().split("\n")[0]));
    }
}
