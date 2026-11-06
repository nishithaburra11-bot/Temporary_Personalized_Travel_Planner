-- Active: 1791466243409@@localhost@3306@personalized_travel_planner
-- Varanasi places table (MySQL syntax)
-- Coordinates are approximate - verify before using in the final app.

USE personalized_travel_planner;




CREATE TABLE IF NOT EXISTS places (
    place_id INT AUTO_INCREMENT PRIMARY KEY,
    place_name VARCHAR(150) NOT NULL,
    region_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    speciality_description TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    address VARCHAR(255),
    opening_time VARCHAR(30),
    closing_time VARCHAR(30),
    closed_days VARCHAR(100),
    visit_duration_minutes INT,
    entry_fee DECIMAL(10, 2) DEFAULT 0.00,
    image_url TEXT
);


INSERT INTO places (
    place_name,
    region_name,
    category,
    speciality_description,
    latitude,
    longitude,
    address,
    opening_time,
    closing_time,
    closed_days,
    visit_duration_minutes,
    entry_fee,
    image_url
)
VALUES
(
    'New Vishwanath Temple (BHU VT)',
    'BHU and Southern Varanasi',
    'spiritual',
    'Shiva temple located inside the Banaras Hindu University campus.',
    25.2677, 82.9913,
    'BHU Campus, Varanasi, Uttar Pradesh',
    '05:00:00 13:00:00','12:00:00 21:00:00', NULL,
    60, 0.00, 'new vt.jpeg'
),
(
    'Bharat Kala Bhavan Museum',
    'BHU and Southern Varanasi',
    'historical',
    'Museum featuring Indian paintings, sculptures and historical artefacts.',
    25.2680, 82.9990,
    'BHU Campus, Varanasi, Uttar Pradesh',
    '10:30:00', '16:30:00', 'sunday',
    90, 250.00, 'bharat kala.jpeg'
),
(
    'Sankat Mochan Hanuman Temple',
    'BHU and Southern Varanasi',
    'spiritual',
    'Famous Hanuman temple known for its religious significance.',
    25.282942, 83.000169,
    'Sankat Mochan Road, Varanasi, Uttar Pradesh',
    '04:00:30 15:00:00', '12:00:00 22:00:00', NULL,
    45, 0.00, 'sankat mochan.jpeg'
),
(
    'Durga Kund Temple',
    'BHU and Southern Varanasi',
    'spiritual',
    'Temple dedicated to Goddess Durga beside Durga Kund.',
    25.288700, 82.999044,
    'Durga Kund, Varanasi, Uttar Pradesh',
    '05:00:00 16:00:00', '12:00:00 21:00:00', NULL,
    30, 0.00, 'durga kund.jpeg'
),
(
    'Tulsi Manas Temple',
    'BHU and Southern Varanasi',
    'spiritual',
    'Temple dedicated to Lord Rama, associated with the Ramcharitmanas.',
    25.287183, 83.00362,
    'Durga Kund Road, Varanasi, Uttar Pradesh',
    NULL, NULL, NULL,
    30, 0.00, 'tulsi manas.jpeg'
),
(
    'Assi Ghat',
    'BHU and Southern Varanasi',
    'cultural & leisure',
    'Popular riverside destination for sunrise views, boat rides and Ganga Aarti.',
    25.289460, 83.006090,
    'Assi Ghat, Varanasi, Uttar Pradesh',
    NULL, NULL, NULL,
    60, 0.00, 'assi.jpeg'
),
(
    'Ravidas Ghat',
    'BHU and Southern Varanasi',
    'spiritual',
    'Riverside location for walking, scenic views and relaxation.',
    25.284894, 83.009440,
    'Ravidas Ghat, Varanasi, Uttar Pradesh',
    NULL, NULL, NULL,
    60, 0.00, 'ravidas.jpeg'
),
(
    'BHU Campus Gardens',
    'BHU and Southern Varanasi',
    'Nature',
    'Green spaces within the university campus for walking and relaxation.',
    25.267275, 82.989893,
    'Banaras Hindu University, Varanasi, Uttar Pradesh',
    '10:00:00', '18:00:00', 'sunday',
    90, 0.00, 'gardens.jpeg'
);
ALTER TABLE places DROP COLUMN address;


INSERT INTO places (
    place_name,
    region_name,
    category,
    speciality_description,
    latitude,
    longitude,
    opening_time,
    closing_time,
    closed_days,
    visit_duration_minutes,
    entry_fee,
    image_url
)
VALUES
(
    'Kashi Vishwanath Temple',
    'Old City and Central Ghats',
    'Spiritual',
    'One of the most important Hindu pilgrimage destinations in India, dedicated to Lord Shiva.',
    25.310866,
    83.010677,
   '03:00:00',
    '23:00:00',
    NULL,
    150,
    0.00,
    'kvt.jpeg'
),

(
    'Dashashwamedh Ghat',
    'Old City and Central Ghats',
    'Spiritual',
    'A famous ghat on the River Ganges, known for its evening Ganga Aarti and religious ceremonies.',
    25.306300,
    83.0101500,
    NULL,
    NULL,
    NULL,
    90,
    0.00,
    'dash ghat.jpeg'
),


(
    'Manikarnika Ghat',
    'Old City and Central Ghats',
    'Spiritual',
    'One of Varanasis principal cremation ghats, holding deep significance in Hindu religious traditions.',
    25.311102,
    83.014142,
    NULL,
    NULL,
    NULL,
    60,
    0.00,
    'mani.jpeg'
),


(
    'Harishchandra Ghat',
    'Old City and Central Ghats',
    'Spiritual',
    'An ancient cremation ghat associated with King Harishchandra and Hindu funeral traditions.',
    25.2983600,
    83.007300,
    NULL,
    NULL,
    NULL,
    30,
    0.00,
    'hari.jpeg'
),

(
    'Man Mandir Ghat',
    'Old City and Central Ghats',
    'Historical',
    'A historic riverside ghat associated with Man Mandir Palace and its astronomical heritage.',
    25.3076600,
    83.011142,
    NULL,
    NULL,
    NULL,
    30,
    0.00,
    'manmandir.jpeg'
),


(
    'Nepali Temple',
    'Old City and Central Ghats',
    'Historical',
    'A historic temple near Lalita Ghat, known for its Nepalese pagoda-style architecture.',
    25.309972,
    83.0130000,
    NULL,
    NULL,
    NULL,
    30,
    0.00,
    'nepali.jpeg'
),

(
    'Lalita Ghat',
    'Old City and Central Ghats',
    'Cultural & Leisure',
    'A riverside ghat known for its cultural significance and proximity to the Nepali Temple.',
    25.310247,
    83.013354,
    NULL,
    NULL,
    NULL,
    50,
    0.00,
    'lalita.jpeg'
),

(
    'Gaudoliya street Market',
    'Old City and Central Ghats',
    'Cultural & Leisure',
    'A busy traditional shopping area known for local shops, street shopping, and access to the old city.',
    25.30918,
    83.00348,
    NULL,
    NULL,
    NULL,
    85,
    0.00,
    'godo.jpeg'
),

(
    'Ganga Boat Ride',
    'Old City and Central Ghats',
    'Cultural & Leisure',
    'Boat ride on the River Ganges offering views of Varanasi ghats, temples, and the riverside landscape.',
    25.306300,
    83.0101500,
    NULL,
    NULL,
    NULL,
    120,
    200.00,
    'boat.jpeg'
);
USE personalized_travel_planner;

INSERT INTO places (
    place_name,
    region_name,
    category,
    speciality_description,
    latitude,
    longitude,
    opening_time,
    closing_time,
    closed_days,
    visit_duration_minutes,
    entry_fee,
    image_url
)
VALUES

(
    'Dhamek Stupa',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'An ancient Buddhist stupa marking the place traditionally associated with Buddha delivering his first sermon after enlightenment.',
    25.380925,
    83.0245000,
    '06:00:00',
    '17:00:00',
    NULL,
    45,
    250.00,
    'dhamek.jpg'
),

(
    'Sarnath Archaeological Museum',
    'Sarnath and Northern Varanasi',
    'Historical',
    'Museum displaying archaeological discoveries, Buddhist sculptures, historical artefacts, and the original Lion Capital of Ashoka.',
    25.379624,
    83.02348,
    '07:00:00',
    '17:00:00',
    'Friday',
    60,
    5.00,
    'sarmuseum.jpg'
),

(
    'Chaukhandi Stupa',
    'Sarnath and Northern Varanasi',
    'Historical',
    'Historic Buddhist monument traditionally associated with Buddha meeting his first disciples.',
    25.3740700,
    83.0236600,
    '06:00:00',
    '18:00:00',
    NULL,
    50,
    20.00,
    'chauk.jpg'
),

(
    'Mulagandha Kuti Vihara',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'Buddhist temple established by the Maha Bodhi Society, known for its murals depicting events from Buddha’s life.',
    25.3814210,
    83.0230270,
    '08:00:00 13:30:00',
    '11:30:00 17:30:00',
    NULL,
    45,
    0.00,
    'mulgandh.jpg'
),

(
    'Sarnath Deer Park',
    'Sarnath and Northern Varanasi',
    'Nature',
    'Green surroundings associated with the historical deer park where Buddha delivered his first sermon.',
    25.38138,
    83.026669,
    '08:00:00',
    '17:30:00',
    NULL,
    45,
    40.00,
    'deer.jpg'
),

(
    'Sarnath Archaeological Ruins',
    'Sarnath and Northern Varanasi',
    'Historical',
    'Ancient remains of Buddhist monasteries, stupas, temples, and other structures excavated at Sarnath.',
    25.3809000,
    83.0245100,
    NULL,
    '08:00:00',
    '18:00:00',
    60,
    250.00,
    'archruins.jpeg'
),

(
    'Thai Temple and Monastery',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'Buddhist temple and monastery showcasing Thai architectural traditions and religious practices.',
    25.3783200,
    83.0217400,
    NULL,
    NULL,
    NULL,
    30,
    0.00,
    NULL
),

(
    'Giant Buddha Statue',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'An approximately 80-foot standing statue of Buddha located within the Thai temple complex.',
    25.377749,
    83.0213,
    NULL,
    NULL,
    NULL,
    30,
    0.00,
    NULL
),

(
    'Chinese Buddhist Temple',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'Buddhist temple representing Chinese Buddhist traditions and architectural influences.',
    25.379603,
    83.028297,
    '08:00:00',
    '18:00:00',
    NULL,
    30,
    0.00,
    NULL
),

(
    'Tibetan Buddhist Temple',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'Buddhist religious site reflecting Tibetan Buddhist traditions and practices.',
    25.377020,
    83.026952,
    '08:30:00 14:30:00',
    '11:50:00 05:00:00',
    NULL,
    50,
    0.00,
    NULL
),

(
    'Jain Temple, Sarnath',
    'Sarnath and Northern Varanasi',
    'Spiritual',
    'Jain religious site associated with Shreyansnath, the eleventh Jain Tirthankara.',
    25.371673,
    83.02512,
    '08:00:00',
    '18:00:00',
    NULL,
    30,
    0.00,
    NULL
),
(
    'Garden of Spiritual Wisdom',
    'Sarnath and Northern Varanasi',
    'Nature',
    'A landscaped garden featuring greenery, educational exhibits, and plants associated with traditional wellness.',
    25.373848,
    83.022426,
    '07:00:00',
    '17:30:00',
    NULL,
    60,
    0.00,
    NULL
);

INSERT INTO places (
    place_name,
    region_name,
    category,
    speciality_description,
    latitude,
    longitude,
    opening_time,
    closing_time,
    closed_days,
    visit_duration_minutes,
    entry_fee,
    image_url
)
VALUES

(
    'Ramnagar Fort',
    'Ramnagar and Eastern Riverbank',
    'Historical',
    'An 18th-century riverside fort of the Kashi Naresh, built in Mughal style with sandstone and overlooking the Ganges.',
    25.268600,
    83.027500,
    '10:00:00',
    '17:00:00',
    NULL,
    90,
    20.00,
    'ramnagar_fort.jpeg'
),

(
    'Ramnagar Fort Museum',
    'Ramnagar and Eastern Riverbank',
    'Historical',
    'A museum inside the fort displaying vintage cars, royal costumes, weapons, palanquins and antique clocks of the Banaras royal family.',
    25.268800,
    83.027200,
    '10:00:00',
    '17:00:00',
    NULL,
    75,
    20.00,
    'ramnagar_museum.jpeg'
),

(
    'Ramnagar Riverfront',
    'Ramnagar and Eastern Riverbank',
    'Cultural & Leisure',
    'A quiet stretch of the Ganges bank beside the fort, good for a calm walk and views across the river to the Varanasi ghats.',
    25.269500,
    83.025000,
    NULL,
    NULL,
    NULL,
    45,
    0.00,
    'ramnagar_riverfront.jpeg'
),

(
    'Ganga Viewpoints on the Eastern Bank',
    'Ramnagar and Eastern Riverbank',
    'Cultural & Leisure',
    'The sandy eastern bank opposite the main ghats, offering a wide view of the Varanasi skyline, especially at sunrise and sunset.',
    25.306000,
    83.019000,
    NULL,
    NULL,
    NULL,
    60,
    0.00,
    'ganga_viewpoint.jpeg'
),


(
    'Kardameshwar Mahadev Temple',
    'Outer Varanasi and Countryside',
    'Spiritual',
    'An ancient Shiva temple in Kandwa village, known for its old stone architecture and a peaceful setting beside a pond.',
    25.367700,
    82.960800,
    '05:00:00',
    '20:00:00',
    NULL,
    60,
    0.00,
    'kardameshwar.jpeg'
),

(
    'Rural Temple Circuits',
    'Outer Varanasi and Countryside',
    'Spiritual',
    'A route through village temples and shrines around Varanasi, linked to the traditional Panchkosi pilgrimage.',
    25.367700,
    82.960800,
    NULL,
    NULL,
    NULL,
    120,
    0.00,
    'rural_temples.jpeg'
),

(
    'Village Walks and Countryside Experiences',
    'Outer Varanasi and Countryside',
    'Cultural & Leisure',
    'Guided walks through farmland and villages, with a look at rural life, local crafts and village food.',
    25.367700,
    82.960800,
    NULL,
    NULL,
    NULL,
    150,
    0.00,
    'village_walk.jpeg'
);

UPDATE places
SET region_name = 'Rural Kashi'
WHERE region_name = 'Outer Varanasi and Countryside';

UPDATE places SET closing_time='11:00:00 17:00:00' WHERE place_name='Tibetan Buddhist Temple';
UPDATE places SET opening_time = '08:00:00', closing_time = '18:00:00', closed_days = NULL WHERE place_name='Sarnath Archaeological Ruins';
UPDATE places SET opening_time = '08:30:00', closing_time = '17:00:00' WHERE place_name='Tibetan Buddhist Temple';

UPDATE places SET region_name='BHU and Southern Varanasi',category='cultural & leisure' WHERE place_name='Assi Ghat';

-- ------------------------------------------------------------
-- REGIONS
-- (MySQL: use INSERT IGNORE instead of INSERT OR IGNORE,
--  and make region_name UNIQUE)
-- ------------------------------------------------------------

INSERT INTO places (
    place_name,
    region_name,
    category,
    speciality_description,
    latitude,
    longitude,
    opening_time,
    closing_time,
    closed_days,
    visit_duration_minutes,
    entry_fee,
    image_url
)
VALUES


(
    'Rajdari Waterfall',
    'Chandauli',
    'Nature',
    'Scenic waterfall inside the Chandraprabha Wildlife Sanctuary, best seen during and after the monsoon.',
    24.9468900,
    83.168660,          -- APPROX
    '06:00:00',
    '18:00:00',
    NULL,
    130,
    0.00,               -- fee not confirmed
    'rajdari.jpg'
),

(
    'Devdari Waterfall',
    'Chandauli',
    'Nature',
    'Waterfall close to Rajdari, usually visited together with it.',
    24.960000,
    83.172590,          -- APPROX (about 700 m from Rajdari)
    NULL,
    NULL,
    NULL,
    110,
    0.00,
    'devdari.jpg'
),

(
    'Chandraprabha Wildlife Sanctuary',
    'Chandauli',
    'Nature',
    'Forest sanctuary of about 78 square km with waterfalls, viewpoints, picnic spots and wildlife.',
    24.946000,
    83.169900,          -- centre of the sanctuary boundary box
    '09:00:00',
    '17:00:00',
    NULL,
    210,
    3000.00,
    'chandrawild.jpg'
),

(
    'Chandraprabha Waterfall',
    'Chandauli',
    'Nature',
    'Waterfall on the Chandraprabha river within the sanctuary area near Naugarh.',
    24.940000,
    83.090000,          -- APPROX, LOW CONFIDENCE
    '08:00:00',
    '16:00:00',
    NULL,
    120,
    0.00,
    'chandrawater.jpg'
),

(
    'Aurvatand Waterfall',
    'Chandauli',
    'Nature',
    'Waterfall on the Karmanasa river, with prehistoric rock paintings in nearby caves.',
    24.865668,
    83.353236,          -- APPROX, LOW CONFIDENCE
    NULL,
    NULL,
    NULL,
    110,
    0.00,
    'auravtand.jpg'
),

(
    'Karmnasha Waterfall',
    'Chandauli',
    'Nature',
    'Waterfall on the Karmanasa river in the eastern part of Chandauli district.',
    24.990000,
    83.360000,          -- APPROX, LOW CONFIDENCE
    NULL,
    NULL,
    NULL,
    100,
    0.00,
    'karmnasha.jpg'
),

(
    'Latif Shah Dam',
    'Chandauli',
    'Nature',
    'Dam and reservoir near Naugarh, popular for quiet views and picnics.',
    24.945000,
    83.240000,          -- APPROX, LOW CONFIDENCE
    '07:00:00',
    '20:00:00',
    NULL,
    45,
    0.00,
    'latif.jpg'
),




(
    'Lakhaniya Dari Waterfall',
    'Mirzapur and Chunar',
    'Nature',
    'Waterfall surrounded by greenery in the Chunar area, at its best in the monsoon.',
    24.95860,
    83.00890,          -- APPROX, LOW CONFIDENCE
    '09:00:00',
    '17:00:00',
    NULL,
    150,
    0.00,
    'lakhaniya.jpeg'
),

(
    'Vindham Falls (Wyndham Falls)',
    'Mirzapur and Chunar',
    'Nature',
    'Waterfall near Mirzapur with a small park and ancient rock paintings in nearby caves.',
    25.030000,
    82.610000,          -- APPROX (about 14 km from Mirzapur)
    '06:00:00',
    '18:00:00',
    NULL,
    110,
    0.00,
    'vindhamfalls.jpg'
),

(
    'Tanda Falls',
    'Mirzapur and Chunar',
    'Nature',
    'Waterfall in the Vindhya hills near Mirzapur, with rocky terrain around it.',
    25.0579000,
    82.700000,          -- APPROX, LOW CONFIDENCE
    NULL,
    NULL,
    NULL,
    110,
    0.00,
    'tanda.jpg'
),

(
    'Chunar Fort',
    'Mirzapur and Chunar',
    'Historical',
    'Historic sandstone hill fort on the Ganges, linked with Sher Shah Suri, the Mughals and the British.',
    25.125500,
    82.874700,          -- VERIFIED (Wikipedia)
    '09:00:00',
    '17:00:00',
    NULL,
    90,
    0.00,
    'chunar.jpg'
),

(
    'Sidh Nath Dari',
    'Mirzapur and Chunar',
    'Nature',
    'Waterfall and picnic spot among the Vindhya hills near Chunar.',
    24.964000,
    82.821700,          -- APPROX, LOW CONFIDENCE
    '06:00:00',
    '19:00:00',
    NULL,
    90,
    0.00,
    'sidh.jpg'
),

(
    'Jargo Dam',
    'Mirzapur and Chunar',
    'Nature',
    'Dam and reservoir in the Chunar area, suited to a relaxed scenic stop.',
    25.0256740,
    82.880000,          -- APPROX, LOW CONFIDENCE
    NULL,
    NULL,
    NULL,
    60,
    0.00,
    'jargo.jpg'
),

(
    'Vindhyachal Temple (Maa Vindhyavasini)',
    'Mirzapur and Chunar',
    'Spiritual',
    'Major Shakti Peeth dedicated to Goddess Vindhyavasini, on the banks of the Ganges.',
    25.315378,
    82.948117,          -- from a temple listing, check on the map
    '05:30:00',
    '21:30:00',         -- from a temple listing, confirm locally
    NULL,
    60,
    0.00,
    'vindhyachal.jpg'
),

(
    'Ashtabhuja Temple',
    'Mirzapur and Chunar',
    'Spiritual',
    'Hilltop temple of Goddess Ashtabhuja (Saraswati), part of the Vindhyachal Trikon circuit.',
    25.125000,
    82.968000,          -- APPROX, LOW CONFIDENCE
    '04:00:00',
    '21:00:00',
    NULL,
    45,
    0.00,
    'ashta.jpg'
),

(
    'Kali Khoh Temple',
    'Mirzapur and Chunar',
    'Spiritual',
    'Ancient cave temple dedicated to Goddess Kali, part of the Vindhyachal Trikon circuit.',
    25.154000,
    82.495000,          -- APPROX, LOW CONFIDENCE
    '04:00:00',
    '21:00:00',
    NULL,
    30,
    0.00,
    'kali_khoh.jpeg'
);

UPDATE places SET region_id = 6 WHERE region_name = 'Chandauli';
UPDATE places SET region_id = 7 WHERE region_name = 'Mirzapur and Chunar';

UPDATE places SET image_url = 'dhamek.jpg'         WHERE place_name = 'Dhamek Stupa';
UPDATE places SET image_url = 'sarmuseum.jpg'       WHERE place_name = 'Sarnath Archaeological Museum';
UPDATE places SET image_url = 'chauk.jpg'     WHERE place_name = 'Chaukhandi Stupa';
UPDATE places SET image_url = 'mulagandh.jpg'      WHERE place_name = 'Mulagandha Kuti Vihara';
UPDATE places SET image_url = 'deer.jpg'            WHERE place_name = 'Sarnath Deer Park';
UPDATE places SET image_url = 'archruins.jpeg'        WHERE place_name = 'Sarnath Archaeological Ruins';
UPDATE places SET image_url = 'thai.jpg'          WHERE place_name = 'Thai Temple and Monastery';
UPDATE places SET image_url = 'giant_budha.jpeg'         WHERE place_name = 'Giant Buddha Statue';
UPDATE places SET image_url = 'chinese.jpeg'       WHERE place_name = 'Chinese Buddhist Temple';
UPDATE places SET image_url = 'tibetan.jpg'       WHERE place_name = 'Tibetan Buddhist Temple';
UPDATE places SET image_url = 'japanese.jpg'  WHERE place_name = 'Jain Temple, Sarnath';
UPDATE places SET image_url = 'wisdom_garden.jpeg' WHERE place_name = 'Garden of Spiritual Wisdom';