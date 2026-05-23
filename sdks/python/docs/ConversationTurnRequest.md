# ConversationTurnRequest

Request body for POST /api/v1/conversations/{id}/turn.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **UUID** |  | 
**question** | **str** |  | 

## Example

```python
from flyquery_sdk.models.conversation_turn_request import ConversationTurnRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationTurnRequest from a JSON string
conversation_turn_request_instance = ConversationTurnRequest.from_json(json)
# print the JSON string representation of the object
print(ConversationTurnRequest.to_json())

# convert the object into a dict
conversation_turn_request_dict = conversation_turn_request_instance.to_dict()
# create an instance of ConversationTurnRequest from a dict
conversation_turn_request_from_dict = ConversationTurnRequest.from_dict(conversation_turn_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


