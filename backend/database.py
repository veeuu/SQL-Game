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
    """Create all app tables + challenge dataset tables."""
    conn = get_conn()
    c = conn.cursor()

    # ── App tables ──────────────────────────────────────────────────────────
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

    # ── Challenge dataset tables (players run queries against these) ─────────
    c.execute("CREATE SCHEMA IF NOT EXISTS challenge")

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.customers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            city TEXT,
            age INTEGER,
            joined_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.orders (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER,
            product TEXT,
            category TEXT,
            amount NUMERIC,
            quantity INTEGER,
            order_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.employees (
            id SERIAL PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary NUMERIC,
            manager_id INTEGER,
            hire_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            category TEXT,
            price NUMERIC,
            stock INTEGER
        )
    """)

    conn.commit()
    c.close()
    conn.close()
    print("✅ PostgreSQL tables + challenge schema ready")


def run_challenge_query(sql: str):
    """
    Execute a player's SQL query against the challenge schema.
    Players write  SELECT * FROM orders  and it hits challenge.orders.
    Always rolled back — never persists.
    Returns (results, columns, exec_time_ms).
    """
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("SET search_path TO challenge, public")
        start = time.time()
        c.execute(sql)
        results = c.fetchall()
        columns = [desc[0] for desc in c.description] if c.description else []
        exec_time = (time.time() - start) * 1000
        return results, columns, exec_time
    except Exception:
        raise
    finally:
        conn.rollback()  # never persist player queries
        c.close()
        conn.close()
