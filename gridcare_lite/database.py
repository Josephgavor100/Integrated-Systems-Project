import sqlite3
import os

# Dynamically resolve path to gridcare.db inside gridcare_lite directory
DB_PATH = os.path.join(os.path.dirname(__file__), "gridcare.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Users table (Role-Based Access Control)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('Admin', 'Engineer', 'Technician', 'Customer Service')) NOT NULL,
            full_name TEXT NOT NULL
        )
    ''')

    # 2. Substations reference table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS substations (
            substation_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            voltage_kv REAL,
            capacity_mva REAL,
            status TEXT
        )
    ''')

    # 3. Outages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outages (
            outage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            substation_id INTEGER NOT NULL,
            reported_by INTEGER NOT NULL,
            fault_type TEXT NOT NULL,
            severity TEXT CHECK(severity IN ('Low', 'Medium', 'High', 'Critical')) NOT NULL,
            status TEXT CHECK(status IN ('Open', 'Assigned', 'In Progress', 'Resolved')) DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (substation_id) REFERENCES substations (substation_id),
            FOREIGN KEY (reported_by) REFERENCES users (user_id)
        )
    ''')

    # 4. Work Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_orders (
            work_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            outage_id INTEGER UNIQUE NOT NULL,
            assigned_technician_id INTEGER,
            scheduled_date TEXT,
            resolution_notes TEXT,
            completed_at TIMESTAMP,
            FOREIGN KEY (outage_id) REFERENCES outages (outage_id),
            FOREIGN KEY (assigned_technician_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("GridCare-Lite Database initialized successfully.")


if __name__ == "__main__":
    init_db()
