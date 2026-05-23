# GlossaryTermRead

Full read representation of a flyquery_glossary_terms row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**definition** | **str** |  | 
**id** | **UUID** |  | 
**related_columns_json** | **List[str]** |  | 
**related_metrics_json** | **List[str]** |  | 
**synonyms_json** | **List[str]** |  | 
**tags_json** | **List[str]** |  | 
**tenant_id** | **str** |  | 
**term** | **str** |  | 
**updated_at** | **datetime** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.glossary_term_read import GlossaryTermRead

# TODO update the JSON string below
json = "{}"
# create an instance of GlossaryTermRead from a JSON string
glossary_term_read_instance = GlossaryTermRead.from_json(json)
# print the JSON string representation of the object
print(GlossaryTermRead.to_json())

# convert the object into a dict
glossary_term_read_dict = glossary_term_read_instance.to_dict()
# create an instance of GlossaryTermRead from a dict
glossary_term_read_from_dict = GlossaryTermRead.from_dict(glossary_term_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


