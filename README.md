# Homelab DevOps Platform

End-to-end DevOps/SRE homelab built on a Dell Latitude E7450 running Proxmox VE.

## Architecture

graph TD
    A[Proxmox VE 8] --> B[Ubuntu Server VM]
    B --> C[Monitoring Stack]
    B --> D[Ecommerce Microservices]
    C --> C1[Prometheus]
    C --> C2[Grafana]
    C --> C3[Alertmanager]
    C --> C4[node-exporter]
    C3 --> C5[ntfy Mobile Push]
    D --> D1[Flask API]
    D --> D2[PostgreSQL]
    D --> D3[RabbitMQ]
    D --> D4[Notify Worker]
    D1 --> D2
    D1 --> D3
    D3 --> D4
    C1 --> D1
    C1 --> C4




## Tech Stack
Layer	Tools
Virtualization	Proxmox VE 8, QEMU/KVM
Containers	Docker, Docker Compose
Metrics	Prometheus, node-exporter
Dashboards	Grafana
Alerting	Alertmanager, ntfy.sh
Backend	Flask, Python
Database	PostgreSQL 16
Message Queue	RabbitMQ
Remote Access	Tailscale

## Key Features

- Infrastructure monitoring via node-exporter
- Business monitoring: request rate, API latency P95, order count
- Alerting pushed to phone via ntfy
- Structured logging: per-module files, 7-day retention, 50MB rotation
- Distributed tracing with request_id across services
- Remote access via Tailscale
- Scheduled shutdown + BIOS RTC wake

## Repository Structure

- `configs/` - Prometheus, Alertmanager, alert rules
- `ecommerce/` - Microservices demo app
- `docs/runbook.md` - Operational runbook
- `scripts/setup.sh` - Setup script
