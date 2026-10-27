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

CREATE TABLE IF NOT EXISTS trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    start_location VARCHAR(255),
    end_location VARCHAR(255),
    number_of_days INT,
    hours_per_day DECIMAL(5,2),
    budget DECIMAL(12,2),
    transport_mode VARCHAR(30),
    food_preference VARCHAR(30),
    stay_preference VARCHAR(30),
    travel_pace VARCHAR(30),
    params_json LONGTEXT,                    -- full validated request, used for recalculation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS trip_places (
    trip_id INT NOT NULL,
    place_id INT NOT NULL,
    is_selected TINYINT(1) DEFAULT 1,
    is_compulsory TINYINT(1) DEFAULT 0,
    PRIMARY KEY (trip_id, place_id),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS itinerary_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    day_number INT,
    place_id INT,
    arrival_time VARCHAR(20),
    departure_time VARCHAR(20),
    travel_duration_minutes DECIMAL(8,1),
    estimated_cost DECIMAL(10,2),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
) ENGINE=InnoDB;
