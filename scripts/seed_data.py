"""Create synthetic data. Refuses to overwrite an existing populated database."""
from app.database import connect, initialize

def seed():
    initialize()
    with connect() as db, db:
        if db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]:
            print("Data already exists; nothing changed.")
            return
        db.executemany("INSERT INTO customers VALUES (?, ?, ?)",
                       [(i, f"Demo Customer {i}", f"customer{i}@example.com") for i in range(1, 21)])
        db.executemany("INSERT INTO products VALUES (?, ?, ?)",
                       [(i, f"Demo Product {i}", i * 500) for i in range(1, 11)])
        for i in range(1, 101):
            db.execute("INSERT INTO orders(id, customer_id) VALUES (?, ?)", (i, (i-1) % 20 + 1))
            db.execute("INSERT INTO order_items(order_id, product_id, quantity, unit_price_cents) VALUES (?, 1, 2, 500)", (i,))
    print("Seeded 20 customers, 10 products and 100 orders.")

if __name__ == "__main__":
    seed()
