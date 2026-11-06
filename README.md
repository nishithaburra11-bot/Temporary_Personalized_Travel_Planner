# Temporary_Personalized_Travel_Planner

## Run Ayan locally (Windows PowerShell)

The existing MySQL database is `personalized_travel_planner`. Keep its current
`places` table and records. Do not execute the unfinished seed/query files.
Flask now serves the existing frontend; no separate frontend server is required.

Dependencies remain those in requirements.txt: Flask, flask-cors, requests,
PyMySQL, cryptography and python-dotenv. No new dependency was added.

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Keep the existing .env. For a new machine only, copy .env.example to .env if .env
does not exist, then set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD and DB_NAME.
Never publish .env. MySQL must be running and the existing project database
must be present. A fresh database needs a separately reviewed data import;
database/schema.sql is not a safe repeatable migration.

The reviewed food-tier migration has already been applied on this machine.
For another copy of the same database, this guarded command adds only the
missing column and checks that places is unchanged:

```powershell
.\.venv\Scripts\python.exe -B database/apply_integration.py
```

Start the application:

```powershell
.\.venv\Scripts\python.exe -B app.py
```

Open http://127.0.0.1:5000/ in the browser. If that port already serves Ayan,
reuse that server. Startup no longer automatically runs schema scripts.
The system Python currently has the dependencies; `python -B app.py` also
works in the inspected environment. The existing .venv lacked PyMySQL during
inspection, so install requirements before using that environment.

## Data entry and supported behavior

- places: unchanged. Existing image_url filenames are served from
  database/images/places/. Matching files appear on Places; NULL or missing
  files show an image slot. Do not enter full Windows paths in image_url.
- hotels: keep category values budget, normal, luxury; enter hotel_name,
  latitude, longitude, price_per_night and optional booking/address details.
  The UI's Basic/Comfort/Luxury choices map to those existing category values.
- food_places: enter name, coordinates, price_range_per_person and the new
  budget_tier (budget, standard or premium). Dietary options remain a separate
  existing field. Unclassified rows are not treated as a guessed price tier.
- travel_resources: link place_id to an existing place and enter
  requirement_type, required_or_optional, procedure_text and official_url.
  Resources returned with a trip belong to scheduled stops.
- trips, trip_places and itinerary_items: used by existing trip persistence
  and recalculation. Do not rename these tables or their fields.
- Hotel and food suggestions rank located records by distance to the nearest
  scheduled stop, returning up to five. This ranking does not guarantee a
  particular maximum distance. Records need both coordinates to be ranked.
- Empty hospitality tables mean no invented recommendations or costs.
  Expenditure includes available entry fees and estimated fuel; food uses
  two meals per day from matching priced records and hotels use days minus
  one nights. Missing data is reported as warnings.
- Start/end inputs use existing curated place names; blank end means return
  to start. Railway-station data is not supplied, so it is not silently added.
- Preferences supports 1–30 days. Relaxed caps at two stops/day, Balanced at
  three, Packed has no stop-count cap. Time, opening hours and budget may
  permit fewer stops. No guaranteed minimum number of stops.
- The supplied Preferences design is preserved. It currently uses one
  traveler, an eight-hour day from 09:00, and own-vehicle fuel estimates.
- Routes use the existing offline distance/time estimator. No geocoding,
  OSRM or map service is called by trip generation. The supplied font link
  in Preferences remains unchanged.

## Verification

```powershell
python -B tests/test_integration.py
python -B tests/test_integration.py --live
```

The live test reads MySQL and disables trip persistence during its requests.
It verifies region unions, image responses, itinerary costs, compulsory stops,
pace exclusions, unknown-location errors, no external routing requests and an
unchanged places fingerprint. Normal browser-generated trips are saved.

See INTEGRATION_REPORT.md for the actual execution results and remaining data
limitations. No pending SQL in database/testqueries.sql, database/schema.sql,
database/schema_extra.sql or schema_extra.sql was executed.
