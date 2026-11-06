-- Integration migration: run once after checking SHOW COLUMNS FROM food_places.
-- Does not modify places or execute any other SQL file.
ALTER TABLE food_places ADD COLUMN budget_tier VARCHAR(20) NULL
COMMENT 'budget, standard, or premium; supplied by the dataset owner';
