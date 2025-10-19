#!/usr/bin/env python3
import argparse
import csv
import os
import sys
from typing import List

import sqlite3

EXPECTED_COLUMNS: List[str] = [
    "pickup_datetime",
    "dropoff_datetime",
    "pickup_lat",
    "pickup_lon",
    "dropoff_lat",
    "dropoff_lon",
    "trip_distance_km",
    "trip_duration_sec",
    "fare_amount",
    "tip_amount",
    "passenger_count",
    "payment_type",
    "avg_speed_kmh",
    "fare_per_km",
    "pickup_hour",
    "weekday",
    "is_weekend",
    "haversine_km",
]


def parse_args():
    p = argparse.ArgumentParser(description="Load cleaned NYC taxi CSV into SQLite trips table")
    p.add_argument("--csv", default=os.path.join("data", "cleaned_data.csv"), help="Path to cleaned CSV (default: data/cleaned_data.csv)")
    p.add_argument("--db", default=os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(__file__), "nyc_taxi.db")), help="Path to SQLite DB file (default: backend/nyc_taxi.db)")
    p.add_argument("--table", default="trips", help="Target table (default: trips)")
    p.add_argument("--truncate", action="store_true", help="Truncate table before load")
    p.add_argument("--skip-header-check", action="store_true", help="Skip CSV header validation")
    return p.parse_args()


def read_csv_header(csv_path: str) -> List[str]:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("CSV appears to be empty or missing a header row")
        return [h.strip() for h in header]


def validate_header(found: List[str], expected: List[str]):
    if found != expected:
        missing = [c for c in expected if c not in found]
        extra = [c for c in found if c not in expected]
        raise ValueError(
            "CSV header does not match expected columns.\n"
            f"Expected (order-sensitive): {expected}\n"
            f"Found: {found}\n"
            f"Missing: {missing}\n"
            f"Extra: {extra}"
        )


def main():
    args = parse_args()

    if not os.path.exists(args.csv):
        print(f"ERROR: CSV not found at {args.csv}", file=sys.stderr)
        sys.exit(1)

    if not args.skip_header_check:
        found = read_csv_header(args.csv)
        validate_header(found, EXPECTED_COLUMNS)
        print("Header validation: OK")

    insert_sql = (
        f"INSERT INTO {args.table} (" + ",".join(EXPECTED_COLUMNS) + ") "
        "VALUES (" + ",".join(["?"] * len(EXPECTED_COLUMNS)) + ")"
    )

    try:
        with sqlite3.connect(args.db) as conn:
            cur = conn.cursor()
            if args.truncate:
                print(f"Truncating table {args.table} ...")
                cur.execute(f"DELETE FROM {args.table};")
                conn.commit()

            print(f"Loading {args.csv} into {args.table} ...")
            with open(args.csv, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                rows = []
                num_cols_float = {"pickup_lat","pickup_lon","dropoff_lat","dropoff_lon","trip_distance_km","fare_amount","tip_amount","avg_speed_kmh","fare_per_km","haversine_km"}
                num_cols_int = {"trip_duration_sec","passenger_count","pickup_hour","weekday","is_weekend"}
                for row in reader:
                    cleaned = []
                    for col in EXPECTED_COLUMNS:
                        val = row.get(col, "")
                        if isinstance(val, str):
                            val = val.strip()
                        if val == "":
                            cleaned.append(None)
                            continue
                        if col in num_cols_float:
                            try:
                                cleaned.append(float(val))
                            except ValueError:
                                cleaned.append(None)
                        elif col in num_cols_int:
                            try:
                                cleaned.append(int(float(val)))
                            except ValueError:
                                cleaned.append(None)
                        else:
                            cleaned.append(val)
                    rows.append(tuple(cleaned))
                cur.executemany(insert_sql, rows)
            conn.commit()

            cur.execute(f"SELECT COUNT(*) FROM {args.table};")
            total = cur.fetchone()[0]
            print(f"Load complete. Row count: {total}")
    except Exception as e:
        print("ERROR during load:", e, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
