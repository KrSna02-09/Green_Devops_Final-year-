import sqlite3
from datetime import datetime
import os

# Set DB path to the root folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "green_metrics.db")

def init_db():
    """Initializes the database and creates the metrics table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            commit_hash TEXT,
            duration_sec REAL,
            energy_kwh REAL,
            co2_mg REAL,
            smell_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_metric(commit_hash, duration, energy, co2, smells):
    """Inserts a new measurement into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO carbon_logs (timestamp, commit_hash, duration_sec, energy_kwh, co2_mg, smell_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), commit_hash, duration, energy, co2, smells))
    conn.commit()
    conn.close()