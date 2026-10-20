# Employee Management System
### End-to-End DevOps Pipeline — Undergraduate Mini-Project

A full-stack Employee Management System built with **Python Flask** and **SQLite**, demonstrating a complete DevOps pipeline using Docker, Jenkins, Prometheus, and Grafana.

---

## Features

| Feature | Description |
|---|---|
| Dashboard | Summary cards, department chart, recently added employees |
| Add Employee | Form with server-side validation (unique ID, email, required fields) |
| View Employees | Responsive sortable table |
| Search & Filter | Filter by name, employee ID, or department |
| Edit Employee | Update any field with validation |
| Delete Employee | Confirmation modal before deletion |
| Employee Details | Full record view |
| `/health` | JSON health-check endpoint |
| `/metrics` | Prometheus-compatible metrics endpoint |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, Jinja2 |
| Backend | Python 3.11, Flask 3.0, Gunicorn |
| Database | SQLite (Docker named volume for persistence) |
| Testing | Pytest 8, Flask test client |
| Version Control | Git, GitHub |
| CI/CD | Jenkins (Declarative Pipeline) |
| Containerization | Docker, Docker Compose |
| Registry | Docker Hub |
| Monitoring | Prometheus |
| Visualization | Grafana |

---

## Prerequisites

| Tool | Purpose | Install |
|---|---|---|
| Python 3.11+ | Run the app locally | https://python.org |
| Git | Version control | https://git-scm.com |
| Docker Desktop | Containers + Compose | https://docs.docker.com/desktop/ |
| Jenkins | CI/CD server | https://jenkins.io/download/ |

---

## Running Locally (No Docker)

```powershell
# 1 — Create virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate       # Linux / macOS

# 2 — Install dependencies
pip install -r requirements.txt

# 3 — Initialise the database and load sample data
python -c "from app import init_db, seed_db; init_db(); seed_db()"

# 4 — Start the development server
python app.py
```

Open **http://localhost:5000**

To stop: press `Ctrl+C`

---

## Running Automated Tests

```powershell
# Activate the virtual environment first (see above), then:
pytest test_app.py -v
```

**Verified result (13 tests, 0 failures):**
```
test_dashboard_returns_200                  PASSED
test_employee_listing_returns_200           PASSED
test_create_employee_success                PASSED
test_employee_saved_in_database             PASSED
test_duplicate_employee_id_rejected         PASSED
test_invalid_email_rejected                 PASSED
test_missing_required_fields_rejected       PASSED
test_update_employee                        PASSED
test_delete_employee                        PASSED
test_search_employee                        PASSED
test_nonexistent_employee_returns_404       PASSED
test_health_check                           PASSED
test_metrics_endpoint                       PASSED
======================== 13 passed in 0.73s ==============================
```

Tests use a temporary database — real data is never modified.

---

## Docker — Single Container

```bash
# Build the image
docker build -t employee-management-system .

# Run the container (database stored in a named volume)
docker run -d \
  --name ems \
  -p 5000:5000 \
  -v ems_db:/app/data \
  -e SECRET_KEY=my-secret-key \
  employee-management-system

# Check it is running
docker ps

# View logs
docker logs -f ems

# Stop and remove
docker stop ems && docker rm ems
```

---

## Docker Compose — Full Stack (App + Prometheus + Grafana)

```bash
# Start all services in the background
docker-compose up -d

# Check all containers are running (should show 3 containers Up)
docker-compose ps

# Stream logs from the app
docker-compose logs -f app

# Rebuild the app image (after code changes)
docker-compose up -d --build

# Stop all services (keeps volumes/database intact)
docker-compose down

# Stop and DELETE all data (volumes)
docker-compose down -v
```

| Service | URL | Credentials |
|---|---|---|
| Application | http://localhost:5000 | None |
| Prometheus | http://localhost:9090 | None |
| Grafana | http://localhost:3000 | admin / admin |
| Health check | http://localhost:5000/health | None |
| Metrics | http://localhost:5000/metrics | None |

---

## Verifying Database Persistence

The SQLite database is stored in the Docker named volume `ems_db_data`, mounted at `/app/data/employees.db` inside the container.

```bash
# Add an employee through the web UI, then restart the container:
docker-compose restart app

# The employee should still be visible at http://localhost:5000
# Verify directly:
docker-compose exec app python -c \
  "from app import get_db, app
with app.app_context():
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
    print(f'Employees in DB: {count}')"
```

---

## Git and GitHub

```bash
# Initialise a repository (only needed once)
git init
git add .
git commit -m "Initial commit – Employee Management System with DevOps pipeline"

# Connect to your GitHub repository (replace with your details)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main

# After making changes
git add .
git commit -m "Describe your change here"
git push
```

---

## Jenkins CI/CD Pipeline Setup

### Required Jenkins Plugins
Install these at **Manage Jenkins → Plugins → Available**:
- Pipeline
- Git Plugin
- Docker Pipeline
- Credentials Binding
- JUnit
- Workspace Cleanup

### Configure Docker Hub Credentials
1. **Manage Jenkins → Credentials → (global) → Add Credentials**
2. Kind: **Username with password**
3. Username: your Docker Hub username
4. Password: your Docker Hub password or access token
5. ID: `DOCKERHUB_CREDENTIALS` ← exact spelling required

### Configure Your Docker Hub Username
**Manage Jenkins → System → Global Properties → Environment Variables**
- Name: `DOCKERHUB_USERNAME`
- Value: your Docker Hub username

### Create the Pipeline Job
1. **New Item → Pipeline**
2. Pipeline Definition: **Pipeline script from SCM**
3. SCM: **Git**
4. Repository URL: your GitHub repository URL
5. Script Path: `Jenkinsfile`
6. Click **Save → Build Now**

### What Each Stage Does
| Stage | What Happens | Stops on Failure? |
|---|---|---|
| Checkout | Pulls code from GitHub | Yes |
| Install Dependencies | `pip install -r requirements.txt` | Yes |
| Build | Python syntax check | Yes |
| Automated Tests | Runs 13 Pytest tests, publishes JUnit results | **Yes** |
| Docker Build | `docker build` the image | Yes |
| Docker Push | Push to Docker Hub (skipped if credentials absent) | Yes |
| Deploy | `docker-compose up -d` | Yes |

---

## Docker Hub

```bash
# Login
docker login

# Build with your username
docker build -t YOUR_USERNAME/employee-management-system:latest .

# Push
docker push YOUR_USERNAME/employee-management-system:latest

# Pull on another machine
docker pull YOUR_USERNAME/employee-management-system:latest

# Run the pulled image
docker run -d -p 5000:5000 -v ems_db:/app/data \
  YOUR_USERNAME/employee-management-system:latest
```

---

## Prometheus

After `docker-compose up -d`:

1. Open **http://localhost:9090/targets**
2. Both targets should be **UP**:
   - `employee_management_system` → `http://app:5000/metrics`
   - `prometheus` → `http://localhost:9090/metrics`

**Useful queries** (paste into the Expression box at http://localhost:9090/graph):

```promql
# Is the app running? (1 = yes, 0 = down)
up{job="employee_management_system"}

# Total HTTP requests served
sum(flask_http_request_total{job="employee_management_system"})

# Request rate over the last 5 minutes
sum(rate(flask_http_request_total{job="employee_management_system"}[5m]))

# 95th-percentile response time
histogram_quantile(0.95,
  sum(rate(flask_http_request_duration_seconds_bucket{job="employee_management_system"}[5m])) by (le))
```

---

## Grafana Dashboard

After `docker-compose up -d`:

1. Open **http://localhost:3000** → login `admin` / `admin`
2. The **Prometheus** data source is provisioned automatically
3. Go to **Dashboards → EMS → Employee Management System**

If the dashboard shows "No data", generate traffic by visiting the app, then wait 30 seconds.

**To import the dashboard manually:**
1. Click **+** → **Import dashboard**
2. Upload `monitoring/grafana/dashboards/ems-dashboard.json`
3. Select the **Prometheus** data source
4. Click **Import**

---

## Alerting

Three alert rules are defined in `monitoring/alert-rules.yml`:

| Alert | Condition | Severity |
|---|---|---|
| `EmployeeManagementSystemDown` | App unreachable for >1 minute | critical |
| `HighHttpErrorRate` | >10% 5xx errors (with traffic) | warning |
| `SlowResponseTime` | p95 latency >2s (with traffic) | warning |

**To test the availability alert:**

```bash
# Stop the app container
docker-compose stop app

# Wait 1–2 minutes, then open:
# http://localhost:9090/alerts
# "EmployeeManagementSystemDown" will show as FIRING

# Restart the app
docker-compose start app
```

---

## System Metrics (CPU / Memory / Disk / Network)

These require the **Prometheus Node Exporter**. See [`docs/node-exporter.md`](docs/node-exporter.md) for full instructions. Import Grafana dashboard **ID 1860** for a pre-built host metrics dashboard.

---

## Environment Variables

Create a `.env` file (see `.env.example`):

```bash
cp .env.example .env
# Edit .env with a real SECRET_KEY and GRAFANA_PASSWORD
```

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | dev-secret-key-... | Flask session key — change in production |
| `DATABASE_PATH` | /app/data/employees.db | SQLite file path inside container |
| `FLASK_DEBUG` | false | Never enable in production |
| `GRAFANA_USER` | admin | Grafana login username |
| `GRAFANA_PASSWORD` | admin | Grafana login password |

---

## Project Structure

```
employee-management-system/
├── app.py                        Flask application + routes + DB helpers
├── requirements.txt              Python dependencies
├── test_app.py                   13 automated Pytest tests
├── Dockerfile                    Container image definition
├── docker-compose.yml            App + Prometheus + Grafana stack
├── Jenkinsfile                   CI/CD pipeline (7 stages)
├── entrypoint.sh                 Container startup helper
├── .env.example                  Template for local environment variables
├── .dockerignore
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html                 Sidebar + navbar layout
│   ├── index.html                Dashboard
│   ├── employees.html            Employee list + search
│   ├── add_employee.html
│   ├── edit_employee.html
│   ├── employee_details.html
│   ├── 404.html
│   └── 500.html
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
├── monitoring/
│   ├── prometheus.yml            Scrape config (app:5000/metrics)
│   ├── alert-rules.yml           3 alert rules (down, errors, latency)
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/prometheus.yml   Auto-provision Prometheus DS
│       │   └── dashboards/dashboard.yml     Dashboard file provider
│       └── dashboards/
│           └── ems-dashboard.json           7-panel dashboard
│
└── docs/
    ├── architecture.md           System and pipeline diagrams
    ├── setup-guide.md            Detailed setup instructions
    ├── troubleshooting.md        Common problems and solutions
    ├── node-exporter.md          Adding system metrics (CPU/RAM/disk)
    └── project-report.md         Full mini-project report template
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Port 5000 already in use | Change `"5000:5000"` to `"5001:5000"` in docker-compose.yml |
| `No such table: employees` | Run `python -c "from app import init_db; init_db()"` |
| Prometheus target DOWN | Check `docker-compose ps` — is the app container running? |
| Grafana "No data" | Visit the app to generate traffic, wait 30s, refresh |
| Docker permission denied | On Linux: `sudo usermod -aG docker $USER` then log out and back in |
| `ERR_CONNECTION_REFUSED` | The app is not running — start it with `python app.py` or `docker-compose up -d` |
| Jenkins "DOCKERHUB_CREDENTIALS not found" | Add the credential in Jenkins with ID exactly `DOCKERHUB_CREDENTIALS` |
