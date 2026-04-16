import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# ─── PostgreSQL Connection Config ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("PG_HOST", "localhost"),
    "port":     int(os.getenv("PG_PORT", "5432")),
    "database": os.getenv("PG_DB",   "sql_dungeon"),
    "user":     os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASS", "postgres"),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Create all app tables + a challenge schema with sample data."""
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

    # ── Challenge schema with sample data (players run queries against this) ─
    c.execute("CREATE SCHEMA IF NOT EXISTS challenge")

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.users (
            id SERIAL PRIMARY KEY,
            username TEXT,
            email TEXT,
            age INTEGER,
            city TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM challenge.users")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO challenge.users (username, email, age, city) VALUES
            ('Alice',   'alice@mail.com',   28, 'NYC'),
            ('Bob',     'bob@mail.com',     35, 'LA'),
            ('Charlie', 'charlie@mail.com', 42, 'NYC'),
            ('Diana',   'diana@mail.com',   31, 'Chicago'),
            ('Eve',     'eve@mail.com',     25, 'LA'),
            ('Frank',   'frank@mail.com',   38, 'NYC')
        """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            product TEXT,
            amount NUMERIC,
            created_at TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM challenge.orders")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO challenge.orders (user_id, product, amount, created_at) VALUES
            (1, 'Sword',   150.00, '2024-01-15'),
            (1, 'Shield',  200.00, '2024-02-20'),
            (2, 'Potion',   75.50, '2024-01-10'),
            (3, 'Armor',   300.00, '2024-03-05'),
            (3, 'Helmet',  125.75, '2024-01-25'),
            (3, 'Boots',    89.99, '2024-02-14'),
            (4, 'Staff',   450.00, '2024-01-30'),
            (2, 'Wand',    180.25, '2024-03-12')
        """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS challenge.employees (
            id SERIAL PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary NUMERIC,
            manager_id INTEGER
        )
    """)
    c.execute("SELECT COUNT(*) FROM challenge.employees")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO challenge.employees (name, department, salary, manager_id) VALUES
            ('CEO',         'Executive',   200000, NULL),
            ('VP Eng',      'Engineering', 150000, 1),
            ('VP Sales',    'Sales',       140000, 1),
            ('Engineer 1',  'Engineering',  90000, 2),
            ('Engineer 2',  'Engineering',  85000, 2),
            ('Sales Rep 1', 'Sales',        70000, 3),
            ('Sales Rep 2', 'Sales',        75000, 3)
        """)

    conn.commit()
    c.close()
    conn.close()
    print("✅ PostgreSQL tables + challenge schema initialized")


def run_challenge_query(sql: str):
    """
    Execute a player's SQL query against the challenge schema.
    Returns (results, columns, exec_time_ms) or raises on error.
    """
    conn = get_conn()
    # Set search_path so players can write  SELECT * FROM users  without schema prefix
    conn.cursor().execute("SET search_path TO challenge, public")
    c = conn.cursor()
    import time
    start = time.time()
    c.execute(sql)
    results = c.fetchall()
    columns = [desc[0] for desc in c.description] if c.description else []
    exec_time = (time.time() - start) * 1000
    conn.rollback()   # never persist player queries
    c.close()
    conn.close()
    return results, columns, exec_time
