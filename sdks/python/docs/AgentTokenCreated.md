# AgentTokenCreated

Mint response: includes the full ``token`` ONCE.  Subsequent reads only ever expose ``prefix`` -- the secret hash is stored server-side and never returned. Callers MUST capture the token at mint time; there is no recovery path.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**created_by** | **str** |  | 
**expires_at** | **datetime** |  | 
**id** | **str** |  | 
**last_used_at** | **datetime** |  | 
**name** | **str** |  | 
**prefix** | **str** |  | 
**rate_limit_rpm** | **int** |  | 
**revoked_at** | **datetime** |  | 
**scopes** | **List[str]** |  | 
**token** | **str** |  | 
**workspace_allowlist** | **List[str]** |  | 

## Example

```python
from flyquery_sdk.models.agent_token_created import AgentTokenCreated

# TODO update the JSON string below
json = "{}"
# create an instance of AgentTokenCreated from a JSON string
agent_token_created_instance = AgentTokenCreated.from_json(json)
# print the JSON string representation of the object
print(AgentTokenCreated.to_json())

# convert the object into a dict
agent_token_created_dict = agent_token_created_instance.to_dict()
# create an instance of AgentTokenCreated from a dict
agent_token_created_from_dict = AgentTokenCreated.from_dict(agent_token_created_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


