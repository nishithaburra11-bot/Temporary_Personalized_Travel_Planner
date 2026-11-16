# Ayan — Personalized Travel Planner

A local Flask + MySQL application for planning visits in Varanasi and surrounding regions. The frontend is plain HTML, CSS and JavaScript served by Flask.

## Run locally (Windows PowerShell)

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B app.py
```

For a new machine, copy `.env.example` to `.env` only if `.env` does not already exist. Configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`. The database name used by the project is `personalized_travel_planner`. Keep `.env` private.

MySQL must be running with the project data imported. Open [Ayan locally](http://127.0.0.1:5000/). Use this host and port: several frontend pages hardcode the API address. No separate frontend server is required.

Install requirements into the interpreter you actually use. During the latest check, system Python had the dependencies, but `.venv` could not import `requests`.

## User flow

1. Home → Destinations → Regions: select the destination and regions.
2. Places: select attractions.
3. Preferences: choose 1–30 days, a positive budget, food budget and pace; optionally select accommodation, starting/ending places and a travel date.
4. Customize: mark compulsory stops or remove selections, then generate the itinerary.
5. Plan: view scheduled stops, times, distance, exclusions and compulsory-stop conflicts. The separate Estimated Spend section shows transport, food, stay and total. Attraction entry fees are included in the total and identified separately in a note.
6. Suggestions: view food options around lunch/dinner stops and hotel suggestions by day.

To change a plan, return to Preferences or Customize, make the changes and generate again. There is no separate Recalculate button or saved-trip endpoint.

The calendar disables dates before the browser's current local date and prevents navigation to earlier months. It expands within the preferences card so its dates are not clipped.

Preferences and results use browser storage, not database trip records. **Current behavior: refreshing a page clears planning selections, preferences and results through `planning-state.js`.** Browser storage is not a saved-trip history or a cross-device account feature.

## Planning and cost rules

- The current preferences UI requests one traveler, an eight-hour day starting at 09:00, and own-vehicle transport.
- Relaxed allows at most two stops/day; Balanced three; Packed has no count cap. Opening hours, visit/travel times and budget still limit stops.
- Selected places may be excluded. Compulsory stops that cannot fit produce conflicts and suggestions; they are not guaranteed to fit.
- Distances and travel times use an offline estimate (straight-line distance with a detour factor), not live traffic or verified road routing.
- Larger searches return a best-found result rather than a guaranteed optimum.
- Blank endpoints are chosen automatically from selected places. A blank end does **not** necessarily mean returning to the start.
- Split opening hours are reduced to the longest opening session. Without a start date, weekday closures cannot be checked.
- Total cost = entry fees + estimated fuel + food + accommodation.
- Food uses two meals per visiting day at the average available price in the selected food tier. Accommodation uses the cheapest available price in the selected stay category, multiplied by `max(visiting_days - 1, 0)`. Empty itinerary days are not charged for food or stay.
- Hotel/food suggestions are recommendations, not reservations. Fallback options may be farther away or in another tier and are labelled accordingly. Their individual prices need not equal the planning estimate.
- Public-transport requests are rejected. The API accepts `mixed`, but currently plans it using own-vehicle estimates.

## Database and files

Runtime planning reads these tables:

| Table | Purpose |
| --- | --- |
| `places` | Attractions, region/category, coordinates, opening hours, closures, visit duration, entry fee and image filename |
| `food_places` | Restaurant coordinates, dietary information, price per person and `budget_tier` (`budget`, `standard`, `premium`) |
| `hotels` | Hotel coordinates, category (`budget`, `normal`, `luxury`), nightly price, address and optional official booking URL |

Place images are served from `database/images/places/`. Store filenames in `places.image_url`, not Windows absolute paths. Basic/Comfort/Luxury in the UI map to hotel categories budget/normal/luxury.

`travel_resources` is not used by the runtime and was absent in the database checked during this review. Older SQL reference files still mention it; they are not a reliable current migration set.

`trips`, `trip_places` and `itinerary_items` are no longer read, written or created by the app's trip flow. For an existing database, run `database/remove_trip_storage.sql` manually to permanently remove their stored records. This deletion is not automatic.

Flask startup does not run schema scripts. **Do not execute `database/schema_extra.sql` as a general setup script:** it contains legacy `ALTER TABLE` and `DROP TABLE` statements. Seed files are not guaranteed repeatable. A new database needs a reviewed import of the current data and schema.

For an existing food table missing only `budget_tier`, the guarded migration is:

```powershell
.\.venv\Scripts\python.exe -B database/apply_integration.py
```

This checks whether the column exists and verifies that places are unchanged. It is not a complete database installer.

## API

| Method and path | Purpose |
| --- | --- |
| `GET /api/health` | App health; does not prove database connectivity |
| `GET /api/regions` | Region names and place counts |
| `GET /api/places?region=NAME` | Attractions; repeat `region` to select several |
| `GET /api/images/places/<filename>` | Attraction images |
| `GET /api/data-quality` | Issues detected in stored attraction data |
| `POST /api/trip` | Generate a fresh plan from the submitted preferences and selected places |

Trip generation returns its result directly and does not write trip records to MySQL.

## Verification

```powershell
python -B tests/test_integration.py
python -B tests/test_integration.py --live
node --test tests/frontend-preferences.test.cjs
```

Use an interpreter with requirements installed. Node.js is needed for JavaScript checks. `--live` performs read-only MySQL checks and API planning requests; it verifies that places, food and hotel records remain unchanged.

On 2026-11-16, all 19 backend tests (including live checks) and four frontend tests passed. The live database contained 52 places across seven regions, 36 hotels and 36 food places. All 52 place images were present. Additional API probes covered 25 normal/boundary/malformed-input cases; they also exposed the issues below. Browser visual and interaction testing was not performed in this review, so these results do not establish exhaustive end-to-end coverage.

## Known limitations and cleanup candidates

- API validation allows past dates even though the calendar blocks them.
- Fractional and boolean place IDs are converted to integers. An infinite ID produces HTTP 500 instead of a validation error.
- Missing food/hotel price data can produce a zero estimate without a warning. Zero does not necessarily mean free.
- Normalization issues and routing/optimization warnings are not consistently surfaced on the Plan page.
- Refresh resets the planning flow; blocked or malformed browser storage is not handled consistently across every page.
- Hardcoded localhost URLs need changing before hosting elsewhere.
- Unused backend imports (`re`, `timedelta`, `requests`) and `_geocode_cache`, the unused `database.init_db()` setup helper, and legacy schema files are cleanup candidates. Optional OSRM helpers are unused by the current API but could support a future routing feature.

See `REVIEW_NOTES.md` for the latest review findings. `INTEGRATION_REPORT.md` describes an earlier project state and should not be treated as the current feature specification.
