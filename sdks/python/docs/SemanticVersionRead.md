# SemanticVersionRead

Read representation of a flyquery_semantic_versions row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**compiled_sql_template** | **str** |  | 
**created_at** | **datetime** |  | 
**created_by** | **str** |  | 
**definition_yaml** | **str** |  | 
**id** | **UUID** |  | 
**kind** | **str** |  | 
**parent_id** | **UUID** |  | 
**tenant_id** | **str** |  | 
**version** | **int** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.semantic_version_read import SemanticVersionRead

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticVersionRead from a JSON string
semantic_version_read_instance = SemanticVersionRead.from_json(json)
# print the JSON string representation of the object
print(SemanticVersionRead.to_json())

# convert the object into a dict
semantic_version_read_dict = semantic_version_read_instance.to_dict()
# create an instance of SemanticVersionRead from a dict
semantic_version_read_from_dict = SemanticVersionRead.from_dict(semantic_version_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


