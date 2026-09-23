# Homelab DevOps Platform

End-to-end DevOps/SRE homelab built on a Dell Latitude E7450 running Proxmox VE.

## Architecture

```mermaid
graph TD
    A[Proxmox VE 8<br/>Type-1 Hypervisor] --> B[Ubuntu Server VM<br/>192.168.0.154]
    B --> C[Monitoring Stack]
    B --> D[Ecommerce Microservices]

    C --> C1[Prometheus<br/>:9090]
    C --> C2[Grafana<br/>:3000]
    C --> C3[Alertmanager<br/>:9093]
    C --> C4[node-exporter<br/>:9100]
    C3 --> C5[ntfy.sh<br/>Mobile Push]

    D --> D1[Flask API<br/>:5000]
    D --> D2[PostgreSQL 16]
    D --> D3[RabbitMQ<br/>:15672]
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
Remote Access	Tailscale (WireGuard mesh VPN)## Key Features

- **Infrastructure monitoring** — CPU, memory, disk, network via node-exporter
- **Business monitoring** — request rate, API latency P95, order count in Grafana
- **Alerting** — High CPU, high latency, service-down alerts pushed to phone via ntfy
- **Structured logging** — per-module files (startup/api/order/notify/error), colored output, 7-day retention, 50MB rotation
- **Distributed tracing** — request_id flows across Flask API → PostgreSQL → RabbitMQ → notify worker
- **Remote access** — Tailscale mesh VPN, reachable from any network
- **Automation** — scheduled shutdown (cron) + BIOS RTC wake at 09:00

## Repository Structure
├── configs/           # Prometheus, Alertmanager, alert rules
├── ecommerce/         # Microservices demo app
│   ├── backend/       # Flask API + notify worker
│   ├── frontend/      # Product catalog + orders UI
│   ├── db/            # PostgreSQL init schema
│   ├── docker-compose.yml
│   └── seed.json     # Product catalog data
├── docs/runbook.md   # Operational runbook
└── scripts/setup.sh  # One-command setup
