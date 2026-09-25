# Homelab DevOps Platform

End-to-end DevOps/SRE homelab built on a Dell Latitude E7450 running Proxmox VE.

## Architecture

- **Proxmox VE 8.4** (host: 192.168.0.10)
  - **VM 100 monitor-lb**: Nginx load balancer + Prometheus + Grafana + Alertmanager
  - **VM 101 db-node**: PostgreSQL 16 + RabbitMQ 3
  - **VM 102 app-node1**: Flask ecommerce app
  - **VM 103 app-node2**: Flask ecommerce app

Nginx distributes traffic round-robin to app-node1 and app-node2.
Both app nodes connect to the same PostgreSQL and RabbitMQ on db-node.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Hypervisor | Proxmox VE 8.4 |
| OS | Ubuntu Server 24.04 |
| Load Balancer | Nginx |
| App | Flask |
| Database | PostgreSQL 16 |
| Message Queue | RabbitMQ 3 |
| Monitoring | Prometheus + Grafana |
| Alerting | Alertmanager + ntfy.sh |
| VPN | Tailscale |

## Services

| Service | Local URL | Tailscale URL |
|---------|-----------|---------------|
| Ecommerce Shop | http://192.168.0.154 | http://100.125.96.30 |
| Grafana | http://192.168.0.154:3000 | http://100.125.96.30:3000 |
| RabbitMQ | http://192.168.0.155:15672 | http://100.119.22.30:15672 |

## Features

- Nginx round-robin load balancing across 2 app nodes
- Real product data scraped from joybuy.de
- Multi-language UI (German / English / Chinese)
- Shopping cart, checkout, order history
- Prometheus metrics from all nodes
- Grafana dashboards
- ntfy push notifications for alerts
- Tailscale remote access from anywhere
