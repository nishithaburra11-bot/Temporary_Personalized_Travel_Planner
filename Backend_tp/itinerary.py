"""STAND-IN scheduler so the backend runs end to end.

>>> Member 4 replaces the body of generate_itinerary() but KEEPS THE SIGNATURE AND RETURN SHAPE. <<<

Inputs
  places : list of place dicts (DB rows). Node i+1 in `matrix` is places[i].
  params : validated trip params (days, hours_per_day, compulsory_ids, start_date, ...)
  matrix : (n+2)x(n+2); node 0 = start, node n+1 = end. Cell = {"distance_km","duration_min","source"} or None.
  skip_ids : place_ids the backend already excluded (e.g. for budget); do not schedule them.

Returns
  {"itinerary_by_day": [{"day": 1, "items": [...], "return_leg": {...}}],
   "excluded_places": [{"place_id","place_name","reason_code","reason"}],
   "conflicts": [{"place_id","place_name","message","suggestions":[...]}],
   "warnings": [str]}
"""
from datetime import date, timedelta

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _mins(hhmm, default):
    if not hhmm:
        return default
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _fmt(t):
    t = int(round(t))
    return f"{t // 60:02d}:{t % 60:02d}"


def generate_itinerary(places, params, matrix, skip_ids=()):
    n = len(places)
    end_node = n + 1
    comp = set(params.get("compulsory_ids", []))
    warnings = []
    day_start = params.get("day_start_minute", 9 * 60)
    break_min = params.get("break_minutes", 60)
    deadline_len = params["hours_per_day"] * 60 - break_min
    start_date = params.get("start_date")
    if not start_date:
        warnings.append("No start_date given: closed-day rules were not checked.")
    if any(not p.get("opening_time") or not p.get("closing_time") for p in places):
        warnings.append("Some places have no verified opening hours; they were treated as open all day.")

    remaining = {i + 1: p for i, p in enumerate(places) if p["place_id"] not in skip_ids}
    excluded, days_out = [], []
    reasons = {}

    for d in range(params["days"]):
        weekday = None
        if start_date:
            weekday = WEEKDAYS[(date.fromisoformat(start_date) + timedelta(days=d)).weekday()]
        cur, t, items = 0, day_start, []
        deadline = day_start + deadline_len
        while True:
            best = None
            for node, p in remaining.items():
                leg = matrix[cur][node]
                back = matrix[node][end_node]
                if leg is None or back is None:
                    reasons[node] = ("no_route", "No reliable route information available.")
                    continue
                if weekday and weekday in (p.get("closed_days") or ""):
                    reasons.setdefault(node, ("closed", f"Closed on {weekday}."))
                    continue
                arrive = t + leg["duration_min"]
                opens, closes = _mins(p.get("opening_time"), 0), _mins(p.get("closing_time"), 24 * 60)
                arrive = max(arrive, opens)
                dep = arrive + (p.get("visit_duration_minutes") or 60)
                if dep > closes:
                    reasons[node] = ("closed", "Cannot be visited within its opening hours in the available window.")
                    continue
                if dep + back["duration_min"] > deadline:
                    reasons[node] = ("insufficient_time", "Not enough remaining time in the available hours.")
                    continue
                key = (node not in {i + 1 for i, q in enumerate(places) if q["place_id"] in comp}, leg["duration_min"])
                if best is None or key < best[0]:
                    best = (key, node, leg, arrive, dep)
            if best is None:
                break
            _, node, leg, arrive, dep = best
            p = remaining.pop(node)
            reasons.pop(node, None)
            items.append({"place_id": p["place_id"], "place_name": p["place_name"],
                          "arrival_time": _fmt(arrive), "departure_time": _fmt(dep),
                          "visit_duration_minutes": p.get("visit_duration_minutes") or 60,
                          "travel_duration_minutes": leg["duration_min"],
                          "travel_distance_km": leg["distance_km"],
                          "travel_source": leg["source"],
                          "from_node": cur, "to_node": node})
            t, cur = dep, node
        ret = matrix[cur][end_node]
        days_out.append({"day": d + 1, "items": items,
                         "return_leg": {"distance_km": ret["distance_km"], "duration_min": ret["duration_min"],
                                        "source": ret["source"], "from_node": cur, "to_node": end_node} if ret and items else None})

    conflicts = []
    for node, p in remaining.items():
        code, msg = reasons.get(node, ("insufficient_time", "Not enough remaining time in the available hours."))
        excluded.append({"place_id": p["place_id"], "place_name": p["place_name"],
                         "reason_code": code, "reason": msg})
        if p["place_id"] in comp:
            conflicts.append({"place_id": p["place_id"], "place_name": p["place_name"],
                              "message": f"Compulsory place '{p['place_name']}' could not be scheduled: {msg}",
                              "suggestions": ["Increase the number of days", "Increase hours per day",
                                              "Remove another compulsory place", "Change the start/end point"]})
    return {"itinerary_by_day": days_out, "excluded_places": excluded,
            "conflicts": conflicts, "warnings": warnings}
