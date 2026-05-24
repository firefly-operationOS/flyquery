# PaginatedGlossaryTermRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[GlossaryTermRead]**](GlossaryTermRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_glossary_term_read import PaginatedGlossaryTermRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedGlossaryTermRead from a JSON string
paginated_glossary_term_read_instance = PaginatedGlossaryTermRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedGlossaryTermRead.to_json())

# convert the object into a dict
paginated_glossary_term_read_dict = paginated_glossary_term_read_instance.to_dict()
# create an instance of PaginatedGlossaryTermRead from a dict
paginated_glossary_term_read_from_dict = PaginatedGlossaryTermRead.from_dict(paginated_glossary_term_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


