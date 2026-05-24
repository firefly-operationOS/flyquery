

# QueryResultRead

Re-download envelope for `GET /api/v1/queries/{id}/result`.  The preview is always inlined. ``parquet_presigned_url`` is set when the full Parquet is still available on the object store (i.e. ``ttl_expires_at`` hasn't elapsed). When the TTL is past the URL is ``None`` and the consumer must rerun the query.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**parquetPresignedUrl** | **String** |  |  [optional] |
|**previewJson** | **Object** |  |  |
|**queryId** | **UUID** |  |  |
|**resultByteSize** | **Integer** |  |  [optional] |
|**ttlExpiresAt** | **OffsetDateTime** |  |  [optional] |



