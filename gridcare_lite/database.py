import sqlite3
import hashlib
from pathlib import Path

# Target central project data folder using pathlib
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "gridcare.db"

def hash_password(password: str) -> str:
    """Hash plain text password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize database tables matching your initial schema and seed default users."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Users table (Matching your initial schema from last week)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('Admin', 'Engineer', 'Technician', 'Customer Service')) NOT NULL,
            full_name TEXT NOT NULL
        )
    """)

    # 2. Outages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outages (
            outage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed Default Accounts if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("admin", hash_password("admin123"), "Admin", "System Admin"),
            ("engineer", hash_password("eng123"), "Engineer", "Lead Engineer"),
            ("tech", hash_password("tech123"), "Technician", "Field Technician")
        ]
        cursor.executemany(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            default_users
        )

    # Seed Sample Outages if empty
    cursor.execute("SELECT COUNT(*) FROM outages")
    if cursor.fetchone()[0] == 0:
        sample_outages = [
            ("Accra Central", "High", "Active", "Transformer failure at Substation 4"),
            ("Tema Industrial", "Critical", "Investigating", "Main feeder line trip"),
            ("Kumasi North", "Medium", "Resolved", "Scheduled maintenance completed")
        ]
        cursor.executemany(
            "INSERT INTO outages (region, severity, status, description) VALUES (?, ?, ?, ?)",
            sample_outages
        )

    conn.commit()
    conn.close()

def verify_user(username, password):
    """Authenticate user against user_id, password_hash, and role."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, full_name, role FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"user_id": user[0], "username": user[1], "full_name": user[2], "role": user[3]}
    return None

def fetch_all_outages():
    """Retrieve all outage records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT outage_id, region, severity, status, description, timestamp FROM outages ORDER BY outage_id DESC")
    records = cursor.fetchall()
    conn.close()
    return records

def add_outage(region, severity, status, description):
    """Create a new outage entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO outages (region, severity, status, description) VALUES (?, ?, ?, ?)",
        (region, severity, status, description)
    )
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at data/gridcare.db!")