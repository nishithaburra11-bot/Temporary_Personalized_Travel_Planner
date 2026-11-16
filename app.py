"""Varanasi Smart Trip Planner - Flask backend (MySQL + the team's itenary_logic.py).

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
"""
import json
import math
import os
import re
from datetime import timedelta

import requests
from flask import Flask, jsonify, request, send_from_directory
try:
    from flask_cors import CORS
except ImportError:
    CORS = None

import database as db
import itinenary_logic as planner_module        # Member 4's module (itenary_logic.py): ALL scheduling logic lives there

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
        if isinstance(val, bool) or not math.isfinite(float(val)) or (integer and float(val) != int(float(val))):
            raise ValueError()
        val = int(val) if integer else float(val)
    except (TypeError, ValueError, OverflowError):
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
    p["days"] = _num(data, "days", minimum=1, maximum=30, integer=True, errors=errors)
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
    p["food_budget"] = data.get("food_budget", "standard")
    if not isinstance(p["food_budget"], str) or p["food_budget"] not in {"budget", "standard", "premium"}:
        errors.append("'food_budget' must be budget, standard or premium.")
    p["stay_preference"] = data.get("stay_preference", "none")
    p["travel_pace"] = data.get("travel_pace", "normal")
    for key, allowed in (("food_preference", FOOD_PREFS), ("stay_preference", STAY_PREFS), ("travel_pace", set(PACES))):
        if not isinstance(p[key], str) or p[key] not in allowed:
            errors.append(f"'{key}' must be one of {sorted(allowed)}.")
    p["start_time"] = data.get("start_time") or "09:00"
    p["start_date"] = data.get("start_date")
    p["selected_ids"] = _id_list(data, "selected_places", errors)
    p["compulsory_ids"] = _id_list(data, "compulsory_places", errors)
    p["selected_ids"] = list(dict.fromkeys(p["selected_ids"] + p["compulsory_ids"]))
    if not p["selected_ids"]:
        errors.append("Select at least one place.")
    if errors:
        raise ApiError("Invalid input.", 400, errors)
    return p


def resolve_location(value):
    """Resolve coordinates or a curated place/hotel name without external services."""
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
    raise ApiError(f"'{text}' is not a stored location. Choose a place from the location suggestions.", 400)


# ------------------------------------------------------------ planning
def _call_planner(trip, places):
    """Call generate_itinerary(trip, places, use_osrm, include_geometry) from itenary_logic.py."""
    try:
        return planner_module.generate_itinerary(trip, places, use_osrm=False, include_geometry=False)
    except ValueError as exc:                      # planner's own validation messages -> HTTP 400
        raise ApiError(str(exc), 400)


def _near(rows, pts, limit=5):
    if not pts:
        return []
    located = [dict(r) for r in rows if r.get("latitude") is not None and r.get("longitude") is not None]
    for r in located:
        r["distance_to_stop_km"] = round(min(planner_module.haversine_km(
            pt, (r["latitude"], r["longitude"])) for pt in pts), 2)
    return sorted(located, key=lambda r: r["distance_to_stop_km"])[:limit]


def food_suggestions_by_day(days, foods, budget_tier, radius_km=3.0):
    """Suggestions only: hours, meal time and detours do not alter the schedule."""
    matching = [f for f in foods if f.get("budget_tier") == budget_tier]

    def noon_distance(stop):
        try:
            arrival = sum(int(v) * scale for v, scale in zip(stop["arrival_time"].split(":"), (60, 1)))
            departure = sum(int(v) * scale for v, scale in zip(stop["departure_time"].split(":"), (60, 1)))
            return max(arrival - 13 * 60, 13 * 60 - departure, 0)
        except (KeyError, TypeError, ValueError):
            return float("inf")

    groups = []
    for index, day in enumerate(days, 1):
        stops = [s for s in day.get("stops", [])
                 if s.get("latitude") is not None and s.get("longitude") is not None]
        lunch = min(stops, key=noon_distance) if stops else None
        dinner = stops[-1] if stops else None
        meals = []
        for meal, anchor in (("Lunch", lunch), ("Dinner", dinner)):
            candidates = _near(matching, [(anchor["latitude"], anchor["longitude"])], limit=len(matching)) if anchor else []
            # Compare unrounded distances at the boundary; rounded values are display-only.
            nearby = [f for f in candidates if planner_module.haversine_km(
                (anchor["latitude"], anchor["longitude"]), (f["latitude"], f["longitude"])) <= radius_km]
            selection = nearby
            mode = "nearby"
            message = ""
            if not anchor:
                mode, message = "unavailable", "No scheduled stops for this day."
            elif not nearby and candidates:
                selection, mode = candidates, "farther"
                message = (f"No restaurants in your selected food tier are listed within an estimated {radius_km:g} km "
                           "of this stop. Here are the closest available options farther away; allow extra travel time.")
            elif not nearby:
                selection = _near(foods, [(anchor["latitude"], anchor["longitude"])], limit=len(foods))
                mode = "other_tiers" if selection else "unavailable"
                message = ("No restaurants with locations are listed in your selected food tier. "
                           "Here are the closest available options from other tiers; check their estimated prices."
                           if selection else "No restaurant locations are available in our current list.")
            meals.append({"meal": meal, "anchor_place_id": anchor.get("place_id") if anchor else None,
                          "anchor_place_name": anchor.get("place_name") if anchor else None,
                          "restaurants": selection, "selection_mode": mode, "message": message})
        groups.append({"day": day.get("day", index), "radius_km": radius_km, "meals": meals})
    return groups


def hotel_suggestions_by_day(days, hotels, category, radius_km=3.0):
    """Daily alternatives, not bookings or changes to the itinerary's endpoints."""
    if category == "none":
        return []
    matching = [h for h in hotels if h.get("category") == category]
    groups = []
    for index, day in enumerate(days, 1):
        located = [s for s in day.get("stops", [])
                   if s.get("latitude") is not None and s.get("longitude") is not None]
        anchor = located[-1] if located else None
        choices, mode, message = [], "unavailable", "No scheduled stops for this day."
        if anchor:
            point = (anchor["latitude"], anchor["longitude"])
            candidates = _near(matching, [point], limit=len(matching))
            choices = [h for h in candidates if planner_module.haversine_km(
                point, (h["latitude"], h["longitude"])) <= radius_km]
            mode, message = "nearby", ""
            if not choices and candidates:
                choices, mode = candidates, "farther"
                message = (f"No stays in your selected comfort level are listed within an estimated {radius_km:g} km "
                           "of this stop. These are the closest options farther away.")
            elif not choices:
                choices = _near(hotels, [point], limit=len(hotels))
                mode = "other_tiers" if choices else "unavailable"
                message = ("No located stays match your selected comfort level. These alternatives use other "
                           "comfort levels; check their estimated rates." if choices
                           else "No hotel locations are available in our current list.")
        groups.append({"day": day.get("day", index), "optional_after_trip": index == len(days),
                       "anchor_place_name": anchor.get("place_name") if anchor else None,
                       "hotels": choices, "selection_mode": mode, "message": message})
    return groups


def plan_trip(params):
    ids = params["selected_ids"]
    marks = ",".join(["%s"] * len(ids))
    rows = db.query(f"SELECT * FROM places WHERE place_id IN ({marks})", ids)
    missing = [i for i in ids if i not in {r["place_id"] for r in rows}]
    if missing:
        raise ApiError(f"Unknown place IDs: {missing}", 400)

    if params["transport"] == "public_transport":
        raise ApiError("Public-transport planning is unavailable: no verified Varanasi bus data has been "
                       "loaded. Choose 'own_vehicle' or 'mixed'.", 422)

    # clean the data + collect issues
    clean, issues = [], []
    for r in rows:
        nr, iss = normalize_place_row(r)
        clean.append(nr)
        issues += iss
    if params["travelers"] > 1:                    # planner has no 'travelers' field: scale fees here
        for r in clean:
            r["entry_fee"] = float(r.get("entry_fee") or 0) * params["travelers"]

    located = [p for p in clean if p.get("latitude") is not None and p.get("longitude") is not None]
    if not located:
        raise ApiError("Selected places have no usable coordinates.")
    def endpoint(place):
        return place["latitude"], place["longitude"], place["place_name"]
    auto_start = not params["raw"].get("start")
    auto_end = not params["raw"].get("end")
    s_lat, s_lon, s_label = endpoint(located[0]) if auto_start else resolve_location(params["raw"]["start"])
    e_lat, e_lon, e_label = endpoint(located[-1]) if auto_end else resolve_location(params["raw"]["end"])

    # food / hotel (tables may not exist yet - then they are simply not included)
    if params["food_preference"] != "any":
        key = params["food_preference"].replace("_", "-")
        foods = db.safe_query("SELECT * FROM food_places WHERE LOWER(COALESCE(dietary_options,'')) LIKE %s",
                              (f"%{key}%",))
    else:
        foods = db.safe_query("SELECT * FROM food_places")
    foods_all_tiers = foods
    foods = [f for f in foods if f.get("budget_tier") == params["food_budget"]]
    hotels_every_tier = db.safe_query("SELECT * FROM hotels")
    hotels_all = [h for h in hotels_every_tier if h.get("category") == params["stay_preference"]]
    prices = [f["price_range_per_person"] for f in foods if f.get("price_range_per_person") is not None]
    food_per_day = (sum(prices) / len(prices)) * MEALS_PER_DAY * params["travelers"] if prices else 0.0
    hotel_prices = [h["price_per_night"] for h in hotels_all if h.get("price_per_night") is not None]
    hotel_per_night = min(hotel_prices) if (hotel_prices and params["stay_preference"] != "none") else 0.0

    trip = {"days": params["days"], "hours_per_day": params["hours_per_day"], "budget": params["budget"],
            "start_coords": (s_lat, s_lon), "end_coords": (e_lat, e_lon),
            "start_time": params["start_time"], "break_minutes": PACES[params["travel_pace"]],
            "transport": "own_vehicle", "mileage_kmpl": params["mileage_kmpl"],
            "fuel_price": params["fuel_price"], "food_per_day": food_per_day,
            "hotel_per_night": hotel_per_night, "travel_time_factor": params["travel_time_factor"],
            "selected_places": ids, "compulsory_places": params["compulsory_ids"]}
    trip["max_stops_per_day"] = {"relaxed": 2, "normal": 3, "fast": None}[params["travel_pace"]]
    if params["start_date"]:
        trip["start_date"] = params["start_date"]      # (planner warns by itself if it is missing)

    if auto_start or auto_end:
        # Try a nearest-neighbour route from each possible start. Prefer plans
        # that include compulsory stops, then more visits, then use more of the budget.
        starts = [endpoint(p) for p in located] if auto_start else [(s_lat, s_lon, s_label)]
        best = None
        for start in starts:
            remaining = list(located)
            point = start[:2]
            while remaining:
                last = min(remaining, key=lambda p: planner_module.haversine_km(point, endpoint(p)[:2]))
                remaining.remove(last)
                point = endpoint(last)[:2]
            end = endpoint(last) if auto_end else (e_lat, e_lon, e_label)
            candidate = dict(trip, start_coords=start[:2], end_coords=end[:2])
            planned = _call_planner(candidate, clean)
            stops = [stop for day in planned.get("itinerary_by_day", []) for stop in day.get("stops", [])]
            scheduled = {stop.get("place_id") for stop in stops}
            score = (len(scheduled.intersection(params["compulsory_ids"])), len(stops),
                     planned["cost_breakdown"]["total"],
                     -planned.get("total_distance_km", 0))
            if best is None or score > best[0]:
                best = (score, planned, start, end)
        _, result, (s_lat, s_lon, s_label), (e_lat, e_lon, e_label) = best
    else:
        result = _call_planner(trip, clean)
    params["start_label"], params["end_label"] = s_label, e_label
    response = dict(result)                         # pass the planner's own keys through untouched
    response.setdefault("itinerary_by_day", [])
    response.setdefault("excluded_places", [])
    response.setdefault("conflicts", [])
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
    response["food_suggestions_by_day"] = food_suggestions_by_day(
        response["itinerary_by_day"], foods_all_tiers, params["food_budget"])
    hotels = hotels_all if params["stay_preference"] != "none" else []
    response["hotel_suggestions"] = _near(hotels, sched_pts)
    response["hotel_suggestions_by_day"] = hotel_suggestions_by_day(
        response["itinerary_by_day"], hotels_every_tier, params["stay_preference"])
    try:
        response["trip_id"] = db.save_trip(params, response["itinerary_by_day"], set(params["compulsory_ids"]), ids)
    except Exception:
        app.logger.exception("Could not save trip")
        response["trip_id"] = None
    return response


# ------------------------------------------------------------ routes
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def home():
    return send_from_directory(os.path.join(app.root_path, "frontend"), "index.html")


@app.get("/<path:filename>")
def frontend_file(filename):
    if filename.startswith("api/"):
        raise ApiError("Endpoint not found.", 404)
    return send_from_directory(os.path.join(app.root_path, "frontend"), filename)


@app.get("/api/regions")
def regions():
    rows = db.query("SELECT region_name, COUNT(*) AS place_count FROM places GROUP BY region_name ORDER BY region_name")
    return jsonify({"success": True, "regions": rows})


REGION_SLUGS = {
    "bhu-south": "BHU and Southern Varanasi",
    "old-city": "Old City and Central Ghats",
    "sarnath-north": "Sarnath and Northern Varanasi",
    "ramnagar-east": "Ramnagar and Eastern Riverbank",
    "rural-kashi": "Rural Kashi",
    "chandauli": "Chandauli region",
    "mirzapur-chunar": "Mirzapur and Chunar Region",
    "kaimoor": "Kaimoor region"
}
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "images", "places")


@app.get("/api/places")
def places():
    names = [n for n in request.args.getlist("region") if n.strip()]
    for rid in request.args.getlist("region_id"):
        for sub in rid.split(","):
            sub = sub.strip()
            if sub:
                names.append(REGION_SLUGS.get(sub, sub))
    sql, args = "SELECT * FROM places", []
    if names:
        sql += f" WHERE region_name IN ({','.join(['%s'] * len(names))})"
        args = names
    rows = db.query(sql + " ORDER BY place_name", args)
    for r in rows:                                   # attach per-place data problems for the UI
        r["data_issues"] = normalize_place_row(r)[1]
    return jsonify({"success": True, "places": rows})


@app.get("/api/images/places/<path:filename>")
def place_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.get("/api/data-quality")
def data_quality():
    out = []
    for r in db.query("SELECT * FROM places ORDER BY place_id"):
        out += normalize_place_row(r)[1]
    return jsonify({"success": True, "issue_count": len(out), "issues": out})


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
    app.run(debug=True, host="127.0.0.1", port=5000)
