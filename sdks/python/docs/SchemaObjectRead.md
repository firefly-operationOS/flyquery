# SchemaObjectRead

Response for GET /schema-objects/{id} or PUT /schema-objects/{id}.  See :class:`SchemaObjectUpdate` for shape contract. Reads always return canonical shapes; the validators forgive a legacy row that has not yet been touched by migration 0012.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**business_owner** | **str** |  | 
**created_at** | **datetime** |  | 
**data_type** | **str** |  | 
**description** | **str** |  | 
**description_source** | **str** |  | 
**governance_json** | **Dict[str, object]** |  | [optional] 
**id** | **UUID** |  | 
**is_active** | **bool** |  | 
**is_nullable** | **bool** |  | 
**kind** | **str** |  | 
**last_changed_at** | **datetime** |  | 
**pii_source** | **str** |  | 
**pii_tag** | **str** |  | 
**qualified_name** | **str** |  | 
**snapshot_id** | **UUID** |  | 
**synonyms_json** | **List[Optional[str]]** |  | [optional] [default to []]
**table_id** | **UUID** |  | 
**tenant_id** | **str** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.schema_object_read import SchemaObjectRead

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaObjectRead from a JSON string
schema_object_read_instance = SchemaObjectRead.from_json(json)
# print the JSON string representation of the object
print(SchemaObjectRead.to_json())

# convert the object into a dict
schema_object_read_dict = schema_object_read_instance.to_dict()
# create an instance of SchemaObjectRead from a dict
schema_object_read_from_dict = SchemaObjectRead.from_dict(schema_object_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


