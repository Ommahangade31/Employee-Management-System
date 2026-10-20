"""
Automated tests for the Employee Management System.
Uses a temporary SQLite database so real data is never touched.
Tests are independent and can run in any order.
"""

import os
import tempfile
import pytest

# Point to a temporary database BEFORE importing app so the app uses it
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_PATH"] = _db_path

# Now import the app (it picks up DATABASE_PATH from the environment)
from app import app as flask_app, init_db, seed_db, get_db  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables once for the whole test session."""
    init_db()
    yield
    # Cleanup temp file after all tests
    try:
        os.unlink(_db_path)
    except OSError:
        pass


@pytest.fixture
def client():
    """Return a Flask test client with testing mode enabled."""
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _employee_payload(**overrides):
    """Return a valid employee form payload with optional field overrides."""
    base = {
        "employee_id":  "TEST001",
        "full_name":    "Test Employee",
        "email":        "test@example.com",
        "phone":        "555-9999",
        "department":   "Engineering",
        "designation":  "Tester",
        "joining_date": "2024-01-01",
        "salary":       "50000",
    }
    base.update(overrides)
    return base


def _add_employee(client, **overrides):
    """POST a new employee and return the response."""
    return client.post(
        "/employees/add",
        data=_employee_payload(**overrides),
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# 1. Dashboard returns HTTP 200
# ---------------------------------------------------------------------------

def test_dashboard_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. Employee listing page returns HTTP 200
# ---------------------------------------------------------------------------

def test_employee_listing_returns_200(client):
    resp = client.get("/employees")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 3. A new employee can be created successfully
# ---------------------------------------------------------------------------

def test_create_employee_success(client):
    resp = _add_employee(client, employee_id="EMP_NEW001", email="new001@example.com")
    assert resp.status_code == 200
    assert b"EMP_NEW001" in resp.data or b"added successfully" in resp.data


# ---------------------------------------------------------------------------
# 4. Employee data is saved in the database
# ---------------------------------------------------------------------------

def test_employee_saved_in_database(client):
    _add_employee(client, employee_id="EMP_DB001", email="db001@example.com",
                  full_name="Database Test User")
    resp = client.get("/employees?search=Database+Test+User")
    assert resp.status_code == 200
    assert b"Database Test User" in resp.data


# ---------------------------------------------------------------------------
# 5. Duplicate employee IDs are rejected
# ---------------------------------------------------------------------------

def test_duplicate_employee_id_rejected(client):
    _add_employee(client, employee_id="EMP_DUP001", email="dup001@example.com")
    resp = _add_employee(client, employee_id="EMP_DUP001", email="dup002@example.com")
    assert resp.status_code == 200
    assert b"already exists" in resp.data


# ---------------------------------------------------------------------------
# 6. Invalid email addresses are rejected
# ---------------------------------------------------------------------------

def test_invalid_email_rejected(client):
    resp = _add_employee(client, employee_id="EMP_EMAIL001", email="not-an-email")
    assert resp.status_code == 200
    assert b"valid email" in resp.data


# ---------------------------------------------------------------------------
# 7. Missing required fields are rejected
# ---------------------------------------------------------------------------

def test_missing_required_fields_rejected(client):
    resp = client.post(
        "/employees/add",
        data={"employee_id": "", "full_name": "", "email": ""},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"required" in resp.data


# ---------------------------------------------------------------------------
# 8. An existing employee can be updated
# ---------------------------------------------------------------------------

def test_update_employee(client):
    _add_employee(client, employee_id="EMP_UPD001", email="upd001@example.com",
                  full_name="Before Update")
    # Find the internal PK
    from app import get_db
    with flask_app.app_context():
        db = get_db()
        emp = db.execute("SELECT id FROM employees WHERE employee_id='EMP_UPD001'").fetchone()
    assert emp is not None, "Employee not found in DB after creation"
    pk = emp["id"]

    resp = client.post(
        f"/employees/{pk}/edit",
        data=_employee_payload(
            employee_id="EMP_UPD001",
            email="upd001@example.com",
            full_name="After Update",
        ),
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"After Update" in resp.data


# ---------------------------------------------------------------------------
# 9. An existing employee can be deleted
# ---------------------------------------------------------------------------

def test_delete_employee(client):
    _add_employee(client, employee_id="EMP_DEL001", email="del001@example.com",
                  full_name="To Be Deleted")
    from app import get_db
    with flask_app.app_context():
        db = get_db()
        emp = db.execute("SELECT id FROM employees WHERE employee_id='EMP_DEL001'").fetchone()
    assert emp is not None
    pk = emp["id"]

    resp = client.post(f"/employees/{pk}/delete", follow_redirects=True)
    assert resp.status_code == 200
    # Verify the record is gone by querying the database directly
    with flask_app.app_context():
        db = get_db()
        deleted = db.execute("SELECT id FROM employees WHERE employee_id='EMP_DEL001'").fetchone()
    assert deleted is None, "Employee record should have been deleted from the database"


# ---------------------------------------------------------------------------
# 10. Searching for an employee works
# ---------------------------------------------------------------------------

def test_search_employee(client):
    _add_employee(client, employee_id="EMP_SRCH001", email="srch001@example.com",
                  full_name="Searchable Person")
    resp = client.get("/employees?search=Searchable+Person")
    assert resp.status_code == 200
    assert b"Searchable Person" in resp.data


# ---------------------------------------------------------------------------
# 11. A nonexistent employee returns 404
# ---------------------------------------------------------------------------

def test_nonexistent_employee_returns_404(client):
    resp = client.get("/employees/999999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 12. The health-check endpoint works
# ---------------------------------------------------------------------------

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"


# ---------------------------------------------------------------------------
# 13. The metrics endpoint exposes Prometheus-compatible metrics
# ---------------------------------------------------------------------------

def test_metrics_endpoint(client):
    # Hit a page first so there is something to measure
    client.get("/")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    # Prometheus text format always contains flask_ or python_ counters
    assert b"flask_" in resp.data or b"python_" in resp.data or b"http_" in resp.data
