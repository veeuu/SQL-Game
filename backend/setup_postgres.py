"""
Run this once to create the PostgreSQL database and tables.
Make sure PostgreSQL is running and update .env with your credentials.
"""
import psycopg2
import os

# First connect to default 'postgres' DB to create our database
def create_database():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            port=int(os.getenv("PG_PORT", "5432")),
            database="postgres",  # connect to default db first
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASS", "postgres"),
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
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("Make sure PostgreSQL is running and credentials in .env are correct")
        raise

if __name__ == "__main__":
    create_database()
    
    # Now init tables
    from database import init_db
    init_db()
    print("\n✅ PostgreSQL setup complete!")
    print("Now run: python main.py")
