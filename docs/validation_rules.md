# Validation Rules (v1)

## Timestamps
- Parse to UTC (document your parser behavior).
- pickup_datetime <= dropoff_datetime.
- duration_sec = (dropoff - pickup).seconds > 0.

## Coordinates (NYC Bounding Box)
- Latitude: [40.4774, 40.9176]
- Longitude: [-74.2591, -73.7004]
- Both pickup and dropoff must be within bbox.

## Distance, Speed, Fare, Tip
- trip_distance_km >= 0 (convert from miles if input is in miles).
- avg_speed_kmh = distance_km / (duration_sec/3600) <= 120.
- fare_amount >= 0 and <= 500.
- tip_amount >= 0.
- Zero distance with positive fare → exclude (unless justified otherwise).

## Duplicates
- Preferred key: trip_id if present.
- Fallback composite: (pickup_datetime, dropoff_datetime, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, passenger_count).
- Keep first; log others with reason=duplicate.

## Exclusion Logging
- File: data/exclusions_v1.csv
- Columns: raw_row_id, reason_code, pickup_ts_raw, dropoff_ts_raw, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, distance_raw, fare_raw.

## Derived Features
- avg_speed_kmh
- fare_per_km (with epsilon to avoid div-by-zero)
- pickup_hour (0–23), weekday (0=Mon), is_weekend (bool)
- haversine_km (sanity check vs reported distance)

## Notes
- Document assumptions (e.g., input distance units, timezone handling)
- Keep thresholds versioned; bump to v1.1 if you change them.
