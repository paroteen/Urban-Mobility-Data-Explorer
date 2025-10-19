#!/usr/bin/env python3
import os
import sys
import sqlite3

"""Initialize the SQLite database using `schema.sql`."""

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')
DB_PATH = os.getenv('SQLITE_PATH', os.path.join(os.path.dirname(__file__), 'nyc_taxi.db'))


def apply_schema():
    if not os.path.exists(SCHEMA_PATH):
        print(f"ERROR: schema.sql not found at {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(2)
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(sql)
    print(f"Applied schema from {SCHEMA_PATH} to {DB_PATH}")


def main():
    try:
        apply_schema()
        print("DB initialization complete")
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
