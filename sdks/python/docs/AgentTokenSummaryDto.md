# AgentTokenSummaryDto

Token surface as listed back to user-tier callers -- secret omitted.  Every read path through ``GET /api/v1/agent-tokens`` returns this shape. The raw token is *only* available on the :class:`AgentTokenCreated` returned by the mint endpoint and is never round-tripped through any other endpoint.

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
**workspace_allowlist** | **List[str]** |  | 

## Example

```python
from flyquery_sdk.models.agent_token_summary_dto import AgentTokenSummaryDto

# TODO update the JSON string below
json = "{}"
# create an instance of AgentTokenSummaryDto from a JSON string
agent_token_summary_dto_instance = AgentTokenSummaryDto.from_json(json)
# print the JSON string representation of the object
print(AgentTokenSummaryDto.to_json())

# convert the object into a dict
agent_token_summary_dto_dict = agent_token_summary_dto_instance.to_dict()
# create an instance of AgentTokenSummaryDto from a dict
agent_token_summary_dto_from_dict = AgentTokenSummaryDto.from_dict(agent_token_summary_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


