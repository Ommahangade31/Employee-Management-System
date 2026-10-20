"""
Employee Management System
A Flask-based web application for managing employee records.
"""

import os
import re
import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort, g
)
from prometheus_flask_exporter import PrometheusMetrics

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Database path – can be overridden via environment variable so the Docker
# volume path is easy to configure.
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(app.root_path, "data", "employees.db"))

# ---------------------------------------------------------------------------
# Prometheus Metrics
# ---------------------------------------------------------------------------

metrics = PrometheusMetrics(app)
metrics.info("app_info", "Employee Management System", version="1.0.0")

# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------

def get_db():
    """Return a database connection for the current request context."""
    db = getattr(g, "_database", None)
    if db is None:
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
    return db


@app.teardown_appcontext
def close_db(exception):
    """Close the database connection at the end of each request."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they do not already exist."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id   TEXT    NOT NULL UNIQUE,
            full_name     TEXT    NOT NULL,
            email         TEXT    NOT NULL,
            phone         TEXT    NOT NULL,
            department    TEXT    NOT NULL,
            designation   TEXT    NOT NULL,
            joining_date  TEXT    NOT NULL,
            salary        REAL    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    """Insert sample employees for demonstration – skips if records already exist."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if count == 0:
        sample_employees = [
            ("EMP001", "Alice Johnson",    "alice.johnson@example.com",   "555-0101", "Engineering",   "Software Engineer",      "2022-01-15", 72000),
            ("EMP002", "Bob Martinez",     "bob.martinez@example.com",    "555-0102", "Engineering",   "DevOps Engineer",        "2021-06-01", 75000),
            ("EMP003", "Carol Williams",   "carol.williams@example.com",  "555-0103", "HR",            "HR Manager",             "2020-03-10", 65000),
            ("EMP004", "David Chen",       "david.chen@example.com",      "555-0104", "Finance",       "Financial Analyst",      "2022-08-22", 68000),
            ("EMP005", "Eva Brown",        "eva.brown@example.com",       "555-0105", "Marketing",     "Marketing Specialist",   "2023-02-14", 60000),
        ]
        conn.executemany("""
            INSERT INTO employees
                (employee_id, full_name, email, phone, department, designation, joining_date, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_employees)
        conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

DEPARTMENTS = ["Engineering", "HR", "Finance", "Marketing", "Operations", "Sales", "IT", "Legal"]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_employee_form(form, existing_employee_id=None):
    """
    Validate employee form data.
    Returns (cleaned_data dict, list_of_errors).
    existing_employee_id is passed during updates to allow same ID.
    """
    errors = []
    data = {}

    # Employee ID
    emp_id = form.get("employee_id", "").strip()
    if not emp_id:
        errors.append("Employee ID is required.")
    else:
        data["employee_id"] = emp_id

    # Full name
    full_name = form.get("full_name", "").strip()
    if not full_name:
        errors.append("Full name is required.")
    else:
        data["full_name"] = full_name

    # Email
    email = form.get("email", "").strip()
    if not email:
        errors.append("Email address is required.")
    elif not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")
    else:
        data["email"] = email

    # Phone
    phone = form.get("phone", "").strip()
    if not phone:
        errors.append("Phone number is required.")
    else:
        data["phone"] = phone

    # Department
    department = form.get("department", "").strip()
    if not department:
        errors.append("Department is required.")
    else:
        data["department"] = department

    # Designation
    designation = form.get("designation", "").strip()
    if not designation:
        errors.append("Job designation is required.")
    else:
        data["designation"] = designation

    # Joining date
    joining_date = form.get("joining_date", "").strip()
    if not joining_date:
        errors.append("Joining date is required.")
    else:
        try:
            datetime.strptime(joining_date, "%Y-%m-%d")
            data["joining_date"] = joining_date
        except ValueError:
            errors.append("Joining date must be in YYYY-MM-DD format.")

    # Salary
    salary_raw = form.get("salary", "").strip()
    if not salary_raw:
        errors.append("Salary is required.")
    else:
        try:
            salary = float(salary_raw)
            if salary < 0:
                errors.append("Salary must be a non-negative number.")
            else:
                data["salary"] = salary
        except ValueError:
            errors.append("Salary must be a valid number.")

    return data, errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    dept_counts = db.execute(
        "SELECT department, COUNT(*) as cnt FROM employees GROUP BY department ORDER BY cnt DESC"
    ).fetchall()
    recent = db.execute(
        "SELECT * FROM employees ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    return render_template("index.html",
                           total=total,
                           dept_counts=dept_counts,
                           recent=recent,
                           departments=DEPARTMENTS)


@app.route("/employees")
def employees():
    db = get_db()
    search = request.args.get("search", "").strip()
    dept_filter = request.args.get("department", "").strip()

    query = "SELECT * FROM employees WHERE 1=1"
    params = []

    if search:
        query += " AND (full_name LIKE ? OR employee_id LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if dept_filter:
        query += " AND department = ?"
        params.append(dept_filter)

    query += " ORDER BY created_at DESC"
    employee_list = db.execute(query, params).fetchall()

    return render_template("employees.html",
                           employees=employee_list,
                           search=search,
                           dept_filter=dept_filter,
                           departments=DEPARTMENTS)


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        data, errors = validate_employee_form(request.form)

        if not errors:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM employees WHERE employee_id = ?", (data["employee_id"],)
            ).fetchone()
            if existing:
                errors.append(f"Employee ID '{data['employee_id']}' already exists.")

        if errors:
            return render_template("add_employee.html",
                                   errors=errors,
                                   form=request.form,
                                   departments=DEPARTMENTS)

        db = get_db()
        db.execute("""
            INSERT INTO employees
                (employee_id, full_name, email, phone, department, designation, joining_date, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["employee_id"], data["full_name"], data["email"],
            data["phone"], data["department"], data["designation"],
            data["joining_date"], data["salary"]
        ))
        db.commit()
        flash(f"Employee '{data['full_name']}' added successfully!", "success")
        return redirect(url_for("employees"))

    return render_template("add_employee.html", errors=[], form={}, departments=DEPARTMENTS)


@app.route("/employees/<int:emp_pk>")
def employee_details(emp_pk):
    db = get_db()
    employee = db.execute("SELECT * FROM employees WHERE id = ?", (emp_pk,)).fetchone()
    if not employee:
        abort(404)
    return render_template("employee_details.html", employee=employee)


@app.route("/employees/<int:emp_pk>/edit", methods=["GET", "POST"])
def edit_employee(emp_pk):
    db = get_db()
    employee = db.execute("SELECT * FROM employees WHERE id = ?", (emp_pk,)).fetchone()
    if not employee:
        abort(404)

    if request.method == "POST":
        data, errors = validate_employee_form(request.form, existing_employee_id=employee["employee_id"])

        if not errors:
            # Check uniqueness – allow the employee to keep their own ID
            conflict = db.execute(
                "SELECT id FROM employees WHERE employee_id = ? AND id != ?",
                (data["employee_id"], emp_pk)
            ).fetchone()
            if conflict:
                errors.append(f"Employee ID '{data['employee_id']}' is already used by another employee.")

        if errors:
            return render_template("edit_employee.html",
                                   errors=errors,
                                   employee=employee,
                                   form=request.form,
                                   departments=DEPARTMENTS)

        db.execute("""
            UPDATE employees
            SET employee_id=?, full_name=?, email=?, phone=?,
                department=?, designation=?, joining_date=?, salary=?
            WHERE id=?
        """, (
            data["employee_id"], data["full_name"], data["email"],
            data["phone"], data["department"], data["designation"],
            data["joining_date"], data["salary"], emp_pk
        ))
        db.commit()
        flash(f"Employee '{data['full_name']}' updated successfully!", "success")
        return redirect(url_for("employee_details", emp_pk=emp_pk))

    return render_template("edit_employee.html",
                           errors=[],
                           employee=employee,
                           form=employee,
                           departments=DEPARTMENTS)


@app.route("/employees/<int:emp_pk>/delete", methods=["POST"])
def delete_employee(emp_pk):
    db = get_db()
    employee = db.execute("SELECT * FROM employees WHERE id = ?", (emp_pk,)).fetchone()
    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))
    db.execute("DELETE FROM employees WHERE id = ?", (emp_pk,))
    db.commit()
    flash(f"Employee '{employee['full_name']}' deleted successfully.", "success")
    return redirect(url_for("employees"))


# ---------------------------------------------------------------------------
# Health & Metrics
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    """Simple health-check endpoint for Docker and Prometheus."""
    try:
        db = get_db()
        db.execute("SELECT 1")
        return jsonify({"status": "healthy", "database": "ok"}), 200
    except Exception as exc:  # pragma: no cover
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500


# /metrics is automatically provided by PrometheusMetrics


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    seed_db()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
