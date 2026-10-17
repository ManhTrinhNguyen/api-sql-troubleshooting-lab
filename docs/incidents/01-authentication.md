# Authentication failure (simulated)

This is a reproducible training exercise, not a real customer incident.

## Reproduce

Start the API using fault mode `none`; see the README fault instructions. For `none`, keep the normal server running.

```bash
curl -i http://127.0.0.1:8000/orders/1
```

Expected symptom: **401**.

## Investigate

No X-API-Key header is supplied.

Capture the response headers and body. Find the generated request ID in terminal logs. Inspect the relevant code in `app/main.py`. Record your evidence in a copy of [the template](../INCIDENT_TEMPLATE.md).

## Resolve and verify

Retry with `-H "X-API-Key: local-demo-key"`; expect 200.

Run `python -m pytest -q` to check for regressions.

## Example customer response

The request was missing the API key header. Adding the configured key restores access.

## Learning question

What evidence distinguishes a request problem from an application defect here?
