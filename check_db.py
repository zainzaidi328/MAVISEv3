import sqlite3
import os

DB_PATH = "frontend/mavise.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("--- USERS ---")
c.execute("SELECT * FROM users")
print(c.fetchall())

print("\n--- VIDEOS ---")
c.execute("SELECT * FROM videos")
print(c.fetchall())

conn.close()
