# Missing order history (simulated)

This is a reproducible training exercise, not a real customer incident.

## Reproduce

Start the API using fault mode `missing_orders`; see the README fault instructions. For `none`, keep the normal server running.

```bash
curl -i http://127.0.0.1:8000/customers/1/orders -H "X-API-Key: local-demo-key"
```

Expected symptom: **200 with []**.

## Investigate

The injected fault changes the SQL customer filter to -1. `python -m scripts.query sql/customer_orders.sql` proves customer 1 has five seeded orders.

Capture the response headers and body. Find the generated request ID in terminal logs. Inspect the relevant code in `app/main.py`. Record your evidence in a copy of [the template](../INCIDENT_TEMPLATE.md).

## Resolve and verify

Restart with LAB_FAULT=none and retry; expect five orders on a fresh database.

Run `python -m pytest -q` to check for regressions.

## Example customer response

An incorrect customer filter hid existing orders. Correcting the filter restores the history.

## Learning question

What evidence distinguishes a request problem from an application defect here?
