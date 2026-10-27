"""MySQL access layer (PyMySQL). Connection details come from environment variables / a .env file."""
import datetime
import decimal
import json
import os

import pymysql

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRA_SCHEMA = os.path.join(BASE_DIR, "schema_extra.sql")


def _config():
    return dict(host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", "3306")),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", ""),
                database=os.environ.get("DB_NAME", "personalized_travel_planner"),
                charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)


def get_conn():
    return pymysql.connect(**_config())


def _clean(v):
    """MySQL types -> JSON-friendly Python types."""
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, datetime.timedelta):          # TIME columns
        s = int(v.total_seconds())
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def query(sql, args=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return [{k: _clean(v) for k, v in row.items()} for row in cur.fetchall()]
    finally:
        conn.close()


def query_one(sql, args=()):
    rows = query(sql, args)
    return rows[0] if rows else None


def safe_query(sql, args=()):
    """Like query(), but returns [] if the table doesn't exist yet (e.g. hotels not loaded)."""
    try:
        return query(sql, args)
    except pymysql.err.ProgrammingError:
        return []


def execute(sql, args=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            last = cur.lastrowid
        conn.commit()
        return last
    finally:
        conn.close()


def init_db():
    """Create the extra tables if missing. Never touches `places`. Returns list of problems."""
    problems = []
    with open(EXTRA_SCHEMA, encoding="utf-8") as f:
        text = "\n".join(l for l in f.read().splitlines() if not l.strip().startswith("--"))
    for stmt in [s.strip() for s in text.split(";") if s.strip()]:
        if stmt.upper().startswith("USE "):
            continue                                   # connection already selects DB_NAME
        try:
            execute(stmt)
        except Exception as exc:
            problems.append(f"{type(exc).__name__}: {exc}")
    return problems


def save_trip(params, days, compulsory_ids, selected_ids):
    """Persist a trip + its itinerary. `days` = itinerary_by_day from the planner. Returns trip_id."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO trips (start_location, end_location, number_of_days, hours_per_day, budget,
                   transport_mode, food_preference, stay_preference, travel_pace, params_json)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (params["start_label"], params["end_label"], params["days"], params["hours_per_day"],
                 params["budget"], params["transport"], params["food_preference"],
                 params["stay_preference"], params["travel_pace"], json.dumps(params["raw"])))
            trip_id = cur.lastrowid
            for pid in selected_ids:
                cur.execute("INSERT INTO trip_places (trip_id, place_id, is_selected, is_compulsory) "
                            "VALUES (%s,%s,1,%s)", (trip_id, pid, 1 if pid in compulsory_ids else 0))
            for day in days:
                for s in day.get("stops", []):
                    pid = s.get("place_id", s.get("id"))
                    if pid is None:
                        continue
                    cur.execute(
                        """INSERT INTO itinerary_items (trip_id, day_number, place_id, arrival_time,
                           departure_time, travel_duration_minutes, estimated_cost)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (trip_id, day.get("day"), pid,
                         str(s.get("arrival_time", s.get("arrive", ""))),
                         str(s.get("departure_time", s.get("leave", ""))),
                         s.get("travel_duration_minutes", s.get("travel_min", s.get("travel_minutes"))),
                         s.get("estimated_cost", s.get("cost"))))
        conn.commit()
        return trip_id
    finally:
        conn.close()
