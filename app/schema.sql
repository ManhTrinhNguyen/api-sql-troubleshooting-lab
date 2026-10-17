CREATE TABLE IF NOT EXISTS customers (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents >= 0)
);
CREATE TABLE IF NOT EXISTS orders (
 id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','shipped','cancelled')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_items (
 id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id),
 product_id INTEGER NOT NULL REFERENCES products(id),
 quantity INTEGER NOT NULL CHECK(quantity > 0),
 unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0)
);
CREATE INDEX IF NOT EXISTS idx_orders_customer_created ON orders(customer_id, created_at DESC);
