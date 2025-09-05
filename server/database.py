import sqlite3
import os
from datetime import datetime

def init_database(db_path: str = "experiment_bot.db"):
    """Initialize the SQLite database with required tables"""

    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                api_key TEXT UNIQUE NOT NULL,
                chat_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Processes table (for future use)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                process_uuid TEXT UNIQUE NOT NULL,
                name TEXT,
                status TEXT DEFAULT 'running',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_api_key ON users (api_key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processes_user_id ON processes (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processes_uuid ON processes (process_uuid)')

        conn.commit()
        print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    init_database()