# ============================================================
# Dockerfile – Employee Management System
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# Create non-root user BEFORE copying files (better layer ordering)
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Install dependencies (layer cached separately from source code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and set ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user (security best practice)
USER appuser

# Expose the Gunicorn/Flask port
EXPOSE 5000

# Runtime environment variables – override at docker run / docker-compose
ENV DATABASE_PATH=/app/data/employees.db \
    SECRET_KEY=change-this-in-production \
    FLASK_DEBUG=false

# Initialise the database then start Gunicorn (2 workers, 60s timeout)
CMD ["sh", "-c", "python -c 'from app import init_db, seed_db; init_db(); seed_db()' && gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app"]
