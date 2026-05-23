# ConversationCreate

Request body for POST /api/v1/conversations.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | [optional] 

## Example

```python
from flyquery_sdk.models.conversation_create import ConversationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationCreate from a JSON string
conversation_create_instance = ConversationCreate.from_json(json)
# print the JSON string representation of the object
print(ConversationCreate.to_json())

# convert the object into a dict
conversation_create_dict = conversation_create_instance.to_dict()
# create an instance of ConversationCreate from a dict
conversation_create_from_dict = ConversationCreate.from_dict(conversation_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


