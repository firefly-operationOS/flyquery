# ValidateResponse

Response from POST /api/v1/query:validate — includes AST + scope check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ast_classification** | **str** |  | 
**clarification** | [**ClarificationFrame**](ClarificationFrame.md) |  | [optional] 
**scope_error** | **str** |  | [optional] 
**single_statement** | **bool** |  | [optional] [default to True]
**sql** | **str** |  | 
**table_refs** | **List[str]** |  | [optional] 

## Example

```python
from flyquery_sdk.models.validate_response import ValidateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ValidateResponse from a JSON string
validate_response_instance = ValidateResponse.from_json(json)
# print the JSON string representation of the object
print(ValidateResponse.to_json())

# convert the object into a dict
validate_response_dict = validate_response_instance.to_dict()
# create an instance of ValidateResponse from a dict
validate_response_from_dict = ValidateResponse.from_dict(validate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


