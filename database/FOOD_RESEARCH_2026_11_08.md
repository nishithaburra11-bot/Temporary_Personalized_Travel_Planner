# Food research for Ayan — 8 November 2026

## Latest update: 36 records with user-authorized demo locations and hours

This update supersedes the missing-coordinate/hour descriptions below. The user explicitly requested approximate coordinates, assumed display timings, four screenshot restaurants and more venues. The SQL now has 36 rows: the prior 24, four screenshot venues, six Domino's branches and two local eateries. All have prices, tiers, coordinates and display hours. Some addresses remain NULL.

Existing sourced coordinates/hours were preserved. Previously missing coordinates are rough area-level demo points, written to three decimals and labelled in SQL comments, NOT geocoded or verified venue locations. Their accuracy has not been measured; nearest-stop rankings and distance values produced from them are demonstrative only. Assumed hours include '(demo estimate)' in the actual stored display text. Published hours remain unchanged. Prices remain user-approved estimates except the Vedanta menu benchmark. No schema or frontend changes were made.

Screenshot transcriptions: Biryani Mahal Banaras (25.295493, 83.002300), Aman-E-Khaas (25.296953, 83.002523), Dawat e Zaika (25.295538, 83.001922), and DAWAT E KHAS - The Triumph Hotel (25.301082, 82.969041). These are coordinates shown in the user's images, not independently verified pins. In particular, Dawat e Zaika's screenshot also shows a nearby Biryani Mahal label.

Additional branch addresses and service times come from the [official Domino's Varanasi locator](https://www.dominos.co.in/store-location/varanasi/varanasi): Sarnath, JHV Mall, Susuwahi, Kandwa, Vijaya Mall and PDR Mall. Address strings were shortened to fit the existing column. [Visit Kashi lists Deena Chat Bhandar](https://visitkashi.in/things-to-do/local-food/deena-chat-bhandar); [InsideBanaras lists Kerala Cafe Bhelupur](https://www.insidebanaras.com/kerala-cafe-since-1962), a third-party source. These eight added coordinates are demo approximations; their venue names were not invented. Deena is a chaat/light-meal option, not a full restaurant meal guarantee.

Validation: the INSERT statements ran in an isolated in-memory SQLite table (MySQL USE omitted), confirming 36 unique names, non-null core demonstration fields, tier thresholds, numeric coordinate bounds and string lengths. This does not verify geographic accuracy or MySQL execution. No live database queries/writes were made in this update. If earlier rows have already been inserted, running just the new block adds twelve rows but does NOT update the old rows' missing coordinates/hours; rerunning the full file duplicates rows.

## Current pricing update — user-approved demonstration estimates

The user subsequently approved estimated meal prices and the project tier ranges. The INSERT file now supplies prices and tiers for all 24 records: 1 budget (up to INR 250), 11 standard (above INR 250 through 600), and 12 premium (above INR 600). Prices are illustrative per-person meal allowances, not verified venue bills; cafe/patisserie allowances represent light meals. Vedanta retains its published INR 449 thali benchmark. All other research gaps, including missing coordinates and service times, remain unchanged. The earlier missing-price descriptions below record the original research findings, not the current SQL values. No database writes were made. All 24 price/tier assignments were checked locally in memory against the approved thresholds.

This is a partial, source-backed research draft, not a comprehensive restaurant directory. Official pages establish published information, not a guarantee that prices, opening times or operations remain unchanged. No database writes or application edits were performed for this research.

The accompanying SQL matches the inspected live food_places columns: food_place_id (auto-generated), name, latitude, longitude, address (100 characters), price_range_per_person, opening_hours and budget_tier. It does not restore deleted columns or touch places.

## How to use the draft

The current file is insert_food_places_2026_11_08.sql. At the user's request it uses plain INSERT INTO ... VALUES and now contains 24 restaurant/cafe records. The superseded food_places_research_2026_11_08.sql was deleted. There is no completeness or duplicate filter in the current file: all rows will be inserted, including NULL fields, and rerunning it can duplicate records. Only Vedanta currently has all fields populated. The additional ten entries form a separate INSERT block so someone who already inserted the original fourteen can run only the new block. No SQL was executed against MySQL.

## Additional ten venues

- [Taj Ganges dining](https://www.tajhotels.com/en-in/hotels/taj-ganges-varanasi/restaurants): Varuna and Chowk; [hotel address](https://www.tajhotels.com/en-in/hotels/taj-ganges-varanasi) is Nadesar Grounds. Varuna lunch 12:30-15:00 and dinner 19:00-23:00.
- [HHI Atrium Cafe](https://www.hhivaranasi.com/dining/atrium-cafe): C-21/3 Maldahiya Road; 07:30-22:30. Postal code omitted because its contact and dining pages disagree.
- [Brown Bread Bakery](https://brownbreadbakery.com/): Ganga Mahal, D25/42, Bangali Tola Road, Pandey Ghat.
- [Surya dining](https://www.hotelsuryavns.com/dining): Canton Royale and Mangi Ferra Cafe. [Address](https://www.hotelsuryavns.com/membership): S.20/51 A-5, The Mall Road, Cantonment.
- [BrijRama dining](https://www.brijhotels.com/hotels/brijrama-palace-varanasi/hotel-overview): Darbhanga and Udayan Terrace. [Address](https://www.brijhotels.com/hotels/brijrama-palace-varanasi/contact-us): Darbhanga Ghat, Dashashwamedh.
- [DoubleTree dining](https://www.hilton.com/en/hotels/vnsdidi-doubletree-varanasi/dining/): Divo and Anandam Veg Thali, SA2/320 Chhota Lalpur, Pandeypur.

Exact coordinates, meal prices and budget tiers for these ten remain unverified and are NULL. Unpublished exact service times also remain NULL. They are additional research records, not ten ready-to-use nearby recommendations. No geographic coverage claim is made for rural/excursion areas. The updated SQL was checked in an in-memory SQLite database after omitting MySQL USE: 24 distinct names and all string lengths fit. This is not a MySQL execution test.

Vedanta's 449 rupees is the published Shahi Thali price, used as a representative meal benchmark. It is not an observed average customer bill. Taxes, drinks and extras are not established. The proposed classification is budget up to 250, standard above 250 through 600, premium above 600 rupees per meal/person. These thresholds are a project policy proposal, not official restaurant classifications; the existing application only matches tier strings. Using this SQL accepts that benchmark and policy for this one row.

Unknown values remain NULL. In particular, never substitute zero for an unknown meal price or use a region/attraction coordinate as a restaurant coordinate. Dessert/snack outlets should not acquire a full-meal price based on a single snack.

## Regional coverage and evidence

Region associations below are research groupings, not verified proximity to every attraction in a region. The existing food table does not require region_id: proximity is calculated from coordinates.

| Area | Candidates and official evidence | Still needed |
|---|---|---|
| Old City and Central Ghats | [Vedanta](https://vedanta.ghoomarthali.in/): Luxa Road, daily 07:00-midnight. [Menu](https://vedanta.ghoomarthali.in/menu): Shahi Thali 449. [Official directions link](https://maps.app.goo.gl/s8832v921GPU8zNg8) resolves to destination 25.3090378, 83.0016921. | Confirm current bill/taxes if using more than a benchmark. |
| BHU and Southern Varanasi | [Pizzeria Vaatika](https://www.pizzeriavaatika.com/): Assi branch address and official directions pin 25.2893070, 83.0061070. [Baati Chokha Dafi](https://baatichokha.com/detail/baati-chokha-dafi): branch and daily 09:00-23:00. | Vaatika hours/current menu; Dafi street address, pin and price. Vaatika's fetched site included unrelated spam, so advertised prices were not promoted to SQL. |
| Sarnath and Northern Varanasi | [Sarnath Cafe](https://sarnathcafe.com/about-us/location/): Mawaiya Road opposite Tibetan Institute; address shortened for VARCHAR(100). | Exact pin, meal price and hours. |
| Ramnagar and Eastern Riverbank | [Arzoo at Ramada Katesar](https://ramadavaranasikatesar.com/dining/); [Wyndham property page](https://www.wyndhamhotels.com/ramada/chandauli-india/ramada-varanasi-ketesar/overview) gives Katesar Ramnagar Road and 07:00-22:30. | Exact pin and public diner meal price. A hotel breakfast inclusion is not a free restaurant meal for everyone. |
| Rural Kashi | Dafi is a candidate on the southern side, not proven close to every rural attraction. | No complete verified restaurant row for this region; local confirmation needed. |
| Chandauli | Katesar has an administrative Chandauli address, but this does not establish proximity to the project's waterfall/excursion stops. | No complete verified dining coverage for those excursion areas. Do not treat Katesar as coverage for the entire district. |
| Mirzapur and Chunar | [Baati Chokha Ahraura](https://baatichokha.com/detail/baati-chokha-ahraura): SH5A near Ahraura Toll Plaza, 09:00-23:00. [Konark Grand dining](https://konarkgrandhotel.com/dine.html): Aroma lunch/dinner, Clove breakfast, Cafe Express 24 hours. | Prices and exact venue pins; complete Konark address. These venues do not establish proximity to every Chunar/Mirzapur stop. |
| Nearby city alternatives | [Baati Chokha Teliabagh](https://baatichokha.com/detail/baati-chokha-varanasi), Vaatika Cantonment branch above; [Ramada JHV dining](https://www.ramadajhvvns.com/drink-dine/) lists Tadka, The Palate and Temptationz. [JHV contact](https://www.ramadajhvvns.com/contact-us/) provides Cantonment address. | Exact pins and verified meal prices; full Teliabagh street address. Temptationz is a patisserie, not a verified lunch substitute. |

The map coordinates used for Vedanta come from destination !3d/!4d in the resolved official link, not @viewport coordinates. Vaatika's official directions link supplies destination !2m2!1d83.006107!2d25.289307. A generic map centre is not sufficient verification.

## What the current application actually does

Code inspected: app.py (food selection, food costing, _near, pace caps), itinenary_logic.py (schedule feasibility/travel estimates), frontend/suggestions.html (food display). This was code inspection, not a complete itinerary execution test.

1. Frontend sends selected places, compulsory places, days, budget, pace and food tier. The server obtains the attraction records from places.
2. Planner attempts compulsory stops first, then optional feasible stops, and optimizes ordering. Available time, visit durations, opening times, estimated travel, breaks and budget constrain the result. This is a heuristic, not a guarantee of the maximum possible number of visits.
3. app.py imposes relaxed=2 stops/day, balanced (normal)=3, packed (fast)=no fixed count cap. Thus relaxed allows at most 4/6 and balanced 6/9 stops over 2/3 days. Packed may fit more but remains time/budget constrained. More restaurant rows do not change these caps.
4. Offline travel is estimated using straight-line distance multiplied by 1.3 and 25 km/h. This does not model congestion, exact roads, bridge crossings, queues or walking access accurately.
5. Food rows are filtered by exact budget_tier. Cost is mean(non-null matching prices) x 2 meals x travelers x days. This mean includes matching restaurants across the whole dataset, before nearby restaurants are selected.
6. _near sorts restaurants by their minimum straight-line distance to ANY scheduled attraction and returns at most five overall. Missing coordinates are excluded. There is no maximum-distance cutoff, per-day grouping, meal-time assignment, restaurant-hours check or meal detour scheduling.
7. Food cost is reserved, but explicit lunch/dinner time is not reserved. Inter-stop breaks are not a reliable meal allowance.

If Vedanta were the only standard-priced record, the present formula would estimate 449 x 2 x 3 = 2694 rupees for one traveler's three-day food cost. That does not mean all six meals take place there, and is not a verified citywide average. Budget/premium tiers would still lack priced records. An unknown price is not free food.

## Recommended behavior, not implemented

Generate each day's sightseeing route, identify a midday stop and an evening stop, and suggest two or three restaurants near each meal anchor that match the chosen tier. A configurable 1-2 km urban radius could be an initial policy; rural trips need a separately reviewed allowance. Consider river side and actual access before calling a venue nearby. Label distance as an estimate without a road-routing service.

Allow about 45-60 minutes per meal plus estimated detour time, check service hours, and rerun feasibility so meals cannot push the trip beyond its daily time limit. These durations/radii are proposed planning assumptions. Show an honest no-verified-option message when coverage is absent. Calculate estimated food expenditure from the day's applicable meal options, rather than a mean over unrelated regions. Keep restaurants separate from sightseeing stop counts.

For illustration only: a day around BHU/Assi should get southern-area meal options, a ghats day central options, and a Sarnath day Sarnath options. A Mirzapur or Chandauli excursion should get route-appropriate options, not the closest Varanasi restaurant regardless of distance. This is not a tested three-day itinerary.

Changes would require targeted edits to app.py and possibly itinenary_logic.py for meal time/feasibility, plus suggestions.html for day/meal grouping. Current frontend fallbacks say 'Affordable', 'Open Daily', and 'Near Varanasi Ghats' when data is missing; those must be changed before presenting incomplete records as trustworthy recommendations. No such edits were made here. The unused dietary filter branch in app.py also still refers to the removed dietary_options column; the current frontend's 'any' path avoids it.

## Verification and limits

Live schema was inspected read-only; official pages and map links were checked. An in-memory SQLite structural check, with MySQL's null-safe equality translated to SQLite IS, verified 14 candidates, one admitted row, no second-run duplicate, and all name/address/hours string lengths within the live column limits. This does not verify MySQL execution. No SQL was run against the project's database, and no unfinished user SQL, migration or application behavior change was run. Complete coverage of all restaurants/all seven regions remains unverified; confirm missing fields directly with venues or their current published menus rather than guessing.
