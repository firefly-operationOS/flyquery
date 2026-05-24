# BillingBreakdownItem

One bucket of the billing rollup -- day, week, or month.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_date** | **datetime** |  | 
**ingest_cost_cents** | [**IngestCostCents**](IngestCostCents.md) |  | 
**other_cost_cents** | [**OtherCostCents**](OtherCostCents.md) |  | 
**query_cost_cents** | [**QueryCostCents**](QueryCostCents.md) |  | 
**total_cost_cents** | [**TotalCostCents**](TotalCostCents.md) |  | 

## Example

```python
from flyquery_sdk.models.billing_breakdown_item import BillingBreakdownItem

# TODO update the JSON string below
json = "{}"
# create an instance of BillingBreakdownItem from a JSON string
billing_breakdown_item_instance = BillingBreakdownItem.from_json(json)
# print the JSON string representation of the object
print(BillingBreakdownItem.to_json())

# convert the object into a dict
billing_breakdown_item_dict = billing_breakdown_item_instance.to_dict()
# create an instance of BillingBreakdownItem from a dict
billing_breakdown_item_from_dict = BillingBreakdownItem.from_dict(billing_breakdown_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


