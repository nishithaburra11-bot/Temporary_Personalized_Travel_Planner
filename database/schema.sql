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
    'cultural & leisure',
    'Ghat',
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
    NULL
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
    NULL
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
    NULL
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
    NULL
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
    NULL
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
    NULL
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
