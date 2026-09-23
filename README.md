# Homelab DevOps Platform

End-to-end DevOps/SRE homelab built on a Dell Latitude E7450 running Proxmox VE.

## Architecture

Proxmox VE (Type-1 Hypervisor)
└── Ubuntu Server VM (Docker)
├── Monitoring Stack
│   ├── Prometheus (metrics scraper)
│   ├── Grafana (dashboards)
│   ├── Alertmanager → ntfy (mobile push)
│   └── node-exporter (host metrics)
└── Ecommerce Demo (microservices)
├── Flask API (port 5000)
├── PostgreSQL (orders DB)
├── RabbitMQ (async order events)
└── Notify Worker (email simulation)
## Tech Stack

| Layer | Tools |
|---|---|
| Virtualization | Proxmox VE 8, QEMU/KVM |
| Containers | Docker, Docker Compose |
| Metrics | Prometheus, node-exporter |
| Dashboards | Grafana |
| Alerting | Alertmanager, ntfy.sh |
| Backend | Flask, Python |
| Database | PostgreSQL 16 |
| Message Queue | RabbitMQ |
| Remote Access | Tailscale (WireGuard mesh VPN) |

## Projects

- `configs/` — Prometheus scrape configs, alert rules, Alertmanager
- `ecommerce/` — Flask + PostgreSQL + RabbitMQ microservices with structured logging, request_id tracing, and Prometheus metrics
- `docs/runbook.md` — Operational runbook
- `scripts/setup.sh` — One-command setup script

## Features

- Infrastructure monitoring (CPU, memory, disk, network)
- Business monitoring (request rate, API latency P95, order count)
- Alerting with mobile push notification
- Structured logging with per-module files, rotation (7-day retention, 50MB sharding)
- Distributed tracing via request_id across Flask API → PostgreSQL → RabbitMQ → notify worker
- Remote access from anywhere via Tailscale
- Automated scheduled shutdown/startup via cron + BIOS RTC wake
