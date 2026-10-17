"""Isolated, reproducible SQL benchmark; never changes lab.db."""
import json
import sqlite3
import statistics
import time
from pathlib import Path

QUERY = "SELECT id, created_at FROM orders WHERE customer_id=? ORDER BY created_at DESC LIMIT 50"

def main():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, created_at TEXT)")
    db.executemany("INSERT INTO orders VALUES (?,?,?)",
                   ((i, i % 1000 + 1, f"2026-01-{i % 28 + 1:02d} 12:00:00") for i in range(1,100001)))
    db.commit()
    def measure():
        plan = [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + QUERY, (7,))]
        db.execute(QUERY, (7,)).fetchall()  # warmup
        samples = []
        for _ in range(30):
            start = time.perf_counter()
            db.execute(QUERY, (7,)).fetchall()
            samples.append((time.perf_counter()-start)*1000)
        return {"median_ms": round(statistics.median(samples), 4), "query_plan": plan}
    before = measure()
    db.execute("CREATE INDEX idx_customer_created ON orders(customer_id, created_at DESC)")
    after = measure()
    result = {"rows":100000,"runs_per_phase":30,"scope":"in-memory SQL only; warm cache; not API latency", "before":before,"after":after}
    Path("benchmark-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    db.close()

if __name__ == "__main__":
    main()
