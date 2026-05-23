# GlossaryTermUpdate

Sparse-update payload for an existing glossary term.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**definition** | **str** |  | [optional] 
**related_columns_json** | **List[str]** |  | [optional] 
**related_metrics_json** | **List[str]** |  | [optional] 
**synonyms_json** | **List[str]** |  | [optional] 
**tags_json** | **List[str]** |  | [optional] 

## Example

```python
from flyquery_sdk.models.glossary_term_update import GlossaryTermUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of GlossaryTermUpdate from a JSON string
glossary_term_update_instance = GlossaryTermUpdate.from_json(json)
# print the JSON string representation of the object
print(GlossaryTermUpdate.to_json())

# convert the object into a dict
glossary_term_update_dict = glossary_term_update_instance.to_dict()
# create an instance of GlossaryTermUpdate from a dict
glossary_term_update_from_dict = GlossaryTermUpdate.from_dict(glossary_term_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


