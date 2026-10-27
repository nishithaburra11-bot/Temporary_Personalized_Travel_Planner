# Backend v2 (MySQL + team itinerary.py)

Put these files in the SAME folder as your teammates' real files:
  - itinerary.py   (Member 4's full file - not included here)
  - schema.sql     (Member 3's MySQL script that creates/fills `places`)

1. Run Member 3's schema.sql in MySQL so database `personalized_travel_planner` and table `places` exist.
2. Copy `.env.example` to `.env` and put your MySQL password in it.
3. pip install -r requirements.txt
4. python app.py   (creates the extra tables from schema_extra.sql automatically)
5. Open http://127.0.0.1:5000/api/data-quality to see problems in the places data.
