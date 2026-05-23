# AgentTokenMintRequest

Request body for ``POST /api/v1/agent-tokens``.  ``workspace_allowlist`` is optional -- ``None`` means the token can be used in any workspace under the tenant. ``scopes`` defaults to ``[\"*\"]`` (all scopes); the verify path treats ``\"*\"`` as a wildcard. ``rate_limit_rpm`` is advisory metadata today and reserved for the per-token rate limiter we add later; ``expires_at`` is enforced by the verify path.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expires_at** | **datetime** |  | [optional] 
**name** | **str** |  | 
**rate_limit_rpm** | **int** |  | [optional] 
**scopes** | **List[str]** |  | [optional] 
**workspace_allowlist** | **List[str]** |  | [optional] 

## Example

```python
from flyquery_sdk.models.agent_token_mint_request import AgentTokenMintRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AgentTokenMintRequest from a JSON string
agent_token_mint_request_instance = AgentTokenMintRequest.from_json(json)
# print the JSON string representation of the object
print(AgentTokenMintRequest.to_json())

# convert the object into a dict
agent_token_mint_request_dict = agent_token_mint_request_instance.to_dict()
# create an instance of AgentTokenMintRequest from a dict
agent_token_mint_request_from_dict = AgentTokenMintRequest.from_dict(agent_token_mint_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


