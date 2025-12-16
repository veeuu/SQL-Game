import sqlite3

DB_PATH = "game.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if winner_id column exists
    c.execute("PRAGMA table_info(rooms)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'winner_id' not in columns:
        print("Adding winner_id column to rooms table...")
        c.execute("ALTER TABLE rooms ADD COLUMN winner_id INTEGER")
        print("✓ Added winner_id column")
    else:
        print("✓ winner_id column already exists")
    
    # Add multi-round columns
    if 'total_rounds' not in columns:
        print("Adding multi-round support columns...")
        c.execute("ALTER TABLE rooms ADD COLUMN total_rounds INTEGER DEFAULT 3")
        c.execute("ALTER TABLE rooms ADD COLUMN current_round INTEGER DEFAULT 1")
        c.execute("ALTER TABLE rooms ADD COLUMN player1_score INTEGER DEFAULT 0")
        c.execute("ALTER TABLE rooms ADD COLUMN player2_score INTEGER DEFAULT 0")
        print("✓ Added multi-round columns")
    else:
        print("✓ Multi-round columns already exist")
    
    # Create duo_submissions table if not exists
    c.execute("""CREATE TABLE IF NOT EXISTS duo_submissions (
        id INTEGER PRIMARY KEY,
        room_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        is_correct BOOLEAN NOT NULL,
        execution_time REAL NOT NULL,
        submitted_at TEXT NOT NULL,
        round_number INTEGER DEFAULT 1,
        FOREIGN KEY(room_id) REFERENCES rooms(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    print("✓ duo_submissions table ready")
    
    conn.commit()
    conn.close()
    print("\n✅ Database migration completed!")

if __name__ == "__main__":
    migrate()
