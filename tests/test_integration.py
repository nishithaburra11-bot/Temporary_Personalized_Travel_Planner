"""Run with python -B tests/test_integration.py [--live]. Live tests only read MySQL."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app as backend

LIVE = "--live" in sys.argv
if LIVE:
    sys.argv.remove("--live")


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = backend.app.test_client()

    def test_syntax(self):
        for path in ROOT.glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"))
        for path in (ROOT / "frontend").glob("*.html"):
            for script in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", path.read_text(encoding="utf-8"), re.S):
                result = subprocess.run(["node", "--check"], input=script, encoding="utf-8", capture_output=True)
                self.assertEqual(result.returncode, 0, f"{path}: {result.stderr}")

    def test_pages_and_assets(self):
        for path in ["/", "/api/health", "/style.css", "/ayan_main.svg"] + ["/" + p.name for p in (ROOT / "frontend").glob("*.html")]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            response.close()
        self.assertEqual(self.client.get("/api/unknown").status_code, 404)

    def test_backend_failure_response(self):
        with patch.object(backend.db, "query", side_effect=RuntimeError("Simulated unavailable database")):
            with self.assertLogs(backend.app.logger, level="ERROR"):
                response = self.client.get("/api/places")
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.get_json()["success"])

    def test_invalid_requests(self):
        for value in [None, [], {}, {"days": float("inf")}, {"days": 1.5}, {"food_preference": []}, {"food_budget": []}]:
            self.assertEqual(self.client.post("/api/trip", json=value).status_code, 400)

    def test_pace_budget_and_duration(self):
        rows = [dict(place_id=i, place_name=f"Test {i}", latitude=25.3, longitude=83.0,
                     opening_time="00:00", closing_time="23:59", visit_duration_minutes=60, entry_fee=100) for i in range(1, 5)]
        trip = dict(days=1, hours_per_day=8, budget=1000, start_coords=[25.3, 83.0],
                    selected_places=[1, 2, 3, 4], compulsory_places=[1], max_stops_per_day=2)
        result = backend.planner_module.generate_itinerary(trip, rows)
        self.assertEqual(len(result["itinerary_by_day"][0]["stops"]), 2)
        self.assertEqual(result["cost_breakdown"]["total"], 200)
        self.assertEqual(len(result["excluded_places"]), 2)
        self.assertIn("pace", result["excluded_places"][0]["reason"])
        self.assertEqual(result["itinerary_by_day"][0]["stops"][0]["visit_duration_minutes"], 60)
        trip.update(days=30, budget=0)
        result = backend.planner_module.generate_itinerary(trip, rows)
        self.assertEqual(len(result["itinerary_by_day"]), 30)
        self.assertFalse(result["all_compulsory_scheduled"])

    def test_nearest_suggestions(self):
        rows = [dict(name="far", latitude=26, longitude=83), dict(name="near", latitude=25.31, longitude=83), dict(name="unknown")]
        self.assertEqual(backend._near(rows, [(25.3, 83)])[0]["name"], "near")
        self.assertEqual(backend._near(rows, []), [])

    @unittest.skipUnless(LIVE, "Pass --live to read the actual database")
    def test_live_database_api_images_and_planning(self):
        def fingerprint():
            return hashlib.sha256(json.dumps(backend.db.query("SELECT * FROM places ORDER BY place_id"), sort_keys=True).encode()).hexdigest()
        before = fingerprint()
        regions = self.client.get("/api/regions").get_json()["regions"]
        self.assertGreaterEqual(len(regions), 2)
        names = [r["region_name"] for r in regions[:2]]
        response = self.client.get("/api/places", query_string=[("region", n) for n in names])
        rows = response.get_json()["places"]
        self.assertEqual({r["region_name"] for r in rows}, set(names))
        all_rows = self.client.get("/api/places").get_json()["places"]
        mapped = [r for r in all_rows if r.get("image_url") and (Path(backend.IMAGES_DIR) / r["image_url"]).is_file()]
        self.assertTrue(mapped)
        for row in mapped:
            response = self.client.get("/api/images/places/" + row["image_url"])
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.content_type.startswith("image/"))
            response.close()
        paid = next(r for r in rows if r["entry_fee"] > 0)
        payload = dict(days=2, hours_per_day=8, budget=10000, start=paid["place_name"], end=paid["place_name"],
                       selected_places=[r["place_id"] for r in rows], compulsory_places=[paid["place_id"]],
                       food_budget="standard", travel_pace="relaxed")
        with patch.object(backend.db, "save_trip", return_value=None), patch("requests.get", side_effect=AssertionError("External network called")):
            response = self.client.post("/api/trip", json=payload)
            self.assertEqual(response.status_code, 200, response.get_json())
            result = response.get_json()
            self.assertGreater(result["cost_breakdown"]["total"], 0)
            self.assertEqual(result["travel_source"], "estimate")
            self.assertTrue(result["all_compulsory_scheduled"])
            self.assertTrue(all(len(d["stops"]) <= 2 for d in result["itinerary_by_day"]))
            self.assertTrue(result["excluded_places"])
            payload["start"] = "Unknown location test"
            self.assertEqual(self.client.post("/api/trip", json=payload).status_code, 400)
        self.assertEqual(fingerprint(), before)
        print(f"Live checks: {len(all_rows)} places, {len(regions)} regions, {len(mapped)} mapped images; places unchanged.")
        print("Image gaps:", [(r["place_id"], r["image_url"]) for r in all_rows if r not in mapped])
        for table in ("hotels", "food_places", "travel_resources"):
            print(table, backend.db.query(f"SELECT COUNT(*) AS records FROM {table}"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
