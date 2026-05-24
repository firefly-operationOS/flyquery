# QueryResultRead

Re-download envelope for `GET /api/v1/queries/{id}/result`.  The preview is always inlined. ``parquet_presigned_url`` is set when the full Parquet is still available on the object store (i.e. ``ttl_expires_at`` hasn't elapsed). When the TTL is past the URL is ``None`` and the consumer must rerun the query.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parquet_presigned_url** | **str** |  | [optional] 
**preview_json** | **object** |  | 
**query_id** | **UUID** |  | 
**result_byte_size** | **int** |  | [optional] 
**ttl_expires_at** | **datetime** |  | [optional] 

## Example

```python
from flyquery_sdk.models.query_result_read import QueryResultRead

# TODO update the JSON string below
json = "{}"
# create an instance of QueryResultRead from a JSON string
query_result_read_instance = QueryResultRead.from_json(json)
# print the JSON string representation of the object
print(QueryResultRead.to_json())

# convert the object into a dict
query_result_read_dict = query_result_read_instance.to_dict()
# create an instance of QueryResultRead from a dict
query_result_read_from_dict = QueryResultRead.from_dict(query_result_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


