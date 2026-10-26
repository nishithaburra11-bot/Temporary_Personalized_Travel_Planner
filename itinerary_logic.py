"""
itinerary.py - Varanasi Smart Trip Planner: itinerary optimisation module.

Method (all standard techniques, pure Python, no dependencies):
  1. Cheapest-insertion heuristic  - builds the day-wise routes. Compulsory
     places are inserted first, then the optional selected places. Each
     insertion is the one that adds the LEAST extra distance.
  2. 2-opt local search            - untangles each day's route to cut distance.
  3. Constraint checking           - every candidate route is simulated against
     opening/closing hours, closed days, daily time limit and total budget.
  4. Rule-based exclusion          - every unscheduled place gets a reason.
  5. Full re-planning              - recalculate() always rebuilds from scratch.

Backend usage (Flask):
    from itinerary import generate_itinerary, recalculate
    result = generate_itinerary(trip_dict, places_from_sqlite)
"""
import math
from datetime import date, datetime, timedelta

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def hm(text):
    """'09:30' -> 570 minutes after midnight."""
    h, m = str(text).split(":")[:2]
    return int(h) * 60 + int(m)


def fmt(minutes):
    """570 -> '09:30'."""
    minutes = int(round(minutes))
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def haversine_km(a, b):
    """Straight-line distance between two (lat, lon) points in km."""
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


# --------------------------------------------------------------------------
# Travel-time functions. A travel function takes two (lat, lon) tuples and
# returns (distance_km, minutes), or None if no reliable route exists.
# --------------------------------------------------------------------------

def make_estimate_fn(speed_kmph=25.0, detour=1.3):
    """Offline fallback: straight-line distance x detour factor. ESTIMATED only."""
    def fn(a, b):
        km = haversine_km(a, b) * detour
        return km, km / speed_kmph * 60
    return fn


def collect_points(trip, places):
    """All (lat, lon) points needed for a distance matrix."""
    pts = {tuple(trip["start_coords"]), tuple(trip.get("end_coords", trip["start_coords"]))}
    for p in places:
        try:
            pts.add((float(p["latitude"]), float(p["longitude"])))
        except (KeyError, TypeError, ValueError):
            pass
    return sorted(pts)


def make_osrm_matrix_fn(points, base_url="https://router.project-osrm.org",
                        fallback=None, timeout=20):
    """
    Real road distances/times from OSRM using ONE request to the /table
    endpoint (much kinder to the public server than one call per pair).
    Check OSRM's usage policy before relying on the public demo server.
    """
    import requests
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    r = requests.get(f"{base_url}/table/v1/driving/{coords}",
                     params={"annotations": "duration,distance"}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    durations, distances = data["durations"], data["distances"]
    index = {p: i for i, p in enumerate(points)}

    def fn(a, b):
        i, j = index[a], index[b]
        d, t = distances[i][j], durations[i][j]
        if d is None or t is None:
            return fallback(a, b) if fallback else None
        return d / 1000.0, t / 60.0
    return fn


# --------------------------------------------------------------------------
# Core planner
# --------------------------------------------------------------------------

class Planner:
    def __init__(self, trip, places, travel_fn=None):
        self.validate(trip)
        self.trip = trip
        self.days = int(trip["days"])
        self.day_len = float(trip["hours_per_day"]) * 60
        self.start_min = hm(trip.get("start_time", "09:00"))
        self.break_min = float(trip.get("break_minutes", 10))
        self.budget = float(trip["budget"])
        self.own = trip.get("transport", "own_vehicle") == "own_vehicle"
        self.mileage = float(trip.get("mileage_kmpl", 40))
        self.fuel_price = float(trip.get("fuel_price", 100))
        self.start = tuple(trip["start_coords"])
        self.end = tuple(trip.get("end_coords", trip["start_coords"]))
        self.fixed_cost = (float(trip.get("food_per_day", 0)) * self.days
                           + float(trip.get("hotel_per_night", 0)) * max(self.days - 1, 0))
        self.start_date = self._parse_date(trip.get("start_date"))
        self.travel_fn = travel_fn or make_estimate_fn()
        self.cache = {}

        selected = set(trip.get("selected_places", [])) | set(trip.get("compulsory_places", []))
        self.compulsory = list(dict.fromkeys(trip.get("compulsory_places", [])))
        self.places, self.bad_data = {}, {}
        for raw in places:
            pid = raw["place_id"]
            if selected and pid not in selected:
                continue
            norm = self._normalise(raw)
            if norm["xy"] is None:
                self.bad_data[pid] = norm
            else:
                self.places[pid] = norm

    # ---------- validation / normalisation ----------
    @staticmethod
    def validate(trip):
        for key in ("days", "hours_per_day", "budget", "start_coords"):
            if key not in trip:
                raise ValueError(f"Missing required field: {key}")
        if int(trip["days"]) < 1:
            raise ValueError("days must be at least 1")
        if float(trip["hours_per_day"]) <= 0 or float(trip["hours_per_day"]) > 24:
            raise ValueError("hours_per_day must be between 0 and 24")
        if float(trip["budget"]) < 0:
            raise ValueError("budget cannot be negative")

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        if isinstance(value, date):
            return value
        return datetime.strptime(value, "%Y-%m-%d").date()

    @staticmethod
    def _normalise(p):
        closed = p.get("closed_days") or ""
        if isinstance(closed, str):
            closed = {c.strip().lower() for c in closed.split(",") if c.strip()}
        else:
            closed = {str(c).lower() for c in closed}
        try:
            xy = (float(p["latitude"]), float(p["longitude"]))
        except (KeyError, TypeError, ValueError):
            xy = None
        return {
            "id": p["place_id"], "name": p.get("place_name", f"Place {p['place_id']}"),
            "xy": xy, "closed": closed,
            "open": hm(p.get("opening_time") or "00:00"),
            "close": hm(p.get("closing_time") or "23:59"),
            "dur": int(p.get("visit_duration_minutes") or 60),
            "fee": float(p.get("entry_fee") or 0),
            "fee_verified": bool(p.get("source_checked_date")),
            "priority": float(p.get("priority", 1) or 1),
        }

    def weekday(self, d):
        if self.start_date is None:
            return None
        return (self.start_date + timedelta(days=d)).strftime("%A").lower()

    def leg(self, a, b):
        if a == b:
            return 0.0, 0.0
        if (a, b) not in self.cache:
            self.cache[(a, b)] = self.travel_fn(a, b)
        return self.cache[(a, b)]

    def fuel(self, km):
        return km / self.mileage * self.fuel_price if self.own else 0.0

    # ---------- constraint check: simulate one day ----------
    def sim_day(self, d, pids):
        """Return (day_dict, None) if feasible, else (None, reason_code)."""
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
            stops.append({"pid": pid, "arrive": begin, "leave": finish, "km": km,
                          "travel_min": mins, "from": pos})
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
                "end_time": finish + back[1] if pids else self.start_min}, None

    # ---------- insertion heuristic ----------
    def try_insert(self, pid, routes, sims):
        """Cheapest feasible (day, position) for pid. Returns (best, reasons, overshoot)."""
        total = sum(s["cost"] for s in sims) + self.fixed_cost
        best, reasons, min_over = None, set(), None
        for d in range(self.days):
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
                added = (res["km"] - sims[d]["km"]) / self.places[pid]["priority"]
                if best is None or added < best[0]:
                    best = (added, d, pos, res)
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
        while improved and len(best_route) > 2:
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
        compulsory = [p for p in self.compulsory if p in self.places]
        optional = [p for p in self.places if p not in compulsory]
        self.insert_phase(compulsory, routes, sims)
        self.insert_phase(optional, routes, sims)
        for d in range(self.days):
            routes[d], sims[d] = self.two_opt(d, routes[d], sims[d])
        # After shortening routes there may be room for places that did not fit.
        scheduled = {p for r in routes for p in r}
        leftover = [p for p in compulsory + optional if p not in scheduled]
        self.insert_phase(leftover, routes, sims)
        for d in range(self.days):
            routes[d], sims[d] = self.two_opt(d, routes[d], sims[d])
        return routes, sims

    # ---------- exclusion reasons & conflicts ----------
    REASON_TEXT = {
        "closed": "closed on the trip day(s) available",
        "hours": "cannot be reached within its opening hours alongside the other stops",
        "time": "insufficient remaining time in the available days",
        "budget": "budget constraint exceeded",
        "no_route": "no reliable route information available",
    }

    def explain_excluded(self, routes, sims):
        scheduled = {p for r in routes for p in r}
        excluded, conflicts = [], []
        for pid, bad in self.bad_data.items():
            excluded.append({"place_id": pid, "place_name": bad["name"],
                             "reason": "no reliable coordinates stored for this place"})
        for pid, p in self.places.items():
            if pid in scheduled:
                continue
            _, reasons, over = self.try_insert(pid, routes, sims)
            order = ["closed", "no_route", "hours", "time", "budget"]
            text = "; ".join(self.REASON_TEXT[r] for r in order if r in reasons) \
                or "insufficient remaining time in the available days"
            excluded.append({"place_id": pid, "place_name": p["name"], "reason": text,
                             "compulsory": pid in self.compulsory})
            if pid in self.compulsory:
                conflicts.append(self._suggest(pid, p, reasons, over))
        return excluded, conflicts

    def _suggest(self, pid, p, reasons, over):
        tips = []
        if "time" in reasons or "hours" in reasons:
            tips.append("Increase the number of days or hours per day, or start the day earlier.")
        if "budget" in reasons and over:
            tips.append(f"Increase the budget by about {math.ceil(over)} (estimated).")
        if "closed" in reasons:
            tips.append("Choose trip dates when this place is open.")
        if "no_route" in reasons:
            tips.append("No verified route data: remove it or add route data.")
        tips.append("Or remove another compulsory place that competes for the same time/budget.")
        return {"place_id": pid, "place_name": p["name"],
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
                             "duration_min": round(st["travel_min"]), "cost_status": "estimated"})
                items.append({"place_id": p["id"], "place_name": p["name"],
                              "arrival_time": fmt(st["arrive"]), "departure_time": fmt(st["leave"]),
                              "travel_duration_minutes": round(st["travel_min"]),
                              "estimated_cost": round(p["fee"] + leg_cost, 2)})
                all_verified &= p["fee_verified"]
                pos_name = p["name"]
            if sim["stops"]:
                legs.append({"day": d + 1, "from": pos_name, "to": "End",
                             "distance_km": round(sim["back_km"], 2),
                             "duration_min": round(sim["back_min"]), "cost_status": "estimated"})
            entry_total += sim["fees"]
            fuel_total += self.fuel(sim["km"])
            by_day.append({"day": d + 1, "stops": items, "total_distance_km": round(sim["km"], 2),
                           "day_ends_at": fmt(sim["end_time"])})
        food = float(self.trip.get("food_per_day", 0)) * self.days
        hotel = float(self.trip.get("hotel_per_night", 0)) * max(self.days - 1, 0)
        total = entry_total + fuel_total + food + hotel
        if not self.own:
            warnings.append("Public-transport fares are not included: no verified fare data is loaded.")
        if self.start_date is None:
            warnings.append("No start_date given, so closed days were not checked.")
        warnings.append("Distances/times are estimates unless a road-routing function (OSRM) was supplied.")
        if conflicts:
            warnings.append("Some compulsory places could not be scheduled. See 'conflicts'.")
        return {
            "success": True,
            "all_compulsory_scheduled": not conflicts,
            "compulsory_places": self.compulsory,
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

def generate_itinerary(trip, places, travel_fn=None):
    """trip: dict like the POST /api/trip body plus start_coords.
    places: list of dicts using the Places-table column names."""
    return Planner(trip, places, travel_fn).result()


def recalculate(trip, places, new_compulsory_ids, travel_fn=None):
    """Make places compulsory and rebuild the WHOLE itinerary from scratch.
    Previously compulsory places stay compulsory (union of old + new)."""
    merged = list(dict.fromkeys(list(trip.get("compulsory_places", [])) + list(new_compulsory_ids)))
    return Planner({**trip, "compulsory_places": merged}, places, travel_fn).result()


# --------------------------------------------------------------------------
# Demo / self-test:  python itinerary.py
# NOTE: the place data below is PLACEHOLDER test data (approximate coordinates,
# invented hours/fees). Replace with verified records from the SQLite database.
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    sample = [
        {"place_id": 1, "place_name": "Kashi Vishwanath Temple", "latitude": 25.3109, "longitude": 83.0107,
         "opening_time": "05:00", "closing_time": "21:00", "visit_duration_minutes": 90, "entry_fee": 0},
        {"place_id": 2, "place_name": "Dashashwamedh Ghat", "latitude": 25.3070, "longitude": 83.0104,
         "opening_time": "00:00", "closing_time": "23:59", "visit_duration_minutes": 60, "entry_fee": 0},
        {"place_id": 3, "place_name": "Sarnath", "latitude": 25.3811, "longitude": 83.0240,
         "opening_time": "09:00", "closing_time": "17:00", "visit_duration_minutes": 120, "entry_fee": 25,
         "closed_days": ""},
        {"place_id": 4, "place_name": "Assi Ghat", "latitude": 25.2880, "longitude": 83.0060,
         "opening_time": "00:00", "closing_time": "23:59", "visit_duration_minutes": 45, "entry_fee": 0},
        {"place_id": 5, "place_name": "Ramnagar Fort", "latitude": 25.2690, "longitude": 83.0282,
         "opening_time": "10:00", "closing_time": "17:00", "visit_duration_minutes": 90, "entry_fee": 50},
        {"place_id": 6, "place_name": "BHU Campus", "latitude": 25.2677, "longitude": 82.9913,
         "opening_time": "06:00", "closing_time": "18:00", "visit_duration_minutes": 60, "entry_fee": 0},
    ]
    trip = {"days": 2, "hours_per_day": 8, "budget": 3000, "transport": "own_vehicle",
            "start_coords": (25.3320, 82.9890),   # approx. Varanasi Junction
            "selected_places": [1, 2, 3, 4, 5, 6], "compulsory_places": [3],
            "mileage_kmpl": 40, "fuel_price": 100, "food_per_day": 400, "hotel_per_night": 800,
            "start_date": "2026-11-02"}
    print(json.dumps(generate_itinerary(trip, sample), indent=2))
    print("\n--- recalculate with Ramnagar Fort compulsory and a tiny budget ---")
    tight = {**trip, "budget": 1200}
    out = recalculate(tight, sample, [5])
    print(json.dumps({k: out[k] for k in ("all_compulsory_scheduled", "excluded_places", "conflicts")}, indent=2))
