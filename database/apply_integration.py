"""Apply only the reviewed food-tier migration; never run the pending seed scripts."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database as db


def places_fingerprint():
    rows = db.query("SELECT * FROM places ORDER BY place_id")
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    before = places_fingerprint()
    columns = {r["Field"] for r in db.query("SHOW COLUMNS FROM food_places")}
    if "budget_tier" not in columns:
        sql = Path(__file__).with_name("integration_food_tier.sql").read_text(encoding="utf-8")
        db.execute(sql)
        print("Added food_places.budget_tier; existing table and column names preserved.")
    else:
        print("food_places.budget_tier already exists; no migration needed.")
    assert places_fingerprint() == before, "Places changed during migration; investigate concurrent writes."
    print("Verified: places contents unchanged.")
