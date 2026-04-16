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
    "sslmode":  "require" if os.getenv("PG_HOST", "localhost") != "localhost" else "disable",
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
            energy INTEGER DEFAULT 100,
            total_levels INTEGER DEFAULT 30
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

    # ── Challenge schema with sample data (players run queries against this) ──
    c.execute("CREATE SCHEMA IF NOT EXISTS challenge")

    # ── customers ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.customers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            city TEXT,
            country TEXT,
            age INTEGER,
            joined_date TEXT,
            is_premium BOOLEAN DEFAULT FALSE
        )
    """)

    # ── orders ─────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.orders (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER,
            product TEXT,
            category TEXT,
            amount NUMERIC,
            quantity INTEGER,
            status TEXT,
            order_date TEXT
        )
    """)

    # ── products ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            category TEXT,
            price NUMERIC,
            stock INTEGER,
            supplier_id INTEGER,
            rating NUMERIC
        )
    """)

    # ── employees ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.employees (
            id SERIAL PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary NUMERIC,
            manager_id INTEGER,
            hire_date TEXT,
            city TEXT
        )
    """)

    # ── departments ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.departments (
            id SERIAL PRIMARY KEY,
            name TEXT,
            budget NUMERIC,
            location TEXT,
            head_id INTEGER
        )
    """)

    # ── students ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.students (
            id SERIAL PRIMARY KEY,
            name TEXT,
            age INTEGER,
            grade TEXT,
            gpa NUMERIC,
            major TEXT,
            enrollment_year INTEGER
        )
    """)

    # ── courses ────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.courses (
            id SERIAL PRIMARY KEY,
            title TEXT,
            department TEXT,
            credits INTEGER,
            instructor TEXT,
            max_students INTEGER
        )
    """)

    # ── enrollments ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.enrollments (
            id SERIAL PRIMARY KEY,
            student_id INTEGER,
            course_id INTEGER,
            grade TEXT,
            semester TEXT,
            year INTEGER
        )
    """)

    # ── movies ─────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.movies (
            id SERIAL PRIMARY KEY,
            title TEXT,
            genre TEXT,
            release_year INTEGER,
            director TEXT,
            rating NUMERIC,
            box_office NUMERIC
        )
    """)

    # ── reviews ────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.reviews (
            id SERIAL PRIMARY KEY,
            movie_id INTEGER,
            reviewer TEXT,
            score INTEGER,
            comment TEXT,
            review_date TEXT
        )
    """)

    # ── suppliers ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.suppliers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            country TEXT,
            contact_email TEXT,
            rating NUMERIC
        )
    """)

    # ── transactions ───────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.transactions (
            id SERIAL PRIMARY KEY,
            account_id INTEGER,
            type TEXT,
            amount NUMERIC,
            balance_after NUMERIC,
            transaction_date TEXT
        )
    """)

    # ── accounts ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.accounts (
            id SERIAL PRIMARY KEY,
            owner TEXT,
            account_type TEXT,
            balance NUMERIC,
            opened_date TEXT,
            is_active BOOLEAN DEFAULT TRUE
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
