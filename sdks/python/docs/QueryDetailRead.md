# QueryDetailRead

Full single-query payload for `GET /api/v1/queries/{id}`.  Includes every candidate proposal, the AST classification, every model identifier used (grounding / generation / critic / explainer), PII findings, clarification frame, and the final error envelope if any. JSONB columns are passed through as Python dicts / lists.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ast_classification** | **str** |  | [optional] 
**candidates_json** | **List[object]** |  | [optional] 
**chosen_candidate_index** | **int** |  | [optional] 
**clarification_emitted** | **bool** |  | [optional] [default to False]
**clarification_json** | **Dict[str, object]** |  | [optional] 
**cost_cents** | [**CostCents1**](CostCents1.md) |  | [optional] 
**created_at** | **datetime** |  | 
**dataset_id** | **UUID** |  | [optional] 
**elapsed_ms** | **int** |  | [optional] 
**error_json** | **Dict[str, object]** |  | [optional] 
**executed_sql** | **str** |  | [optional] 
**execution_engine** | **str** |  | [optional] [default to 'duckdb']
**execution_status** | **str** |  | [optional] 
**finalised_at** | **datetime** |  | [optional] 
**id** | **UUID** |  | 
**model_critic** | **str** |  | [optional] 
**model_explainer** | **str** |  | [optional] 
**model_generation** | **str** |  | [optional] 
**model_grounding** | **str** |  | [optional] 
**pii_findings_json** | **Dict[str, object]** |  | [optional] 
**prior_turn_ids** | **List[UUID]** |  | [optional] 
**question** | **str** |  | 
**retries** | **int** |  | [optional] [default to 0]
**row_count** | **int** |  | [optional] 
**semantic_path_taken** | **str** |  | [optional] 
**table_id_snapshot_pins_json** | **Dict[str, object]** |  | [optional] 
**tenant_id** | **str** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.query_detail_read import QueryDetailRead

# TODO update the JSON string below
json = "{}"
# create an instance of QueryDetailRead from a JSON string
query_detail_read_instance = QueryDetailRead.from_json(json)
# print the JSON string representation of the object
print(QueryDetailRead.to_json())

# convert the object into a dict
query_detail_read_dict = query_detail_read_instance.to_dict()
# create an instance of QueryDetailRead from a dict
query_detail_read_from_dict = QueryDetailRead.from_dict(query_detail_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


