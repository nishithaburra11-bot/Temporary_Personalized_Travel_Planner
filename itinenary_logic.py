"""
itinerary.py - Varanasi Smart Trip Planner: itinerary optimisation module (v2).

Method (standard techniques, pure Python; `requests` is needed only for OSRM):
  1. Cheapest-insertion heuristic  - builds the day-wise routes. Compulsory
     places are inserted first, then the optional selected places. Each
     insertion is the one that adds the LEAST extra distance (divided by the
     place's priority).
  2. 2-opt local search            - untangles each day's route to cut distance.
  3. Constraint checking           - every candidate route is simulated against
     opening/closing hours, closed days, the daily time limit and the budget.
  4. Rule-based exclusion          - every unscheduled place gets a reason.
  5. Full re-planning              - recalculate() always rebuilds from scratch.
  6. Optional OSRM road distances  - one /table request, automatic fallback to
     straight-line estimates if OSRM is unreachable.
  7. Optional road geometry        - real road lines (per day) for the map.

IMPORTANT: this is a heuristic planner. It gives a good route, not a proven
optimum, and it is only as accurate as the data and travel times it is given.
Verify opening hours, fees and travel times before relying on a plan.

Backend usage (Flask):
    from itinerary import generate_itinerary, recalculate
    result = generate_itinerary(trip, places, use_osrm=True, include_geometry=True)

trip (dict) - required: days, hours_per_day, budget, start_coords=(lat, lon)
              optional: end_coords, start_time ("09:00"), break_minutes (10),
              transport ("own_vehicle" | "public_transport"), mileage_kmpl (40),
              fuel_price (100), food_per_day, hotel_per_night, start_date
              ("YYYY-MM-DD"), selected_places [ids], compulsory_places [ids],
              travel_time_factor (1.0; use 1.2-1.5 to leave slack for traffic)
              If selected_places is empty/missing, ALL given places are considered.
places (list of dict) - Places-table columns: place_id, place_name, latitude,
              longitude, opening_time, closing_time, closed_days,
              visit_duration_minutes, entry_fee, priority, source_checked_date
"""
import math
import re
from datetime import date, datetime, timedelta

DEFAULT_OSRM_URL = "https://router.project-osrm.org"
USER_AGENT = "varanasi-trip-planner/2.0"
MAX_DAYS = 30

DAY_NAMES = {"mon": "monday", "tue": "tuesday", "wed": "wednesday",
             "thu": "thursday", "fri": "friday", "sat": "saturday", "sun": "sunday"}

TRANSPORT_ALIASES = {
    "own_vehicle": "own_vehicle", "own": "own_vehicle", "car": "own_vehicle",
    "bike": "own_vehicle", "scooter": "own_vehicle", "motorcycle": "own_vehicle",
    "public_transport": "public_transport", "public": "public_transport",
    "bus": "public_transport", "train": "public_transport", "metro": "public_transport",
}

_TIME_RE = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?(?::\d{2})?\s*([AaPp][Mm])?\s*$")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def hm(text):
    """'09:30' / '9:30 AM' / '21:00:00' -> minutes after midnight. Raises ValueError."""
    m = _TIME_RE.match(str(text))
    if not m:
        raise ValueError(f"Invalid time '{text}' (use HH:MM, 24-hour)")
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if ap:
        if not 1 <= h <= 12:
            raise ValueError(f"Invalid time '{text}'")
        h = h % 12 + (12 if ap.lower() == "pm" else 0)
    if h > 24 or mi > 59 or (h == 24 and mi):
        raise ValueError(f"Invalid time '{text}'")
    return h * 60 + mi


def fmt(minutes):
    """570 -> '09:30'; values past midnight show '(+1d)'."""
    minutes = int(round(minutes))
    days, minutes = divmod(minutes, 1440)
    s = f"{minutes // 60:02d}:{minutes % 60:02d}"
    return s + (f" (+{days}d)" if days else "")


def haversine_km(a, b):
    """Straight-line distance between two (lat, lon) points in km."""
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def _key(pid):
    """Normalise ids so 1, 1.0 and '1' are the same place."""
    if isinstance(pid, float) and pid.is_integer():
        pid = int(pid)
    return str(pid).strip()


def _to_float(value, default=0.0):
    if value is None or value == "":
        return default
    try:
        return float(str(value).replace(",", "").replace("\u20b9", "").strip())
    except ValueError:
        return default


def _num(trip, key, default, minimum=0.0):
    value = trip.get(key)
    if value is None or value == "":
        return float(default)
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be a number")
    if math.isnan(v) or v < minimum:
        raise ValueError(f"{key} must be at least {minimum}")
    return v


def _coords(value, name):
    try:
        lat, lon = float(value[0]), float(value[1])
    except (TypeError, ValueError, IndexError, KeyError):
        raise ValueError(f"{name} must be a (latitude, longitude) pair")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f"{name} is outside valid latitude/longitude ranges")
    return lat, lon


def _transport(value):
    raw = str(value or "own_vehicle").strip().lower().replace(" ", "_").replace("-", "_")
    if raw not in TRANSPORT_ALIASES:
        raise ValueError(f"Unknown transport '{value}'. Use 'own_vehicle' or 'public_transport'.")
    return TRANSPORT_ALIASES[raw]


def _parse_closed(value):
    if not value:
        return set()
    items = value.split(",") if isinstance(value, str) else value
    out = set()
    for c in items:
        c = str(c).strip().lower()
        if c:
            out.add(DAY_NAMES.get(c[:3], c))
    return out


# --------------------------------------------------------------------------
# Travel-time functions. A travel function takes two (lat, lon) tuples and
# returns (distance_km, minutes), or None if no reliable route exists.
# They carry a `.source` attribute ("estimate" / "osrm") used for warnings.
# --------------------------------------------------------------------------

def make_estimate_fn(speed_kmph=25.0, detour=1.3):
    """Offline fallback: straight-line distance x detour factor. ESTIMATED only."""
    def fn(a, b):
        km = haversine_km(a, b) * detour
        return km, km / speed_kmph * 60
    fn.source = "estimate"
    return fn


def collect_points(trip, places):
    """All (lat, lon) points needed for a distance matrix."""
    start = _coords(trip["start_coords"], "start_coords")
    end = _coords(trip.get("end_coords") or trip["start_coords"], "end_coords")
    pts = {start, end}
    for p in places:
        try:
            pts.add((float(p["latitude"]), float(p["longitude"])))
        except (KeyError, TypeError, ValueError):
            pass
    return sorted(pts)


def make_osrm_matrix_fn(points, base_url=DEFAULT_OSRM_URL, fallback=None,
                        timeout=15, max_points=100):
    """
    Real road distances/times from OSRM using ONE request to /table.
    NOTE: the public demo server is for light use only and covers driving only;
    for production, host your own OSRM. Raises on any failure (use
    build_travel_fn() for automatic fallback).
    """
    import requests
    if len(points) > max_points:
        raise ValueError(f"{len(points)} points exceed the OSRM table limit ({max_points})")
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
    r = requests.get(f"{base_url}/table/v1/driving/{coords}",
                     params={"annotations": "duration,distance"},
                     headers={"User-Agent": USER_AGENT}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM error: {data.get('code')} {data.get('message', '')}".strip())
    durations, distances = data["durations"], data["distances"]
    index = {p: i for i, p in enumerate(points)}
    stats = {"fallback_legs": 0}

    def fn(a, b):
        i, j = index.get(a), index.get(b)
        d = t = None
        if i is not None and j is not None:
            d, t = distances[i][j], durations[i][j]
        if d is None or t is None:
            stats["fallback_legs"] += 1
            return fallback(a, b) if fallback else None
        return d / 1000.0, t / 60.0
    fn.source = "osrm"
    fn.stats = stats
    return fn


def build_travel_fn(trip, places, use_osrm=False, osrm_url=DEFAULT_OSRM_URL, timeout=15):
    """OSRM if requested and reachable, otherwise the estimate function."""
    estimate = make_estimate_fn()
    if not use_osrm:
        return estimate
    try:
        return make_osrm_matrix_fn(collect_points(trip, places), base_url=osrm_url,
                                   fallback=estimate, timeout=timeout)
    except Exception as exc:          # no internet, timeout, bad response, too many points...
        estimate.osrm_error = f"{type(exc).__name__}: {exc}"
        return estimate


def fetch_route_geometry(points, base_url=DEFAULT_OSRM_URL, timeout=15):
    """Road-following line through `points` in order, as [[lat, lon], ...]. Raises on failure."""
    import requests
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
    r = requests.get(f"{base_url}/route/v1/driving/{coords}",
                     params={"overview": "full", "geometries": "geojson"},
                     headers={"User-Agent": USER_AGENT}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError(f"OSRM route error: {data.get('code')}")
    return [[lat, lon] for lon, lat in data["routes"][0]["geometry"]["coordinates"]]


def add_route_geometry(result, base_url=DEFAULT_OSRM_URL, timeout=15, fetch_fn=None):
    """
    Adds to every day: route_geometry ([[lat, lon], ...] for Leaflet's L.polyline)
    and route_geometry_status ("road_network" | "straight_line_fallback" | "no_stops").
    """
    fetch = fetch_fn or (lambda pts: fetch_route_geometry(pts, base_url, timeout))
    start, end = tuple(result["start_coords"]), tuple(result["end_coords"])
    for day in result["itinerary_by_day"]:
        if not day["stops"]:
            day["route_geometry"], day["route_geometry_status"] = [], "no_stops"
            continue
        pts = [start] + [(s["latitude"], s["longitude"]) for s in day["stops"]] + [end]
        try:
            day["route_geometry"] = fetch(pts)
            day["route_geometry_status"] = "road_network"
        except Exception as exc:
            day["route_geometry"] = [[la, lo] for la, lo in pts]
            day["route_geometry_status"] = "straight_line_fallback"
            result["warnings"].append(
                f"Day {day['day']}: road geometry unavailable ({type(exc).__name__}); "
                "straight lines are shown instead of roads.")
    return result


# --------------------------------------------------------------------------
# Core planner
# --------------------------------------------------------------------------

class Planner:
    REASON_TEXT = {
        "closed": "closed on all the trip day(s)",
        "hours": "cannot be reached within its opening hours alongside the other stops",
        "time": "insufficient remaining time in the available days",
        "budget": "budget constraint exceeded",
        "no_route": "no reliable route information available",
    }

    def __init__(self, trip, places, travel_fn=None):
        self.validate(trip)
        self.trip = trip
        self.days = int(trip["days"])
        self.day_len = float(trip["hours_per_day"]) * 60
        self.start_min = hm(trip.get("start_time") or "09:00")
        self.break_min = _num(trip, "break_minutes", 10)
        self.budget = float(trip["budget"])
        self.transport = _transport(trip.get("transport"))
        self.own = self.transport == "own_vehicle"
        self.mileage = _num(trip, "mileage_kmpl", 40, minimum=0.1)
        self.fuel_price = _num(trip, "fuel_price", 100)
        self.time_factor = _num(trip, "travel_time_factor", 1.0, minimum=0.5)
        self.start = _coords(trip["start_coords"], "start_coords")
        self.end = _coords(trip.get("end_coords") or trip["start_coords"], "end_coords")
        self.fixed_cost = (_num(trip, "food_per_day", 0) * self.days
                           + _num(trip, "hotel_per_night", 0) * max(self.days - 1, 0))
        self.start_date = self._parse_date(trip.get("start_date"))
        self.travel_fn = travel_fn or make_estimate_fn()
        self.source = getattr(self.travel_fn, "source", "custom")
        self.cache = {}

        self.compulsory = list(dict.fromkeys(_key(x) for x in (trip.get("compulsory_places") or [])))
        selected = {_key(x) for x in (trip.get("selected_places") or [])}
        self.select_all = not selected
        selected |= set(self.compulsory)

        self.places, self.bad_data, self.skipped_records = {}, {}, 0
        for raw in places:
            if raw.get("place_id") in (None, ""):
                self.skipped_records += 1
                continue
            pid = _key(raw["place_id"])
            if not self.select_all and pid not in selected:
                continue
            norm, problem = self._normalise(raw)
            if problem:
                norm["problem"] = problem
                self.bad_data[pid] = norm
            else:
                self.places[pid] = norm

    # ---------- validation / normalisation ----------
    @staticmethod
    def validate(trip):
        for key in ("days", "hours_per_day", "budget", "start_coords"):
            if trip.get(key) is None:
                raise ValueError(f"Missing required field: {key}")
        try:
            days = int(trip["days"])
            hours = float(trip["hours_per_day"])
            budget = float(trip["budget"])
        except (TypeError, ValueError):
            raise ValueError("days, hours_per_day and budget must be numbers")
        if not 1 <= days <= MAX_DAYS:
            raise ValueError(f"days must be between 1 and {MAX_DAYS}")
        if not 0 < hours <= 24:
            raise ValueError("hours_per_day must be greater than 0 and at most 24")
        if math.isnan(budget) or budget < 0:
            raise ValueError("budget cannot be negative")
        _coords(trip["start_coords"], "start_coords")
        if trip.get("end_coords"):
            _coords(trip["end_coords"], "end_coords")
        _transport(trip.get("transport"))
        _num(trip, "mileage_kmpl", 40, minimum=0.1)
        _num(trip, "fuel_price", 100)
        _num(trip, "food_per_day", 0)
        _num(trip, "hotel_per_night", 0)
        _num(trip, "break_minutes", 10)
        _num(trip, "travel_time_factor", 1.0, minimum=0.5)
        hm(trip.get("start_time") or "09:00")
        Planner._parse_date(trip.get("start_date"))

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("start_date must look like 2026-11-02 (YYYY-MM-DD)")

    @staticmethod
    def _normalise(p):
        """Returns (normalised dict, problem text or None)."""
        problem = None
        try:
            xy = (float(p["latitude"]), float(p["longitude"]))
            if not (-90 <= xy[0] <= 90 and -180 <= xy[1] <= 180):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            xy = None
            problem = "no reliable coordinates stored for this place"
        try:
            opening = hm(p.get("opening_time") or "00:00")
            closing = hm(p.get("closing_time") or "23:59")
        except ValueError:
            opening, closing = 0, 1439
            problem = problem or "opening/closing time is not in a valid format"
        if closing == opening:                 # same time both ends: treat as open all day
            opening, closing = 0, 1440
        elif closing < opening:                # open past midnight, e.g. 18:00-02:00
            closing += 1440
        dur = int(_to_float(p.get("visit_duration_minutes"), 60))
        priority = _to_float(p.get("priority"), 1.0)
        entry = p.get("entry_fee")
        return {
            "id": p["place_id"], "name": p.get("place_name") or f"Place {p['place_id']}",
            "xy": xy, "closed": _parse_closed(p.get("closed_days")),
            "open": opening, "close": closing,
            "dur": dur if dur > 0 else 60,
            "fee": max(_to_float(entry, 0.0), 0.0),
            "fee_verified": bool(p.get("source_checked_date")) and entry not in (None, ""),
            "priority": priority if priority > 0 else 1.0,
        }, problem

    def _orig(self, pid):
        if pid in self.places:
            return self.places[pid]["id"]
        if pid in self.bad_data:
            return self.bad_data[pid]["id"]
        return pid

    def weekday(self, d):
        if self.start_date is None:
            return None
        return (self.start_date + timedelta(days=d)).strftime("%A").lower()

    def leg(self, a, b):
        if a == b:
            return 0.0, 0.0
        if (a, b) not in self.cache:
            res = self.travel_fn(a, b)
            if res is not None:
                res = (res[0], res[1] * self.time_factor)
            self.cache[(a, b)] = res
        return self.cache[(a, b)]

    def fuel(self, km):
        return km / self.mileage * self.fuel_price if self.own else 0.0

    # ---------- constraint check: simulate one day ----------
    def sim_day(self, d, pids):
        """Return (day_dict, None) if feasible, else (None, reason_code)."""
        if not pids:
            return {"stops": [], "km": 0.0, "fees": 0.0, "cost": 0.0, "back_km": 0.0,
                    "back_min": 0.0, "end_time": self.start_min}, None
        weekday = self.weekday(d)
        limit = self.start_min + self.day_len
        pos, now, finish = self.start, self.start_min, self.start_min
        stops, km_total, fees = [], 0.0, 0.0
        for pid in pids:
            p = self.places[pid]
            if weekday and weekday in p["closed"]:
                return None, "closed"
            leg = self.leg(pos, p["xy"])
            if leg is None:
                return None, "no_route"
            km, mins = leg
            arrive = now + mins
            begin = max(arrive, p["open"])
            finish = begin + p["dur"]
            if finish > p["close"]:
                return None, "hours"
            if finish > limit:
                return None, "time"
            stops.append({"pid": pid, "arrive": arrive, "begin": begin, "leave": finish,
                          "wait": begin - arrive, "km": km, "travel_min": mins})
            km_total += km
            fees += p["fee"]
            now, pos = finish + self.break_min, p["xy"]
        back = self.leg(pos, self.end)
        if back is None:
            return None, "no_route"
        if finish + back[1] > limit:
            return None, "time"
        km_total += back[0]
        return {"stops": stops, "km": km_total, "fees": fees,
                "cost": fees + self.fuel(km_total),
                "back_km": back[0], "back_min": back[1],
                "end_time": finish + back[1]}, None

    # ---------- insertion heuristic ----------
    def try_insert(self, pid, routes, sims):
        """Cheapest feasible (day, position) for pid. Returns (best, reasons, min_overshoot)."""
        p = self.places[pid]
        total = sum(s["cost"] for s in sims) + self.fixed_cost
        best, reasons, min_over, closed_days = None, set(), None, 0
        for d in range(self.days):
            wd = self.weekday(d)
            if wd and wd in p["closed"]:
                closed_days += 1
                continue
            for pos in range(len(routes[d]) + 1):
                cand = routes[d][:pos] + [pid] + routes[d][pos:]
                res, why = self.sim_day(d, cand)
                if res is None:
                    reasons.add(why)
                    continue
                new_total = total - sims[d]["cost"] + res["cost"]
                if new_total > self.budget + 1e-9:
                    reasons.add("budget")
                    over = new_total - self.budget
                    min_over = over if min_over is None else min(min_over, over)
                    continue
                added = (res["km"] - sims[d]["km"]) / p["priority"]
                if best is None or added < best[0]:
                    best = (added, d, pos, res)
        if closed_days == self.days:          # only report "closed" if closed on EVERY day
            reasons = {"closed"}
        return best, reasons, min_over

    def insert_phase(self, pending, routes, sims):
        pending = list(pending)
        while pending:
            options = []
            for pid in pending:
                best, _, _ = self.try_insert(pid, routes, sims)
                if best:
                    options.append((best[0], pid, best))
            if not options:
                break
            _, pid, (added, d, pos, res) = min(options, key=lambda o: o[0])
            routes[d].insert(pos, pid)
            sims[d] = res
            pending.remove(pid)

    # ---------- 2-opt improvement ----------
    def two_opt(self, d, route, sim):
        best_route, best_sim = route, sim
        improved = True
        while improved and len(best_route) > 1:
            improved = False
            for i in range(len(best_route) - 1):
                for j in range(i + 1, len(best_route)):
                    cand = best_route[:i] + best_route[i:j + 1][::-1] + best_route[j + 1:]
                    res, _ = self.sim_day(d, cand)
                    if res and res["km"] < best_sim["km"] - 1e-9:
                        best_route, best_sim, improved = cand, res, True
        return best_route, best_sim

    # ---------- main ----------
    def build(self):
        routes = [[] for _ in range(self.days)]
        sims = [self.sim_day(d, [])[0] for d in range(self.days)]
        comp_set = set(self.compulsory)
        compulsory = [p for p in self.compulsory if p in self.places]
        optional = [p for p in self.places if p not in comp_set]
        self.insert_phase(compulsory, routes, sims)
        self.insert_phase(optional, routes, sims)
        for d in range(self.days):
            routes[d], sims[d] = self.two_opt(d, routes[d], sims[d])
        # Shorter routes may have freed room: retry leftovers, compulsory FIRST.
        for group in (compulsory, optional):
            scheduled = {p for r in routes for p in r}
            self.insert_phase([p for p in group if p not in scheduled], routes, sims)
        for d in range(self.days):
            routes[d], sims[d] = self.two_opt(d, routes[d], sims[d])
        return routes, sims

    # ---------- exclusion reasons & conflicts ----------
    def explain_excluded(self, routes, sims):
        scheduled = {p for r in routes for p in r}
        comp = set(self.compulsory)
        excluded, conflicts = [], []

        def record(pid, name, orig_id, reason, reasons, tips):
            excluded.append({"place_id": orig_id, "place_name": name, "reason": reason,
                             "compulsory": pid in comp})
            if pid in comp:
                conflicts.append({"place_id": orig_id, "place_name": name,
                                  "reasons": reasons, "suggestions": tips})

        for pid, bad in self.bad_data.items():
            record(pid, bad["name"], bad["id"], bad["problem"], [bad["problem"]],
                   ["Fix this place's record in the database, or remove it from the compulsory places."])
        for pid in self.compulsory:
            if pid not in self.places and pid not in self.bad_data:
                msg = "place id not found in the places list"
                record(pid, f"Place {pid}", pid, msg, [msg],
                       ["Check the place id, or remove it from the compulsory places."])

        order = ["closed", "no_route", "hours", "time", "budget"]
        for pid, p in self.places.items():
            if pid in scheduled:
                continue
            _, reasons, over = self.try_insert(pid, routes, sims)
            if not reasons:
                reasons = {"time"}
            text = "; ".join(self.REASON_TEXT[r] for r in order if r in reasons)
            excluded.append({"place_id": p["id"], "place_name": p["name"], "reason": text,
                             "compulsory": pid in comp})
            if pid in comp:
                conflicts.append(self._suggest(p, reasons, over))
        return excluded, conflicts

    def _suggest(self, p, reasons, over):
        tips = []
        if "time" in reasons or "hours" in reasons:
            tips.append("Increase the number of days or hours per day, or start the day earlier.")
        if "budget" in reasons and over:
            tips.append(f"Increase the budget by about {math.ceil(over)} (estimated).")
        if "closed" in reasons:
            closed = ", ".join(sorted(p["closed"])) or "the trip days"
            tips.append(f"Choose trip dates when this place is open (closed: {closed}).")
        if "no_route" in reasons:
            tips.append("No verified route data: remove it or add route data.")
        tips.append("Or remove another compulsory place that competes for the same time/budget.")
        return {"place_id": p["id"], "place_name": p["name"],
                "reasons": [self.REASON_TEXT[r] for r in sorted(reasons)], "suggestions": tips}

    # ---------- assemble JSON-friendly result ----------
    def result(self):
        routes, sims = self.build()
        excluded, conflicts = self.explain_excluded(routes, sims)
        by_day, legs, warnings = [], [], []
        entry_total = fuel_total = 0.0
        all_verified = True
        for d in range(self.days):
            sim, items = sims[d], []
            pos_name = "Start"
            for st in sim["stops"]:
                p = self.places[st["pid"]]
                leg_cost = self.fuel(st["km"])
                legs.append({"day": d + 1, "from": pos_name, "to": p["name"],
                             "distance_km": round(st["km"], 2),
                             "duration_min": round(st["travel_min"]),
                             "distance_source": self.source, "cost_status": "estimated"})
                items.append({"place_id": p["id"], "place_name": p["name"],
                              "latitude": p["xy"][0], "longitude": p["xy"][1],
                              "arrival_time": fmt(st["arrive"]),
                              "visit_start_time": fmt(st["begin"]),
                              "departure_time": fmt(st["leave"]),
                              "wait_minutes": round(st["wait"]),
                              "travel_duration_minutes": round(st["travel_min"]),
                              "entry_fee": round(p["fee"], 2),
                              "estimated_cost": round(p["fee"] + leg_cost, 2)})
                all_verified = all_verified and p["fee_verified"]
                pos_name = p["name"]
            if sim["stops"]:
                legs.append({"day": d + 1, "from": pos_name, "to": "End",
                             "distance_km": round(sim["back_km"], 2),
                             "duration_min": round(sim["back_min"]),
                             "distance_source": self.source, "cost_status": "estimated"})
            entry_total += sim["fees"]
            fuel_total += self.fuel(sim["km"])
            by_day.append({"day": d + 1, "stops": items,
                           "total_distance_km": round(sim["km"], 2),
                           "day_ends_at": fmt(sim["end_time"])})
        food = _num(self.trip, "food_per_day", 0) * self.days
        hotel = _num(self.trip, "hotel_per_night", 0) * max(self.days - 1, 0)
        total = entry_total + fuel_total + food + hotel

        if not self.own:
            warnings.append("Public-transport fares are not included: no verified fare data is loaded.")
        if self.start_date is None:
            warnings.append("No start_date given, so closed days were not checked.")
        if self.source == "estimate":
            warnings.append("Distances/times are straight-line estimates, not real road data.")
        if getattr(self.travel_fn, "osrm_error", None):
            warnings.append(f"OSRM road routing was unavailable ({self.travel_fn.osrm_error}); "
                            "estimates were used instead.")
        fallback_legs = getattr(getattr(self.travel_fn, "stats", None), "get", lambda *_: 0)("fallback_legs", 0)
        if fallback_legs:
            warnings.append(f"{fallback_legs} leg(s) had no OSRM data and used estimates.")
        if self.time_factor != 1.0:
            warnings.append(f"Travel times were multiplied by {self.time_factor} to allow for traffic.")
        if self.select_all:
            warnings.append("No places were selected, so every available place was considered.")
        if self.skipped_records:
            warnings.append(f"{self.skipped_records} place record(s) without a place_id were ignored.")
        if self.fixed_cost > self.budget:
            warnings.append(f"Food and accommodation alone ({round(self.fixed_cost)}) exceed the "
                            f"budget ({round(self.budget)}); no places can be added.")
        if conflicts:
            warnings.append("Some compulsory places could not be scheduled. See 'conflicts'.")
        warnings.append("Verify opening hours, fees and travel times before travelling; "
                        "this plan is a heuristic, not a guaranteed optimum.")
        return {
            "success": True,
            "all_compulsory_scheduled": not conflicts,
            "compulsory_places": [self._orig(k) for k in self.compulsory],
            "start_coords": list(self.start),
            "end_coords": list(self.end),
            "travel_source": self.source,
            "itinerary_by_day": by_day,
            "travel_legs": legs,
            "total_distance_km": round(sum(s["km"] for s in sims), 2),
            "cost_breakdown": {
                "entry_fees": {"amount": round(entry_total, 2),
                               "status": "verified" if all_verified else "estimated"},
                "fuel": {"amount": round(fuel_total, 2), "status": "estimated"},
                "food": {"amount": round(food, 2), "status": "estimated"},
                "accommodation": {"amount": round(hotel, 2), "status": "estimated"},
                "total": round(total, 2), "budget": self.budget,
                "remaining": round(self.budget - total, 2),
            },
            "excluded_places": excluded,
            "conflicts": conflicts,
            "warnings": warnings,
        }


# --------------------------------------------------------------------------
# Public API for the Flask backend
# --------------------------------------------------------------------------

def generate_itinerary(trip, places, travel_fn=None, use_osrm=False,
                       include_geometry=False, osrm_url=DEFAULT_OSRM_URL):
    """
    trip: dict like the POST /api/trip body plus start_coords.
    places: list of dicts using the Places-table column names.
    use_osrm: fetch real road distances (falls back to estimates on failure).
    include_geometry: add road-following map lines per day (needs internet).
    Raises ValueError for invalid trip input (return it to the client as HTTP 400).
    """
    Planner.validate(trip)
    if travel_fn is None:
        travel_fn = build_travel_fn(trip, places, use_osrm=use_osrm, osrm_url=osrm_url)
    result = Planner(trip, places, travel_fn).result()
    if include_geometry:
        add_route_geometry(result, base_url=osrm_url)
    return result


def recalculate(trip, places, new_compulsory_ids, travel_fn=None, use_osrm=False,
                include_geometry=False, osrm_url=DEFAULT_OSRM_URL):
    """Make places compulsory and rebuild the WHOLE itinerary from scratch.
    Previously compulsory places stay compulsory (union of old + new)."""
    merged = list(dict.fromkeys(_key(x) for x in
                                list(trip.get("compulsory_places") or []) + list(new_compulsory_ids or [])))
    return generate_itinerary({**trip, "compulsory_places": merged}, places, travel_fn,
                              use_osrm, include_geometry, osrm_url)


