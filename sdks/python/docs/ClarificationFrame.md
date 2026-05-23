# ClarificationFrame

Emitted when grounding confidence is below the threshold and missing_info is set.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**questions** | **List[str]** |  | 
**reasons** | **List[str]** |  | [optional] 

## Example

```python
from flyquery_sdk.models.clarification_frame import ClarificationFrame

# TODO update the JSON string below
json = "{}"
# create an instance of ClarificationFrame from a JSON string
clarification_frame_instance = ClarificationFrame.from_json(json)
# print the JSON string representation of the object
print(ClarificationFrame.to_json())

# convert the object into a dict
clarification_frame_dict = clarification_frame_instance.to_dict()
# create an instance of ClarificationFrame from a dict
clarification_frame_from_dict = ClarificationFrame.from_dict(clarification_frame_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


