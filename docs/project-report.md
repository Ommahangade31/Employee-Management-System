# Employee Management System with DevOps Pipeline
## Mini-Project Report

**Submitted by:** [Your Name]
**Roll Number:** [Your Roll Number]
**Department:** Artificial Intelligence and Data Science
**Institution:** [Your College Name]
**Academic Year:** 2024–2025
**Guide:** [Guide's Name]

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Proposed System](#4-proposed-system)
5. [Technology Stack](#5-technology-stack)
6. [System Architecture](#6-system-architecture)
7. [Application Development](#7-application-development)
8. [Git and GitHub Implementation](#8-git-and-github-implementation)
9. [Automated Testing](#9-automated-testing)
10. [Jenkins CI/CD Pipeline](#10-jenkins-cicd-pipeline)
11. [Docker Implementation](#11-docker-implementation)
12. [Docker Hub](#12-docker-hub)
13. [Deployment](#13-deployment)
14. [Prometheus Monitoring](#14-prometheus-monitoring)
15. [Grafana Dashboard](#15-grafana-dashboard)
16. [Alerting](#16-alerting)
17. [Results](#17-results)
18. [Challenges](#18-challenges)
19. [Future Scope](#19-future-scope)
20. [Conclusion](#20-conclusion)
21. [References](#21-references)

---

## 1. Introduction

This project presents the design and implementation of an **Employee Management System (EMS)** with a complete end-to-end DevOps pipeline. The application is developed as an undergraduate mini-project for the AI and Data Science program.

Modern software engineering does not end when the code is written. DevOps practices bridge the gap between software development and IT operations, enabling teams to build, test, deploy, and monitor applications reliably and repeatedly. This project demonstrates how those practices are applied to a real working application.

The system allows an administrator to manage employee records through a web browser, and the entire lifecycle—from code commit to deployment and monitoring—is automated using industry-standard tools.

---

## 2. Problem Statement

Organizations need a reliable way to manage employee information. Manual record-keeping using spreadsheets is error-prone and does not scale. Developing a web application to manage employee records is straightforward, but deploying it reliably, testing it automatically, and monitoring it in production are challenges that many students have not yet encountered.

This project addresses both problems:
1. Building a functional Employee Management System.
2. Implementing a DevOps pipeline that automates testing, building, and deployment.

---

## 3. Objectives

- Design and develop a functional web-based Employee Management System.
- Implement CRUD (Create, Read, Update, Delete) operations for employee records.
- Store data persistently in a relational database.
- Write automated tests to validate application behaviour.
- Containerize the application using Docker for consistent deployment.
- Implement a CI/CD pipeline using Jenkins to automate the build, test, and deploy workflow.
- Publish the Docker image to Docker Hub.
- Monitor the application using Prometheus and visualize metrics using Grafana.
- Configure practical alerts to notify about application availability.
- Document the project thoroughly to support the mini-project report.

---

## 4. Proposed System

The proposed system is a **three-tier web application** consisting of:

1. **Presentation Tier** – HTML5 web pages rendered by Flask's Jinja2 template engine, styled with Bootstrap 5 for a professional responsive interface.
2. **Application Tier** – A Python Flask application handling HTTP requests, form validation, and business logic.
3. **Data Tier** – An SQLite database storing employee records persistently.

The system includes:
- A dashboard with summary statistics
- Full CRUD operations for employee records
- Server-side input validation with meaningful error messages
- A `/health` endpoint for availability monitoring
- A `/metrics` endpoint exposing Prometheus-compatible metrics

---

## 5. Technology Stack

### Frontend
- **HTML5** – Page structure and forms
- **CSS3** – Custom styling
- **Bootstrap 5** – Responsive UI components, layout, and utilities
- **Bootstrap Icons** – Icon set
- **Jinja2** – Server-side template rendering (built into Flask)

### Backend
- **Python 3.11** – Programming language
- **Flask 3.0** – Web framework providing routing, request handling, and template rendering
- **Werkzeug** – WSGI utilities (Flask dependency)
- **Gunicorn** – Production WSGI HTTP server

### Database
- **SQLite** – Embedded relational database; no separate database server required
- **sqlite3** – Python standard-library module for database access

### Testing
- **Pytest** – Test framework
- **Flask Test Client** – Simulates HTTP requests without running a real server
- **pytest-cov** – Code coverage reporting

### Version Control
- **Git** – Distributed version control
- **GitHub** – Remote repository hosting

### CI/CD
- **Jenkins** – Open-source automation server
- **Jenkinsfile** – Declarative Pipeline configuration

### Containerization
- **Docker** – Container runtime
- **Docker Compose** – Multi-container orchestration

### Container Registry
- **Docker Hub** – Public Docker image registry

### Monitoring
- **Prometheus** – Time-series metrics database and scraper
- **prometheus-flask-exporter** – Flask integration for Prometheus metrics

### Visualization
- **Grafana** – Dashboard and visualization platform

---

## 6. System Architecture

The application follows a standard MVC-inspired architecture within Flask:

**Routes (Controller):** Flask routes in `app.py` receive HTTP requests, invoke database queries, validate input, and return rendered templates or JSON responses.

**Templates (View):** Jinja2 HTML templates in the `templates/` directory generate the HTML sent to the browser.

**Database (Model):** SQLite database accessed via Python's `sqlite3` module with parameterized queries to prevent SQL injection.

### Docker Compose Service Network

All services run on a shared Docker bridge network named `monitoring`, which allows them to address each other by service name:

| Service    | Internal address | Host port |
|------------|-----------------|-----------|
| app        | app:5000        | 5000      |
| prometheus | prometheus:9090 | 9090      |
| grafana    | grafana:3000    | 3000      |

Prometheus scrapes the Flask application at `http://app:5000/metrics` – it uses the Docker service name `app`, not `localhost`.

---

## 7. Application Development

### Project Structure

```
app.py                   ← Main application: routes, validation, DB helpers
requirements.txt         ← Python dependencies
test_app.py              ← Automated tests
templates/               ← Jinja2 HTML templates
static/                  ← CSS and JavaScript
```

### Database Design

The `employees` table schema:

| Column       | Type    | Constraint       |
|--------------|---------|------------------|
| id           | INTEGER | PRIMARY KEY, AUTO |
| employee_id  | TEXT    | NOT NULL, UNIQUE  |
| full_name    | TEXT    | NOT NULL          |
| email        | TEXT    | NOT NULL          |
| phone        | TEXT    | NOT NULL          |
| department   | TEXT    | NOT NULL          |
| designation  | TEXT    | NOT NULL          |
| joining_date | TEXT    | NOT NULL          |
| salary       | REAL    | NOT NULL          |
| created_at   | TEXT    | DEFAULT now()     |

### Key Implementation Decisions

1. **No ORM** – Python's built-in `sqlite3` module is used directly. This keeps the code simple and easy to understand without requiring knowledge of SQLAlchemy.
2. **Parameterized queries** – All SQL queries use `?` placeholders to prevent SQL injection attacks.
3. **Server-side validation** – All form data is validated in Python before any database operation.
4. **`g` object for DB connection** – Flask's `g` object stores the database connection per request, ensuring connections are properly closed after each request.
5. **Non-root Docker user** – The container runs as a dedicated `appuser` for security.
6. **`init_db` / `seed_db`** – Database initialisation is separate from seeding; `seed_db` only inserts sample data if the table is empty, preventing duplicate records on restart.

### Flask Routes

| Method | URL                          | Purpose                        |
|--------|------------------------------|--------------------------------|
| GET    | /                            | Dashboard                      |
| GET    | /employees                   | Employee list with search/filter|
| GET    | /employees/add               | Add employee form              |
| POST   | /employees/add               | Process add employee form      |
| GET    | /employees/\<pk\>            | Employee details               |
| GET    | /employees/\<pk\>/edit       | Edit employee form             |
| POST   | /employees/\<pk\>/edit       | Process edit employee form     |
| POST   | /employees/\<pk\>/delete     | Delete employee                |
| GET    | /health                      | Health check (JSON)            |
| GET    | /metrics                     | Prometheus metrics             |

---

## 8. Git and GitHub Implementation

Git is used for version control. Each meaningful change is committed with a descriptive message. The project is hosted on GitHub, making it accessible for collaboration and also serving as the source for the Jenkins CI/CD pipeline.

### Basic Git Workflow

```bash
git init
git add .
git commit -m "message"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### .gitignore

The `.gitignore` file excludes:
- Python cache files (`__pycache__/`, `*.pyc`)
- Virtual environment directories (`venv/`)
- Local database files (`*.db`, `data/`)
- Test artifacts (`.coverage`, `.pytest_cache/`)
- IDE configuration files (`.vscode/`, `.idea/`)
- Environment variable files (`.env`)

This keeps the repository clean and prevents sensitive data from being committed.

---

## 9. Automated Testing

Automated tests are written in `test_app.py` using Pytest and the Flask test client.

### Test Strategy

- A temporary SQLite database is created at the start of the test session.
- Each test is independent – it creates its own test data and does not depend on other tests.
- The real application database is never touched during testing.

### Test Cases

| # | Test Name                          | What it verifies                                |
|---|------------------------------------|-------------------------------------------------|
| 1 | test_dashboard_returns_200         | Dashboard page loads successfully               |
| 2 | test_employee_listing_returns_200  | Employee list page loads successfully           |
| 3 | test_create_employee_success       | A valid employee can be added                   |
| 4 | test_employee_saved_in_database    | Added employee appears in the database          |
| 5 | test_duplicate_employee_id_rejected| Duplicate employee IDs are not allowed          |
| 6 | test_invalid_email_rejected        | Invalid email format is rejected                |
| 7 | test_missing_required_fields_rejected | Empty required fields are rejected           |
| 8 | test_update_employee               | Employee record can be updated                  |
| 9 | test_delete_employee               | Employee record can be deleted                  |
|10 | test_search_employee               | Search by name returns correct results          |
|11 | test_nonexistent_employee_returns_404 | 404 is returned for unknown employee ID     |
|12 | test_health_check                  | /health returns {"status": "healthy"}           |
|13 | test_metrics_endpoint              | /metrics exposes Prometheus-format metrics      |

### Running Tests

```bash
pytest test_app.py -v
```

> **[REPLACE THIS SECTION]** Insert your actual test run output and pass/fail results here. Run `pytest test_app.py -v` and paste the terminal output.

---

## 10. Jenkins CI/CD Pipeline

Jenkins automates the process of building, testing, and deploying the application whenever code is pushed to GitHub.

### Pipeline Stages

1. **Checkout** – Jenkins fetches the latest code from the GitHub repository.
2. **Install Dependencies** – Creates a Python virtual environment and installs packages from `requirements.txt`.
3. **Build** – Performs a Python syntax check (`py_compile`) to catch errors before testing.
4. **Automated Tests** – Runs all Pytest tests. The pipeline stops if any test fails.
5. **Docker Build** – Builds the Docker image and tags it with the build number.
6. **Docker Push** – Pushes the image to Docker Hub using stored credentials.
7. **Deploy** – Runs `docker-compose up -d` to deploy the updated application.

### Jenkins Setup Requirements

- Jenkins server installed and running.
- Required plugins: Pipeline, Git, Docker Pipeline, Credentials Binding, JUnit.
- Docker Hub credentials stored in Jenkins with ID: `DOCKERHUB_CREDENTIALS`.
- GitHub repository URL configured in the Pipeline job.

### Why CI/CD?

Without CI/CD, a developer must manually run tests, build the Docker image, push it to the registry, and redeploy—steps that take time and can be forgotten or skipped. Jenkins automates all of these steps, ensuring that only tested code is deployed.

> **[REPLACE THIS SECTION]** Insert screenshots of your Jenkins pipeline execution and stage results here.

---

## 11. Docker Implementation

### Dockerfile Explanation

```dockerfile
FROM python:3.11-slim        # Official Python image, slim variant (smaller size)
WORKDIR /app                 # All commands run from /app inside the container
COPY requirements.txt .      # Copy dependencies first (layer caching)
RUN pip install ...          # Install dependencies
COPY . .                     # Copy application source code
RUN mkdir -p /app/data && adduser appuser  # Non-root user for security
USER appuser                 # Run as non-root
EXPOSE 5000                  # Document the port
CMD [...]                    # Start Gunicorn
```

### Why Docker?

Docker packages the application and all its dependencies into a container image. This ensures the application runs identically on any machine—a developer's laptop, a CI/CD server, or a cloud server—eliminating "it works on my machine" problems.

### Persistent Volume

The SQLite database is stored in `/app/data/employees.db` inside the container. A Docker named volume (`ems_db_data`) is mounted at `/app/data`, ensuring the database persists when the container is restarted or updated.

> **[REPLACE THIS SECTION]** Insert screenshots of your Docker build and container running here.

---

## 12. Docker Hub

Docker Hub is a public registry for Docker images. After building the image locally, it is tagged with the Docker Hub username and repository name, then pushed.

```bash
docker build -t USERNAME/employee-management-system:latest .
docker push USERNAME/employee-management-system:latest
```

The image can then be pulled and run on any machine with Docker installed, without needing the source code.

> **[REPLACE THIS SECTION]** Insert a screenshot of your Docker Hub repository page here.

---

## 13. Deployment

The application is deployed using Docker Compose, which starts the Flask application, Prometheus, and Grafana with a single command:

```bash
docker-compose up -d
```

In the Jenkins pipeline, the Deploy stage runs this command automatically after the image is successfully built and pushed.

### Production Considerations

- `FLASK_DEBUG` is set to `false` in the container.
- Gunicorn (not Flask's built-in server) is used as the WSGI server.
- The application runs as a non-root user inside the container.
- The `SECRET_KEY` should be set to a strong random value via environment variable.

---

## 14. Prometheus Monitoring

Prometheus is an open-source monitoring system that collects metrics by periodically making HTTP GET requests to a configured endpoint (scraping). The Flask application exposes metrics at `/metrics` using the `prometheus-flask-exporter` library.

### Metrics Provided by Flask

| Metric | Description |
|--------|-------------|
| `flask_http_request_total` | Total HTTP requests, labeled by method, path, and status |
| `flask_http_request_duration_seconds` | Request duration histogram |
| `up` | 1 if the target is reachable, 0 otherwise |

### Prometheus Configuration

`monitoring/prometheus.yml` configures Prometheus to:
1. Scrape its own metrics every 15 seconds.
2. Scrape the Flask application at `http://app:5000/metrics` every 15 seconds.
3. Load alert rules from `alert-rules.yml`.

The target address `app:5000` uses the Docker service name because Prometheus runs in the same Docker network as the Flask application.

> **[REPLACE THIS SECTION]** Insert a screenshot of the Prometheus Targets page (Status → Targets) showing the `employee_management_system` target as UP.

---

## 15. Grafana Dashboard

Grafana connects to Prometheus as a data source and visualizes the collected metrics. The data source and dashboard are provisioned automatically when the Grafana container starts, using YAML configuration files in `monitoring/grafana/provisioning/`.

### Dashboard Panels

| Panel | Description |
|-------|-------------|
| App Status | Shows UP or DOWN based on Prometheus `up` metric |
| Total HTTP Requests | Cumulative count of all HTTP requests |
| Request Rate (5m) | Requests per second averaged over 5 minutes |
| HTTP Error Rate (5xx) | Percentage of requests returning 5xx errors |
| p95 Response Time | 95th-percentile response duration |
| HTTP Request Rate by Status | Time series showing request rate per status code |
| Response Duration p50/p95/p99 | Time series showing response time percentiles |

### System Metrics

CPU, memory, disk, and network metrics require the **Node Exporter** (a separate Prometheus exporter that runs on the host). These are not included in the default stack to keep the project simple, but can be added by:
1. Adding `prom/node-exporter` as a service in `docker-compose.yml`.
2. Adding a scrape job for it in `prometheus.yml`.
3. Creating a Grafana dashboard using `node_cpu_seconds_total`, `node_memory_MemFree_bytes`, etc.

> **[REPLACE THIS SECTION]** Insert a screenshot of your Grafana dashboard here.

---

## 16. Alerting

Three alert rules are defined in `monitoring/alert-rules.yml`:

### Alert 1: EmployeeManagementSystemDown (Critical)

- **Condition:** `up{job="employee_management_system"} == 0`
- **For:** 1 minute (must be down for 1 full minute before alerting)
- **Severity:** critical
- **What it means:** The Flask application is not responding to Prometheus scrapes.
- **How to test:** Stop the app container with `docker-compose stop app`, wait 2 minutes, then check Prometheus → Alerts.
- **How to resolve:** Restart the app: `docker-compose start app`.

### Alert 2: HighHttpErrorRate (Warning)

- **Condition:** More than 10% of HTTP responses are 5xx errors over 5 minutes.
- **Severity:** warning

### Alert 3: SlowResponseTime (Warning)

- **Condition:** p95 response time exceeds 2 seconds.
- **Severity:** warning

### Alert Notifications

These alerts appear in the Prometheus Alerts tab (http://localhost:9090/alerts). To send notifications (email, Slack, PagerDuty), **Alertmanager** must be configured. Alertmanager is not included in this project to keep it simple, but the configuration would involve:
1. Adding an `alertmanager` service to `docker-compose.yml`.
2. Creating `alertmanager.yml` with receiver configuration.
3. Adding the `alerting:` section to `prometheus.yml`.

---

## 17. Results

> **[REPLACE THIS SECTION]** This section must be completed after running the actual project. Replace the placeholders with real screenshots and outputs.

### Application

- **[INSERT SCREENSHOT]** – Dashboard showing total employees and department breakdown.
- **[INSERT SCREENSHOT]** – Employee list with search/filter working.
- **[INSERT SCREENSHOT]** – Add Employee form with validation error.
- **[INSERT SCREENSHOT]** – Successfully added employee.

### Automated Tests

```
[INSERT OUTPUT OF: pytest test_app.py -v]
```

Number of tests passed: ___  
Number of tests failed: ___

### Docker

```
[INSERT OUTPUT OF: docker build -t employee-management-system . ]
[INSERT OUTPUT OF: docker-compose ps]
```

### Prometheus

- **[INSERT SCREENSHOT]** – Prometheus Targets page showing employee_management_system as UP.
- **[INSERT SCREENSHOT]** – Prometheus Expression browser with a query result.

### Grafana

- **[INSERT SCREENSHOT]** – Grafana dashboard showing application metrics.

### Jenkins

- **[INSERT SCREENSHOT]** – Jenkins pipeline showing all stages green.

---

## 18. Challenges

1. **Database path in Docker** – SQLite's database path must be consistent between development and Docker. Solved by using the `DATABASE_PATH` environment variable and mounting a Docker volume at `/app/data`.

2. **Prometheus cannot scrape localhost** – When Prometheus and the Flask app run in separate Docker containers, Prometheus cannot reach `localhost:5000` because `localhost` refers to the Prometheus container itself. Solved by using the Docker service name `app:5000`.

3. **Test isolation** – Tests must not interfere with each other or with real data. Solved by setting `DATABASE_PATH` to a temporary file before importing the app, and using the session-scoped `setup_database` fixture.

4. **Non-root container user** – Setting up a non-root user in Docker requires careful permission management on the `/app/data` directory. Solved by running `chown -R appuser:appuser /app` in the Dockerfile after creating the user.

5. **Grafana provisioning** – Grafana's automatic provisioning requires specific file paths inside the container. Solved by mapping the local `monitoring/grafana/provisioning` directory to `/etc/grafana/provisioning` in `docker-compose.yml`.

---

## 19. Future Scope

1. **Authentication** – Add administrator login with hashed passwords (using `werkzeug.security`).
2. **Node Exporter** – Add Prometheus Node Exporter for host CPU, memory, disk, and network metrics.
3. **Alertmanager** – Integrate Alertmanager to send email or Slack notifications when alerts fire.
4. **PostgreSQL** – Migrate from SQLite to PostgreSQL for better concurrent access and scalability.
5. **Kubernetes** – Deploy the application on a Kubernetes cluster for auto-scaling and high availability.
6. **HTTPS** – Configure an Nginx reverse proxy with a TLS certificate.
7. **Pagination** – Add server-side pagination to the employee list for large datasets.
8. **Export** – Add CSV/PDF export of employee records.
9. **Role-based access** – Separate HR manager and read-only roles.
10. **Audit log** – Record who changed what and when.

---

## 20. Conclusion

This mini-project successfully demonstrates the development and deployment of a full-stack Employee Management System using modern DevOps practices.

The project covers the complete software lifecycle:
- **Development** – A functional Flask web application with SQLite persistence.
- **Testing** – 13 automated Pytest tests covering all major features.
- **Version Control** – Git and GitHub for source code management.
- **Containerization** – Docker and Docker Compose for consistent, portable deployment.
- **CI/CD** – Jenkins pipeline automating build, test, and deploy.
- **Monitoring** – Prometheus scraping application metrics, Grafana visualizing them, and alert rules for availability monitoring.

This project demonstrates that DevOps is not a separate process added after development—it is integrated from the beginning, making the software more reliable, more testable, and easier to deploy and maintain.

---

## 21. References

1. Flask Documentation – https://flask.palletsprojects.com
2. Bootstrap 5 Documentation – https://getbootstrap.com/docs/5.3
3. Pytest Documentation – https://docs.pytest.org
4. Docker Documentation – https://docs.docker.com
5. Jenkins Documentation – https://www.jenkins.io/doc
6. Prometheus Documentation – https://prometheus.io/docs
7. Grafana Documentation – https://grafana.com/docs
8. prometheus-flask-exporter – https://github.com/rycus86/prometheus_flask_exporter
9. Gunicorn Documentation – https://gunicorn.org
10. SQLite Documentation – https://www.sqlite.org/docs.html
11. Python sqlite3 Module – https://docs.python.org/3/library/sqlite3.html
