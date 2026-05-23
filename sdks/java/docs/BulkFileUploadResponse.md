

# BulkFileUploadResponse

Response from POST /datasets/{id}/files:bulk.  Returns one ``results`` entry per uploaded file. Per-file failures do NOT abort the bulk -- the caller sees which files succeeded and which didn't, with the error message inline. Aggregate counts let a UI render \"4/5 uploaded successfully\" without scanning the list.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**failed** | **Integer** |  |  |
|**results** | [**List&lt;BulkFileResult&gt;**](BulkFileResult.md) |  |  |
|**succeeded** | **Integer** |  |  |
|**totalFiles** | **Integer** |  |  |



