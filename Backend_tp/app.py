
"""Varanasi Smart Trip Planner - Flask backend.

Run:  pip install -r requirements.txt
      python app.py            (creates the DB if needed, serves on http://127.0.0.1:5000)

Endpoints
  GET  /api/health
  GET  /api/regions
  GET  /api/places?region_id=1,2
  POST /api/trip               generate a trip
  POST /api/trip/recalculate   full regeneration (body: trip_id + compulsory_places, or a full trip payload)
  GET  /api/resources?place_ids=1,2
"""
import json
import re
from datetime import date

import requests
from flask import Flask, jsonify, request
try:
    from flask_cors import CORS
except ImportError:  # CORS only needed if the frontend is served from another origin
    CORS = None

import database as db
import routing
from itinerary import generate_itinerary  # Member 4's module (single source of scheduling logic)

app = Flask(__name__)
if CORS:
    CORS(app)

TRANSPORT_MODES = {"own_vehicle", "public", "mixed"}
STAY_PREFS = {"none", "budget", "normal", "luxury"}
FOOD_PREFS = {"any", "vegetarian", "vegan", "non_vegetarian", "jain"}
PACES = {"relaxed", "normal", "fast"}
DEFAULT_MILEAGE_KMPL = 40.0     # assumption - user can override
DEFAULT_FUEL_PRICE = 100.0      # INR/litre assumption - user can override
MEALS_PER_DAY = 2
_geocode_cache = {}


# ---------------------------------------------------------------- helpers
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
    return jsonify({"success": False, "error": "Internal server error."}), 500


def _num(data, key, default=None, minimum=None, maximum=None, integer=False, errors=None):
    val = data.get(key, default)
    if val is None:
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
    errors = []
    p = {"raw": data}
    p["days"] = _num(data, "days", minimum=1, maximum=14, integer=True, errors=errors)
    p["hours_per_day"] = _num(data, "hours_per_day", minimum=1, maximum=16, errors=errors)
    p["budget"] = _num(data, "budget", minimum=0, errors=errors)
    p["travelers"] = _num(data, "travelers", default=1, minimum=1, maximum=50, integer=True, errors=errors)
    p["mileage_kmpl"] = _num(data, "mileage_kmpl", default=DEFAULT_MILEAGE_KMPL, minimum=1, maximum=100, errors=errors)
    p["fuel_price"] = _num(data, "fuel_price", default=DEFAULT_FUEL_PRICE, minimum=0, errors=errors)
    p["transport"] = data.get("transport", "own_vehicle")
    p["food_preference"] = data.get("food_preference", "any")
    p["stay_preference"] = data.get("stay_preference", "none")
    p["travel_pace"] = data.get("travel_pace", "normal")
    for key, allowed in (("transport", TRANSPORT_MODES), ("food_preference", FOOD_PREFS),
                         ("stay_preference", STAY_PREFS), ("travel_pace", PACES)):
        if p[key] not in allowed:
            errors.append(f"'{key}' must be one of {sorted(allowed)}.")
    p["selected_ids"] = _id_list(data, "selected_places", errors)
    p["compulsory_ids"] = _id_list(data, "compulsory_places", errors)
    p["start_date"] = data.get("start_date")
    if p["start_date"]:
        try:
            date.fromisoformat(p["start_date"])
        except ValueError:
            errors.append("'start_date' must be YYYY-MM-DD.")
    for key in ("start", "end"):
        if not data.get(key):
            errors.append(f"'{key}' is required (place name or {{lat, lng}}).")
    # compulsory places are always part of the selection
    p["selected_ids"] = list(dict.fromkeys(p["selected_ids"] + p["compulsory_ids"]))
    if not p["selected_ids"]:
        errors.append("Select at least one place.")
    if errors:
        raise ApiError("Invalid input.", 400, errors)
    p["break_minutes"] = {"relaxed": 90, "normal": 60, "fast": 30}[p["travel_pace"]]
    return p


def resolve_location(value):
    """-> (lat, lon, label). Accepts {lat,lng}, a known place/hotel name, or free text via Nominatim."""
    if isinstance(value, dict):
        try:
            return float(value["lat"]), float(value["lng"]), f"{value['lat']},{value['lng']}"
        except (KeyError, TypeError, ValueError):
            raise ApiError("Location object must contain numeric 'lat' and 'lng'.")
    text = str(value).strip()
    for table, col, name in (("Places", "place_name", "place_name"), ("Hotels", "hotel_name", "hotel_name")):
        row = db.query_one(f"SELECT latitude, longitude, {name} AS n FROM {table} "
                           f"WHERE LOWER({col}) = LOWER(?) AND latitude IS NOT NULL", (text,))
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
                       "Send coordinates as {\"lat\":..,\"lng\":..} instead.", 503)
    if not res:
        raise ApiError(f"Could not find a location for '{text}'.", 400)
    out = (float(res[0]["lat"]), float(res[0]["lon"]), text)
    _geocode_cache[text.lower()] = out
    return out


def _fee_info(place):
    fee = place.get("entry_fee")
    if fee is None:
        return 0.0, "unknown"
    return float(fee), "verified" if place.get("source_checked_date") else "estimated"


def compute_costs(params, schedule, places_by_id, hotels, foods):
    """Algorithm 4. Every line is labelled verified / estimated / unknown."""
    lines, unknown = [], []
    trav = params["travelers"]

    # entry fees
    fee_total, fee_status = 0.0, "verified"
    for day in schedule:
        for it in day["items"]:
            fee, status = _fee_info(places_by_id[it["place_id"]])
            it["entry_fee_total"] = fee * trav
            it["entry_fee_status"] = status
            fee_total += fee * trav
            if status == "unknown":
                unknown.append(f"Entry fee unknown for {it['place_name']}")
            elif status == "estimated":
                fee_status = "estimated"
    lines.append({"item": "Attraction entry fees", "amount": round(fee_total, 2), "status": fee_status})

    # transport
    km = sum(it["travel_distance_km"] for d in schedule for it in d["items"])
    km += sum(d["return_leg"]["distance_km"] for d in schedule if d.get("return_leg"))
    sources = {it["travel_source"] for d in schedule for it in d["items"]}
    if params["transport"] in ("own_vehicle", "mixed"):
        fuel = km / params["mileage_kmpl"] * params["fuel_price"]
        lines.append({"item": f"Fuel ({km:.1f} km @ {params['mileage_kmpl']} km/L, INR {params['fuel_price']}/L)",
                      "amount": round(fuel, 2), "status": "estimated"})
        unknown.append("Parking charges are not included (no verified data).")
    total_km = round(km, 1)

    # food
    prices = [f["price_range_per_person"] for f in foods if f.get("price_range_per_person") is not None]
    active_days = sum(1 for d in schedule if d["items"]) or 0
    if prices and active_days:
        avg = sum(prices) / len(prices)
        lines.append({"item": f"Food (avg INR {avg:.0f}/meal x {MEALS_PER_DAY} meals x {active_days} days x {trav} people)",
                      "amount": round(avg * MEALS_PER_DAY * active_days * trav, 2), "status": "estimated"})
    else:
        unknown.append("Food cost not included (no priced food data for this preference).")

    # accommodation
    nights = max(params["days"] - 1, 0)
    if params["stay_preference"] != "none" and nights:
        priced = [h["price_per_night"] for h in hotels if h.get("price_per_night") is not None]
        if priced:
            lines.append({"item": f"Accommodation ({nights} night(s), cheapest {params['stay_preference']} option)",
                          "amount": round(min(priced) * nights, 2), "status": "estimated"})
        else:
            unknown.append("Accommodation cost not included (no priced hotels in database).")

    total = round(sum(l["amount"] for l in lines), 2)
    return {"lines": lines, "total_estimated": total, "budget": params["budget"],
            "within_budget": total <= params["budget"], "total_distance_km": total_km,
            "distance_source": "osrm" if sources == {"osrm"} else "estimated",
            "not_included_or_unknown": unknown}


def _suggestions(table, sql, args, pts, limit=5):
    rows = db.query(sql, args)
    if pts:
        clat = sum(p[0] for p in pts) / len(pts)
        clon = sum(p[1] for p in pts) / len(pts)
        rows.sort(key=lambda r: routing.haversine_km((clat, clon), (r["latitude"], r["longitude"]))
                  if r.get("latitude") is not None else 1e9)
    return rows[:limit]


def food_query(pref):
    sql = "SELECT * FROM FoodPlaces"
    args = []
    if pref != "any":
        sql += " WHERE LOWER(COALESCE(dietary_options,'')) LIKE ?"
        args.append(f"%{pref.replace('_', '-')}%" if pref == "non_vegetarian" else f"%{pref}%")
    return sql, args


# ---------------------------------------------------------------- core planning
def plan_trip(params):
    places = db.query(
        f"SELECT * FROM Places WHERE place_id IN ({','.join('?' * len(params['selected_ids']))})",
        params["selected_ids"])
    found = {p["place_id"] for p in places}
    missing = [i for i in params["selected_ids"] if i not in found]
    if missing:
        raise ApiError(f"Unknown place IDs: {missing}", 400)
    no_coords = [p["place_name"] for p in places if p["latitude"] is None or p["longitude"] is None]
    if no_coords:
        raise ApiError("These places have no verified coordinates and cannot be routed: "
                       + ", ".join(no_coords), 422)

    warnings = []
    if params["transport"] == "public":
        has_bus = db.query_one("SELECT 1 AS x FROM BusRouteStops LIMIT 1")
        if not has_bus:
            raise ApiError("Public-transport planning is unavailable: no verified Varanasi bus data "
                           "has been loaded. Choose 'own_vehicle' or 'mixed'.", 422)
        raise ApiError("Public-transport routing is not implemented yet.", 501)
    if params["transport"] == "mixed":
        warnings.append("No verified bus data is used: all legs are planned as road travel (own vehicle).")

    s_lat, s_lon, s_label = resolve_location(params["raw"]["start"])
    e_lat, e_lon, e_label = resolve_location(params["raw"]["end"])
    params["start_label"], params["end_label"] = s_label, e_label

    places_by_id = {p["place_id"]: p for p in places}
    pts = [(s_lat, s_lon)] + [(p["latitude"], p["longitude"]) for p in places] + [(e_lat, e_lon)]
    matrix, route_warn = routing.build_matrix(pts)
    warnings += route_warn

    hotels = db.query("SELECT * FROM Hotels WHERE category = ?", (params["stay_preference"],)) \
        if params["stay_preference"] != "none" else []
    fsql, fargs = food_query(params["food_preference"])
    foods = db.query(fsql, fargs)

    # Constraint loop: schedule -> cost -> if over budget drop the last non-compulsory place -> repeat
    comp = set(params["compulsory_ids"])
    skip, budget_excluded = set(), []
    while True:
        result = generate_itinerary(places, params, matrix, skip_ids=skip)
        costs = compute_costs(params, result["itinerary_by_day"], places_by_id, hotels, foods)
        if costs["within_budget"]:
            break
        droppable = [it for d in result["itinerary_by_day"] for it in d["items"] if it["place_id"] not in comp]
        if not droppable:
            result.setdefault("conflicts", []).append({
                "place_id": None,
                "message": f"Estimated cost INR {costs['total_estimated']} exceeds the budget of INR {params['budget']} "
                           "even with only compulsory places.",
                "suggestions": ["Increase the budget", "Remove a compulsory place",
                                "Reduce the number of days (accommodation/food)", "Choose a cheaper stay option"]})
            break
        last = droppable[-1]
        skip.add(last["place_id"])
        budget_excluded.append({"place_id": last["place_id"], "place_name": last["place_name"],
                                "reason_code": "budget", "reason": "Budget constraint exceeded."})

    excluded = result["excluded_places"] + budget_excluded
    schedule = result["itinerary_by_day"]
    warnings += result.get("warnings", [])

    # route geometry per day for the map
    route_lines = []
    for d in schedule:
        if d["items"]:
            seq = [pts[0]] + [(places_by_id[i["place_id"]]["latitude"], places_by_id[i["place_id"]]["longitude"])
                              for i in d["items"]] + [pts[-1]]
            geom = routing.route_geometry(seq)
            route_lines.append({"day": d["day"], "geometry": geom,
                                "available": geom is not None})
    if route_lines and not all(r["available"] for r in route_lines):
        warnings.append("Route lines are unavailable for some days (routing service did not respond).")

    scheduled_ids = [i["place_id"] for d in schedule for i in d["items"]]
    scheduled_pts = [(places_by_id[i]["latitude"], places_by_id[i]["longitude"]) for i in scheduled_ids]
    hotel_sql = "SELECT * FROM Hotels" + (" WHERE category = ?" if params["stay_preference"] != "none" else "")
    hotel_args = (params["stay_preference"],) if params["stay_preference"] != "none" else ()
    food_suggestions = _suggestions("FoodPlaces", fsql, fargs, scheduled_pts)
    hotel_suggestions = _suggestions("Hotels", hotel_sql, hotel_args, scheduled_pts)
    resources = db.query(
        f"SELECT r.*, p.place_name FROM TravelResources r JOIN Places p ON p.place_id = r.place_id "
        f"WHERE r.place_id IN ({','.join('?' * len(params['selected_ids']))})", params["selected_ids"])

    trip_id = db.save_trip(params, schedule, comp, params["selected_ids"])
    markers = [{"place_id": p["place_id"], "name": p["place_name"], "lat": p["latitude"], "lng": p["longitude"],
                "scheduled": p["place_id"] in scheduled_ids} for p in places]

    return {
        "success": not result.get("conflicts"),
        "trip_id": trip_id,
        "itinerary_by_day": schedule,
        "travel_legs": [dict(day=d["day"], **{k: i[k] for k in ("from_node", "to_node", "travel_distance_km",
                         "travel_duration_minutes", "travel_source")}) for d in schedule for i in d["items"]],
        "route_lines": route_lines,
        "markers": markers,
        "start": {"label": s_label, "lat": s_lat, "lng": s_lon},
        "end": {"label": e_label, "lat": e_lat, "lng": e_lon},
        "cost_breakdown": costs,
        "excluded_places": excluded,
        "conflicts": result.get("conflicts", []),
        "food_suggestions": food_suggestions,
        "hotel_suggestions": hotel_suggestions,
        "resources": resources,
        "warnings": warnings,
    }


# ---------------------------------------------------------------- routes
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/regions")
def regions():
    return jsonify({"success": True, "regions": db.query("SELECT * FROM Regions ORDER BY region_name")})


@app.get("/api/places")
def places():
    sql, args = "SELECT * FROM Places", []
    rid = request.args.get("region_id", "").strip()
    if rid:
        try:
            ids = [int(x) for x in rid.split(",")]
        except ValueError:
            raise ApiError("'region_id' must be comma-separated integers.")
        sql += f" WHERE region_id IN ({','.join('?' * len(ids))})"
        args = ids
    return jsonify({"success": True, "places": db.query(sql + " ORDER BY place_name", args)})


@app.get("/api/resources")
def resources():
    raw = request.args.get("place_ids", "").strip()
    sql, args = ("SELECT r.*, p.place_name FROM TravelResources r JOIN Places p ON p.place_id = r.place_id"), []
    if raw:
        if not re.fullmatch(r"\d+(,\d+)*", raw):
            raise ApiError("'place_ids' must be comma-separated integers.")
        ids = [int(x) for x in raw.split(",")]
        sql += f" WHERE r.place_id IN ({','.join('?' * len(ids))})"
        args = ids
    return jsonify({"success": True, "resources": db.query(sql, args)})


@app.post("/api/trip")
def create_trip():
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError("Body must be valid JSON.")
    return jsonify(plan_trip(validate_trip(data)))


@app.post("/api/trip/recalculate")
def recalculate():
    """Rebuild the WHOLE itinerary from scratch (never patch the old one).

    Body option A: {"trip_id": 7, "compulsory_places": [1, 4]}  -> reload stored trip, replace compulsory set
    Body option B: a full /api/trip payload with the new compulsory_places
    compulsory_places is the COMPLETE list (previous ones must be included by the caller, or use
    "add_compulsory": [id] to add to the stored set).
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Body must be a JSON object.")
    if "trip_id" in data:
        row = db.query_one("SELECT params_json FROM Trips WHERE trip_id = ?", (data["trip_id"],))
        if not row:
            raise ApiError("Unknown trip_id.", 404)
        base = json.loads(row["params_json"])
        prev = db.query("SELECT place_id FROM TripPlaces WHERE trip_id = ? AND is_compulsory = 1", (data["trip_id"],))
        prev_ids = [r["place_id"] for r in prev]
        if "compulsory_places" in data:
            base["compulsory_places"] = data["compulsory_places"]
        else:
            base["compulsory_places"] = list(dict.fromkeys(prev_ids + list(data.get("add_compulsory", []))))
        # keep selected set; allow overrides of other fields
        for k, v in data.items():
            if k not in ("trip_id", "compulsory_places", "add_compulsory"):
                base[k] = v
        data = base
    elif "add_compulsory" in data:
        raise ApiError("'add_compulsory' needs a 'trip_id'.")
    return jsonify(plan_trip(validate_trip(data)))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
