#!/usr/bin/env python3
import os
from flask import Flask, jsonify, request
from database import get_conn
from flask_cors import CORS


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    # Allow browser-based frontends (served from file:// or other ports) to call this API.
    CORS(app)

    @app.get("/health")
    def health():
        """Simple health probe."""
        return jsonify({"status": "ok"}), 200

    @app.get("/api/summary")
    def summary():
        """High-level dataset summary values."""
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM trips")
            total = cur.fetchone()[0]
            cur.execute("SELECT AVG(avg_speed_kmh) FROM trips WHERE avg_speed_kmh IS NOT NULL")
            avg_speed = cur.fetchone()[0]
            cur.execute("SELECT AVG(fare_per_km) FROM trips WHERE fare_per_km IS NOT NULL")
            avg_fpkm = cur.fetchone()[0]
            return jsonify({
                "total_trips": int(total) if total is not None else 0,
                "avg_speed_kmh": float(round(avg_speed, 3)) if avg_speed is not None else None,
                "avg_fare_per_km": float(round(avg_fpkm, 3)) if avg_fpkm is not None else None,
            })
        except Exception as e:
            return jsonify({"error": "database_unavailable", "detail": str(e)}), 503
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    @app.get("/api/trips")
    def trips():
        """Paginated list of trips with simple filters."""
        start = request.args.get("start")
        end = request.args.get("end")
        min_distance = request.args.get("min_distance", type=float)
        max_distance = request.args.get("max_distance", type=float)
        time_of_day = request.args.get("time_of_day")
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=100, type=int)
        per_page = max(1, min(per_page, 500))
        offset = (page - 1) * per_page

        where = []
        params = []
        if start:
            where.append("pickup_datetime >= ?")
            params.append(start)
        if end:
            where.append("pickup_datetime <= ?")
            params.append(end)
        if min_distance is not None:
            where.append("trip_distance_km >= ?")
            params.append(min_distance)
        if max_distance is not None:
            where.append("trip_distance_km <= ?")
            params.append(max_distance)
        if time_of_day:
            where.append("pickup_hour IS NOT NULL AND pickup_hour BETWEEN 0 AND 23")

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT id, pickup_datetime, dropoff_datetime,
                   pickup_lat, pickup_lon, dropoff_lat, dropoff_lon,
                   trip_distance_km, trip_duration_sec,
                   fare_amount, tip_amount, passenger_count, payment_type,
                   avg_speed_kmh, fare_per_km, pickup_hour, weekday, is_weekend, haversine_km
            FROM trips
            {where_sql}
            ORDER BY pickup_datetime DESC
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            return jsonify({"page": page, "per_page": per_page, "results": rows})
        except Exception as e:
            return jsonify({"error": "database_unavailable", "detail": str(e)}), 503
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

