"""
Run once to create the database and all tables.
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        database="postgres",
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASS", ""),
    )
    conn.autocommit = True
    c = conn.cursor()
    db_name = os.getenv("PG_DB", "sql_dungeon")
    c.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
    if not c.fetchone():
        c.execute(f"CREATE DATABASE {db_name}")
        print(f"✅ Created database: {db_name}")
    else:
        print(f"✅ Database '{db_name}' already exists")
    c.close()
    conn.close()

if __name__ == "__main__":
    print("Creating database...")
    create_database()
    print("Creating tables...")
    from database import init_db
    init_db()
    print("\n✅ All done! Run: python main.py")
