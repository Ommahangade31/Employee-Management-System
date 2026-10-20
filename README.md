# Employee Management System

A full-stack Employee Management System built with **Python Flask**, **SQLite**, and a complete **DevOps pipeline** using Docker, Jenkins, Prometheus, and Grafana.

This is an undergraduate AI & Data Science mini-project demonstrating end-to-end DevOps practices.

---

## Features

- **Dashboard** – Summary cards, department breakdown, recently added employees
- **Add Employee** – Form with server-side validation
- **View Employees** – Paginated responsive table
- **Search & Filter** – Filter by name, ID, or department
- **Edit Employee** – Update any field with validation
- **Delete Employee** – Confirmation modal before deletion
- **Employee Details** – Full record view
- **Health Check** – `/health` endpoint
- **Prometheus Metrics** – `/metrics` endpoint

---

## Technology Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Frontend      | HTML5, CSS3, Bootstrap 5, Jinja2    |
| Backend       | Python 3.11, Flask 3                |
| Database      | SQLite (persistent via Docker volume)|
| Testing       | Pytest, Flask test client           |
| Containerization | Docker, Docker Compose           |
| CI/CD         | Jenkins (Declarative Pipeline)      |
| Registry      | Docker Hub                          |
| Monitoring    | Prometheus                          |
| Visualization | Grafana                             |

---

## Prerequisites

- Python 3.11+
- pip
- Docker Desktop (for containerized runs)
- Git

---

## Installation – Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/employee-management-system.git
cd employee-management-system

# 2. Create a virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialise the database and add sample data
python -c "from app import init_db, seed_db; init_db(); seed_db()"

# 5. Run the application
python app.py
```

Open your browser at **http://localhost:5000**

---

## Running Automated Tests

```bash
# Activate your virtual environment first (see above)

# Run all tests
pytest test_app.py -v

# Run with coverage report
pytest test_app.py -v --cov=app --cov-report=term-missing
```

Tests use a temporary database – your real data is never touched.

---

## Docker – Build and Run

### Build the image

```bash
docker build -t employee-management-system .
```

### Run the container

```bash
docker run -d \
  --name ems_app \
  -p 5000:5000 \
  -v ems_db_data:/app/data \
  -e SECRET_KEY=my-secret-key \
  employee-management-system
```

Open **http://localhost:5000**

### Stop the container

```bash
docker stop ems_app && docker rm ems_app
```

---

## Docker Compose – Full Stack (App + Prometheus + Grafana)

```bash
# Start all services in the background
docker-compose up -d

# Check running services
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

| Service    | URL                    |
|------------|------------------------|
| Application| http://localhost:5000  |
| Prometheus | http://localhost:9090  |
| Grafana    | http://localhost:3000  |

---

## Git and GitHub

```bash
# Initialise a new repository
git init

# Stage all files
git add .

# Create the initial commit
git commit -m "Initial commit – Employee Management System"

# Add your GitHub remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git push -u origin main
```

---

## Jenkins CI/CD Pipeline

### Required Jenkins Plugins
- Pipeline
- Git Plugin
- Docker Pipeline Plugin
- Credentials Binding Plugin
- JUnit Plugin (for test reports)

### Setup Steps

1. Install Jenkins (https://www.jenkins.io/download/).
2. Install the plugins listed above.
3. Add Docker Hub credentials:
   - Jenkins → Manage Jenkins → Credentials → (global) → Add Credentials
   - Kind: **Username with password**
   - ID: `DOCKERHUB_CREDENTIALS`
4. Create a new Pipeline job:
   - New Item → Pipeline
   - Pipeline Definition: **Pipeline script from SCM**
   - SCM: Git → your repository URL
   - Script Path: `Jenkinsfile`
5. Set the `DOCKERHUB_USERNAME` environment variable in the Jenkinsfile or as a Jenkins environment variable.
6. Click **Build Now**.

### Pipeline Stages

```
Checkout → Install Dependencies → Build → Tests → Docker Build → Docker Push → Deploy
```

---

## Docker Hub

```bash
# Login to Docker Hub
docker login

# Build with your username
docker build -t YOUR_DOCKERHUB_USERNAME/employee-management-system:latest .

# Push the image
docker push YOUR_DOCKERHUB_USERNAME/employee-management-system:latest

# Pull from another machine
docker pull YOUR_DOCKERHUB_USERNAME/employee-management-system:latest

# Run the pulled image
docker run -d -p 5000:5000 YOUR_DOCKERHUB_USERNAME/employee-management-system:latest
```

---

## Prometheus Monitoring

1. Start services: `docker-compose up -d`
2. Open Prometheus: **http://localhost:9090**
3. Go to **Status → Targets** to verify the `employee_management_system` target is **UP**.
4. Try these queries in the Expression browser:
   - `up{job="employee_management_system"}` – Is the app up?
   - `sum(flask_http_request_total)` – Total requests
   - `rate(flask_http_request_total[5m])` – Request rate

---

## Grafana Dashboard

1. Open Grafana: **http://localhost:3000**
2. Login: `admin` / `admin` (change after first login)
3. The **Prometheus** data source is provisioned automatically.
4. Go to **Dashboards → EMS → Employee Management System** to view the pre-built dashboard.

### Dashboard Panels
- App Status (UP/DOWN)
- Total HTTP Requests
- Request Rate (5m)
- HTTP Error Rate (5xx)
- p95 Response Time
- HTTP Request Rate by Status (time series)
- Response Duration p50/p95/p99 (time series)

### System Metrics (CPU, Memory, Disk, Network)
These require the **Node Exporter** (not included in the default Compose stack to keep it simple).
Add it to `docker-compose.yml` and scrape it with Prometheus to monitor host resources.

---

## Alerting

Three alert rules are defined in `monitoring/alert-rules.yml`:

| Alert                      | Condition                          | Severity |
|----------------------------|------------------------------------|----------|
| `EmployeeManagementSystemDown` | App unreachable for >1 minute  | critical |
| `HighHttpErrorRate`        | >10% 5xx errors over 5 minutes     | warning  |
| `SlowResponseTime`         | p95 latency >2 seconds             | warning  |

To verify an alert:
1. Stop the app container: `docker-compose stop app`
2. Wait 1–2 minutes.
3. Open Prometheus → **Alerts** to see the `EmployeeManagementSystemDown` alert fire.
4. Restart the app: `docker-compose start app`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5000 already in use | Change the host port in `docker-compose.yml`: `"5001:5000"` |
| Database not found | Run `python -c "from app import init_db; init_db()"` |
| Prometheus target DOWN | Ensure the app is running; check Docker network with `docker network ls` |
| Grafana can't reach Prometheus | Both must be on the same Docker network (`monitoring`) |
| Permission denied on `/app/data` | The Docker volume may be owned by root; rebuild with `docker-compose up -d --build` |

---

## Project Structure

```
employee-management-system/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── test_app.py              # Automated tests (Pytest)
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-service stack
├── Jenkinsfile              # CI/CD pipeline
├── entrypoint.sh            # Container startup script
├── .dockerignore
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html           # Dashboard
│   ├── employees.html       # Employee list
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
│   ├── prometheus.yml
│   ├── alert-rules.yml
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/prometheus.yml
│       │   └── dashboards/dashboard.yml
│       └── dashboards/ems-dashboard.json
│
└── docs/
    ├── architecture.md
    ├── setup-guide.md
    ├── troubleshooting.md
    └── project-report.md
```
