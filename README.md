# NYC Taxi App

A lightweight Urban Mobility explorer that ingests NYC taxi-style data, cleans it, loads it into SQLite, and serves a simple API consumed by a Leaflet frontend. 
by 
1. Kayisire Kira Armel, 
2. Israel Ayong
3. Sheja Dorian
4. Kenny Crepin Rukoro

## Tutorial
<video controls src="docs/Recording.mov" title="Title"></video>

## Features
- **Backend**: Flask API with CORS over SQLite.
- **Data prep**: `backend/clean_data.py` transforms raw CSV → cleaned CSV.
- **Loader**: `backend/load_data.py` bulk-inserts cleaned CSV into SQLite.
- **Frontend**: `frontend/riders.html` + `riders.js` renders a map and basic stats using API calls.

## Tech Stack
- Python 3.10+, Flask, flask-cors, sqlite3
- HTML/CSS/JS, Leaflet, OpenStreetMap tiles
- CSV → SQLite

## Repository Structure
- `backend/app.py` Flask API
- `backend/database.py` SQLite connection
- `backend/init_db.py` applies `backend/schema.sql`
- `backend/clean_data.py` raw → cleaned CSV
- `backend/load_data.py` cleaned CSV → SQLite
- `frontend/riders.html|.css|.js` web UI
- `data/raw/` raw CSVs (gitignored)
- `data/cleaned_data.csv` cleaned output
- `docs/cleaned_schema.md` cleaned data schema

## Prerequisites
- Python 3.10+
- A raw CSV at `data/raw/train.csv` (Kaggle-like columns: pickup/dropoff timestamps, lat/lon, trip_duration, etc.)

## Installation
```bash
pip install -r backend/requirements.txt
```

## Configuration
- `SQLITE_PATH` (optional): path to the SQLite DB file. Default: `backend/nyc_taxi.db`
- `PORT` (optional): backend port. Default: `5000`
- Frontend expects backend at `http://localhost:5000` (configurable via `API_BASE` in `frontend/riders.js`)

Example `.env` in repo root:
```
SQLITE_PATH=backend/nyc_taxi.db
PORT=5000
```

## Data Pipeline

### 1) Initialize the database
Creates tables and indexes in SQLite.
```bash
python backend/init_db.py
```

### 2) Clean the raw data
Transforms `data/raw/train.csv` into `data/cleaned_data.csv` with exact columns used by the loader.
```bash
python backend/clean_data.py
```
Outputs columns (see `docs/cleaned_schema.md`):
- `pickup_datetime, dropoff_datetime, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, trip_distance_km, trip_duration_sec, fare_amount, tip_amount, passenger_count, payment_type, avg_speed_kmh, fare_per_km, pickup_hour, weekday, is_weekend, haversine_km`

Notes:
- `fare_amount`, `tip_amount`, `payment_type` may be NULL if not present in the raw data.
- `avg_speed_kmh`, `fare_per_km`, `pickup_hour`, `weekday`, `is_weekend`, `haversine_km` are computed.

### 3) Load the cleaned data
Inserts into `trips` table.
```bash
python backend/load_data.py --csv data/cleaned_data.csv
# options:
# --db /path/to/nyc_taxi.db
# --truncate   # clear existing rows before load
# --table trips
```

## Run the Backend
```bash
python backend/app.py
# Serves at http://localhost:${PORT:-5000}
# Health: http://localhost:5000/health
```

## Run the Frontend
- Open `frontend/riders.html` in your browser.
- The page will fetch `/api/summary` and `/api/trips` and display results on the map and summary cards.
- If your backend runs elsewhere, update `API_BASE` at the top of `frontend/riders.js`.

## API Reference

- `GET /health`
  - Response: `{ "status": "ok" }`

- `GET /api/summary`
  - Response:
```json
{
  "total_trips": 12345,
  "avg_speed_kmh": 18.234,
  "avg_fare_per_km": 3.12
}
```

- `GET /api/trips`
  - Query params:
    - `start` `YYYY-MM-DD HH:MM:SS`
    - `end` `YYYY-MM-DD HH:MM:SS`
    - `min_distance` number (km)
    - `max_distance` number (km)
    - `page` default 1
    - `per_page` default 100 (max 500)
  - Response:
```json
{
  "page": 1,
  "per_page": 100,
  "results": [
    {
      "id": 1,
      "pickup_datetime": "2016-03-14 17:24:55",
      "dropoff_datetime": "2016-03-14 17:32:30",
      "pickup_lat": 40.7679,
      "pickup_lon": -73.9821,
      "dropoff_lat": 40.7656,
      "dropoff_lon": -73.9646,
      "trip_distance_km": 2.1,
      "trip_duration_sec": 455,
      "fare_amount": null,
      "tip_amount": null,
      "passenger_count": 1,
      "payment_type": null,
      "avg_speed_kmh": 16.6,
      "fare_per_km": null,
      "pickup_hour": 17,
      "weekday": 0,
      "is_weekend": 0,
      "haversine_km": 2.07
    }
  ]
}
```

## Troubleshooting
- **No markers on map**: Ensure DB has rows (`/api/summary`), then re-run: init → clean → load.
- **CORS errors**: `flask-cors` is enabled; verify backend is running and `API_BASE` is correct.
- **Date filters**: Use `YYYY-MM-DD HH:MM:SS` format.
- **SQLite performance**: `executemany` is used; keep DB on SSD; avoid external processes locking the DB file.

## Development Notes
- Environment variables: `SQLITE_PATH`, `PORT`.
- Data locations: raw files in `data/raw/` (gitignored), cleaned at `data/cleaned_data.csv`.
- Code style: concise docstrings and minimal comments for clarity.

## License
MIT (or your preferred license).

## Acknowledgements
- OpenStreetMap tiles and Leaflet for mapping.
- NYC taxi-style datasets for sample data.

