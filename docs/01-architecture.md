# Architecture Design Document

## 1. Overview

End-to-end DevOps/SRE practice environment. A single Dell Latitude E7450 laptop runs Proxmox VE with 4 virtual machines forming a complete cluster: load balancer, application nodes, database, message queue, and monitoring.

## 2. Physical Node

| Item | Spec |
|------|------|
| Model | Dell Latitude E7450 |
| CPU | Intel Core i5-5300U (2c4t) |
| RAM | 16GB |
| Disk | 256GB SSD |
| Hypervisor | Proxmox VE 8.4 |

## 3. Virtual Machine Topology

```
Proxmox VE (192.168.0.10)
|
+-- VM 100 monitor-lb (2GB RAM, 1 vCPU)
|   +-- Nginx :80         (load balancer)
|   +-- Prometheus :9090  (metrics)
|   +-- Grafana :3000     (dashboards)
|   +-- Alertmanager :9093 (alerts)
|   +-- node-exporter :9100
|
+-- VM 101 db-node (4GB RAM, 2 vCPU)
|   +-- PostgreSQL 16 :5432
|   +-- RabbitMQ 3 :5672 / :15672
|
+-- VM 102 app-node1 (4GB RAM, 2 vCPU)
|   +-- Flask :5000
|
+-- VM 103 app-node2 (4GB RAM, 2 vCPU)
    +-- Flask :5000
```

## 4. Network

| VM | LAN IP | Tailscale IP |
|----|--------|-------------|
| monitor-lb | 192.168.0.154 | 100.125.96.30 |
| db-node | 192.168.0.155 | 100.119.22.30 |
| app-node1 | 192.168.0.156 | 100.64.88.3 |
| app-node2 | 192.168.0.157 | 100.116.57.112 |

All VMs connect through the home router (192.168.0.1). Tailscale provides a virtual overlay network for remote access.

## 5. Request Flow

```
User Browser
  -> Nginx (monitor-lb:80)
    -> round-robin to app-node1:5000 or app-node2:5000
      -> Flask handles request
        -> PostgreSQL (db-node:5432) read/write
        -> RabbitMQ (db-node:5672) order message
          -> notify consumer logs message
```

## 6. Monitoring Flow

```
Prometheus (monitor-lb:9090)
  every 15s scrape:
    -> app-node1:5000/metrics  (Flask business metrics)
    -> app-node2:5000/metrics
    -> db-node:9100/metrics    (host metrics)
    -> monitor-lb:9100/metrics (host metrics)

Grafana -> Prometheus (query and visualize)
Alertmanager -> Prometheus (evaluate alert rules)
Alertmanager -> ntfy.sh (push to phone)
```

## 7. Application Structure

```
ecommerce-app/
+-- app.py              # Flask routes
+-- logging_config.py   # modular logging
+-- requirements.txt
+-- templates/
|   +-- base.html       # common layout
|   +-- index.html      # product list
|   +-- product.html    # product detail
|   +-- orders.html      # order history
+-- static/
    +-- style.css       # styles
    +-- app.js          # frontend logic
```

## 8. Database Schema

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(100),
    price NUMERIC(10,2),
    description TEXT DEFAULT '',
    stock INT DEFAULT 50,
    image TEXT DEFAULT ''
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    price NUMERIC(10,2),
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 9. Security

- SSH key-only login (no password)
- Tailscale VPN, no public ports exposed
- Database listens on internal network only
- Nginx as reverse proxy only
