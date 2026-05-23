# ConversationRead

A conversation, optionally with its turns.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actor** | **str** |  | 
**created_at** | **datetime** |  | 
**id** | **UUID** |  | 
**summary** | **str** |  | 
**tenant_id** | **str** |  | 
**title** | **str** |  | 
**turns** | [**List[TurnRead]**](TurnRead.md) |  | [optional] 
**updated_at** | **datetime** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.conversation_read import ConversationRead

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationRead from a JSON string
conversation_read_instance = ConversationRead.from_json(json)
# print the JSON string representation of the object
print(ConversationRead.to_json())

# convert the object into a dict
conversation_read_dict = conversation_read_instance.to_dict()
# create an instance of ConversationRead from a dict
conversation_read_from_dict = ConversationRead.from_dict(conversation_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


