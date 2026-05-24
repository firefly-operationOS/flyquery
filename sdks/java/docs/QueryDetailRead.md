

# QueryDetailRead

Full single-query payload for `GET /api/v1/queries/{id}`.  Includes every candidate proposal, the AST classification, every model identifier used (grounding / generation / critic / explainer), PII findings, clarification frame, and the final error envelope if any. JSONB columns are passed through as Python dicts / lists.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**astClassification** | **String** |  |  [optional] |
|**candidatesJson** | **List&lt;Object&gt;** |  |  [optional] |
|**chosenCandidateIndex** | **Integer** |  |  [optional] |
|**clarificationEmitted** | **Boolean** |  |  [optional] |
|**clarificationJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**costCents** | [**CostCents1**](CostCents1.md) |  |  [optional] |
|**createdAt** | **OffsetDateTime** |  |  |
|**datasetId** | **UUID** |  |  [optional] |
|**elapsedMs** | **Integer** |  |  [optional] |
|**errorJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**executedSql** | **String** |  |  [optional] |
|**executionEngine** | **String** |  |  [optional] |
|**executionStatus** | **String** |  |  [optional] |
|**finalisedAt** | **OffsetDateTime** |  |  [optional] |
|**id** | **UUID** |  |  |
|**modelCritic** | **String** |  |  [optional] |
|**modelExplainer** | **String** |  |  [optional] |
|**modelGeneration** | **String** |  |  [optional] |
|**modelGrounding** | **String** |  |  [optional] |
|**piiFindingsJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**priorTurnIds** | **List&lt;UUID&gt;** |  |  [optional] |
|**question** | **String** |  |  |
|**retries** | **Integer** |  |  [optional] |
|**rowCount** | **Integer** |  |  [optional] |
|**semanticPathTaken** | **String** |  |  [optional] |
|**tableIdSnapshotPinsJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**tenantId** | **String** |  |  |
|**workspaceId** | **UUID** |  |  |



