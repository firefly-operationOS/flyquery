# GlossaryTermCreate

Payload for creating a new glossary term.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**definition** | **str** |  | 
**related_columns** | **List[str]** |  | [optional] 
**related_metrics** | **List[str]** |  | [optional] 
**synonyms** | **List[str]** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**term** | **str** |  | 

## Example

```python
from flyquery_sdk.models.glossary_term_create import GlossaryTermCreate

# TODO update the JSON string below
json = "{}"
# create an instance of GlossaryTermCreate from a JSON string
glossary_term_create_instance = GlossaryTermCreate.from_json(json)
# print the JSON string representation of the object
print(GlossaryTermCreate.to_json())

# convert the object into a dict
glossary_term_create_dict = glossary_term_create_instance.to_dict()
# create an instance of GlossaryTermCreate from a dict
glossary_term_create_from_dict = GlossaryTermCreate.from_dict(glossary_term_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


