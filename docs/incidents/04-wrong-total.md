# Incorrect order total (simulated)

This is a reproducible training exercise, not a real customer incident.

## Reproduce

Start the API using fault mode `wrong_total`; see the README fault instructions. For `none`, keep the normal server running.

```bash
curl -i http://127.0.0.1:8000/orders/1 -H "X-API-Key: local-demo-key"
```

Expected symptom: **200 with total_cents=500**.

## Investigate

The injected calculation ignores quantity. `python -m scripts.query sql/order_total.sql` returns 1000.

Capture the response headers and body. Find the generated request ID in terminal logs. Inspect the relevant code in `app/main.py`. Record your evidence in a copy of [the template](../INCIDENT_TEMPLATE.md).

## Resolve and verify

Restart with LAB_FAULT=none; retry and confirm total_cents=1000.

Run `python -m pytest -q` to check for regressions.

## Example customer response

The calculation omitted item quantities. The corrected total is 1,000 cents for this sample order.

## Learning question

What evidence distinguishes a request problem from an application defect here?
