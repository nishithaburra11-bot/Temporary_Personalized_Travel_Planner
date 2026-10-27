"""Varanasi Smart Trip Planner - Flask backend (MySQL + the team's itinerary.py).

Run (from this folder, venv active):
    pip install -r requirements.txt
    copy .env.example to .env and put your MySQL password in it
    python app.py          -> http://127.0.0.1:5000

Endpoints
  GET  /api/health
  GET  /api/regions                       distinct region_name values with place counts
  GET  /api/places?region=A&region=B      (region filter optional; use region NAMES)
  GET  /api/data-quality                  problems found in the places data
  POST /api/trip                          generate a trip
  POST /api/trip/recalculate              FULL regeneration ({trip_id, add_compulsory|compulsory_places} or a full payload)
  GET  /api/resources?place_ids=1,2
"""
import inspect
import json
import re
from datetime import timedelta

import requests
from flask import Flask, jsonify, request
try:
    from flask_cors import CORS
except ImportError:
    CORS = None

import database as db
import itenary_logic as planner_module            # Member 4's module: ALL scheduling logic lives there

app = Flask(__name__)
if CORS:
    CORS(app)

TRANSPORT_ALIASES = {"own_vehicle": "own_vehicle", "public": "public_transport",
                     "public_transport": "public_transport", "mixed": "mixed"}
STAY_PREFS = {"none", "budget", "normal", "luxury"}
FOOD_PREFS = {"any", "vegetarian", "vegan", "non_vegetarian", "jain"}
PACES = {"relaxed": 20, "normal": 10, "fast": 5}          # -> break_minutes between stops
MEALS_PER_DAY = 2
DAY_PREFIXES = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
_geocode_cache = {}


class ApiError(Exception):
    def __init__(self, message, status=400, details=None):
        super().__init__(message)
        self.message, self.status, self.details = message, status, details


@app.errorhandler(ApiError)
def handle_api_error(e):
    body = {"success": False, "error": e.message}
    if e.details:
        body["details"] = e.details
    return jsonify(body), e.status


@app.errorhandler(404)
def not_found(_):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404


@app.errorhandler(Exception)
def handle_unexpected(e):
    app.logger.exception("Unhandled error")
    return jsonify({"success": False, "error": "Internal server error (check the server terminal)."}), 500


# ------------------------------------------------------------ data cleaning
def _txt(v):
    s = None if v is None else str(v).strip()
    return s or None


def _mins(tok):
    parts = tok.split(":")
    h, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
    if not (0 <= h <= 24 and 0 <= m <= 59):
        raise ValueError(tok)
    return h * 60 + m


def _hhmm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def normalize_place_row(row):
    """Make one `places` row safe for itinerary.py. Returns (row, issues[]).

    The planner understands ONE opening window per place. The data has split sessions such as
    opening '05:00:00 13:00:00' / closing '12:00:00 21:00:00' (= 05-12 and 13-21). For those we pass the
    LONGEST session, so the planner never schedules a visit while the place is closed (it may exclude a
    place it could in reality have visited in the shorter session - that is flagged in the warnings).
    """
    r, issues, name = dict(row), [], row.get("place_name")
    o, c = _txt(r.get("opening_time")), _txt(r.get("closing_time"))

    if (o is None) != (c is None):
        issues.append(f"{name}: only one of opening_time/closing_time is filled "
                      f"(opening={o!r}, closing={c!r}) - possible shifted columns. Hours treated as UNKNOWN.")
        o = c = None
    elif o is not None:
        try:
            ot, ct = o.split(), c.split()
            if len(ot) != len(ct):
                raise ValueError("session count differs")
            sessions = []
            for a, b in zip(ot, ct):
                s, e = _mins(a), _mins(b)
                sessions.append((s, e if e > s else e + 1440))
            if len(sessions) > 1:
                best = max(sessions, key=lambda x: x[1] - x[0])
                shown = ", ".join(f"{_hhmm(s)}-{_hhmm(e % 1440)}" for s, e in sessions)
                issues.append(f"{name}: has split opening hours ({shown}); the planner uses only the longest "
                              f"session {_hhmm(best[0])}-{_hhmm(best[1] % 1440)}.")
                o, c = _hhmm(best[0]), _hhmm(best[1] % 1440)
            else:
                o, c = _hhmm(sessions[0][0]), _hhmm(sessions[0][1] % 1440)
        except (ValueError, IndexError):
            issues.append(f"{name}: opening/closing time could not be read ({o!r} / {c!r}). Hours treated as UNKNOWN.")
            o = c = None
    r["opening_time"], r["closing_time"] = o, c

    cd = _txt(r.get("closed_days"))
    if cd:
        tokens = [t.strip().lower() for t in cd.replace(";", ",").split(",") if t.strip()]
        if all(t[:3] in DAY_PREFIXES for t in tokens):
            r["closed_days"] = ", ".join(tokens)
        else:
            issues.append(f"{name}: closed_days={cd!r} is not a list of weekdays - ignored.")
            r["closed_days"] = None
    else:
        r["closed_days"] = None

    if r.get("latitude") is None or r.get("longitude") is None:
        issues.append(f"{name}: no coordinates stored - it cannot be routed.")
    return r, issues


# ------------------------------------------------------------ validation
def _num(data, key, default=None, minimum=None, maximum=None, integer=False, errors=None):
    val = data.get(key, default)
    if val is None or val == "":
        errors.append(f"'{key}' is required.")
        return None
    try:
        val = int(val) if integer else float(val)
    except (TypeError, ValueError):
        errors.append(f"'{key}' must be a number.")
        return None
    if (minimum is not None and val < minimum) or (maximum is not None and val > maximum):
        errors.append(f"'{key}' must be between {minimum} and {maximum}.")
        return None
    return val


def _id_list(data, key, errors):
    val = data.get(key, [])
    if not isinstance(val, list):
        errors.append(f"'{key}' must be a list of place IDs.")
        return []
    try:
        return list(dict.fromkeys(int(v) for v in val))
    except (TypeError, ValueError):
        errors.append(f"'{key}' must contain only integers.")
        return []


def validate_trip(data):
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object.")
    errors, p = [], {"raw": data}
    p["days"] = _num(data, "days", minimum=1, maximum=14, integer=True, errors=errors)
    p["hours_per_day"] = _num(data, "hours_per_day", minimum=1, maximum=16, errors=errors)
    p["budget"] = _num(data, "budget", minimum=0, errors=errors)
    p["travelers"] = _num(data, "travelers", default=1, minimum=1, maximum=50, integer=True, errors=errors)
    p["mileage_kmpl"] = _num(data, "mileage_kmpl", default=40, minimum=1, maximum=100, errors=errors)
    p["fuel_price"] = _num(data, "fuel_price", default=100, minimum=0, errors=errors)
    p["travel_time_factor"] = _num(data, "travel_time_factor", default=1.0, minimum=0.5, maximum=3, errors=errors)
    p["transport"] = TRANSPORT_ALIASES.get(str(data.get("transport", "own_vehicle")))
    if p["transport"] is None:
        errors.append(f"'transport' must be one of {sorted(TRANSPORT_ALIASES)}.")
    p["food_preference"] = data.get("food_preference", "any")
    p["stay_preference"] = data.get("stay_preference", "none")
    p["travel_pace"] = data.get("travel_pace", "normal")
    for key, allowed in (("food_preference", FOOD_PREFS), ("stay_preference", STAY_PREFS), ("travel_pace", set(PACES))):
        if p[key] not in allowed:
            errors.append(f"'{key}' must be one of {sorted(allowed)}.")
    p["start_time"] = data.get("start_time") or "09:00"
    p["start_date"] = data.get("start_date")
    p["selected_ids"] = _id_list(data, "selected_places", errors)
    p["compulsory_ids"] = _id_list(data, "compulsory_places", errors)
    for key in ("start", "end"):
        if not data.get(key):
            errors.append(f"'{key}' is required (place name or {{lat, lng}}).")
    p["selected_ids"] = list(dict.fromkeys(p["selected_ids"] + p["compulsory_ids"]))
    if not p["selected_ids"]:
        errors.append("Select at least one place.")
    if errors:
        raise ApiError("Invalid input.", 400, errors)
    return p


def resolve_location(value):
    """-> (lat, lon, label). Accepts {lat,lng}, a place/hotel name from the DB, or free text (Nominatim)."""
    if isinstance(value, dict):
        try:
            return float(value["lat"]), float(value["lng"]), f"{value['lat']},{value['lng']}"
        except (KeyError, TypeError, ValueError):
            raise ApiError("Location object must contain numeric 'lat' and 'lng'.")
    text = str(value).strip()
    row = db.query_one("SELECT place_name AS n, latitude, longitude FROM places "
                       "WHERE LOWER(place_name) = LOWER(%s) AND latitude IS NOT NULL", (text,))
    if not row:
        hrows = db.safe_query("SELECT hotel_name AS n, latitude, longitude FROM hotels "
                              "WHERE LOWER(hotel_name) = LOWER(%s) AND latitude IS NOT NULL", (text,))
        row = hrows[0] if hrows else None
    if row:
        return row["latitude"], row["longitude"], row["n"]
    if text.lower() in _geocode_cache:
        return _geocode_cache[text.lower()]
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": f"{text}, Varanasi, India", "format": "json", "limit": 1},
                         headers={"User-Agent": "varanasi-trip-planner/1.0 (student project)"}, timeout=8)
        r.raise_for_status()
        res = r.json()
    except Exception:
        raise ApiError(f"Could not look up '{text}' (geocoding service unavailable). "
                       'Send coordinates as {"lat":..,"lng":..} instead.', 503)
    if not res:
        raise ApiError(f"Could not find a location for '{text}'.", 400)
    out = (float(res[0]["lat"]), float(res[0]["lon"]), text)
    _geocode_cache[text.lower()] = out
    return out


# ------------------------------------------------------------ planning
def _call_planner(trip, places):
    """Call itinerary.generate_itinerary with only the keyword arguments it actually supports."""
    fn = planner_module.generate_itinerary
    wanted = {"use_osrm": True, "include_geometry": True}
    sig = inspect.signature(fn).parameters
    kwargs = {k: v for k, v in wanted.items() if k in sig or any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.values())}
    try:
        return fn(trip, places, **kwargs)
    except ValueError as exc:                      # planner's own validation messages
        raise ApiError(str(exc), 400)


def _near(rows, pts, limit=5):
    if pts:
        clat, clon = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        rows.sort(key=lambda r: planner_module.haversine_km((clat, clon), (r["latitude"], r["longitude"]))
                  if r.get("latitude") is not None else 1e9)
    return rows[:limit]


def plan_trip(params):
    ids = params["selected_ids"]
    marks = ",".join(["%s"] * len(ids))
    rows = db.query(f"SELECT * FROM places WHERE place_id IN ({marks})", ids)
    missing = [i for i in ids if i not in {r["place_id"] for r in rows}]
    if missing:
        raise ApiError(f"Unknown place IDs: {missing}", 400)

    warnings = []
    if params["transport"] == "public_transport":
        raise ApiError("Public-transport planning is unavailable: no verified Varanasi bus data has been "
                       "loaded. Choose 'own_vehicle' or 'mixed'.", 422)
    if params["transport"] == "mixed":
        warnings.append("No verified bus data is used: all legs are planned as road travel (own vehicle).")

    # clean the data + collect issues
    clean, issues = [], []
    for r in rows:
        nr, iss = normalize_place_row(r)
        clean.append(nr)
        issues += iss
    no_hours = [r["place_name"] for r in clean if not r["opening_time"]]
    if no_hours:
        warnings.append(f"No opening hours stored for {len(no_hours)} place(s) ({', '.join(no_hours)}); "
                        "they are treated as open all day. Verify before travelling.")
    warnings += issues
    if params["travelers"] > 1:                    # planner has no 'travelers' field: scale fees here
        for r in clean:
            r["entry_fee"] = float(r.get("entry_fee") or 0) * params["travelers"]
        warnings.append(f"Entry fees are multiplied by {params['travelers']} travelers.")
    warnings.append("Entry fees come from the database without a verification date, so they are shown as "
                    "estimates. A fee of 0 may also mean 'not collected yet'.")

    s_lat, s_lon, s_label = resolve_location(params["raw"]["start"])
    e_lat, e_lon, e_label = resolve_location(params["raw"]["end"])
    params["start_label"], params["end_label"] = s_label, e_label

    # food / hotel (tables may not exist yet - then they are simply not included)
    if params["food_preference"] != "any":
        key = params["food_preference"].replace("_", "-")
        foods = db.safe_query("SELECT * FROM food_places WHERE LOWER(COALESCE(dietary_options,'')) LIKE %s",
                              (f"%{key}%",))
    else:
        foods = db.safe_query("SELECT * FROM food_places")
    hotels_all = db.safe_query("SELECT * FROM hotels" + (" WHERE category = %s" if params["stay_preference"] != "none" else ""),
                               (params["stay_preference"],) if params["stay_preference"] != "none" else ())
    prices = [f["price_range_per_person"] for f in foods if f.get("price_range_per_person") is not None]
    food_per_day = (sum(prices) / len(prices)) * MEALS_PER_DAY * params["travelers"] if prices else 0.0
    hotel_prices = [h["price_per_night"] for h in hotels_all if h.get("price_per_night") is not None]
    hotel_per_night = min(hotel_prices) if (hotel_prices and params["stay_preference"] != "none") else 0.0
    if not prices:
        warnings.append("Food cost is not included (no priced food places in the database).")
    if params["stay_preference"] != "none" and not hotel_prices and params["days"] > 1:
        warnings.append("Accommodation cost is not included (no priced hotels in the database).")

    trip = {"days": params["days"], "hours_per_day": params["hours_per_day"], "budget": params["budget"],
            "start_coords": (s_lat, s_lon), "end_coords": (e_lat, e_lon),
            "start_time": params["start_time"], "break_minutes": PACES[params["travel_pace"]],
            "transport": "own_vehicle", "mileage_kmpl": params["mileage_kmpl"],
            "fuel_price": params["fuel_price"], "food_per_day": food_per_day,
            "hotel_per_night": hotel_per_night, "travel_time_factor": params["travel_time_factor"],
            "selected_places": ids, "compulsory_places": params["compulsory_ids"]}
    if params["start_date"]:
        trip["start_date"] = params["start_date"]
    else:
        warnings.append("No start_date given: closed-day rules cannot be checked.")

    result = _call_planner(trip, clean)
    response = dict(result)                         # pass the planner's own keys through untouched
    response.setdefault("itinerary_by_day", [])
    response.setdefault("excluded_places", [])
    response.setdefault("conflicts", [])
    response["warnings"] = list(dict.fromkeys(warnings + list(result.get("warnings", []))))
    response.setdefault("success", not response["conflicts"])

    stops = [s for d in response["itinerary_by_day"] for s in d.get("stops", [])]
    sched_pts = [(s["latitude"], s["longitude"]) for s in stops if s.get("latitude") is not None]
    sched_ids = {s.get("place_id", s.get("id")) for s in stops}
    response["markers"] = [{"place_id": r["place_id"], "name": r["place_name"], "lat": r["latitude"],
                            "lng": r["longitude"], "scheduled": r["place_id"] in sched_ids}
                           for r in clean if r.get("latitude") is not None]
    response["start"] = {"label": s_label, "lat": s_lat, "lng": s_lon}
    response["end"] = {"label": e_label, "lat": e_lat, "lng": e_lon}
    response["food_suggestions"] = _near(foods, sched_pts)
    hotels = hotels_all if params["stay_preference"] != "none" else db.safe_query("SELECT * FROM hotels")
    response["hotel_suggestions"] = _near(hotels, sched_pts)
    response["resources"] = db.safe_query(
        f"SELECT r.*, p.place_name FROM travel_resources r JOIN places p ON p.place_id = r.place_id "
        f"WHERE r.place_id IN ({marks})", ids)
    try:
        response["trip_id"] = db.save_trip(params, response["itinerary_by_day"], set(params["compulsory_ids"]), ids)
    except Exception:
        app.logger.exception("Could not save trip")
        response["trip_id"] = None
        response["warnings"].append("The trip could not be saved to the database (recalculation by trip_id "
                                    "will not work; send the full payload instead).")
    return response


# ------------------------------------------------------------ routes
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/regions")
def regions():
    rows = db.query("SELECT region_name, COUNT(*) AS place_count FROM places GROUP BY region_name ORDER BY region_name")
    return jsonify({"success": True, "regions": rows})


@app.get("/api/places")
def places():
    names = [n for n in request.args.getlist("region") if n.strip()]
    sql, args = "SELECT * FROM places", []
    if names:
        sql += f" WHERE region_name IN ({','.join(['%s'] * len(names))})"
        args = names
    rows = db.query(sql + " ORDER BY place_name", args)
    for r in rows:                                   # attach per-place data problems for the UI
        r["data_issues"] = normalize_place_row(r)[1]
    return jsonify({"success": True, "places": rows})


@app.get("/api/data-quality")
def data_quality():
    out = []
    for r in db.query("SELECT * FROM places ORDER BY place_id"):
        out += normalize_place_row(r)[1]
    return jsonify({"success": True, "issue_count": len(out), "issues": out})


@app.get("/api/resources")
def resources():
    raw = request.args.get("place_ids", "").strip()
    sql = "SELECT r.*, p.place_name FROM travel_resources r JOIN places p ON p.place_id = r.place_id"
    args = []
    if raw:
        if not re.fullmatch(r"\d+(,\d+)*", raw):
            raise ApiError("'place_ids' must be comma-separated integers.")
        ids = [int(x) for x in raw.split(",")]
        sql += f" WHERE r.place_id IN ({','.join(['%s'] * len(ids))})"
        args = ids
    return jsonify({"success": True, "resources": db.safe_query(sql, args)})


@app.post("/api/trip")
def create_trip():
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError("Body must be valid JSON.")
    return jsonify(plan_trip(validate_trip(data)))


@app.post("/api/trip/recalculate")
def recalculate():
    """Rebuild the WHOLE itinerary from scratch with the new compulsory set (never patch the old one)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Body must be a JSON object.")
    if "trip_id" in data:
        row = db.query_one("SELECT params_json FROM trips WHERE trip_id = %s", (data["trip_id"],))
        if not row:
            raise ApiError("Unknown trip_id.", 404)
        base = json.loads(row["params_json"])
        prev = [r["place_id"] for r in db.query(
            "SELECT place_id FROM trip_places WHERE trip_id = %s AND is_compulsory = 1", (data["trip_id"],))]
        base["compulsory_places"] = data["compulsory_places"] if "compulsory_places" in data else \
            list(dict.fromkeys(prev + list(data.get("add_compulsory", []))))
        for k, v in data.items():
            if k not in ("trip_id", "compulsory_places", "add_compulsory"):
                base[k] = v
        data = base
    elif "add_compulsory" in data:
        raise ApiError("'add_compulsory' needs a 'trip_id'.")
    return jsonify(plan_trip(validate_trip(data)))


if __name__ == "__main__":
    for problem in db.init_db():
        print("WARNING creating extra tables:", problem)
    app.run(debug=True, host="127.0.0.1", port=5000)
