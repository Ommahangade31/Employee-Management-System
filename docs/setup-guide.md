# Setup Guide

## Running Locally (Development)

### Prerequisites

- Python 3.11 or higher
- pip (comes with Python)
- Git

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/YOUR_USERNAME/employee-management-system.git
cd employee-management-system

# 2. Create a virtual environment (isolates project dependencies)
python -m venv venv

# Activate on Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activate on Windows CMD
venv\Scripts\activate.bat

# Activate on Linux / macOS
source venv/bin/activate

# 3. Install all Python dependencies
pip install -r requirements.txt

# 4. Set up the database (creates tables and inserts sample data)
python -c "from app import init_db, seed_db; init_db(); seed_db()"

# 5. Start the application
python app.py
```

Visit **http://localhost:5000** in your browser.

---

## Running with Docker (Single Container)

```bash
# Build the image
docker build -t employee-management-system .

# Run the container
docker run -d \
  --name ems \
  -p 5000:5000 \
  -v ems_db:/app/data \
  employee-management-system

# View logs
docker logs -f ems
```

---

## Running with Docker Compose (Recommended)

```bash
# Start all services (app + Prometheus + Grafana)
docker-compose up -d

# Verify containers are running
docker-compose ps

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database!)
docker-compose down -v
```

---

## Environment Variables

| Variable         | Default                              | Description                     |
|------------------|--------------------------------------|---------------------------------|
| `SECRET_KEY`     | dev-secret-key-change-in-production  | Flask session secret key        |
| `DATABASE_PATH`  | ./data/employees.db                  | Path to the SQLite database     |
| `FLASK_DEBUG`    | false                                | Enable Flask debug mode         |
| `GRAFANA_USER`   | admin                                | Grafana admin username          |
| `GRAFANA_PASSWORD` | admin                              | Grafana admin password          |

Set these in a `.env` file (never commit it to Git):

```
SECRET_KEY=your-very-secure-random-key
GRAFANA_PASSWORD=secure-grafana-password
```

---

## Running Tests

```bash
# Activate virtual environment first
pytest test_app.py -v
```

---

## Accessing Services

| Service       | URL                    | Credentials        |
|---------------|------------------------|--------------------|
| Application   | http://localhost:5000  | No login required  |
| Prometheus    | http://localhost:9090  | No login required  |
| Grafana       | http://localhost:3000  | admin / admin      |
| Health Check  | http://localhost:5000/health | –           |
| Metrics       | http://localhost:5000/metrics | –          |
