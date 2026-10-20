#!/bin/sh
# Initialize database and seed data before starting the server
python -c "from app import init_db, seed_db; init_db(); seed_db()"
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app
