"""Run a SELECT/EXPLAIN file using a read-only SQLite connection."""
import os
import sqlite3
import sys
from pathlib import Path

def main():
    path = Path(os.getenv("LAB_DB_PATH", "lab.db")).resolve()
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        cursor = db.execute(Path(sys.argv[1]).read_text())
        print(" | ".join(column[0] for column in cursor.description))
        for row in cursor:
            print(" | ".join(str(value) for value in row))

if __name__ == "__main__":
    main()
