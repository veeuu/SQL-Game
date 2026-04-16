import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("PG_HOST", "localhost"),
    "port":     int(os.getenv("PG_PORT", "5432")),
    "database": os.getenv("PG_DB",   "sql_dungeon"),
    "user":     os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASS", ""),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Create all app tables. No sample data — real data only."""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id),
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 100
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            date TEXT,
            queries_solved INTEGER DEFAULT 0,
            points_earned INTEGER DEFAULT 0,
            UNIQUE(user_id, date)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS level_completions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            level INTEGER,
            query TEXT,
            execution_time REAL,
            completed_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS mini_game_scores (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            game_type TEXT,
            score INTEGER,
            played_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            mode TEXT,
            level INTEGER DEFAULT 1,
            creator_id INTEGER REFERENCES users(id),
            opponent_id INTEGER REFERENCES users(id),
            status TEXT DEFAULT 'waiting',
            winner_id INTEGER REFERENCES users(id),
            total_rounds INTEGER DEFAULT 3,
            current_round INTEGER DEFAULT 1,
            player1_score INTEGER DEFAULT 0,
            player2_score INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS duo_submissions (
            id SERIAL PRIMARY KEY,
            room_id TEXT REFERENCES rooms(id),
            user_id INTEGER REFERENCES users(id),
            round_number INTEGER,
            query TEXT,
            is_correct BOOLEAN,
            execution_time REAL,
            submitted_at TEXT
        )
    """)

    conn.commit()
    c.close()
    conn.close()
    print("✅ PostgreSQL tables ready")


def run_challenge_query(sql: str):
    """
    Execute a player's SQL query against the public schema (real data).
    Always rolled back — player queries never persist.
    Returns (results, columns, exec_time_ms).
    """
    conn = get_conn()
    c = conn.cursor()
    try:
        start = time.time()
        c.execute(sql)
        results = c.fetchall()
        columns = [desc[0] for desc in c.description] if c.description else []
        exec_time = (time.time() - start) * 1000
        conn.rollback()  # never persist
        return results, columns, exec_time
    except Exception:
        conn.rollback()
        raise
    finally:
        c.close()
        conn.close()
