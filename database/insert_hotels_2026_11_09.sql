-- 36 hotel/stay records for the Ayan college demonstration, 2026-11-09.
-- NOT executed. Review and run once; repeating this INSERT creates duplicates.
-- ALL coordinates are coarse AREA-LEVEL DEMO ESTIMATES, not verified hotel pins.
-- ALL prices are DEMO room/night allowances, not live quotes, taxes or availability.
-- Basic/budget <=2000; Comfort/normal >2000 to 5000; Luxury/luxury >5000 INR.
-- These are project price bands, NOT official star ratings. No hostel dorm rates used.
-- Names/localities come from cited pages; operating status is not independently confirmed.
-- Works with the current table, with or without source_checked_date.
USE personalized_travel_planner;
INSERT INTO hotels
(
    hotel_name,
    address,
    latitude,
    longitude,
    category,
    price_per_night,
    official_booking_url
)
VALUES
(
    'Taj Ganges',
    'Nadesar Grounds, Varanasi',
    25.338,
    82.989,
    'luxury',
    9000,
    'https://www.tajhotels.com/en-in/hotels/taj-ganges-varanasi'
),

(
    'Radisson Hotel Varanasi',
    'The Mall, Cantonment, Varanasi',
    25.336,
    82.981,
    'luxury',
    7500,
    'https://www.radissonhotels.com/en-us/hotels/radisson-varanasi'
),

(
    'Hotel Clarks Varanasi',
    'The Mall, Cantonment, Varanasi',
    25.335,
    82.978,
    'luxury',
    6500,
    NULL
),

(
    'Hotel Sidhartha',
    'Sigra, Varanasi',
    25.312,
    82.987,
    'budget',
    1800,
    NULL
),

(
    'HHI Varanasi',
    'C-21/3, Maldahiya, Varanasi',
    25.325,
    82.991,
    'normal',
    4800,
    'https://www.hhivaranasi.com/'
),

(
    'Hotel India',
    'Nadesar, Varanasi',
    25.338,
    82.992,
    'normal',
    3000,
    NULL
),

(
    'Hotel De-Paris',
    'The Mall, Cantonment, Varanasi',
    25.336,
    82.98,
    'normal',
    3200,
    NULL
),

(
    'Hotel Vaibhav',
    'Varanasi (street address unverified)',
    25.334,
    82.986,
    'budget',
    1900,
    NULL
),

(
    'Hotel Meredian Grant',
    'Patel Nagar, Varanasi',
    25.335,
    82.98,
    'normal',
    3500,
    NULL
),

(
    'Hotel Pradeep',
    'Lahurabir, Varanasi',
    25.326,
    83.001,
    'budget',
    1900,
    NULL
),

(
    'Hotel Pallavi International',
    'Hathua Market, Chetganj, Varanasi',
    25.323,
    83.0,
    'normal',
    3500,
    NULL
),

(
    'Ramada Plaza JHV',
    'The Mall, Cantonment, Varanasi',
    25.335,
    82.977,
    'luxury',
    8000,
    'https://www.ramadajhvvns.com/'
),

(
    'BrijRama Palace',
    'Darbhanga Ghat, Dashashwamedh, Varanasi',
    25.305,
    83.01,
    'luxury',
    18000,
    'https://www.brijhotels.com/hotels/brijrama-palace-varanasi/hotel-overview'
),

(
    'Hotel Surya Kaiser Palace',
    'S.20/51 A-5, The Mall Road, Cantonment, Varanasi',
    25.337,
    82.981,
    'normal',
    4500,
    'https://www.hotelsuryavns.com/'
),

(
    'Ramada Varanasi Katesar',
    'Katesar Ramnagar Road, Chandauli',
    25.302,
    83.043,
    'luxury',
    6500,
    'https://ramadavaranasikatesar.com/'
),

(
    'DoubleTree by Hilton Varanasi',
    'SA2/320 Chhota Lalpur, Pandeypur, Varanasi',
    25.359,
    83.002,
    'luxury',
    8000,
    'https://www.hilton.com/en/hotels/vnsdidi-doubletree-varanasi/'
),

(
    'Taj Nadesar Palace',
    'Nadesar Palace Grounds, Varanasi',
    25.338,
    82.989,
    'luxury',
    30000,
    'https://www.tajhotels.com/en-in/hotels/taj-nadesar-palace-varanasi'
),

(
    'Konark Grand Hotel',
    'Mirzapur (confirm street address with hotel)',
    25.136,
    82.558,
    'normal',
    4500,
    'https://konarkgrandhotel.com/'
),

(
    'Hotel The Galaxy',
    'Lal Diggi Road, Mirzapur',
    25.145,
    82.566,
    'normal',
    2800,
    NULL
),

(
    'Hotel Temple On Ganges',
    'Assi Ghat, Varanasi',
    25.289,
    83.006,
    'normal',
    4000,
    'https://www.hoteltemple.com/'
),

(
    'Hotel Banaras Haveli',
    'Near Assi Ghat, Varanasi',
    25.289,
    83.004,
    'normal',
    3800,
    'https://hotelbanarashaveli.com/'
),

(
    'Ganpati Guest House',
    'D3/24, Meer Ghat, Varanasi',
    25.309,
    83.011,
    'normal',
    3500,
    'https://www.ganpatihospitality.com/'
),

(
    'Alka Hotel',
    'Ganges riverfront, Varanasi (confirm street address)',
    25.309,
    83.011,
    'normal',
    2500,
    'https://hotelalkavns.com/'
),

(
    'Palace on Ganges',
    'Assi Ghat, Varanasi',
    25.289,
    83.006,
    'luxury',
    6000,
    'https://palaceonganges.com/'
),

(
    'Sterling Varanasi',
    'Near Sankat Mochan Temple, Varanasi',
    25.282,
    83.001,
    'luxury',
    5500,
    'https://www.sterlingholidays.com/resorts-hotels/varanasi'
),

(
    'Guleria Kothi',
    'Ganges riverfront, Varanasi (confirm street address)',
    25.316,
    83.016,
    'luxury',
    9500,
    'https://www.guleriakothi.com/'
),

(
    'Hotel Sri Balaji',
    'Near Kaal Bhairav Temple, Varanasi',
    25.322,
    83.01,
    'budget',
    2000,
    'https://sribalajihotel.co.in/'
),

(
    'Rahi Tourist Bungalow Sarnath',
    'Sarnath, Varanasi',
    25.377,
    83.025,
    'budget',
    1800,
    'https://www.upstdc.co.in/hotels-in-varanasi'
),

(
    'Varanasi Ganges',
    'Opposite Banaras Railway Station, Varanasi',
    25.299,
    82.974,
    'normal',
    3000,
    'https://varanasiganges.com/'
),

(
    'Hotel Buddha',
    'C26/35 Ramkatora, near Lahurabir Crossing, Varanasi',
    25.324,
    83.001,
    'normal',
    2800,
    'https://hotelbuddhavaranasi.com/'
),

(
    'Marigold Guest House',
    'Munshi Ghat, Varanasi',
    25.305,
    83.01,
    'budget',
    1800,
    'https://manjhisonu100.wixsite.com/marigoldhouse'
),

(
    'Shanti Guest House',
    'CK8/129 Garwasi Tola Road, near Manikarnika Ghat, Varanasi',
    25.313,
    83.013,
    'budget',
    1200,
    NULL
),
(
    'Saini Guest House',
    'SA15/129 K-1, Mawaiya Road, opposite Tibetan Institute, Sarnath',
    25.369,
    83.025,
    'budget',
    1400,
    'https://sarnathcafe.com/saini-guest-house/'
),

(
    'Rahul Guest House',
    'N1/15 D-10, Gangotri Vihar Colony, Nagwa, near Ravidas Park, Varanasi',
    25.283,
    83.01,
    'budget',
    1600,
    NULL
),

(
    'Hotel Ganges View',
    'Assi Ghat, Varanasi',
    25.289,
    83.006,
    'luxury',
    6500,
    'https://www.hotelgangesview.in/'
),

(
    'Rivatas by Ideal',
    'The Mall Road, Cantonment, Varanasi',
    25.336,
    82.98,
    'luxury',
    7000,
    'https://www.rivatas.com/'
);
