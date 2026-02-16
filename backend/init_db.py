import sqlite3
import os

# Create database and tables in the app directory
db_path = os.path.join(os.path.dirname(__file__), 'app', 'sar_ai.db')
db_path = os.path.normpath(db_path)

# Ensure directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)

# Read and execute schema
with open('app/database/schema.sql') as f:
    sql = f.read()
    conn.executescript(sql)
    conn.commit()

print(f"✅ Database initialized at: {db_path}")

# Verify tables were created
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print(f"Tables created: {[t[0] for t in tables]}")

conn.close()
