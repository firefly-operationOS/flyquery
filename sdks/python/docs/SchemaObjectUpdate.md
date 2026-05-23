# SchemaObjectUpdate

Request body for PUT /schema-objects/{id}.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**business_owner** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**governance_json** | **Dict[str, object]** |  | [optional] 
**pii_tag** | **str** |  | [optional] 
**synonyms_json** | **List[object]** |  | [optional] 

## Example

```python
from flyquery_sdk.models.schema_object_update import SchemaObjectUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaObjectUpdate from a JSON string
schema_object_update_instance = SchemaObjectUpdate.from_json(json)
# print the JSON string representation of the object
print(SchemaObjectUpdate.to_json())

# convert the object into a dict
schema_object_update_dict = schema_object_update_instance.to_dict()
# create an instance of SchemaObjectUpdate from a dict
schema_object_update_from_dict = SchemaObjectUpdate.from_dict(schema_object_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


