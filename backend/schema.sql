-- SQLite schema for NYC Taxi trips
DROP TABLE IF EXISTS trips;
CREATE TABLE trips (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pickup_datetime TEXT NOT NULL,
  dropoff_datetime TEXT NOT NULL,
  pickup_lat REAL,
  pickup_lon REAL,
  dropoff_lat REAL,
  dropoff_lon REAL,
  trip_distance_km REAL CHECK (trip_distance_km >= 0),
  trip_duration_sec INTEGER CHECK (trip_duration_sec > 0),
  fare_amount REAL CHECK (fare_amount >= 0),
  tip_amount REAL CHECK (tip_amount >= 0),
  passenger_count INTEGER CHECK (passenger_count >= 0),
  payment_type TEXT,
  avg_speed_kmh REAL CHECK (avg_speed_kmh >= 0),
  fare_per_km REAL,
  pickup_hour INTEGER CHECK (pickup_hour BETWEEN 0 AND 23),
  weekday INTEGER CHECK (weekday BETWEEN 0 AND 6),
  is_weekend INTEGER,
  haversine_km REAL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trips_pickup_time ON trips (pickup_datetime);
CREATE INDEX idx_trips_dropoff_time ON trips (dropoff_datetime);
CREATE INDEX idx_trips_pickup_loc ON trips (pickup_lat, pickup_lon);
CREATE INDEX idx_trips_dropoff_loc ON trips (dropoff_lat, dropoff_lon);
CREATE INDEX idx_trips_speed ON trips (avg_speed_kmh);
CREATE INDEX idx_trips_fare ON trips (fare_amount);
