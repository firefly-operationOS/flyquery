# SchemaChangeRead

Response for GET /tables/{id}/changes items.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**after_json** | **Dict[str, object]** |  | 
**approved_at** | **datetime** |  | [optional] 
**approved_by** | **str** |  | [optional] 
**before_json** | **Dict[str, object]** |  | 
**change** | **str** |  | 
**column_name** | **str** |  | 
**created_at** | **datetime** |  | 
**id** | **UUID** |  | 
**llm_rationale** | **str** |  | 
**next_snapshot_id** | **UUID** |  | 
**prev_snapshot_id** | **UUID** |  | 
**table_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.schema_change_read import SchemaChangeRead

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaChangeRead from a JSON string
schema_change_read_instance = SchemaChangeRead.from_json(json)
# print the JSON string representation of the object
print(SchemaChangeRead.to_json())

# convert the object into a dict
schema_change_read_dict = schema_change_read_instance.to_dict()
# create an instance of SchemaChangeRead from a dict
schema_change_read_from_dict = SchemaChangeRead.from_dict(schema_change_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


