# Cleaned Schema (v1)

## Table: trips
- trip_id: text (nullable or synthetic if not present)
- pickup_datetime: timestamp (UTC)
- dropoff_datetime: timestamp (UTC)
- trip_duration_sec: integer (>0)
- pickup_lat: double
- pickup_lon: double
- dropoff_lat: double
- dropoff_lon: double
- trip_distance_km: double (>=0)
- fare_amount: numeric(10,2) (>=0)
- tip_amount: numeric(10,2) (>=0 or NULL)
- passenger_count: smallint (>=0 or NULL)
- payment_type: text (nullable)
- avg_speed_kmh: double (>=0)
- fare_per_km: numeric(10,3) (nullable)
- pickup_hour: smallint (0–23)
- weekday: smallint (0–6, Mon=0)
- is_weekend: boolean
- haversine_km: double (nullable)

## Notes
- Units: distances in km, fares in USD, speeds in km/h.
- NULL policy: optional source columns may be NULL; derived fields are computed where possible.
- If schema changes, bump to v1.1 and update `backend/schema.sql` accordingly.
