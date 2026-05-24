# CallbackConfig

Webhook delivery target attached to an async ingest job.  Set on job creation (``IngestJobCreate.callback`` or the ``callback_*`` query params on ``POST /datasets/{id}/files:async``). On every terminal status transition the worker writes one row to ``flyquery_callback_outbox``; the ``CallbackWorker`` POSTs the canonical :class:`IngestJobRead` to ``url`` with header ``X-Flyquery-Signature: sha256=<hmac>`` if ``secret`` is provided.  Delivery is at-least-once with exponential backoff (5 attempts: 0s, 30s, 5m, 1h, 6h). After the last failed attempt the row is marked ``DEAD`` and surfaced via ``GET /ingest-jobs/{id}/callbacks``.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**headers** | **Dict[str, str]** | Extra HTTP headers merged onto every callback request. | [optional] 
**secret** | **str** | Shared secret for HMAC-SHA256 over the request body. | [optional] 
**url** | **str** |  | 

## Example

```python
from flyquery_sdk.models.callback_config import CallbackConfig

# TODO update the JSON string below
json = "{}"
# create an instance of CallbackConfig from a JSON string
callback_config_instance = CallbackConfig.from_json(json)
# print the JSON string representation of the object
print(CallbackConfig.to_json())

# convert the object into a dict
callback_config_dict = callback_config_instance.to_dict()
# create an instance of CallbackConfig from a dict
callback_config_from_dict = CallbackConfig.from_dict(callback_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


