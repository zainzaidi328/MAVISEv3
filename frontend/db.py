import sqlite3
import os
import hashlib

DB_PATH = "frontend/mavise.db"

def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _get_connection()
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Videos table
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_file_name TEXT NOT NULL,
            saved_file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = _get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                  (username, _hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = _get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?', 
              (username, _hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def save_video_record(user_id, file_name, file_path):
    conn = _get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO videos (user_id, original_file_name, saved_file_path) VALUES (?, ?, ?)',
              (user_id, file_name, file_path))
    conn.commit()
    conn.close()

def get_user_videos(user_id):
    conn = _get_connection()
    c = conn.cursor()
    c.execute('SELECT id, original_file_name, saved_file_path, created_at FROM videos WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    videos = c.fetchall()
    conn.close()
    return videos

def get_user_stats(user_id):
    """Returns the total number of videos processed by the user."""
    conn = _get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(id) FROM videos WHERE user_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_user_video_timeline(user_id):
    """Returns a list of tuples (date, count) representing the number of videos processed per day."""
    conn = _get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT DATE(created_at) as date, COUNT(id) as count 
        FROM videos 
        WHERE user_id = ? 
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    ''', (user_id,))
    timeline = c.fetchall()
    conn.close()
    return timeline

def get_recent_videos(user_id, limit=5):
    """Returns the most recent videos processed by the user."""
    conn = _get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT original_file_name, created_at, saved_file_path 
        FROM videos 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    recent = c.fetchall()
    conn.close()
    return recent

# Initialize database file and tables on first load
init_db()
