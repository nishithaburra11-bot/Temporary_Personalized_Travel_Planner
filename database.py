"""MySQL access layer (PyMySQL). Connection details come from environment variables / a .env file."""
import datetime
import decimal
import os

import pymysql

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRA_SCHEMA = os.path.join(BASE_DIR, "schema_extra.sql")


def _config():
    return dict(host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", "3306")),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", ""),
                database=os.environ.get("DB_NAME", "personalized_travel_planner"),
                charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)


def get_conn():
    return pymysql.connect(**_config())


def _clean(v):
    """MySQL types -> JSON-friendly Python types."""
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, datetime.timedelta):          # TIME columns
        s = int(v.total_seconds())
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def query(sql, args=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return [{k: _clean(v) for k, v in row.items()} for row in cur.fetchall()]
    finally:
        conn.close()


def query_one(sql, args=()):
    rows = query(sql, args)
    return rows[0] if rows else None


def safe_query(sql, args=()):
    """Like query(), but returns [] if the table doesn't exist yet (e.g. hotels not loaded)."""
    try:
        return query(sql, args)
    except pymysql.err.ProgrammingError:
        return []


def execute(sql, args=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            last = cur.lastrowid
        conn.commit()
        return last
    finally:
        conn.close()


def init_db():
    """Create the extra tables if missing. Never touches `places`. Returns list of problems."""
    problems = []
    with open(EXTRA_SCHEMA, encoding="utf-8") as f:
        text = "\n".join(l for l in f.read().splitlines() if not l.strip().startswith("--"))
    for stmt in [s.strip() for s in text.split(";") if s.strip()]:
        if stmt.upper().startswith("USE "):
            continue                                   # connection already selects DB_NAME
        try:
            execute(stmt)
        except Exception as exc:
            problems.append(f"{type(exc).__name__}: {exc}")
    return problems
