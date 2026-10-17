# Internal server error (simulated)

This is a reproducible training exercise, not a real customer incident.

## Reproduce

Start the API using fault mode `server_error`; see the README fault instructions. For `none`, keep the normal server running.

```bash
curl -i http://127.0.0.1:8000/orders/1 -H "X-API-Key: local-demo-key"
```

Expected symptom: **500**.

## Investigate

The injected SQL references nonexistent_column. Find X-Request-ID in the terminal traceback; the client sees a generic error.

Capture the response headers and body. Find the generated request ID in terminal logs. Inspect the relevant code in `app/main.py`. Record your evidence in a copy of [the template](../INCIDENT_TEMPLATE.md).

## Resolve and verify

Restart with LAB_FAULT=none; retry and expect 200.

Run `python -m pytest -q` to check for regressions.

## Example customer response

A database query referenced an invalid column. Correcting it restores order retrieval.

## Learning question

What evidence distinguishes a request problem from an application defect here?
