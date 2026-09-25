# 架构设计文档

## 1. 概述

本项目是一个端到端 DevOps/SRE 实践环境，在一台 Dell Latitude E7450 笔记本上通过 Proxmox VE 虚拟化搭建完整的集群电商平台，包含负载均衡、应用集群、数据库、消息队列、监控告警全链路。

## 2. 物理节点



| 项目  | 配置                             |
| --- | ------------------------------ |
| 机型  | Dell Latitude E7450            |
| CPU | Intel Core i5-5300U (2 核 4 线程) |
| 内存  | 16GB                           |
| 硬盘  | 256GB SSD                      |
| OS  | Proxmox VE 8.4                 |

## 3. 虚拟机拓扑



```
Proxmox VE (192.168.0.10)

│

├── VM 100 monitor-lb (2GB RAM, 1 vCPU)

│   ├── Nginx :80        (负载均衡)

│   ├── Prometheus :9090 (指标采集)

│   ├── Grafana :3000    (可视化)

│   ├── Alertmanager :9093 (告警)

│   └── node-exporter :9100

│

├── VM 101 db-node (4GB RAM, 2 vCPU)

│   ├── PostgreSQL 16 :5432

│   └── RabbitMQ 3 :5672 / :15672

│

├── VM 102 app-node1 (4GB RAM, 2 vCPU)

│   └── Flask :5000

│

└── VM 103 app-node2 (4GB RAM, 2 vCPU)

&#x20;   └── Flask :5000
```

## 4. 网络配置



| VM         | 内网 IP         | Tailscale IP   |
| ---------- | ------------- | -------------- |
| monitor-lb | 192.168.0.154 | 100.125.96.30  |
| db-node    | 192.168.0.155 | 100.119.22.30  |
| app-node1  | 192.168.0.156 | 100.64.88.3    |
| app-node2  | 192.168.0.157 | 100.116.57.112 |

所有 VM 通过家庭路由器 (192.168.0.1) 联网，同时通过 Tailscale 组成虚拟内网，实现外网访问。

## 5. 请求链路



```
用户浏览器

&#x20; → Nginx (monitor-lb:80)

&#x20;   → 轮询转发到 app-node1:5000 或 app-node2:5000

&#x20;     → Flask 处理请求

&#x20;       → PostgreSQL (db-node:5432) 读写商品/订单

&#x20;       → RabbitMQ (db-node:5672) 发送订单消息

&#x20;         → notify 消费者消费消息
```

## 6. 监控链路



```
Prometheus (monitor-lb:9090)

&#x20; ↓ 每15秒抓取

&#x20; ├── app-node1:5000/metrics  (Flask 业务指标)

&#x20; ├── app-node2:5000/metrics

&#x20; ├── db-node:9100/metrics    (主机指标)

&#x20; └── monitor-lb:9100/metrics (主机指标)

Grafana → Prometheus (查询展示)

Alertmanager → Prometheus (告警规则)

Alertmanager → ntfy.sh (手机推送)
```

## 7. 电商应用架构



```
ecommerce-app/

├── app.py              # Flask 路由

├── logging\_config.py   # 分模块日志配置

├── requirements.txt

├── templates/

│   ├── base.html       # 公共布局

│   ├── index.html      # 商品列表

│   ├── product.html    # 商品详情

│   └── orders.html     # 订单历史

└── static/

&#x20;   ├── style.css       # 样式

&#x20;   └── app.js          # 前端逻辑 (购物车/搜索/分页/i18n)
```

## 8. 数据库设计



```
\-- 商品表

products (

&#x20;   id SERIAL PRIMARY KEY,

&#x20;   name VARCHAR(200),

&#x20;   category VARCHAR(100),

&#x20;   price NUMERIC(10,2),

&#x20;   description TEXT,

&#x20;   stock INT,

&#x20;   image TEXT

)

\-- 订单表

orders (

&#x20;   id SERIAL PRIMARY KEY,

&#x20;   product\_name VARCHAR(200),

&#x20;   price NUMERIC(10,2),

&#x20;   status VARCHAR(20),

&#x20;   created\_at TIMESTAMP

)
```

## 9. 安全



* SSH 密钥登录（无密码）

* Tailscale VPN 内网访问，不暴露公网端口

* 数据库仅监听内网

* Nginx 仅做反向代理