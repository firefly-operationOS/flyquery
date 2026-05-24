

# SchemaObjectUpdate

Request body for PUT /schema-objects/{id}.  ``synonyms_json`` is canonically ``list[str]``; ``governance_json`` is canonically ``dict[str, Any]``. The validators coerce legacy shapes (a synonyms dict envelope, a governance array left behind by the ``NULL || dict`` jsonb-concat bug) so a malformed write payload still lands as the canonical shape.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**businessOwner** | **String** |  |  [optional] |
|**description** | **String** |  |  [optional] |
|**governanceJson** | **Map&lt;String, Object&gt;** |  |  [optional] |
|**piiTag** | **String** |  |  [optional] |
|**synonymsJson** | **List&lt;String&gt;** |  |  [optional] |



