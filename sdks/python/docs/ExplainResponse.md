# ExplainResponse

Response from POST /api/v1/query:explain — Grounding + Generation only.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**clarification** | [**ClarificationFrame**](ClarificationFrame.md) |  | [optional] 
**confidence** | **float** |  | 
**grounded_summary** | **Dict[str, object]** |  | [optional] 
**reasoning** | **str** |  | 
**sql** | **str** |  | 

## Example

```python
from flyquery_sdk.models.explain_response import ExplainResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExplainResponse from a JSON string
explain_response_instance = ExplainResponse.from_json(json)
# print the JSON string representation of the object
print(ExplainResponse.to_json())

# convert the object into a dict
explain_response_dict = explain_response_instance.to_dict()
# create an instance of ExplainResponse from a dict
explain_response_from_dict = ExplainResponse.from_dict(explain_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


