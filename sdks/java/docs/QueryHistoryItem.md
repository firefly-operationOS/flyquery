

# QueryHistoryItem

Compact row for `GET /api/v1/queries` (history list).  Heavy JSONB columns (candidates, clarification, pii_findings) are omitted here so a 50-item page stays under a few KB; the detail endpoint exposes them via :class:`QueryDetailRead`.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**astClassification** | **String** |  |  [optional] |
|**clarificationEmitted** | **Boolean** |  |  [optional] |
|**createdAt** | **OffsetDateTime** |  |  |
|**datasetId** | **UUID** |  |  [optional] |
|**elapsedMs** | **Integer** |  |  [optional] |
|**executedSql** | **String** |  |  [optional] |
|**executionStatus** | **String** |  |  [optional] |
|**finalisedAt** | **OffsetDateTime** |  |  [optional] |
|**id** | **UUID** |  |  |
|**question** | **String** |  |  |
|**retries** | **Integer** |  |  [optional] |
|**rowCount** | **Integer** |  |  [optional] |
|**semanticPathTaken** | **String** |  |  [optional] |
|**tenantId** | **String** |  |  |
|**workspaceId** | **UUID** |  |  |



