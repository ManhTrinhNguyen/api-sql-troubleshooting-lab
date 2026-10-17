import pytest
from fastapi.testclient import TestClient
from app.database import connect
from app.main import app
from scripts.seed_data import seed

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("LAB_API_KEY", "test-only-key")
    monkeypatch.setenv("LAB_FAULT", "none")
    seed()
    with TestClient(app) as c:
        c.headers["X-API-Key"] = "test-only-key"
        yield c

def test_health_and_request_id(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.headers["X-Request-ID"]

@pytest.mark.parametrize("key", [None, "wrong"])
def test_authentication(client, key):
    client.headers.pop("X-API-Key")
    result = client.get("/orders/1", headers={} if key is None else {"X-API-Key": key})
    assert result.status_code == 401

def test_create_and_total(client):
    result = client.post("/orders", json={"customer_id":1,"items":[{"product_id":1,"quantity":3},{"product_id":2,"quantity":2}]})
    assert result.status_code == 201
    detail = client.get(f"/orders/{result.json()['id']}").json()
    assert detail["total_cents"] == 3500
    assert len(detail["items"]) == 2

def test_invalid_quantity(client):
    assert client.post("/orders", json={"customer_id":1,"items":[{"product_id":1,"quantity":0}]}).status_code == 422

def test_missing_resources(client):
    assert client.get("/orders/99999").status_code == 404
    assert client.get("/customers/99999").status_code == 404

def test_customer_filter_and_pagination(client):
    rows = client.get("/customers/1/orders?limit=2").json()
    assert len(rows) == 2
    assert all(row["customer_id"] == 1 for row in rows)
    assert client.get("/customers/1/orders?limit=0").status_code == 422

def test_transaction_rollback(client):
    with connect() as db:
        before = [db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("orders", "order_items")]
    response = client.post("/orders", json={"customer_id":1,"items":[{"product_id":1,"quantity":2},{"product_id":99999,"quantity":1}]})
    assert response.status_code == 404
    with connect() as db:
        after = [db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("orders", "order_items")]
    assert after == before

def test_update_status(client):
    assert client.patch("/orders/1/status", json={"status":"shipped"}).status_code == 200
    assert client.get("/orders/1").json()["status"] == "shipped"
    assert client.patch("/orders/1/status", json={"status":"unknown"}).status_code == 422

@pytest.mark.parametrize("mode,status,total", [("server_error",500,None),("wrong_total",200,500)])
def test_deliberate_faults(client, monkeypatch, mode, status, total):
    monkeypatch.setenv("LAB_FAULT", mode)
    response = client.get("/orders/1")
    assert response.status_code == status
    if total:
        assert response.json()["total_cents"] == total
    monkeypatch.setenv("LAB_FAULT", "none")
    assert client.get("/orders/1").json()["total_cents"] == 1000

def test_missing_orders_fault(client, monkeypatch):
    monkeypatch.setenv("LAB_FAULT", "missing_orders")
    assert client.get("/customers/1/orders").json() == []
    monkeypatch.setenv("LAB_FAULT", "none")
    assert len(client.get("/customers/1/orders").json()) == 5

def test_foreign_keys(client):
    import sqlite3
    with connect() as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO orders(customer_id) VALUES (99999)")

def test_unconfigured_key(client, monkeypatch):
    monkeypatch.delenv("LAB_API_KEY")
    assert client.get("/orders/1").status_code == 503
