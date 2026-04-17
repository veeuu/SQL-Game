from database import get_conn

conn = get_conn()
c = conn.cursor()
c.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name='progress' AND column_name='total_levels'
""")
if not c.fetchone():
    c.execute("ALTER TABLE progress ADD COLUMN total_levels INTEGER DEFAULT 30")
    conn.commit()
    print("Added total_levels column")
else:
    print("Column already exists")
c.close()
conn.close()