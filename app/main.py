"""Local support practice API. Faults are explicitly enabled through LAB_FAULT."""
import logging
import os
import secrets
import sqlite3
import time
import uuid
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from app.database import connect

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("support_lab")
app = FastAPI(title="Customer Orders Troubleshooting Lab", version="1.0.0")
api_key = APIKeyHeader(name="X-API-Key", auto_error=False)

def authenticate(key: str | None = Depends(api_key)):
    expected = os.getenv("LAB_API_KEY")
    if not expected:
        raise HTTPException(503, "Server API key is not configured")
    if key is None or not secrets.compare_digest(key, expected):
        raise HTTPException(401, "Missing or invalid API key")

def fault():
    return os.getenv("LAB_FAULT", "none")

@app.middleware("http")
async def request_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_id=%s unhandled_error", request_id)
        response = JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
                request_id, request.method, request.url.path, response.status_code,
                (time.perf_counter()-start)*1000)
    return response

class ItemInput(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=1000)

class OrderInput(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[ItemInput] = Field(min_length=1, max_length=100)

class StatusInput(BaseModel):
    status: Literal["pending", "shipped", "cancelled"]

@app.get("/health")
def health():
    return {"status": "ok", "scope": "process only; database not checked"}

@app.get("/customers/{customer_id}", dependencies=[Depends(authenticate)])
def customer(customer_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Customer not found")
    return dict(row)

@app.get("/customers/{customer_id}/orders", dependencies=[Depends(authenticate)])
def customer_orders(customer_id: int, limit: int = 50, offset: int = 0):
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(422, "limit must be 1-100; offset must be nonnegative")
    with connect() as db:
        if not db.execute("SELECT 1 FROM customers WHERE id=?", (customer_id,)).fetchone():
            raise HTTPException(404, "Customer not found")
        lookup = -1 if fault() == "missing_orders" else customer_id
        rows = db.execute("SELECT * FROM orders WHERE customer_id=? ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                          (lookup, limit, offset)).fetchall()
    return [dict(row) for row in rows]

@app.get("/orders/{order_id}", dependencies=[Depends(authenticate)])
def order_detail(order_id: int):
    with connect() as db:
        if fault() == "server_error":
            db.execute("SELECT nonexistent_column FROM orders").fetchall()
        order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if order is None:
            raise HTTPException(404, "Order not found")
        items = [dict(row) for row in db.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))]
    total = sum(item["unit_price_cents"] * (1 if fault() == "wrong_total" else item["quantity"]) for item in items)
    return {**dict(order), "items": items, "total_cents": total}

@app.post("/orders", status_code=201, dependencies=[Depends(authenticate)])
def create_order(payload: OrderInput):
    with connect() as db, db:
        if not db.execute("SELECT 1 FROM customers WHERE id=?", (payload.customer_id,)).fetchone():
            raise HTTPException(404, "Customer not found")
        cursor = db.execute("INSERT INTO orders(customer_id) VALUES (?)", (payload.customer_id,))
        order_id = cursor.lastrowid
        for item in payload.items:
            product = db.execute("SELECT price_cents FROM products WHERE id=?", (item.product_id,)).fetchone()
            if product is None:
                # Raising inside the transaction rolls back the order and earlier items.
                raise HTTPException(404, "Product not found")
            db.execute("INSERT INTO order_items(order_id, product_id, quantity, unit_price_cents) VALUES (?,?,?,?)",
                       (order_id, item.product_id, item.quantity, product["price_cents"]))
    return {"id": order_id, "status": "pending"}

@app.patch("/orders/{order_id}/status", dependencies=[Depends(authenticate)])
def update_status(order_id: int, payload: StatusInput):
    with connect() as db, db:
        cursor = db.execute("UPDATE orders SET status=? WHERE id=?", (payload.status, order_id))
        if cursor.rowcount == 0:
            raise HTTPException(404, "Order not found")
    return {"id": order_id, "status": payload.status}
