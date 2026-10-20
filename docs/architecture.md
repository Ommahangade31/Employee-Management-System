# System Architecture

## Overview

The Employee Management System (EMS) follows a simple three-tier web application architecture:

```
Browser (Client)
      |
      | HTTP
      ↓
Flask Application (app.py)          ← Application Tier
      |
      | SQL Queries
      ↓
SQLite Database (employees.db)      ← Data Tier
```

## Component Diagram

```
+---------------------+       +---------------------+
|   User's Browser    |       |     Prometheus       |
|  (HTML + Bootstrap) |       |  (Metrics Scraper)   |
+---------------------+       +---------------------+
          |                             |
          | HTTP :5000                  | HTTP :5000/metrics
          ↓                             ↓
+---------------------------------------------+
|           Flask Application (Gunicorn)       |
|                  app.py                      |
|  Routes: /, /employees, /employees/add, ...  |
|  Endpoints: /health, /metrics                |
+---------------------------------------------+
          |
          | SQLite
          ↓
+---------------------+
|  SQLite Database    |
|  (employees.db)     |
|  (Docker Volume)    |
+---------------------+
```

## Docker Compose Network

```
Docker Network: monitoring
┌─────────────────────────────────────────────┐
│                                             │
│  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │    app    │  │prometheus │  │ grafana │ │
│  │  :5000    │  │   :9090   │  │  :3000  │ │
│  └───────────┘  └───────────┘  └─────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

## CI/CD Pipeline Flow

```
Developer pushes code to GitHub
         │
         ↓
Jenkins polls / receives webhook
         │
         ↓
┌────────────────────┐
│  Stage: Checkout   │  Pull code from GitHub
└────────────────────┘
         │
         ↓
┌─────────────────────────┐
│ Stage: Install Deps     │  pip install -r requirements.txt
└─────────────────────────┘
         │
         ↓
┌────────────────────┐
│  Stage: Build      │  Syntax check (py_compile)
└────────────────────┘
         │
         ↓
┌────────────────────────┐
│  Stage: Tests          │  pytest test_app.py
└────────────────────────┘
     PASS │       FAIL │
          │            └── Pipeline stops here
          ↓
┌─────────────────────┐
│  Stage: Docker Build│  docker build
└─────────────────────┘
         │
         ↓
┌─────────────────────┐
│  Stage: Docker Push │  docker push to Docker Hub
└─────────────────────┘
         │
         ↓
┌────────────────────┐
│  Stage: Deploy     │  docker-compose up
└────────────────────┘
```
