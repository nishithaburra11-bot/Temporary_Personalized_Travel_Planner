-- Extra tables the backend needs, in MySQL syntax, matching the team's lowercase `places` table.
-- Safe to run many times (IF NOT EXISTS). app.py runs this automatically at start-up.
-- It does NOT touch the `places` table.
USE personalized_travel_planner;

CREATE TABLE IF NOT EXISTS food_places (
    food_place_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    cuisine VARCHAR(100),
    dietary_options VARCHAR(150),            -- e.g. 'vegetarian,vegan'
    price_range_per_person DECIMAL(10,2),    -- NULL = unknown
    opening_hours VARCHAR(100),
    source_url TEXT,
    source_checked_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    category VARCHAR(20),                    -- 'budget' | 'normal' | 'luxury'
    price_per_night DECIMAL(10,2),
    facilities TEXT,
    official_booking_url TEXT,
    source_checked_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS travel_resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    place_id INT,
    requirement_type VARCHAR(50),            -- ticket | permission | registration | booking
    required_or_optional VARCHAR(20),
    procedure_text TEXT,
    official_url TEXT,
    fee DECIMAL(10,2),
    source_checked_date DATE
) ENGINE=InnoDB;
SELECT * FROM places;
SELECT * FROM food_places;
SELECT * FROM hotels;
USE personalized_travel_planner;
ALTER TABLE hotels DROP COLUMN facilities;
-- REVIEW BEFORE RUNNING. Not executed by Codex.
ALTER TABLE hotels DROP COLUMN source_checked_date ;
DROP TABLE IF EXISTS travel_resources;

-- Optional: run separately only if you also want to remove this unused research field.
-- ALTER TABLE hotels DROP COLUMN source_checked_date;


