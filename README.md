# Homelab DevOps Platform

End-to-end DevOps/SRE homelab built on a Dell Latitude E7450 running Proxmox VE.

## Architecture

Proxmox VE 8.4 (192.168.0.10)
├── VM 100: monitor-lb (Nginx LB + Prometheus + Grafana + Alertmanager)
├── VM 101: db-node (PostgreSQL + RabbitMQ)
├── VM 102: app-node1 (Flask ecommerce)
└── VM 103: app-node2 (Flask ecommerce)
## Stack

| Component | Technology |
|-----------|-----------|
| Hypervisor | Proxmox VE 8.4 |
| OS | Ubuntu Server 24.04 |
| Load Balancer | Nginx (round-robin) |
| App | Flask + Gunicorn |
| Database | PostgreSQL 16 |
| Message Queue | RabbitMQ 3 |
| Monitoring | Prometheus + Grafana + Alertmanager |
| Alerting | ntfy.sh |
| VPN | Tailscale |

## Services

| Service | URL |
|---------|-----|
| Ecommerce Shop | http://192.168.0.154 |
| Grafana | http://192.168.0.154:3000 |
| Prometheus | http://192.168.0.154:9090 |
| RabbitMQ Mgmt | http://192.168.0.155:15672 |

## Features

- Nginx round-robin load balancing across 2 app nodes
- Real product data scraped from joybuy.de
- Multi-language (DE/EN/ZH)
- Cart, checkout, order history
- Prometheus metrics from all nodes
- Grafana dashboards
- ntfy push notifications
- Tailscale remote access
