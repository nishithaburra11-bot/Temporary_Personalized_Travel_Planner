# Ayan integration report — 2 November 2026

## Implemented flow

Home → Varanasi description → multiple regions → combined place selection and
images → supplied Preferences design → compulsory stops → itinerary and
exclusions → Suggestions.

Regions are read from the live database and no longer list attractions. Place
categories compare without capitalization differences. Selection changes prune
stale compulsory IDs. Preferences stores the existing trip API fields and goes
to Customize; it no longer calls an absent endpoint or absent itinerary page.

The cost display now reads cost_breakdown.total. Total/day distances and visit
durations use the actual planner response. No artificial minimum expenditure
was introduced: genuinely free/zero-distance trips can still cost zero.

## Files changed by this integration

| File | Reason |
|---|---|
| app.py | Serve frontend through Flask; support 30 days and food spending tiers; validate malformed input; resolve curated locations without external geocoding; use existing offline estimates; pass pace limits; rank suggestions by nearest scheduled stop and limit protocols to scheduled places; stop automatic SQL execution at startup. |
| frontend/regions.html | Database-driven multiple-region checkboxes and onward navigation, without attraction listings. |
| frontend/places.html | Union of selected regions, existing image endpoint plus fallback slots, category comparison and consistent selection storage. |
| frontend/preferences.html | Preserve supplied styling, bridge storage/API fields, restore start/end and optional date inputs, navigate to Customize, preserve entered locations during asynchronous loading. |
| frontend/customize.html | Prune stale selections and block navigation after a failed place-details request. |
| frontend/plan.html | Correct cost/distance/duration fields, invalidate stale results and show API validation details. |
| itinenary_logic.py | Small additions for daily stop caps, pace exclusion reasons and actual visit duration in responses. Existing user edits retained. |
| README.md | Setup, exact commands, database entry guidance and limitations. |
| database/integration_food_tier.sql (new) | Single-column additive migration for food spending tiers. |
| database/apply_integration.py (new) | Guarded migration runner that checks the column first and fingerprints places before/after. |
| tests/test_integration.py (new) | Syntax, API, planner, error handling, live database and image checks. |
| INTEGRATION_REPORT.md (new) | This report. |
| itinerary-verification.png, places-verification.png (new) | Browser verification screenshots. |

Shared style.css, images, logo and destination content were not edited. Existing
changes to database/testqueries.sql and pending seed files were left untouched.
The large Git diff for Preferences includes the user's replacement design that
was already present before this implementation, not a new redesign by the agent.

## Actual database changes

Inspected the live MySQL database, not only SQL files. All seven required tables
already existed. Applied only:

```sql
ALTER TABLE food_places ADD COLUMN budget_tier VARCHAR(20) NULL
COMMENT 'budget, standard, or premium; supplied by the dataset owner';
```

No table/column was renamed, no curated records were inserted, and no pending SQL
file was executed. The places schema and rows were not changed. A fingerprint
comparison confirmed identical places contents before/after the migration and
before/after the live automated checks. Normal browser itinerary generation
exercised the existing trip-save path; generated test trips were retained rather
than deleting records.

Live data: 36 places across five regions; hotels, food_places and travel_resources
each have zero rows and remain ready for the owner's data entry.

## Tests actually performed

- `python -B tests/test_integration.py --live`: all seven tests passed.
- Python parsing/imports and Node syntax checks for inline page scripts passed.
- Flask test-client checks for every HTML page, shared CSS/logo, health and unknown
  API paths passed. Simulated database failure returned structured HTTP 500;
  malformed requests returned HTTP 400.
- Actual MySQL reads: region union, place data and image endpoints passed.
  Seventeen existing mapped images returned successful image responses.
- Live trip generation returned nonzero cost, scheduled the compulsory paid
  stop, observed relaxed pace, returned exclusions and made no external routing
  requests (network calls were patched to fail the test). Automated live tests
  disabled persistence; they did not write trip rows.
- Planner checks exercised daily limits, exact entry-fee totals, visit duration,
  a 30-day response, zero-budget exclusions and compulsory conflicts.
- Suggestion-distance ranking was checked using temporary in-memory test
  records; no hospitality data was inserted into the live database.
- Browser: Home/Get Started → Varanasi description → Regions → Places →
  Preferences → Customize → Plan → Suggestions completed successfully against
  the running Flask service. Two regions displayed 17 places with working images.
- Browser test: one relaxed day, three chosen attractions and a compulsory
  Bharat Kala Bhavan Museum stop produced two stops, estimated spend ₹479 and
  total distance 11.45 km. The excluded Kashi Vishwanath Temple displayed the
  pace-limit reason. Suggestions displayed its empty-data states.
- Browser validation rejected an unknown starting location. Testing exposed an
  initialization race that could restore saved location text over newly typed
  text; this was corrected and the validation retest passed.
- Browser test: adding Sarnath displayed 29 combined places; Dhamek Stupa showed
  an image placeholder because its live image_url is NULL.
- The existing running Flask service was reused. A separate new server process,
  dependency installation and fresh-database import were not performed.

## Remaining data and behavior limits

No places-table change is required for the verified flow. To complete all images
later, the owner would need to fill NULL references or correct missing filenames:

- NULL image_url: place IDs 18–29.
- Stored filenames without matching files: ID 30 ramnagar_fort.jpeg;
  31 ramnagar_museum.jpeg; 32 ramnagar_riverfront.jpeg; 33 ganga_viewpoint.jpeg;
  34 kardameshwar.jpeg; 35 rural_temples.jpeg; 36 village_walk.jpeg.

Those mappings were not changed. Existing differently named image files were
not guessed or assigned to records. The frontend retains slots for these places.

Starting locations currently use curated place names. Varanasi Junction Railway
Station is absent from the provided dataset; no coordinates were invented. The
backend still accepts explicit coordinates, but the UI offers stored places.

Food/stay costs and populated suggestion cards cannot be verified against real
hospitality records until those tables contain data. Use README's field guidance.
The existing Suggestions protocol placeholder says no permits are required;
with an empty table this must be understood as missing data, not verified advice.
That existing page wording was left outside the approved frontend file list.

Relaxed caps at two stops/day, Balanced at three, and Packed removes that cap;
time, opening hours and budget can still reduce stop counts. Distances and fuel
costs are estimates. No map service was added; the existing map placeholder stays.
The new Preferences design's existing external font link is preserved.

No further approval is needed for the completed changes. Any later modification
to places records (including image mappings or station data) remains for the owner
to review and authorize separately.

## Open the application

With MySQL running and the existing .env configured:

```powershell
python -B app.py
```

Open http://127.0.0.1:5000/. If Ayan is already running there, use that server.
For virtual-environment installation and test commands, see README.md.
