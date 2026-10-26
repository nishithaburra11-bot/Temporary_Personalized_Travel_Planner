"""TEST-ONLY sample rows so you can run the backend before Member 3 finishes the real data.

!! Values here are PLACEHOLDERS (coordinates approximate, hours/fees NOT verified, source_checked_date left NULL).
!! Do NOT ship them. Member 3's verified data replaces this file.
"""
import database as db

db.init_db()
if db.query_one("SELECT 1 AS x FROM Regions LIMIT 1"):
    print("Database already has data; nothing seeded.")
    raise SystemExit

r1 = db.execute("INSERT INTO Regions (region_name, description) VALUES ('Ghats (TEST)', 'test region')")
r2 = db.execute("INSERT INTO Regions (region_name, description) VALUES ('Sarnath (TEST)', 'test region')")
rows = [
    ("Dashashwamedh Ghat", r1, "ghat", 25.3070, 83.0104, None, None, None, 60, None),
    ("Kashi Vishwanath Temple", r1, "temple", 25.3109, 83.0107, "04:00", "23:00", None, 90, None),
    ("Assi Ghat", r1, "ghat", 25.2884, 83.0067, None, None, None, 45, None),
    ("Sarnath", r2, "heritage", 25.3811, 83.0225, "09:00", "17:00", "Fri", 120, None),
]
for name, rid, cat, lat, lon, o, c, closed, dur, fee in rows:
    db.execute("""INSERT INTO Places (place_name, region_id, category, latitude, longitude, opening_time,
                  closing_time, closed_days, visit_duration_minutes, entry_fee)
                  VALUES (?,?,?,?,?,?,?,?,?,?)""", (name, rid, cat, lat, lon, o, c, closed, dur, fee))
print("Seeded TEST data. Replace with verified data before the demo.")
