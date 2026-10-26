-- Varanasi Smart Trip Planner: SQLite schema (matches the team's agreed field names)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    description TEXT,
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS Places (
    place_id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_name TEXT NOT NULL,
    region_id INTEGER REFERENCES Regions(region_id),
    category TEXT,
    speciality TEXT,
    description TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    opening_time TEXT,            -- 'HH:MM' or NULL if unverified
    closing_time TEXT,            -- 'HH:MM' or NULL if unverified
    closed_days TEXT,             -- e.g. 'Mon,Tue' or NULL
    visit_duration_minutes INTEGER,
    entry_fee REAL,               -- NULL = unknown, 0 = verified free
    official_url TEXT,
    source_checked_date TEXT      -- 'YYYY-MM-DD'; NULL = not verified
);

CREATE TABLE IF NOT EXISTS Routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_location_id INTEGER REFERENCES Places(place_id),
    end_location_id INTEGER REFERENCES Places(place_id),
    transport_mode TEXT,
    distance_km REAL,
    estimated_duration_minutes REAL,
    fare REAL,
    route_geometry TEXT,
    source_checked_date TEXT
);

CREATE TABLE IF NOT EXISTS BusStops (
    stop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stop_name TEXT NOT NULL,
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS BusRoutes (
    bus_route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_name TEXT NOT NULL,
    operating_days TEXT,
    operating_hours TEXT,
    source_checked_date TEXT
);

CREATE TABLE IF NOT EXISTS BusRouteStops (
    bus_route_id INTEGER REFERENCES BusRoutes(bus_route_id),
    stop_id INTEGER REFERENCES BusStops(stop_id),
    stop_sequence INTEGER,
    departure_time TEXT,
    arrival_time TEXT,
    fare REAL,
    transfer_details TEXT
);

CREATE TABLE IF NOT EXISTS FoodPlaces (
    food_place_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    latitude REAL,
    longitude REAL,
    cuisine TEXT,
    dietary_options TEXT,          -- e.g. 'vegetarian,vegan'
    price_range_per_person REAL,   -- NULL = unknown
    opening_hours TEXT,
    source_url TEXT,
    source_checked_date TEXT
);

CREATE TABLE IF NOT EXISTS Hotels (
    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_name TEXT NOT NULL,
    address TEXT,
    latitude REAL,
    longitude REAL,
    category TEXT,                 -- 'budget' | 'normal' | 'luxury'
    price_per_night REAL,
    facilities TEXT,
    official_booking_url TEXT,
    source_checked_date TEXT
);

CREATE TABLE IF NOT EXISTS TravelResources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id INTEGER REFERENCES Places(place_id),
    requirement_type TEXT,         -- ticket | permission | registration | booking
    required_or_optional TEXT,
    procedure TEXT,
    official_url TEXT,
    fee REAL,
    source_checked_date TEXT
);

CREATE TABLE IF NOT EXISTS Trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_location TEXT,
    end_location TEXT,
    number_of_days INTEGER,
    hours_per_day REAL,
    budget REAL,
    transport_mode TEXT,
    food_preference TEXT,
    stay_preference TEXT,
    travel_pace TEXT,
    params_json TEXT,              -- full validated request, used for recalculation
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS TripPlaces (
    trip_id INTEGER REFERENCES Trips(trip_id) ON DELETE CASCADE,
    place_id INTEGER REFERENCES Places(place_id),
    is_selected INTEGER DEFAULT 1,
    is_compulsory INTEGER DEFAULT 0,
    PRIMARY KEY (trip_id, place_id)
);

CREATE TABLE IF NOT EXISTS ItineraryItems (
    trip_id INTEGER REFERENCES Trips(trip_id) ON DELETE CASCADE,
    day_number INTEGER,
    place_id INTEGER REFERENCES Places(place_id),
    arrival_time TEXT,
    departure_time TEXT,
    travel_duration_minutes REAL,
    estimated_cost REAL
);
