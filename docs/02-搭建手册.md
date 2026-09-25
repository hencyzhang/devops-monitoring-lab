# 搭建手册

## 前置条件

- 一台物理机（最低 8GB 内存，建议 16GB）
- 安装 Proxmox VE 8.x
- 家庭网络路由器，一台 Windows 工作站用于管理

## 第 1 步：创建 4 台 VM

在 Proxmox Web UI (https://192.168.0.10:8006) 中创建：

| VM ID | 名称 | 内存 | CPU | 磁盘 |
|-------|------|------|-----|------|
| 100 | monitor-lb | 2GB | 1 | 20GB |
| 101 | db-node | 4GB | 2 | 30GB |
| 102 | app-node1 | 4GB | 2 | 20GB |
| 103 | app-node2 | 4GB | 2 | 20GB |

每台安装 Ubuntu Server 24.04，创建用户 `devops`。

### 设置开机自启

```bash
# 在 PVE Shell 执行
qm set 100 --onboot 1
qm set 101 --onboot 1
qm set 102 --onboot 1
qm set 103 --onboot 1
```

## 第 2 步：网络配置

每台 VM 设静态 IP（通过 Netplan）：

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

## 第 3 步：Tailscale 安装（所有 VM）

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

## 第 4 步：db-node (VM 101)

```bash
# 安装 Docker
sudo apt update && sudo apt install -y docker.io docker-compose-v2

# 创建 docker-compose.yml
mkdir -p ~/db-stack && cd ~/db-stack

cat > docker-compose.yml << 'EOF'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: shop
      POSTGRES_USER: shop
      POSTGRES_PASSWORD: shop123
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: always

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    restart: always

volumes:
  pgdata:
EOF

docker compose up -d
```

## 第 5 步：app-node1 和 app-node2 (VM 102/103)

```bash
# 安装 Python
sudo apt install -y python3-pip python3-venv

# 克隆代码
git clone https://github.com/hencyzhang/devops-monitoring-lab.git
cd devops-monitoring-lab/ecommerce

# 虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install flask psycopg2-binary pika prometheus-client gunicorn

# 数据库建表
psql -h 192.168.0.155 -U shop -d shop -c "
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(100),
    price NUMERIC(10,2),
    description TEXT DEFAULT '',
    stock INT DEFAULT 50,
    image TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    price NUMERIC(10,2),
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

### 配置 systemd 自启

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

## 第 6 步：monitor-lb (VM 100)

```bash
# 安装 Nginx
sudo apt install -y nginx

# 配置负载均衡
sudo tee /etc/nginx/sites-available/ecommerce << 'EOF'
upstream ecommerce_backend {
    server 192.168.0.156:5000;
    server 192.168.0.157:5000;
}
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://ecommerce_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### 监控栈（Docker Compose）

```bash
mkdir -p ~/home-observability-stack/configs
cd ~/home-observability-stack

# prometheus.yml
cat > configs/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
rule_files:
  - /etc/prometheus/alert.rules.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
scrape_configs:
  - job_name: node
    static_configs:
      - targets: ["node-exporter:9100"]
  - job_name: ecommerce
    metrics_path: /metrics
    static_configs:
      - targets: ["192.168.0.156:5000", "192.168.0.157:5000"]
EOF

# docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    restart: always
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    restart: always
  alertmanager:
    image: prom/alertmanager
    ports:
      - "9093:9093"
    restart: always
  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
    restart: always
volumes:
  prometheus-data:
EOF

docker compose up -d
```

## 第 7 步：导入商品数据

在 Windows 上运行 `D:\workspace\PVE\scrape.bat`（详见爬虫手册）。

## 验证

- 电商首页: http://192.168.0.154
- Grafana: http://192.168.0.154:3000 (admin/admin)
- RabbitMQ: http://192.168.0.155:15672 (guest/guest)
