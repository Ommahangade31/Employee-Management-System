# System Metrics with Node Exporter

## What is Node Exporter?

The Flask application exposes **application-level metrics** (request counts, durations, error rates).
To also monitor **host-level metrics** (CPU, memory, disk, network), you need the
**Prometheus Node Exporter** — a separate process that reads Linux kernel statistics.

## Metrics provided by Node Exporter

| Metric | Description |
|---|---|
| `node_cpu_seconds_total` | CPU time per mode (user, system, idle) |
| `node_memory_MemFree_bytes` | Free RAM |
| `node_memory_MemTotal_bytes` | Total RAM |
| `node_filesystem_avail_bytes` | Available disk space |
| `node_network_receive_bytes_total` | Network bytes received |
| `node_network_transmit_bytes_total` | Network bytes transmitted |
| `node_load1` | 1-minute load average |

## Adding Node Exporter to Docker Compose

Add this service to `docker-compose.yml`:

```yaml
  node-exporter:
    image: prom/node-exporter:v1.8.1
    container_name: ems_node_exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - "--path.procfs=/host/proc"
      - "--path.sysfs=/host/sys"
      - "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)"
    networks:
      - ems_network
```

> **Windows note:** Node Exporter is a Linux tool. It works inside the Linux containers
> in Docker Desktop (WSL 2 backend). The metrics reflect the Linux VM, not the Windows host.

## Adding the Scrape Job to prometheus.yml

Add this block to the `scrape_configs` section in `monitoring/prometheus.yml`:

```yaml
  - job_name: "node"
    static_configs:
      - targets: ["node-exporter:9100"]
```

## Useful Grafana Queries for System Metrics

```
# CPU usage % (across all cores)
100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory used %
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# Disk usage %
(1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100

# Network receive rate (bytes/s)
rate(node_network_receive_bytes_total[5m])
```

## Pre-built Grafana Dashboard

Import dashboard **ID 1860** from the Grafana dashboard library:
1. Grafana → Dashboards → New → Import
2. Enter `1860` in the "Import via grafana.com" box
3. Click Load → select Prometheus data source → Import

This gives you a complete Node Exporter host dashboard instantly.

## Why It Is Not Included by Default

Node Exporter is excluded from the default `docker-compose.yml` to keep the stack
minimal and easy to understand for a first demonstration. It is straightforward to add
when needed for a production deployment or extended demo.
