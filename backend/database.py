import os
import sqlite3

"""Module for interacting with the NYC Taxi database."""

def get_conn():
    """Return a SQLite connection using SQLITE_PATH or default DB file."""
    db_path = os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(__file__), "nyc_taxi.db"))
    conn = sqlite3.connect(db_path)
    return conn
