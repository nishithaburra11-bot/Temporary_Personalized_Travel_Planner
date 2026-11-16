-- Run manually after updating the application. Permanently deletes saved trips.
USE personalized_travel_planner;

-- Remove children before their parent to respect foreign-key constraints.
DROP TABLE IF EXISTS itinerary_items;
DROP TABLE IF EXISTS trip_places;
DROP TABLE IF EXISTS trips;
