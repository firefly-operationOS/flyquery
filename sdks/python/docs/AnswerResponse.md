# AnswerResponse

Response from POST /api/v1/query (sync).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chart_hint** | **str** |  | [optional] 
**clarification** | [**ClarificationFrame**](ClarificationFrame.md) |  | [optional] 
**elapsed_ms** | **int** |  | 
**execution_status** | **str** |  | 
**explanation** | **str** |  | [optional] 
**grounded_summary** | **Dict[str, object]** |  | [optional] 
**preview** | **List[Optional[Dict[str, object]]]** |  | 
**query_id** | **UUID** |  | 
**row_count** | **int** |  | 
**snapshot_pins** | **Dict[str, str]** |  | [optional] 
**sql** | **str** |  | 
**truncated** | **bool** |  | [optional] [default to False]
**usage** | [**UsageSummary**](UsageSummary.md) |  | [optional] 

## Example

```python
from flyquery_sdk.models.answer_response import AnswerResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AnswerResponse from a JSON string
answer_response_instance = AnswerResponse.from_json(json)
# print the JSON string representation of the object
print(AnswerResponse.to_json())

# convert the object into a dict
answer_response_dict = answer_response_instance.to_dict()
# create an instance of AnswerResponse from a dict
answer_response_from_dict = AnswerResponse.from_dict(answer_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


