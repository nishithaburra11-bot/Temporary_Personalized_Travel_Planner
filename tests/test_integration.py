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

    def test_affordable_combinations_prioritize_stop_count_then_budget(self):
        rows = [dict(place_id=i, latitude=25.3, longitude=83.0, entry_fee=fee)
                for i, fee in enumerate((800, 350, 300, 300, 360), 1)]
        trip = dict(days=1, hours_per_day=8, budget=1000, start_coords=[25.3, 83.0],
                    selected_places=[1, 2, 3, 4, 5], max_stops_per_day=3)

        result = backend.planner_module.generate_itinerary(trip, rows)
        self.assertEqual({stop["place_id"] for stop in result["itinerary_by_day"][0]["stops"]}, {3, 4, 5})
        self.assertEqual(result["cost_breakdown"]["total"], 960)

        trip["compulsory_places"] = [1]
        result = backend.planner_module.generate_itinerary(trip, rows)
        self.assertTrue(result["all_compulsory_scheduled"])
        self.assertEqual(result["cost_breakdown"]["total"], 800)

    def test_short_visits_can_beat_cheaper_long_visits(self):
        rows = [dict(place_id=i, latitude=25.3, longitude=83,
                     entry_fee=1 if i <= 6 else 200,
                     visit_duration_minutes=110 if i <= 6 else 25)
                for i in range(1, 10)]
        trip = dict(days=1, hours_per_day=2, budget=650, start_coords=[25.3, 83],
                    max_stops_per_day=3)
        planner = backend.planner_module
        self.assertTrue(planner.Planner(trip, rows).exact_search_fits())

        for run_exact in (True, False):
            with self.subTest(run_exact=run_exact):
                with patch.object(planner.Planner, "exact_search_fits", return_value=run_exact):
                    result = planner.generate_itinerary(trip, rows)
                stops = result["itinerary_by_day"][0]["stops"]
                self.assertEqual({stop["place_id"] for stop in stops}, {7, 8, 9})
                self.assertEqual(result["cost_breakdown"]["total"], 600)

    def test_refinement_can_replace_a_long_stop_with_three_short_stops(self):
        rows = [dict(place_id=i, latitude=25.3, longitude=83,
                     visit_duration_minutes=110 if i == 1 else 25,
                     entry_fee=1 if i == 1 else 200) for i in range(1, 5)]
        trip = dict(days=1, hours_per_day=2, budget=650, start_coords=[25.3, 83],
                    max_stops_per_day=3)
        planner_module = backend.planner_module
        planner = planner_module.Planner(trip, rows)
        clock = iter(range(1000))
        with patch.object(planner_module, "monotonic", side_effect=lambda: next(clock)):
            routes, sims = planner.refine([["1"]], seconds=100)
        self.assertEqual(set(routes[0]), {"2", "3", "4"})
        self.assertEqual(planner.trip_cost(sims), 600)
        self.assertEqual(planner.result()["optimization_status"], "optimal")

    def test_equivalent_schedules_use_the_earliest_day(self):
        places = [dict(place_id=i, latitude=25.3, longitude=83, entry_fee=0)
                  for i in range(1, 5)]
        trip = dict(days=8, hours_per_day=8, budget=500, start_coords=[25.3, 83],
                    food_per_day=430, max_stops_per_day=2)
        planner = backend.planner_module
        with patch.object(planner.Planner, "exact_search_fits", return_value=False):
            result = planner.generate_itinerary(trip, places)
        self.assertEqual([len(day["stops"]) for day in result["itinerary_by_day"]],
                         [2, 0, 0, 0, 0, 0, 0, 0])

    def test_nearest_suggestions(self):
        rows = [dict(name="far", latitude=26, longitude=83), dict(name="near", latitude=25.31, longitude=83), dict(name="unknown")]
        self.assertEqual(backend._near(rows, [(25.3, 83)])[0]["name"], "near")
        self.assertEqual(backend._near(rows, []), [])

    def test_day_meal_food_matching(self):
        import copy
        def stop(name, lat, arrival, departure):
            return dict(place_id=name, place_name=name, latitude=lat, longitude=83,
                        arrival_time=arrival, departure_time=departure)
        days = [dict(day=1, stops=[stop("morning", 25.2, "09:00", "10:00"),
                                  stop("midday", 25.3, "12:00", "14:00"),
                                  stop("evening", 25.4, "16:00", "17:00")]),
                dict(day=2, stops=[stop("next day", 25.5, "12:00", "14:00")]),
                dict(day=3, stops=[])]
        foods = [dict(name=str(lat), latitude=lat, longitude=83, budget_tier="standard",
                      opening_hours="Closed (display only)") for lat in (25.2, 25.3, 25.4, 25.5)]
        foods += [dict(name="wrong tier", latitude=25.3, longitude=83, budget_tier="premium"),
                  dict(name="unknown location", budget_tier="standard")]
        original = copy.deepcopy((days, foods))
        result = backend.food_suggestions_by_day(days, foods, "standard")
        self.assertEqual(result[0]["meals"][0]["anchor_place_name"], "midday")
        self.assertEqual(result[0]["meals"][0]["restaurants"][0]["name"], "25.3")
        self.assertEqual(result[0]["meals"][1]["restaurants"][0]["name"], "25.4")
        self.assertEqual(result[1]["meals"][0]["restaurants"][0]["name"], "25.5")
        self.assertEqual(len(result[0]["meals"][0]["restaurants"]), 1)
        self.assertEqual(result[2]["meals"][0]["restaurants"], [])
        self.assertTrue(result[2]["meals"][0]["message"])
        self.assertEqual((days, foods), original)
        fallback = backend.food_suggestions_by_day(days, foods, "budget")[0]["meals"][0]
        self.assertEqual(fallback["selection_mode"], "other_tiers")
        self.assertTrue(fallback["restaurants"])
        far = backend.food_suggestions_by_day(days, [foods[3]], "standard")[0]["meals"][0]
        self.assertEqual(far["selection_mode"], "farther")
        self.assertGreater(far["restaurants"][0]["distance_to_stop_km"], 3)
        self.assertIn("farther away", far["message"])
        empty = backend.food_suggestions_by_day(days, [], "standard")[0]["meals"][0]
        self.assertEqual(empty["selection_mode"], "unavailable")
        self.assertEqual(empty["restaurants"], [])

    def test_food_rendering_and_unchanged_styles(self):
        html = (ROOT / "frontend/suggestions.html").read_text(encoding="utf-8")
        script = re.findall(r"<script>(.*?)</script>", html, re.S)[0]
        fixture = dict(food_suggestions_by_day=[dict(day=2, meals=[
            dict(meal="Lunch", anchor_place_name="Temple", restaurants=[dict(
                name="<img onerror=bad>", address="Test", price_range_per_person=200,
                distance_to_stop_km=12, budget_tier="premium")], message="Closest options farther away", selection_mode="farther"),
            dict(meal="Dinner", restaurants=[], message="No nearby option")])])
        harness = "const grids = {}; const document = {getElementById: id => grids[id] = {innerHTML:''}};\n"
        harness += "const localStorage = {getItem: () => " + json.dumps(json.dumps(fixture)) + "};\n"
        harness += script + "\nconsole.log(grids.foodGrid.innerHTML);"
        result = subprocess.run(["node"], input=harness, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Day 2", result.stdout)
        self.assertIn("Closest options farther away", result.stdout)
        self.assertIn("Distance from Temple", result.stdout)
        self.assertIn("premium", result.stdout)
        self.assertIn("Hours unavailable", result.stdout)
        self.assertIn("No nearby option", result.stdout)
        self.assertIn("&lt;img", result.stdout)
        self.assertNotIn("<img onerror", result.stdout)

    def test_daily_hotel_choices(self):
        import copy
        days = [dict(day=1, stops=[dict(place_name="A", latitude=25.3, longitude=83)]),
                dict(day=2, stops=[dict(place_name="B", latitude=25.5, longitude=83)]),
                dict(day=3, stops=[])]
        hotels = [dict(hotel_name=str(i), latitude=25.3 + i * .001, longitude=83,
                       category="normal", price_per_night=3000) for i in range(5)]
        hotels += [dict(hotel_name="Luxury", latitude=25.5, longitude=83, category="luxury"),
                   dict(hotel_name="Missing coordinates", category="budget")]
        original = copy.deepcopy((days, hotels))
        result = backend.hotel_suggestions_by_day(days, hotels, "normal")
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]["hotels"]), 5)
        self.assertEqual(result[0]["hotels"][0]["hotel_name"], "0")
        self.assertEqual(result[1]["selection_mode"], "farther")
        self.assertTrue(all(h["category"] == "normal" for h in result[1]["hotels"]))
        self.assertEqual(result[2]["hotels"], [])
        self.assertTrue(result[2]["optional_after_trip"])
        self.assertFalse(result[0]["optional_after_trip"])
        self.assertEqual(backend.hotel_suggestions_by_day(days, hotels, "none"), [])
        fallback = backend.hotel_suggestions_by_day(days, hotels, "budget")
        self.assertEqual(fallback[0]["selection_mode"], "other_tiers")
        self.assertEqual(backend.hotel_suggestions_by_day(days, [], "normal")[0]["selection_mode"], "unavailable")
        self.assertEqual((days, hotels), original)

    def test_hotel_sql_draft_and_api_without_inserting(self):
        # Parse VALUES as literals; never execute the supplied SQL against any database.
        sql = (ROOT / "database/insert_hotels_2026_11_09.sql").read_text(encoding="utf-8")
        values = re.findall(r"\(\n    '[\s\S]*?\n\)", sql)
        records = [ast.literal_eval(v.replace("NULL", "None")) for v in values]
        self.assertEqual(len(records), 36)
        self.assertEqual(len({r[0] for r in records}), 36)
        fields = ["hotel_name", "address", "latitude", "longitude", "category", "price_per_night",
                  "official_booking_url"]
        hotels = [dict(zip(fields, r)) for r in records]
        for h in hotels:
            self.assertLessEqual(len(h["hotel_name"]), 150)
            self.assertLessEqual(len(h["address"]), 255)
            price = h["price_per_night"]
            self.assertEqual(h["category"], "budget" if price <= 2000 else "normal" if price <= 5000 else "luxury")
            self.assertTrue(24 < h["latitude"] < 26 and 82 < h["longitude"] < 84)
        place = dict(place_id=1, place_name="Demo stop", latitude=25.3, longitude=83,
                     opening_time="09:00", closing_time="18:00", visit_duration_minutes=60, entry_fee=10)
        payload = dict(days=2, hours_per_day=8, budget=50000,
                       start={"lat":25.3,"lng":83}, end={"lat":25.3,"lng":83},
                       selected_places=[1], compulsory_places=[1], stay_preference="normal")
        with patch.object(backend.db, "query", return_value=[place]), \
             patch.object(backend.db, "safe_query", side_effect=lambda sql, *args: hotels if sql == "SELECT * FROM hotels" else []), \
             patch.object(backend.db, "save_trip", return_value=None):
            response = self.client.post("/api/trip", json=payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        result = response.get_json()
        self.assertEqual(len(result["hotel_suggestions_by_day"]), 2)
        self.assertTrue(result["hotel_suggestions_by_day"][0]["hotels"])
        html = (ROOT / "frontend/suggestions.html").read_text(encoding="utf-8")
        script = re.findall(r"<script>(.*?)</script>", html, re.S)[0]
        harness = "const grids={}; const document={getElementById:id=>grids[id]={innerHTML:''}};\n"
        harness += "const localStorage={getItem:()=>" + json.dumps(json.dumps(result)) + "};\n"
        harness += script + "\nconsole.log(grids.hotelsGrid.innerHTML);"
        rendered = subprocess.run(["node"], input=harness, encoding="utf-8", capture_output=True)
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        self.assertIn("Day 1", rendered.stdout)
        self.assertIn("Comfort", rendered.stdout)
        self.assertIn("/room/night", rendered.stdout)

    def test_costs_only_for_visiting_days(self):
        places = [dict(place_id=i, place_name=f"Stop {i}", latitude=25.3, longitude=83,
                       opening_time="00:00", closing_time="23:59",
                       visit_duration_minutes=30, entry_fee=0) for i in (1, 2)]
        trip = dict(days=8, hours_per_day=8, budget=200,
                    start_coords=[25.3, 83], selected_places=[1, 2],
                    compulsory_places=[1, 2], food_per_day=200, hotel_per_night=1000)
        result = backend.planner_module.generate_itinerary(trip, places)
        self.assertTrue(result["all_compulsory_scheduled"])
        self.assertEqual(result["cost_breakdown"]["food"]["amount"], 200)
        self.assertEqual(result["cost_breakdown"]["accommodation"]["amount"], 0)
        trip.update(max_stops_per_day=1, budget=1400)
        result = backend.planner_module.generate_itinerary(trip, places)
        self.assertTrue(result["all_compulsory_scheduled"])
        self.assertEqual(result["cost_breakdown"]["total"], 1400)
        trip["budget"] = 1399
        result = backend.planner_module.generate_itinerary(trip, places)
        self.assertFalse(result["all_compulsory_scheduled"])
        self.assertEqual(result["cost_breakdown"]["total"], 200)
        trip["budget"] = 0
        result = backend.planner_module.generate_itinerary(trip, places)
        self.assertEqual(result["cost_breakdown"]["total"], 0)

    def test_automatic_endpoints_keep_an_affordable_local_route(self):
        places = [dict(place_id=i, place_name=f"Stop {i}", latitude=25.3,
                       longitude=longitude, visit_duration_minutes=30, entry_fee=0)
                  for i, longitude in enumerate((83, 83.001, 83.4, 83.401, 83.8, 83.801), 1)]
        payload = dict(days=1, hours_per_day=8, budget=500, food_budget="budget",
                       selected_places=[p["place_id"] for p in places], compulsory_places=[2])
        foods = [dict(budget_tier="budget", price_range_per_person=215)]
        with patch.object(backend.db, "query", return_value=places), \
             patch.object(backend.db, "safe_query", side_effect=lambda sql, *args: foods if "food_places" in sql else []), \
             patch.object(backend.db, "save_trip", return_value=None):
            response = self.client.post("/api/trip", json=payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        result = response.get_json()
        self.assertEqual({s["place_id"] for s in result["itinerary_by_day"][0]["stops"]}, {1, 2})
        self.assertLessEqual(result["cost_breakdown"]["total"], 500)

    def test_optional_endpoints_and_no_stay(self):
        places = [dict(place_id=i, place_name=f"Stop {i}", latitude=25.3 + i * .001,
                       longitude=83, opening_time="00:00", closing_time="23:59",
                       visit_duration_minutes=30, entry_fee=0) for i in range(1, 4)]
        hotels = [dict(hotel_name="Test hotel", category="normal", latitude=25.3,
                       longitude=83, price_per_night=1000)]
        payload = dict(days=2, hours_per_day=8, budget=10000, selected_places=[1, 2, 3],
                       compulsory_places=[2], stay_preference="none", start="", end="")
        for start, end in [("", ""), ({"lat":25.3,"lng":83}, ""),
                           ("", {"lat":25.4,"lng":83})]:
            with self.subTest(start=start, end=end), \
                 patch.object(backend.db, "query", return_value=places), \
                 patch.object(backend.db, "safe_query", side_effect=lambda sql, *args: hotels if sql == "SELECT * FROM hotels" else []), \
                 patch.object(backend.db, "save_trip", return_value=None):
                response = self.client.post("/api/trip", json=dict(payload, start=start, end=end))
                self.assertEqual(response.status_code, 200, response.get_json())
                result = response.get_json()
                self.assertEqual(result["cost_breakdown"]["accommodation"]["amount"], 0)
                self.assertEqual(result["hotel_suggestions"], [])
                self.assertEqual(result["hotel_suggestions_by_day"], [])
                self.assertTrue(result["all_compulsory_scheduled"])
                for key, supplied in [("start", start), ("end", end)]:
                    if supplied:
                        self.assertEqual(result[key]["lat"], supplied["lat"])
                    else:
                        self.assertIn(result[key]["label"], [p["place_name"] for p in places])

    @unittest.skipUnless(LIVE, "Pass --live to read the actual database")
    def test_live_database_api_images_and_planning(self):
        def fingerprint():
            return hashlib.sha256(json.dumps(backend.db.query("SELECT * FROM places ORDER BY place_id"), sort_keys=True).encode()).hexdigest()
        before = fingerprint()
        food_before = backend.db.query("SELECT * FROM food_places ORDER BY food_place_id")
        hotels_before = backend.db.query("SELECT * FROM hotels ORDER BY hotel_id")
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
            self.assertEqual(len(result["food_suggestions_by_day"]), 2)
            for day in result["food_suggestions_by_day"]:
                for meal in day["meals"]:
                    self.assertIsInstance(meal["restaurants"], list)
                    for food in meal["restaurants"]:
                        if meal["selection_mode"] != "other_tiers":
                            self.assertEqual(food["budget_tier"], "standard")
                        if meal["selection_mode"] == "nearby":
                            self.assertLessEqual(food["distance_to_stop_km"], 3)
            payload["start"] = "Unknown location test"
            self.assertEqual(self.client.post("/api/trip", json=payload).status_code, 400)
        self.assertEqual(fingerprint(), before)
        self.assertEqual(backend.db.query("SELECT * FROM food_places ORDER BY food_place_id"), food_before)
        self.assertEqual(backend.db.query("SELECT * FROM hotels ORDER BY hotel_id"), hotels_before)
        print(f"Live checks: {len(all_rows)} places, {len(regions)} regions, {len(mapped)} mapped images; places unchanged.")
        print("Image gaps:", [(r["place_id"], r["image_url"]) for r in all_rows if r not in mapped])
        for table in ("hotels", "food_places", "travel_resources"):
            print(table, backend.db.query(f"SELECT COUNT(*) AS records FROM {table}"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
