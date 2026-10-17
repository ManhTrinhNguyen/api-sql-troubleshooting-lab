"""One short-lived connection per operation; every connection enforces relationships."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def connect():
    connection = sqlite3.connect(os.getenv("LAB_DB_PATH", "lab.db"), timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()

def initialize():
    with connect() as db:
        db.executescript(Path(__file__).with_name("schema.sql").read_text())
