# database.py
import sqlite3
import datetime
import os

# Important: This path is specifically for Railway's persistent volumes.
# When you run locally, it will create a 'data' folder in your project.
DB_DIR = "/data"
DB_PATH = os.path.join(DB_DIR, "contribution_points.db")

def initialize_database():
    """Initializes the database and creates the tables if they don't exist."""
    # Ensure the /data directory exists for Railway Volumes
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # This table stores every single point transaction.
    # This allows us to query by date.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS points_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            points INTEGER NOT NULL,
            reason TEXT,
            timestamp DATETIME NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_points(user_id: int, guild_id: int, points: int, reason: str):
    """Adds a new point transaction for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.utcnow()
    
    cursor.execute("""
        INSERT INTO points_log (user_id, guild_id, points, reason, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, guild_id, points, reason, timestamp))
    
    conn.commit()
    conn.close()

def get_leaderboard(guild_id: int, time_delta: datetime.timedelta = None):
    """
    Fetches the leaderboard data.
    - Aggregates points for each user.
    - Can be filtered by a time_delta (e.g., last 7 days).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT user_id, SUM(points) as total_points
        FROM points_log
        WHERE guild_id = ?
    """
    params = [guild_id]

    if time_delta:
        start_date = datetime.datetime.utcnow() - time_delta
        query += " AND timestamp >= ?"
        params.append(start_date)

    query += """
        GROUP BY user_id
        ORDER BY total_points DESC
        LIMIT 20
    """ # Limiting to top 20 to avoid huge messages

    cursor.execute(query, tuple(params))
    leaderboard_data = cursor.fetchall()
    
    conn.close()
    return leaderboard_data