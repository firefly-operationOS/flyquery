# CallbackDeliveryRead

One row from flyquery_callback_outbox.  Returned by ``GET /api/v1/ingest-jobs/{id}/callbacks`` so the caller can audit webhook delivery without inspecting the DB.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attempts** | **int** |  | 
**callback_url** | **str** |  | 
**created_at** | **datetime** |  | 
**event_type** | **str** |  | 
**finished_at** | **datetime** |  | 
**id** | **UUID** |  | 
**ingest_job_id** | **UUID** |  | 
**last_attempt_at** | **datetime** |  | 
**last_error** | **str** |  | 
**last_status_code** | **int** |  | 
**next_attempt_at** | **datetime** |  | 
**status** | **str** |  | 

## Example

```python
from flyquery_sdk.models.callback_delivery_read import CallbackDeliveryRead

# TODO update the JSON string below
json = "{}"
# create an instance of CallbackDeliveryRead from a JSON string
callback_delivery_read_instance = CallbackDeliveryRead.from_json(json)
# print the JSON string representation of the object
print(CallbackDeliveryRead.to_json())

# convert the object into a dict
callback_delivery_read_dict = callback_delivery_read_instance.to_dict()
# create an instance of CallbackDeliveryRead from a dict
callback_delivery_read_from_dict = CallbackDeliveryRead.from_dict(callback_delivery_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


