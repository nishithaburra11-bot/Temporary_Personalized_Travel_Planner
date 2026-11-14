-- REVIEW ONLY: not executed. Does not modify an existing hotels table.
USE personalized_travel_planner;
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    category VARCHAR(20), -- budget=Basic, normal=Comfort, luxury=Luxury
    price_per_night DECIMAL(10,2), -- estimated INR per room/night
    official_booking_url TEXT
) ENGINE=InnoDB;
