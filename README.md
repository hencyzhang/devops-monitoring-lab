# Homelab DevOps Platform

End-to-end DevOps/SRE homelab built on a Dell Latitude E7450 running Proxmox VE.

## Architecture

```mermaid
graph TB
    User[User Browser] --> LB[Nginx Load Balancer<br/>VM100 monitor-lb<br/>192.168.0.154]
    
    LB --> App1[Flask App Node 1<br/>VM102 app-node1<br/>192.168.0.156]
    LB --> App2[Flask App Node 2<br/>VM103 app-node2<br/>192.168.0.157]
    
    App1 --> DB[(PostgreSQL 16<br/>VM101 db-node<br/>192.168.0.155)]
    App2 --> DB
    App1 --> MQ[RabbitMQ<br/>VM101 db-node]
    App2 --> MQ
    
    subgraph Monitoring
        Prom[Prometheus<br/>VM100]
        Graf[Grafana<br/>VM100:3000]
        Alert[Alertmanager<br/>VM100]
    end
    
    Prom --> App1
    Prom --> App2
    Prom --> DB
    Graf --> Prom
    Alert --> Prom
    Alert --> ntfy[ntfy.sh Push]
```   ## Tech StackComponent	Technology
Hypervisor	Proxmox VE 8.4
OS	Ubuntu Server 24.04
Load Balancer	Nginx
App	Flask
Database	PostgreSQL 16
Message Queue	RabbitMQ 3
Monitoring	Prometheus + Grafana
Alerting	Alertmanager + ntfy.sh
VPN	Tailscale
Services
Service	Local URL
Ecommerce Shop	http://192.168.0.154
Grafana	http://192.168.0.154:3000
RabbitMQ Mgmt	http://192.168.0.155:15672
Features
- Nginx round-robin load balancing across 2 app nodes
- Real product data scraped from [joybuy.de](https://joybuy.de)
- Multi-language UI (German / English / Chinese)
- Shopping cart, checkout, order history
- Prometheus metrics from all nodes
- Grafana dashboards
- ntfy push notifications for alerts
- Tailscale remote access from anywhere
