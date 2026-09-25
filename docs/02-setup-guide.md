# Setup Guide

## Prerequisites

- One physical machine (min 8GB RAM, recommended 16GB)
- Proxmox VE 8.x installed
- Home network router
- Windows workstation for management

## Step 1: Create VMs

In Proxmox Web UI (https://192.168.0.10:8006), create:

| VM ID | Name | RAM | vCPU | Disk |
|-------|------|-----|------|------|
| 100 | monitor-lb | 2GB | 1 | 20GB |
| 101 | db-node | 4GB | 2 | 30GB |
| 102 | app-node1 | 4GB | 2 | 20GB |
| 103 | app-node2 | 4GB | 2 | 20GB |

Install Ubuntu Server 24.04 on each, create user `devops`.

### Enable boot autostart

```bash
qm set 100 --onboot 1
qm set 101 --onboot 1
qm set 102 --onboot 1
qm set 103 --onboot 1
```

## Step 2: Network

Set static IP on each VM via Netplan:

```bash
sudo nano /etc/netplan/00-installer-config.yaml
```

```yaml
network:
  ethernets:
    ens18:
      addresses: [192.168.0.154/24]
      gateway4: 192.168.0.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
  version: 2
```

```bash
sudo netplan apply
```

## Step 3: Tailscale (all VMs)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

## Step 4: db-node (VM 101)

```bash
sudo apt update && sudo apt install -y docker.io
mkdir -p ~/db-stack && cd ~/db-stack
```

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: shop
      POSTGRES_USER: shop
      POSTGRES_PASSWORD: shop123
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    restart: always
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
    restart: always
volumes:
  pgdata:
```

```bash
docker compose up -d
```

## Step 5: app-node1 and app-node2 (VM 102/103)

```bash
sudo apt install -y python3-pip python3-venv
git clone https://github.com/hencyzhang/devops-monitoring-lab.git
cd devops-monitoring-lab/ecommerce
python3 -m venv venv
source venv/bin/activate
pip install flask psycopg2-binary pika prometheus-client
```

### Create database tables

```bash
psql -h 192.168.0.155 -U shop -d shop -c "
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200), category VARCHAR(100),
    price NUMERIC(10,2), description TEXT DEFAULT '',
    stock INT DEFAULT 50, image TEXT DEFAULT ''
);
CREATE TABLE orders (
    id SERIAL PRIMARY KEY, product_name VARCHAR(200),
    price NUMERIC(10,2), status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"
```

### systemd autostart

```bash
sudo tee /etc/systemd/system/ecommerce.service << 'EOF'
[Unit]
Description=Flask Ecommerce App
After=network.target
[Service]
User=devops
WorkingDirectory=/home/devops/ecommerce-app
ExecStart=/home/devops/ecommerce-app/venv/bin/python app.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now ecommerce
```

## Step 6: monitor-lb (VM 100)

```bash
sudo apt install -y nginx
```

```nginx
# /etc/nginx/sites-available/ecommerce
upstream ecommerce_backend {
    server 192.168.0.156:5000;
    server 192.168.0.157:5000;
}
server {
    listen 80;
    location / {
        proxy_pass http://ecommerce_backend;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### Monitoring stack

```bash
mkdir -p ~/home-observability-stack/configs
cd ~/home-observability-stack
```

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: always
  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
    restart: always
  alertmanager:
    image: prom/alertmanager
    ports: ["9093:9093"]
    restart: always
  node-exporter:
    image: prom/node-exporter
    ports: ["9100:9100"]
    restart: always
```

```bash
docker compose up -d
```

## Step 7: Import products

Run `D:\workspace\PVE\scrape.bat` on Windows.

## Verification

- Shop: http://192.168.0.154
- Grafana: http://192.168.0.154:3000 (admin/admin)
- RabbitMQ: http://192.168.0.155:15672 (guest/guest)
