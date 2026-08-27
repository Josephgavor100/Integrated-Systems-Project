import sys
from pathlib import Path

# Add project root to Python search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pytest
from gridcare_lite.database import init_db, verify_user, fetch_all_outages, add_outage

def test_database_initialization_and_auth():
    init_db()
    # Test valid credentials
    user = verify_user("admin", "admin123")
    assert user is not None
    assert user["role"] == "Admin"

    # Test invalid credentials
    invalid_user = verify_user("admin", "wrongpassword")
    assert invalid_user is None

def test_outage_creation():
    init_db()
    initial_count = len(fetch_all_outages())
    add_outage("Test Sector", "Critical", "Active", "Automated test outage entry")
    updated_records = fetch_all_outages()
    assert len(updated_records) == initial_count + 1
    assert updated_records[0][1] == "Test Sector"