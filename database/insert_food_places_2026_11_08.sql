-- Restaurant research checked 2026-11-08. Review before running.
-- This file has NOT been run against your database.
-- Prices are USER-APPROVED DEMO ESTIMATES per person per meal, not confirmed restaurant bills.
-- Exception: Vedanta retains the published INR 449 thali benchmark.
-- Tiers: budget <=250; standard >250 to 600; premium >600 INR.
-- Cafe/patisserie estimates represent a light meal, not a verified full-meal menu.
-- Missing coordinates now use USER-APPROVED area-level DEMO ESTIMATES (3 decimals).
-- Missing hours now use labelled DEMO ESTIMATES. Existing sourced values are preserved.
-- Approximate coordinates enable demo ranking, not accurate distances/navigation.
-- 36 records have prices, tiers, coordinates and display hours; some addresses remain NULL.
-- The app excludes rows without a matching budget_tier or coordinates.
-- Vedanta: 449 is its published Shahi Thali price, not an average bill.
-- Tiers use the project ranges approved by the user.
-- opening_hours contains opening AND closing times in one text field.
-- Re-running this plain INSERT may create duplicates.
-- Sources and missing fields: FOOD_RESEARCH_2026_11_08.md

USE personalized_travel_planner;

INSERT INTO food_places
(
    name,
    latitude,
    longitude,
    address,
    price_range_per_person,
    opening_hours,
    budget_tier
)
VALUES
(
    'Vedanta by Ghoomar',
    25.3090378,
    83.0016921,
    'Luxa Road, near Godowlia Chowk, Varanasi 221010',
    449.00,
    'Daily 07:00-00:00; breakfast 07:00-11:00',
    'standard'
),

(
    'Pizzeria Vaatika Cafe - Assi',
    25.289307,
    83.006107,
    'B-1/178 Panch Mandir, Assi Ghat, Varanasi 221005',
    450.00,
    '09:00-22:00 (demo estimate)',
    'standard'
),

(
    'Pizzeria Vaatika Cafe - Cantonment',
    25.335,
    82.980,
    'Shop 1, 4, Mother Teresa Marg, Patel Nagar, Cantonment, Varanasi 221002',
    450.00,
    '09:00-22:00 (demo estimate)',
    'standard'
),

(
    'Sarnath Cafe and Saini Guest House',
    25.369,
    83.025,
    'SA-15/129 K-1, Mawaiya Road, opposite Tibetan Institute, Sarnath, Varanasi 221007',
    225.00,
    '09:00-22:00 (demo estimate)',
    'budget'
),

(
    'Arzoo - Ramada Varanasi Katesar',
    25.302,
    83.043,
    'Ramada, Katesar Ramnagar Road, Chandauli 221008',
    900.00,
    'Daily 07:00-22:30',
    'premium'
),

(
    'Baati Chokha - Dafi',
    25.256,
    82.988,
    NULL,
    300.00,
    'Daily 09:00-23:00',
    'standard'
),

(
    'Baati Chokha - Ahraura',
    25.026,
    83.021,
    'State Highway 5A, near Ahraura Toll Plaza, Ahraura, Mirzapur',
    300.00,
    'Daily 09:00-23:00',
    'standard'
),

(
    'Baati Chokha - Teliabagh',
    25.330,
    82.993,
    NULL,
    350.00,
    'Daily 09:00-23:00',
    'standard'
),

(
    'Aroma - Konark Grand Hotel',
    25.136,
    82.558,
    NULL,
    650.00,
    'Lunch 12:30-15:30; dinner 19:30-23:00',
    'premium'
),

(
    'Clove - Konark Grand Hotel',
    25.136,
    82.558,
    NULL,
    500.00,
    'Breakfast 07:30-10:30; buffet availability must be confirmed',
    'standard'
),

(
    'Cafe Express - Konark Grand Hotel',
    25.136,
    82.558,
    NULL,
    400.00,
    '24 hours',
    'standard'
),

(
    'Tadka - Ramada Plaza JHV',
    25.335,
    82.977,
    'Ramada Plaza JHV, The Mall, Cantonment, Varanasi 221002',
    1000.00,
    'Dinner 19:30-23:00',
    'premium'
),

(
    'The Palate - Ramada Plaza JHV',
    25.335,
    82.977,
    'Ramada Plaza JHV, The Mall, Cantonment, Varanasi 221002',
    1100.00,
    'Breakfast 07:00-10:30 (Sun 11:00); lunch 12:30-15:00; snacks 15:00-19:00; dinner 19:30-23:00',
    'premium'
),

(
    'Temptationz - Ramada Plaza JHV',
    25.335,
    82.977,
    'Ramada Plaza JHV, The Mall, Cantonment, Varanasi 221002',
    450.00,
    'Daily 10:00-22:00',
    'standard'
);

INSERT INTO food_places
(
    name,
    latitude,
    longitude,
    address,
    price_range_per_person,
    opening_hours,
    budget_tier
)
VALUES

(
    'Varuna - Taj Ganges',
    25.338,
    82.989,
    'Taj Ganges, Nadesar Grounds, Varanasi 221002',
    1400.00,
    'Lunch 12:30-15:00; dinner 19:00-23:00',
    'premium'
),

(
    'Chowk - Taj Ganges',
    25.338,
    82.989,
    'Taj Ganges, Nadesar Grounds, Varanasi 221002',
    1200.00,
    '09:00-22:00 (demo estimate)',
    'premium'
),

(
    'Atrium Cafe - HHI Varanasi',
    25.325,
    82.991,
    'HHI, C-21/3 Maldahiya Road, near Maldahiya Crossing, Varanasi',
    750.00,
    '07:30-22:30',
    'premium'
),

(
    'Brown Bread Bakery',
    25.304,
    83.009,
    'Ganga Mahal, D 25/42, Bangali Tola Road, Pandey Ghat, Varanasi 221001',
    350.00,
    '09:00-22:00 (demo estimate)',
    'standard'
),

(
    'Canton Royale - Hotel Surya Kaiser Palace',
    25.337,
    82.981,
    'Hotel Surya, S.20/51 A-5, The Mall Road, Cantonment, Varanasi 221002',
    800.00,
    '09:00-22:00 (demo estimate)',
    'premium'
),

(
    'Mangi Ferra Cafe - Hotel Surya Kaiser Palace',
    25.337,
    82.981,
    'Hotel Surya, S.20/51 A-5, The Mall Road, Cantonment, Varanasi 221002',
    500.00,
    '09:00-22:00 (demo estimate)',
    'standard'
),

(
    'Darbhanga - BrijRama Palace',
    25.305,
    83.010,
    'BrijRama Palace, Darbhanga Ghat, Dashashwamedh, Varanasi 221001',
    1800.00,
    '09:00-22:00 (demo estimate)',
    'premium'
),

(
    'Udayan Terrace - BrijRama Palace',
    25.305,
    83.010,
    'BrijRama Palace, Darbhanga Ghat, Dashashwamedh, Varanasi 221001',
    1600.00,
    '09:00-22:00 (demo estimate)',
    'premium'
),

(
    'Divo - DoubleTree by Hilton Varanasi',
    25.359,
    83.002,
    'DoubleTree, SA 2/320 Chhota Lalpur, Pandeypur, Varanasi 221001',
    1000.00,
    '09:00-22:00 (demo estimate)',
    'premium'
),

(
    'Anandam Veg Thali - DoubleTree by Hilton Varanasi',
    25.359,
    83.002,
    'DoubleTree, SA 2/320 Chhota Lalpur, Pandeypur, Varanasi 221001',
    900.00,
    '09:00-22:00 (demo estimate)',
    'premium'
);

INSERT INTO food_places
(
    name,
    latitude,
    longitude,
    address,
    price_range_per_person,
    opening_hours,
    budget_tier
)
VALUES
(
    'Biryani Mahal Banaras',
    25.295493,
    83.0023,
    'P-94-A, Anandbagh, Bhelupur, Ravindrapuri Road, Varanasi',
    300,
    '11:00-23:00 (demo estimate)',
    'standard'
),

(
    'Aman-E-Khaas',
    25.296953,
    83.002523,
    'IP Mall, Bhelupur Road, Broadway, near Vijaya Cinema, Varanasi',
    800,
    '11:00-23:00 (demo estimate)',
    'premium'
),

(
    'Dawat e Zaika',
    25.295538,
    83.001922,
    'P-89, Anandbagh, Bhelupur, Varanasi',
    700,
    '11:00-23:00 (demo estimate)',
    'premium'
),

(
    'DAWAT E KHAS - The Triumph Hotel',
    25.301082,
    82.969041,
    'Plot 166 and 167, DLW Road, Manduadih Chauraha, Varanasi',
    300,
    '11:00-23:00 (demo estimate)',
    'standard'
),

(
    'Domino''s Pizza - Sarnath',
    25.37,
    83.025,
    'SA 15/3, Mavaiya, Sarnath, Varanasi 221007',
    350,
    '10:59-23:59',
    'standard'
),

(
    'Domino''s Pizza - JHV Mall',
    25.335,
    82.977,
    'Counter FC06, second floor, JHV Mall, Cantonment, Varanasi',
    350,
    '10:59-22:59',
    'standard'
),

(
    'Domino''s Pizza - Susuwahi',
    25.258,
    82.979,
    'Gata 2089, Village Susuwahi, Sadar, Varanasi',
    350,
    '10:59-23:59',
    'standard'
),

(
    'Domino''s Pizza - Kandwa',
    25.269,
    82.965,
    'Arazi 546 old / 1270Ka new, Mauza Kandwa, Varanasi',
    350,
    '10:59-23:59',
    'standard'
),

(
    'Domino''s Pizza - Vijaya Mall',
    25.297,
    83.003,
    'Unit 9, ground floor, IP Vijaya Mall, B-20/44A-4A, Bhelupur, Varanasi',
    350,
    '11:00-23:59',
    'standard'
),

(
    'Domino''s Pizza - PDR Mall',
    25.309,
    83.003,
    'Units 11-13, ground floor, PDR Mall, D-48/142, Ramapura, Varanasi',
    350,
    '10:00-23:59',
    'standard'
),

(
    'Deena Chat Bhandar - Luxa',
    25.309,
    83.002,
    'D47/184, Luxa Road, near PDR Mall, Varanasi',
    200,
    '15:00-22:00 (demo estimate)',
    'budget'
),

(
    'Kerala Cafe - Bhelupur',
    25.299,
    83.001,
    'B20/44, Bhelupur Road, Varanasi',
    225,
    '08:00-22:00 (demo estimate)',
    'budget'
);
ALTER TABLE food_places
ADD COLUMN address VARCHAR(100) AFTER longitude;