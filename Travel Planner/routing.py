"""Road distance/time via the public OSRM demo server, with a clearly-labelled fallback.

Every matrix cell carries a 'source': 'osrm' (real road data) or 'estimated'
(straight-line x 1.3 at 25 km/h) so the UI can label it honestly.
The public OSRM server has usage limits; check its terms before heavy use.
"""
import math
import requests

OSRM_URL = "https://router.project-osrm.org"
TIMEOUT = 8
ROAD_FACTOR = 1.3
FALLBACK_SPEED_KMH = 25.0


def haversine_km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def _fallback(points):
    n = len(points)
    m = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                m[i][j] = {"distance_km": 0.0, "duration_min": 0.0, "source": "estimated"}
            else:
                d = haversine_km(points[i], points[j]) * ROAD_FACTOR
                m[i][j] = {"distance_km": round(d, 2),
                           "duration_min": round(d / FALLBACK_SPEED_KMH * 60, 1),
                           "source": "estimated"}
    return m


def build_matrix(points):
    """points: list of (lat, lon). Returns (matrix, warnings)."""
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    try:
        r = requests.get(f"{OSRM_URL}/table/v1/driving/{coords}",
                         params={"annotations": "distance,duration"}, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != "Ok":
            raise ValueError(data.get("message", "OSRM error"))
        n = len(points)
        m = [[None] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                dist, dur = data["distances"][i][j], data["durations"][i][j]
                if dist is None or dur is None:
                    m[i][j] = None  # no reliable route
                else:
                    m[i][j] = {"distance_km": round(dist / 1000, 2),
                               "duration_min": round(dur / 60, 1), "source": "osrm"}
        return m, []
    except Exception as exc:  # network down, rate limit, bad response...
        return _fallback(points), [
            f"Road-routing service unavailable ({type(exc).__name__}). Distances and times are "
            "straight-line ESTIMATES, not real road data."]


def route_geometry(points):
    """GeoJSON LineString coordinates for an ordered list of (lat, lon); None on failure."""
    if len(points) < 2:
        return None
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    try:
        r = requests.get(f"{OSRM_URL}/route/v1/driving/{coords}",
                         params={"overview": "full", "geometries": "geojson"}, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != "Ok":
            return None
        return data["routes"][0]["geometry"]["coordinates"]  # [[lon, lat], ...]
    except Exception:
        return None
