

# SemanticVersionRead

Read representation of a flyquery_semantic_versions row.  Field names follow the documented payload (``version_number``, ``metric_id``); the underlying columns are ``version`` / ``parent_id`` and are mapped via validation aliases.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**compiledSqlTemplate** | **String** |  |  |
|**createdAt** | **OffsetDateTime** |  |  |
|**createdBy** | **String** |  |  |
|**definitionYaml** | **String** |  |  |
|**id** | **UUID** |  |  |
|**kind** | **String** |  |  |
|**parentId** | **UUID** |  |  |
|**tenantId** | **String** |  |  |
|**version** | **Integer** |  |  |
|**workspaceId** | **UUID** |  |  |



