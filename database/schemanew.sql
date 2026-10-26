-- ============================================================
-- VARANASI SMART TRIP PLANNER
-- SQLite seed data converted from the original MySQL dataset
-- Target schema: Regions + Places from the agreed SQLite schema
-- ============================================================

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ------------------------------------------------------------
-- 1. INSERT REGIONS
-- ------------------------------------------------------------

INSERT OR IGNORE INTO Regions (region_name)
VALUES
    ('BHU and Southern Varanasi'),
    ('Old City and Central Ghats'),
    ('Sarnath and Northern Varanasi'),
    ('Ramnagar and Eastern Riverbank'),
    ('Rural Kashi');

-- ------------------------------------------------------------
-- 2. INSERT PLACES
--
-- Mapping:
-- region_name             -> region_id
-- speciality_description  -> speciality
-- image_url               -> image_url (optional extension)
--
-- Time format: HH:MM
-- Unknown or ambiguous hours: NULL
-- Unknown fees: NULL; original supplied fees are preserved.
-- ------------------------------------------------------------

INSERT INTO Places (
    place_name,
    region_id,
    category,
    speciality,
    description,
    address,
    latitude,
    longitude,
    opening_time,
    closing_time,
    closed_days,
    visit_duration_minutes,
    entry_fee,
    official_url,
    source_checked_date,
    image_url
)
VALUES

-- ============================================================
-- BHU AND SOUTHERN VARANASI
-- ============================================================

(
    'New Vishwanath Temple (BHU VT)',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Spiritual',
    'Shiva temple located inside the Banaras Hindu University campus.',
    NULL,
    'BHU Campus, Varanasi, Uttar Pradesh',
    25.2677, 82.9913,
    NULL, NULL, NULL,
    60, 0.00,
    NULL, NULL, 'new vt.jpeg'
),

(
    'Bharat Kala Bhavan Museum',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Historical',
    'Museum featuring Indian paintings, sculptures and historical artefacts.',
    NULL,
    'BHU Campus, Varanasi, Uttar Pradesh',
    25.2680, 82.9990,
    '10:30', '16:30', 'Sun',
    90, 250.00,
    NULL, NULL, 'bharat kala.jpeg'
),

(
    'Sankat Mochan Hanuman Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Spiritual',
    'Famous Hanuman temple known for its religious significance.',
    NULL,
    'Sankat Mochan Road, Varanasi, Uttar Pradesh',
    25.282942, 83.000169,
    NULL, NULL, NULL,
    45, 0.00,
    NULL, NULL, 'sankat mochan.jpeg'
),

(
    'Durga Kund Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Spiritual',
    'Temple dedicated to Goddess Durga beside Durga Kund.',
    NULL,
    'Durga Kund, Varanasi, Uttar Pradesh',
    25.288700, 82.999044,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, 'durga kund.jpeg'
),

(
    'Tulsi Manas Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Spiritual',
    'Temple dedicated to Lord Rama, associated with the Ramcharitmanas.',
    NULL,
    'Durga Kund Road, Varanasi, Uttar Pradesh',
    25.287183, 83.003620,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, 'tulsi manas.jpeg'
),

(
    'Assi Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Cultural & Leisure',
    'Popular riverside destination for sunrise views, boat rides and Ganga Aarti.',
    NULL,
    'Assi Ghat, Varanasi, Uttar Pradesh',
    25.289460, 83.006090,
    NULL, NULL, NULL,
    60, 0.00,
    NULL, NULL, 'assi.jpeg'
),

(
    'Ravidas Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Spiritual',
    'Riverside location for walking, scenic views and relaxation.',
    NULL,
    'Ravidas Ghat, Varanasi, Uttar Pradesh',
    25.284894, 83.009440,
    NULL, NULL, NULL,
    60, 0.00,
    NULL, NULL, 'ravidas.jpeg'
),

(
    'BHU Campus Gardens',
    (SELECT region_id FROM Regions
     WHERE region_name = 'BHU and Southern Varanasi'),
    'Nature',
    'Green spaces within the university campus for walking and relaxation.',
    NULL,
    'Banaras Hindu University, Varanasi, Uttar Pradesh',
    25.267275, 82.989893,
    '10:00', '18:00', 'Sun',
    90, 0.00,
    NULL, NULL, 'gardens.jpeg'
),

-- ============================================================
-- OLD CITY AND CENTRAL GHATS
-- ============================================================

(
    'Kashi Vishwanath Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Spiritual',
    'One of the most important Hindu pilgrimage destinations in India, dedicated to Lord Shiva.',
    NULL,
    NULL,
    25.310866, 83.010677,
    '03:00', '23:00', NULL,
    150, 0.00,
    NULL, NULL, 'kvt.jpeg'
),

(
    'Dashashwamedh Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Spiritual',
    'A famous ghat on the River Ganges, known for its evening Ganga Aarti and religious ceremonies.',
    NULL,
    NULL,
    25.306300, 83.010150,
    NULL, NULL, NULL,
    90, 0.00,
    NULL, NULL, 'dash ghat.jpeg'
),

(
    'Manikarnika Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Spiritual',
    'One of Varanasi principal cremation ghats, holding deep significance in Hindu religious traditions.',
    NULL,
    NULL,
    25.311102, 83.014142,
    NULL, NULL, NULL,
    60, 0.00,
    NULL, NULL, 'mani.jpeg'
),

(
    'Harishchandra Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Spiritual',
    'An ancient cremation ghat associated with King Harishchandra and Hindu funeral traditions.',
    NULL,
    NULL,
    25.298360, 83.007300,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, 'hari.jpeg'
),

(
    'Man Mandir Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Historical',
    'A historic riverside ghat associated with Man Mandir Palace and its astronomical heritage.',
    NULL,
    NULL,
    25.307660, 83.011142,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, 'manmandir.jpeg'
),

(
    'Nepali Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Historical',
    'A historic temple near Lalita Ghat, known for its Nepalese pagoda-style architecture.',
    NULL,
    NULL,
    25.309972, 83.013000,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, 'nepali.jpeg'
),

(
    'Lalita Ghat',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Cultural & Leisure',
    'A riverside ghat known for its cultural significance and proximity to the Nepali Temple.',
    NULL,
    NULL,
    25.310247, 83.013354,
    NULL, NULL, NULL,
    50, 0.00,
    NULL, NULL, 'lalita.jpeg'
),

(
    'Gaudoliya street Market',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Cultural & Leisure',
    'A busy traditional shopping area known for local shops, street shopping, and access to the old city.',
    NULL,
    NULL,
    25.309180, 83.003480,
    NULL, NULL, NULL,
    85, 0.00,
    NULL, NULL, 'godo.jpeg'
),

(
    'Ganga Boat Ride',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Old City and Central Ghats'),
    'Cultural & Leisure',
    'Boat ride on the River Ganges offering views of Varanasi ghats, temples, and the riverside landscape.',
    NULL,
    NULL,
    25.306300, 83.010150,
    NULL, NULL, NULL,
    120, 200.00,
    NULL, NULL, 'boat.jpeg'
),

-- ============================================================
-- SARNATH AND NORTHERN VARANASI
-- ============================================================

(
    'Dhamek Stupa',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'An ancient Buddhist stupa marking the place traditionally associated with Buddha delivering his first sermon after enlightenment.',
    NULL,
    NULL,
    25.380925, 83.024500,
    '06:00', '17:00', NULL,
    45, 250.00,
    NULL, NULL, NULL
),

(
    'Sarnath Archaeological Museum',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Historical',
    'Museum displaying archaeological discoveries, Buddhist sculptures, historical artefacts, and the original Lion Capital of Ashoka.',
    NULL,
    NULL,
    25.379624, 83.023480,
    '07:00', '17:00', 'Fri',
    60, 5.00,
    NULL, NULL, NULL
),

(
    'Chaukhandi Stupa',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Historical',
    'Historic Buddhist monument traditionally associated with Buddha meeting his first disciples.',
    NULL,
    NULL,
    25.374070, 83.023660,
    '06:00', '18:00', NULL,
    50, 20.00,
    NULL, NULL, NULL
),

(
    'Mulagandha Kuti Vihara',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'Buddhist temple established by the Maha Bodhi Society, known for its murals depicting events from Buddha life.',
    NULL,
    NULL,
    25.381421, 83.023027,
    NULL, NULL, NULL,
    45, 0.00,
    NULL, NULL, NULL
),

(
    'Sarnath Deer Park',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Nature',
    'Green surroundings associated with the historical deer park where Buddha delivered his first sermon.',
    NULL,
    NULL,
    25.381380, 83.026669,
    '08:00', '17:30', NULL,
    45, 40.00,
    NULL, NULL, NULL
),

(
    'Sarnath Archaeological Ruins',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Historical',
    'Ancient remains of Buddhist monasteries, stupas, temples, and other structures excavated at Sarnath.',
    NULL,
    NULL,
    25.380900, 83.024510,
    NULL, NULL, NULL,
    60, 250.00,
    NULL, NULL, NULL
),

(
    'Thai Temple and Monastery',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'Buddhist temple and monastery showcasing Thai architectural traditions and religious practices.',
    NULL,
    NULL,
    25.378320, 83.021740,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, NULL
),

(
    'Giant Buddha Statue',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'An approximately 80-foot standing statue of Buddha located within the Thai temple complex.',
    NULL,
    NULL,
    25.377749, 83.021300,
    NULL, NULL, NULL,
    30, 0.00,
    NULL, NULL, NULL
),

(
    'Chinese Buddhist Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'Buddhist temple representing Chinese Buddhist traditions and architectural influences.',
    NULL,
    NULL,
    25.379603, 83.028297,
    '08:00', '18:00', NULL,
    30, 0.00,
    NULL, NULL, NULL
),

(
    'Tibetan Buddhist Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'Buddhist religious site reflecting Tibetan Buddhist traditions and practices.',
    NULL,
    NULL,
    25.377020, 83.026952,
    NULL, NULL, NULL,
    50, 0.00,
    NULL, NULL, NULL
),

(
    'Jain Temple, Sarnath',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Spiritual',
    'Jain religious site associated with Shreyansnath, the eleventh Jain Tirthankara.',
    NULL,
    NULL,
    25.371673, 83.025120,
    '08:00', '18:00', NULL,
    30, 0.00,
    NULL, NULL, NULL
),

(
    'Garden of Spiritual Wisdom',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Sarnath and Northern Varanasi'),
    'Nature',
    'A landscaped garden featuring greenery, educational exhibits, and plants associated with traditional wellness.',
    NULL,
    NULL,
    25.373848, 83.022426,
    '07:00', '17:30', NULL,
    60, 0.00,
    NULL, NULL, NULL
),

-- ============================================================
-- RAMNAGAR AND EASTERN RIVERBANK
-- ============================================================

(
    'Ramnagar Fort',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Ramnagar and Eastern Riverbank'),
    'Historical',
    'An 18th-century riverside fort of the Kashi Naresh, built in Mughal style with sandstone and overlooking the Ganges.',
    NULL,
    NULL,
    25.268600, 83.027500,
    '10:00', '17:00', NULL,
    90, 20.00,
    NULL, NULL, 'ramnagar_fort.jpeg'
),

(
    'Ramnagar Fort Museum',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Ramnagar and Eastern Riverbank'),
    'Historical',
    'A museum inside the fort displaying vintage cars, royal costumes, weapons, palanquins and antique clocks of the Banaras royal family.',
    NULL,
    NULL,
    25.268800, 83.027200,
    '10:00', '17:00', NULL,
    75, 20.00,
    NULL, NULL, 'ramnagar_museum.jpeg'
),

(
    'Ramnagar Riverfront',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Ramnagar and Eastern Riverbank'),
    'Cultural & Leisure',
    'A quiet stretch of the Ganges bank beside the fort, good for a calm walk and views across the river to the Varanasi ghats.',
    NULL,
    NULL,
    25.269500, 83.025000,
    NULL, NULL, NULL,
    45, 0.00,
    NULL, NULL, 'ramnagar_riverfront.jpeg'
),

(
    'Ganga Viewpoints on the Eastern Bank',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Ramnagar and Eastern Riverbank'),
    'Cultural & Leisure',
    'The sandy eastern bank opposite the main ghats, offering a wide view of the Varanasi skyline, especially at sunrise and sunset.',
    NULL,
    NULL,
    25.306000, 83.019000,
    NULL, NULL, NULL,
    60, 0.00,
    NULL, NULL, 'ganga_viewpoint.jpeg'
),

-- ============================================================
-- RURAL KASHI
-- ============================================================

(
    'Kardameshwar Mahadev Temple',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Rural Kashi'),
    'Spiritual',
    'An ancient Shiva temple in Kandwa village, known for its old stone architecture and a peaceful setting beside a pond.',
    NULL,
    NULL,
    25.367700, 82.960800,
    '05:00', '20:00', NULL,
    60, 0.00,
    NULL, NULL, 'kardameshwar.jpeg'
),

(
    'Rural Temple Circuits',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Rural Kashi'),
    'Spiritual',
    'A route through village temples and shrines around Varanasi, linked to the traditional Panchkosi pilgrimage.',
    NULL,
    NULL,
    25.367700, 82.960800,
    NULL, NULL, NULL,
    120, 0.00,
    NULL, NULL, 'rural_temples.jpeg'
),

(
    'Village Walks and Countryside Experiences',
    (SELECT region_id FROM Regions
     WHERE region_name = 'Rural Kashi'),
    'Cultural & Leisure',
    'Guided walks through farmland and villages, with a look at rural life, local crafts and village food.',
    NULL,
    NULL,
    25.367700, 82.960800,
    NULL, NULL, NULL,
    150, 0.00,
    NULL, NULL, 'village_walk.jpeg'
);

COMMIT;

-- ------------------------------------------------------------
-- 3. VALIDATION QUERIES
-- Run these after the seed script.
-- ------------------------------------------------------------

-- Count the regions.
SELECT COUNT(*) AS total_regions
FROM Regions;

-- Count the inserted places.
SELECT COUNT(*) AS total_places
FROM Places;

-- Check places whose region relationship is missing.
SELECT p.place_id, p.place_name
FROM Places AS p
LEFT JOIN Regions AS r ON r.region_id = p.region_id
WHERE r.region_id IS NULL;

-- Display place counts by region.
SELECT
    r.region_name,
    COUNT(p.place_id) AS total_places
FROM Regions AS r
LEFT JOIN Places AS p ON p.region_id = r.region_id
GROUP BY r.region_id, r.region_name
ORDER BY r.region_name;

-- Display distinct categories.
SELECT DISTINCT category
FROM Places
ORDER BY category;
