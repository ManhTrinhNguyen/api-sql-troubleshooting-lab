# API & SQL Troubleshooting Lab

A local technical support portfolio project using Python, FastAPI, SQLite, Postman, and pytest. Practice reproducing API errors, investigating logs, querying data, and explaining fixes.

**All customers and incidents are simulated.** This supplied project is a starting point: complete the exercises and understand the code before presenting it in interviews.

## What you get

- Customer and order REST API with API key authentication.
- Input validation, parameterized SQL, foreign keys, and transactions.
- Request IDs, server logs, and safe client error messages.
- Six guided support incidents and an incident report template.
- SQL performance benchmark, Postman collection, tests, and GitHub Actions.

## 1. Run on macOS or Linux

Install Python 3.11 or newer. Extract the download and open Terminal in the folder containing this README.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export LAB_API_KEY=local-demo-key
export LAB_FAULT=none
python -m scripts.seed_data
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Keep this terminal open. Press Ctrl+C to stop the server.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:LAB_API_KEY="local-demo-key"
$env:LAB_FAULT="none"
python -m scripts.seed_data
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If activation is blocked, use `.venv\Scripts\python.exe` instead of `python`. Activation is optional. Use the interactive docs or Postman for requests on Windows; curl examples below use macOS/Linux syntax.

The public sample key is for local practice. `.env.example` is a reference only: this application does not automatically load `.env` files.

## 2. Try the API

Open http://127.0.0.1:8000/docs. Click **Authorize**, enter `local-demo-key`, and try the endpoints.

Or open a second terminal:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/orders/1 -H "X-API-Key: local-demo-key"
```

Expect HTTP 200. Seeded order 1 has two units at 500 cents each: `total_cents` is 1000. Find the response's `X-Request-ID` in the server terminal logs.

Create an order:

```bash
curl -i -X POST http://127.0.0.1:8000/orders \
  -H "X-API-Key: local-demo-key" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"items":[{"product_id":1,"quantity":3}]}'
```

Expect 201 and a new order ID. GET `/orders/<returned-id>` and confirm a total of 1500 cents.

## 3. Understand the endpoints

All business endpoints require the key. Health and API documentation are public.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Process health; does not check the database |
| GET | `/customers/{id}` | Customer details |
| GET | `/customers/{id}/orders?limit=50&offset=0` | Paginated order history |
| GET | `/orders/{id}` | Order details and calculated total |
| POST | `/orders` | Create an order and its items atomically |
| PATCH | `/orders/{id}/status` | Set pending, shipped, or cancelled |

| Status | Meaning |
|---|---|
| 200 / 201 | Successful request / resource created |
| 401 | Missing or invalid API key |
| 404 | Resource does not exist |
| 422 | Invalid request input |
| 500 | Unexpected application error; check logs |
| 503 | Server API key is not configured |

## 4. Learn the database

The seed script creates `lab.db` with 20 customers, 10 products, 100 orders, and 100 order items. Running it again preserves existing data. Always run commands from the project root.

One customer has many orders. Each order has items referencing products. Items store the price at purchase time; money is integer cents. Foreign keys are enabled on every connection. Order creation rolls back completely if any product is missing.

Activate your environment in a second terminal, then:

```bash
python -m scripts.query sql/customer_orders.sql
python -m scripts.query sql/order_total.sql
python -m scripts.query sql/query_plan.sql
```

The query runner opens the database read-only. Open the SQL files and inspect the queries. Next, write a JOIN showing customer names beside order IDs.

## 5. Complete the troubleshooting exercises

Start with freshly seeded data for the documented expected values.

| Exercise | Fault mode | Investigation |
|---|---|---|
| [Authentication failure](docs/incidents/01-authentication.md) | none | Request headers and 401 |
| [Invalid quantity](docs/incidents/02-validation.md) | none | JSON and validation detail |
| [Missing orders](docs/incidents/03-missing-orders.md) | missing_orders | API output versus SQL records |
| [Incorrect total](docs/incidents/04-wrong-total.md) | wrong_total | Quantity times price |
| [Internal error](docs/incidents/05-server-error.md) | server_error | Request ID and traceback |
| [Slow SQL lookup](docs/incidents/06-slow-query.md) | Separate benchmark | Plans and measured execution time |

### Enable an application fault

Stop the server. In the same terminal:

```bash
export LAB_FAULT=missing_orders
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Replace `missing_orders` with `wrong_total` or `server_error` for the other exercises. In PowerShell use `$env:LAB_FAULT="missing_orders"`.

### Restore the working implementation

Stop the server, then:

```bash
export LAB_FAULT=none
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The switches select deliberate faulty code paths. Turning them off restores the supplied correct behavior. For coding practice, create a Git branch and implement your own fix after inspecting `app/main.py`.

Copy [the incident template](docs/INCIDENT_TEMPLATE.md) and add your actual requests, outputs, request IDs, SQL evidence, root cause, and verified resolution. The supplied guides describe expected behavior; they do not show that you personally completed the work.

## 6. Measure SQL performance

```bash
python -m scripts.benchmark
```

The script creates 100,000 rows in a temporary in-memory database, warms up the query, and measures 30 runs before and after indexing. It writes `benchmark-results.json` and never changes `lab.db`.

Compare the plans and median milliseconds. These are machine-dependent, warm-cache SQL measurements, not API latency or production performance. The normal API schema already includes the supporting index. Replace the supplied reference results with your own measurements before discussing metrics in interviews.

## 7. Run tests

```bash
python -m pytest -q
```

Each test gets a temporary database. Tests cover authentication, validation, creation, calculations, filtering, pagination, missing records, status updates, foreign keys, rollback, and fault recovery. They do not modify your normal database.

GitHub Actions runs tests on pushes and pull requests.

## 8. Import Postman requests

1. Import `postman/collection.json`.
2. Set collection variable `base_url` to `http://127.0.0.1:8000`.
3. Set `api_key` to your configured key.
4. Run with `LAB_FAULT=none` and inspect response assertions.

Includes successful requests and expected 401, 404, and 422 responses. Create-order requests add records; importing the collection does not reset data.

## 9. Optional Docker setup

```bash
docker build -t api-sql-lab .
docker run --rm -p 127.0.0.1:8000:8000 -e LAB_API_KEY=local-demo-key api-sql-lab
```

The container seeds itself and runs as a non-root user. Data disappears when the container is removed. Python setup is sufficient if you do not have Docker.

## 10. Publish on GitHub

Create an empty GitHub repository named `api-sql-troubleshooting-lab`. Do not initialize another README. Run these commands from your extracted project folder:

```bash
git init
git add .
git commit -m "Add API and SQL troubleshooting lab"
git branch -M main
```

Replace `YOUR_USERNAME` below with your username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/api-sql-troubleshooting-lab.git
git push -u origin main
```

Authenticate through your Git credential manager if requested. For an existing repository, use its existing remote.

Suggested description: **Local support engineering lab with a REST API, SQL investigations, simulated incidents, and regression tests.**

The `.gitignore` excludes virtual environments, databases, `.env`, and logs. The sample key and `example.com` addresses are intentional demo values.


## File guide

| Location | Purpose |
|---|---|
| `app/main.py` | API, authentication, logging, deliberate faults |
| `app/database.py`, `app/schema.sql` | Database connections and structure |
| `scripts/seed_data.py` | Sample data setup |
| `scripts/query.py` | Read-only SQL runner |
| `scripts/benchmark.py` | Isolated performance exercise |
| `tests/` | Regression checks |
| `docs/incidents/` | Guided exercises |
| `postman/` | Requests and response assertions |
| `.github/workflows/` | CI configuration |

## Common problems

- **Module not found:** activate `.venv` and install requirements.
- **No such table:** seed from the project root using the same `LAB_DB_PATH` as the server.
- **401:** check the key matches the server environment.
- **503:** set `LAB_API_KEY` before starting the server.
- **Port busy:** stop the old server or use `--port 8001` and change request URLs.
- **Wrong results:** restart with `LAB_FAULT=none`.
- **Reset data:** stop the server, rename `lab.db` to an unused backup name, then seed again. Use `mv lab.db lab-backup.db` on macOS/Linux or `Move-Item lab.db lab-backup.db` in PowerShell.

## Limitations

Local educational service, not a production deployment. A shared key demonstrates authentication but does not provide per-customer authorization: every key holder can access all sample customers. There is no payment processing, user account system, TLS termination, rate limiting, or production migration system. Keep deliberate faults local. Health checks the process only.


