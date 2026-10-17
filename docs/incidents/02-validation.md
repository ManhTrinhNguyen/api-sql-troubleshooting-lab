# Invalid order quantity (simulated)

This is a reproducible training exercise, not a real customer incident.

## Reproduce

Start the API using fault mode `none`; see the README fault instructions. For `none`, keep the normal server running.

```bash
curl -i -X POST http://127.0.0.1:8000/orders -H "X-API-Key: local-demo-key" -H "Content-Type: application/json" -d '{"customer_id":1,"items":[{"product_id":1,"quantity":0}]}'
```

Expected symptom: **422**.

## Investigate

Quantity must be greater than zero. Inspect the response detail location.

Capture the response headers and body. Find the generated request ID in terminal logs. Inspect the relevant code in `app/main.py`. Record your evidence in a copy of [the template](../INCIDENT_TEMPLATE.md).

## Resolve and verify

Change quantity to 2 and retry; expect 201. Then GET the returned order ID.

Run `python -m pytest -q` to check for regressions.

## Example customer response

The quantity must be a positive integer. Resubmit with a quantity of at least one.

## Learning question

What evidence distinguishes a request problem from an application defect here?
