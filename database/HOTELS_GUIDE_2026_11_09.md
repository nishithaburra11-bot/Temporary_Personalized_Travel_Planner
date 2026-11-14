# Hotel data and integration — 9 November 2026

## Preferences and estimates

Existing preferences are Basic, Comfort and Luxury. The frontend already sends budget, normal and luxury respectively. No field names or preferences controls were changed.

Draft project price bands, per room per night: Basic/budget up to INR 2000; Comfort/normal above 2000 through 5000; Luxury/luxury above 5000. These classifications and all prices in the insert file are illustrative planning assumptions, not star ratings or current hotel quotes. Taxes, occupancy limits, extra beds, availability and date-dependent rates are not represented. All coordinates are coarse area-level demo estimates, not verified hotel pins. Some properties share an area estimate. Addresses may name only a locality. Facilities were removed from the SQL drafts and card rendering at the user's request.

## SQL files (not executed)

1. hotels_table_2026_11_09.sql: CREATE TABLE IF NOT EXISTS using existing column names. Your actual hotels table already exists, so this is only a reference/fresh-setup file. It does not change an existing table.
2. hotels_optional_cleanup_2026_11_09.sql: requested DROP COLUMN facilities; optional source_checked_date removal is commented out. Execute each only if that column exists. No statements have been executed by Codex.
3. insert_hotels_2026_11_09.sql: 36 ordinary INSERT ... VALUES rows, no IDs supplied. Run once after reviewing; reruns create duplicates. No food/place data is changed. official_booking_url is retained for existing booking links; facilities is no longer used. Official links are omitted when not established rather than guessed.

The actual table was inspected read-only: 10 columns, zero rows. No schema or insert SQL was executed. Existing schema_extra.sql and schema_hotels.sql were left untouched, including user work.

## Sources

Each SQL row has a name/locality source comment. The first group uses the [Varanasi district accommodation directory](https://varanasi.nic.in/accommodation/); this is listing evidence, not a guarantee of current operation. It spells one property 'Meredian Grant', preserved here pending confirmation. [Mirzapur district](https://mirzapur.nic.in/accommodation/) lists Hotel The Galaxy. [UPSTDC](https://www.upstdc.co.in/hotels-in-varanasi) lists Rahi Tourist Bungalow Sarnath. Property websites support other names/localities, including [Hotel Temple On Ganges](https://www.hoteltemple.com/), [Ganpati Guest House](https://www.ganpatihospitality.com/), [Hotel Buddha](https://hotelbuddhavaranasi.com/) and [Rivatas](https://www.rivatas.com/).

Rahul Guest House uses a [Maps of India directory](https://www.mapsofindia.com/whitepages/businesses/index/rahulgu) and Shanti Guest House a [booking listing](https://bookmystay.io/ShantiGuestHouse17079), rather than a verified standalone property website; both have NULL official_booking_url. Some source pages contain old information or template text. The dataset is for the college demonstration; it is not verified booking advice or comprehensive regional coverage.

## Daily stay suggestions

app.py returns hotel_suggestions_by_day, leaving the older hotel_suggestions key for compatibility. For each day with a located sightseeing stop, the anchor is its final stop. The app offers at most three matching-category hotels within an estimated 3 km. If none are that close, it offers the closest matching-category hotels farther away with a clear message. If no located matching-category hotels exist, it offers up to three from other categories with an explanation. It never invents records to fill slots. Empty hotel tables and days without located stops get honest messages. stay_preference=none suppresses the new groups.

The same hotel can be suggested on several days; these are alternatives, not a requirement to move hotels. Final-day cards are labelled Optional extra night. A one-day trip can therefore show optional stays without adding a booked night.

frontend/suggestions.html reuses its existing cards and grid with day/comfort labels, estimated per-room/night prices, distance, existing booking-link functionality. Dynamic values are escaped and booking links limited to HTTP(S). Old locally saved trips still render through the previous data shape. Generate a new itinerary after inserting hotels to receive new groups.

## Cost and itinerary limits

Sightseeing scheduling, compulsory places and travel endpoints are unchanged. Hotels are suggestions only; selecting/reserving a hotel is not implemented. The existing cost model remains the cheapest priced hotel in the selected category multiplied by days minus one. It is a baseline for one room, not the total for any chosen set of daily hotel cards, and does not scale room count with travelers. Other-category alternatives do not silently change the budget. The last optional night is not included. Exact hotel travel/detours are not scheduled. Approximate pins limit distance/ranking accuracy.

## Verification

All 11 integration tests passed, including day-specific selection, three-result limit, tier and distance fallback, empty cases, no-stay preference, final-night labeling, Python/JavaScript syntax, mocked API and Node rendering, and read-only live database checks. The 36 SQL records were parsed as literals for fixture tests; SQL was NOT executed, even in a temporary database. Live comparisons confirmed hotels, food_places and places unchanged. Actual live hotels remain empty until you run the insert. Static HTML before the rendering script and the inline CSS were compared with Git HEAD and were identical. No browser visual inspection was performed.
