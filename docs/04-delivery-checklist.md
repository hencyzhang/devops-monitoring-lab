# Delivery Checklist

## Overview

End-to-end DevOps/SRE practice environment built on a single laptop running Proxmox VE.

## Deliverables

### Infrastructure

- [x] Proxmox VE 8.4 hypervisor
- [x] 4 x Ubuntu Server 24.04 VMs
- [x] Tailscale VPN overlay network
- [x] Nginx round-robin load balancer
- [x] VM boot autostart
- [x] Flask systemd autostart
- [x] Docker containers restart=always

### Ecommerce App

- [x] Product catalog (1015 real joybuy.de products)
- [x] Auto-discovered categories
- [x] Search functionality
- [x] Pagination (joybuy style: < 1 2 3 4 5 ... 115 >)
- [x] Shopping cart (drawer, quantity adjust)
- [x] Product detail page
- [x] "Jetzt kaufen" delivery options modal
- [x] Order placement with stock deduction
- [x] Order history (product images, quantity grouping, subtotal)
- [x] Multi-language (DE/EN/ZH)
- [x] Toast notifications

### Data Layer

- [x] PostgreSQL 16
- [x] RabbitMQ 3
- [x] joybuy.de scraper (Windows + Playwright CDP)
- [x] One-click scrape script (scrape.bat)

### Monitoring

- [x] Prometheus metrics collection
- [x] Grafana dashboards
- [x] Alertmanager alerts
- [x] ntfy.sh push notifications
- [x] Flask business metrics
- [x] Host metrics (CPU/memory/disk)

### Code Management

- [x] GitHub repo: https://github.com/hencyzhang/devops-monitoring-lab
- [x] Clean directory structure (ecommerce/, configs/, docs/)
- [x] Mermaid architecture diagram

## Verification

| Item | Method | Expected Result |
|------|--------|----------------|
| Shop homepage | http://192.168.0.154 | Product grid loads |
| Load balancing | Refresh, check app logs | Requests round-robin |
| Cart | Add item -> checkout | Order in database |
| High availability | Stop app-node1, refresh | Site still works |
| Grafana | http://192.168.0.154:3000 | Data visible |
| Alert test | CPU stress | Phone ntfy notification |
| Remote access | Phone Tailscale | All services reachable |

## Tech Stack

| Component | Version |
|-----------|---------|
| Proxmox VE | 8.4 |
| Ubuntu Server | 24.04 |
| Python | 3.12 |
| Flask | 3.x |
| PostgreSQL | 16 |
| RabbitMQ | 3-management |
| Nginx | 1.24 |
| Prometheus | latest |
| Grafana | latest |
| Docker | 29.x |
| Tailscale | latest |

## File Locations

| File | Location |
|------|----------|
| Ecommerce code | GitHub: hencyzhang/devops-monitoring-lab/ecommerce/ |
| Monitoring config | GitHub: hencyzhang/devops-monitoring-lab/configs/ |
| Windows scraper | D:\workspace\PVE\scrape_joybuy.py |
| One-click scrape | D:\workspace\PVE\scrape.bat |
| One-click SSH | D:\workspace\PVE\ssh-all.bat |

## Future Improvements

- [ ] HTTPS certificates
- [ ] Redis cache layer
- [ ] CI/CD pipeline
- [ ] Centralized logging (Loki/ELK)
- [ ] Dockerize ecommerce app
- [ ] RabbitMQ high availability
- [ ] PostgreSQL master-slave replication
