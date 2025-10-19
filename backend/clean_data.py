#!/usr/bin/env python3
import csv
import os
import sys
from datetime import datetime
from math import radians, sin, cos, asin, sqrt

RAW_DEFAULT = os.path.join("data", "raw", "train_10k.csv")
OUT_DEFAULT = os.path.join("data", "cleaned_data.csv")

EXPECTED_COLUMNS = [
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


def haversine_km(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return None
    # Earth radius in km
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def parse_dt(s):
    if not s:
        return None
    # Handles formats like '2016-03-14 17:24:55'
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def clean(raw_path=RAW_DEFAULT, out_path=OUT_DEFAULT):
    if not os.path.exists(raw_path):
        print(f"ERROR: Raw CSV not found at {raw_path}", file=sys.stderr)
        return 2

    with open(raw_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout)
        writer.writerow(EXPECTED_COLUMNS)

        # Detect column names from Kaggle 'NYC Taxi Trip Duration' style
        # Required raw columns: pickup_datetime, dropoff_datetime, passenger_count,
        # pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_duration
        required = [
            "pickup_datetime",
            "dropoff_datetime",
            "passenger_count",
            "pickup_longitude",
            "pickup_latitude",
            "dropoff_longitude",
            "dropoff_latitude",
            "trip_duration",
        ]
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            print(f"ERROR: Raw CSV missing required columns: {missing}", file=sys.stderr)
            return 2

        rows_written = 0
        for row in reader:
            pu = parse_dt(row.get("pickup_datetime"))
            do = parse_dt(row.get("dropoff_datetime"))
            if not pu or not do:
                continue

            try:
                passenger_count = int(float(row.get("passenger_count", "0") or 0))
            except ValueError:
                passenger_count = 0

            # Coordinates
            pu_lon = row.get("pickup_longitude")
            pu_lat = row.get("pickup_latitude")
            do_lon = row.get("dropoff_longitude")
            do_lat = row.get("dropoff_latitude")

            # Duration
            try:
                dur_sec_label = int(float(row.get("trip_duration", "0") or 0))
            except ValueError:
                dur_sec_label = 0
            # Also ensure non-negative and fallback to actual difference if label is bad
            diff_sec = max(0, int((do - pu).total_seconds()))
            trip_duration_sec = dur_sec_label if dur_sec_label > 0 else diff_sec
            if trip_duration_sec <= 0:
                # skip impossible trips
                continue

            # Distances
            h_km = haversine_km(pu_lat, pu_lon, do_lat, do_lon)
            # Allow None values; trip_distance_km = haversine as proxy
            trip_distance_km = h_km if h_km is not None and h_km >= 0 else None

            # Derived
            hours = trip_duration_sec / 3600.0
            avg_speed_kmh = (trip_distance_km / hours) if trip_distance_km and hours > 0 else None

            # Fares not available in this dataset; leave empty/NULL-compatible
            fare_amount = None
            tip_amount = None
            payment_type = None
            fare_per_km = (fare_amount / trip_distance_km) if fare_amount and trip_distance_km and trip_distance_km > 0 else None

            pickup_hour = pu.hour
            weekday = pu.weekday()
            is_weekend = 1 if weekday in (5, 6) else 0

            writer.writerow([
                pu.strftime("%Y-%m-%d %H:%M:%S"),
                do.strftime("%Y-%m-%d %H:%M:%S"),
                pu_lat,
                pu_lon,
                do_lat,
                do_lon,
                f"{trip_distance_km:.6f}" if isinstance(trip_distance_km, float) else "",
                trip_duration_sec,
                "" if fare_amount is None else fare_amount,
                "" if tip_amount is None else tip_amount,
                passenger_count,
                "" if payment_type is None else payment_type,
                f"{avg_speed_kmh:.6f}" if isinstance(avg_speed_kmh, float) else "",
                "" if fare_per_km is None else fare_per_km,
                pickup_hour,
                weekday,
                is_weekend,
                f"{h_km:.6f}" if isinstance(h_km, float) else "",
            ])
            rows_written += 1

    print(f"Wrote cleaned rows: {rows_written} -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(clean())
