# Troubleshooting Guide

## Application Issues

### The application does not start

**Symptom:** Running `python app.py` shows an error.

**Solutions:**
1. Make sure the virtual environment is activated: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS).
2. Make sure dependencies are installed: `pip install -r requirements.txt`.
3. Check that port 5000 is free: `netstat -ano | findstr :5000` (Windows).

---

### Database not initialised

**Symptom:** `OperationalError: no such table: employees`

**Solution:**
```bash
python -c "from app import init_db; init_db()"
```

---

### Port 5000 already in use

**Solution:**
```bash
# Find what is using port 5000 (Windows)
netstat -ano | findstr :5000

# Kill the process (replace <PID> with the actual PID)
taskkill /PID <PID> /F
```
Or change the port in `app.py` and `docker-compose.yml`.

---

## Docker Issues

### Docker build fails

**Symptom:** `ERROR [4/5] RUN pip install ...`

**Solution:**
- Ensure `requirements.txt` is present and correctly formatted.
- Try: `docker build --no-cache -t employee-management-system .`

---

### Container exits immediately

**Solution:**
```bash
# Check the container logs
docker logs ems_app
```

---

### Cannot reach http://localhost:5000 after `docker-compose up`

**Solutions:**
1. Check containers are running: `docker-compose ps`
2. Check for port conflicts on the host.
3. Try `docker-compose up -d --build` to rebuild.

---

## Prometheus Issues

### Target shows "DOWN" in Prometheus

**Possible causes:**
- The Flask application container is not running.
- The service name in `prometheus.yml` does not match the `docker-compose.yml` service name.

**Checks:**
```bash
docker-compose ps            # Is the app container running?
docker network inspect employee_management_system_monitoring  # Are app and prometheus on the same network?
```

---

### No metrics in Prometheus

**Solution:**
- Open http://localhost:5000/metrics in your browser.
- If you see Prometheus text output, the app is exposing metrics correctly.
- If you see a 404, the `prometheus_flask_exporter` may not have been installed: `pip install prometheus-flask-exporter`.

---

## Grafana Issues

### Grafana shows "No data"

**Possible causes:**
- Prometheus is not configured as a data source (check http://localhost:3000/datasources).
- The time range in Grafana is set too far in the past.
- The application has not received any requests yet (no metrics to show).

**Solution:**
1. Visit the app at http://localhost:5000 to generate some requests.
2. Wait 30 seconds for Prometheus to scrape.
3. Refresh the Grafana dashboard.

---

### Cannot log in to Grafana

**Default credentials:** `admin` / `admin`

If you have changed the password and forgotten it:
```bash
docker-compose down -v   # WARNING: this deletes Grafana data
docker-compose up -d
```

---

## Jenkins Issues

### Pipeline fails at "Docker Build" stage

**Possible cause:** Jenkins agent does not have Docker installed.

**Solution:** Install Docker on the Jenkins agent machine and add the Jenkins user to the `docker` group:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Credential error when pushing to Docker Hub

**Solution:** Ensure the credential ID in the Jenkinsfile (`DOCKERHUB_CREDENTIALS`) exactly matches the credential ID configured in Jenkins → Manage Jenkins → Credentials.
