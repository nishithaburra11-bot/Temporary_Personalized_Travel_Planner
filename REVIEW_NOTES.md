# Review notes — 2026-11-16

## Scope and verified results

Reviewed the Flask API, planner, browser-storage flow, date picker, plan rendering, SQL setup references and test suite. No production behavior was changed during this review. The obsolete travel_resources table-count assertion was removed from the live test because that unused table has already been deleted.

- All 19 backend tests passed with real MySQL reads enabled.
- All four JavaScript tests passed: date boundaries, month/year rollover and leap day, budget rendering, inline script parsing.
- Database fingerprints for places, restaurants and hotels remained unchanged.
- Live data: 52 places, seven regions, 36 food places, 36 hotels; all place images present.
- System Python worked. Project .venv lacked requests.
- No browser-driven visual/interaction pass was performed. Automated DOM stubs do not prove popup sizing, mouse interactions, keyboard focus or mobile layout.

## Additional API probes (mocked data; no database writes)

25 requests were checked with a one-place fixture and explicit start/end coordinates:

| Case | Result |
| --- | --- |
| Normal plan | 200, one scheduled stop |
| Zero budget | 200, paid stop excluded |
| Negative budget | 400 |
| Zero days / 31 days / fractional days / boolean days | 400 |
| 30 days | 200 |
| Empty selection / unknown place ID | 400 |
| Duplicate place IDs | 200, one stop without duplication |
| Fractional ID / boolean ID | 200: incorrectly coerced into a valid ID |
| Infinite place ID | 500: should be a validation error |
| Invalid calendar date | 400 |
| Past date | 200: API lacks the UI's past-date restriction |
| Closed weekday | 200, closed attraction excluded |
| Compulsory attraction on closed weekday | 200, unscheduled with conflict handling |
| Invalid start time / coordinates / food tier | 400 |
| Public transport | 422, unsupported |
| Mixed transport | 200, uses own-vehicle calculations |
| No stay | 200 |
| Luxury requested with no hotel records | 200, zero stay estimate and no warning |

## Findings to address

1. **Refresh loses the whole plan.** frontend/planning-state.js clears both storage areas on reload, including preferences, selected places and the result. Reloading Plan can consequently show the no-selection state. This is explicit existing behavior, but surprising unless intentional.
2. **Server-side date validation is incomplete.** The calendar and preferences submission block past dates, while direct POST /api/trip accepts them. API validation should enforce the same policy using an agreed timezone.
3. **Place ID validation is permissive.** app.py _id_list uses int(v), accepting booleans and truncating fractions; OverflowError from infinity is uncaught. Reject these values explicitly rather than converting them.
4. **Zero hospitality estimates may be misleading.** Empty/unpriced food or hotel records lead to zero costs. The current planner returns an empty warnings list; the Plan page does not show missing-price notices. Clarify unavailable prices rather than suggesting free food/stay.
5. **Data/optimization uncertainty is under-displayed.** Split opening-hour warnings are gathered but not passed through consistently; optimization_status and warnings are not displayed by Plan. Date omission also prevents closure checks without a prominent notice.
6. **Not deployment-ready unchanged.** Multiple frontend pages call http://127.0.0.1:5000 explicitly. Use same-origin paths for hosted access. The Flask entry point enables debug mode for local development.
7. **Browser storage failures need wider coverage.** Several storage accesses occur outside guarded blocks. Invalid JSON shapes or disabled storage can interrupt page initialization. This was identified by code inspection, not a full browser test.

## Unnecessary or legacy code (reported, not removed)

- Unused re, timedelta and requests imports and _geocode_cache in app.py.
- database.init_db is no longer called at app startup. Its old schema-script comments conflict with current startup behavior.
- travel_resources definitions/references remain in legacy SQL although the runtime does not use it and the live table is absent.
- database/schema_extra.sql mixes CREATE statements with destructive manual ALTER/DROP statements. It should eventually be separated into reference schemas and explicit migrations.
- Optional OSRM route helpers are not used by the current API; retain only if future road-routing integration is intended.

Removing these is separate from this review. No database tables or records were modified.
