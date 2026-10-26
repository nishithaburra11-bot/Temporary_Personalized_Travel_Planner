"""SQLite access layer. All SQL lives here or in app.py queries; no other module opens the DB."""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("TRIP_DB", os.path.join(BASE_DIR, "varanasi.db"))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables (safe to run repeatedly)."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        script = f.read()
    conn = get_conn()
    try:
        conn.executescript(script)
        conn.commit()
    finally:
        conn.close()


def query(sql, args=()):
    """Run a SELECT and return a list of dicts."""
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


def query_one(sql, args=()):
    rows = query(sql, args)
    return rows[0] if rows else None


def execute(sql, args=()):
    """Run one write statement; returns lastrowid."""
    conn = get_conn()
    try:
        cur = conn.execute(sql, args)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def save_trip(params, scheduled_by_day, compulsory_ids, selected_ids):
    """Persist a trip, its places and itinerary items. Returns trip_id."""
    import json
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO Trips (start_location, end_location, number_of_days, hours_per_day,
               budget, transport_mode, food_preference, stay_preference, travel_pace, params_json)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (params["start_label"], params["end_label"], params["days"], params["hours_per_day"],
             params["budget"], params["transport"], params["food_preference"],
             params["stay_preference"], params["travel_pace"], json.dumps(params["raw"])))
        trip_id = cur.lastrowid
        for pid in selected_ids:
            conn.execute("INSERT INTO TripPlaces VALUES (?,?,?,?)",
                         (trip_id, pid, 1, 1 if pid in compulsory_ids else 0))
        for day in scheduled_by_day:
            for it in day["items"]:
                conn.execute("INSERT INTO ItineraryItems VALUES (?,?,?,?,?,?,?)",
                             (trip_id, day["day"], it["place_id"], it["arrival_time"],
                              it["departure_time"], it["travel_duration_minutes"],
                              it.get("entry_fee_total")))
        conn.commit()
        return trip_id
    finally:
        conn.close()
