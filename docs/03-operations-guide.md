# Operations Guide

## Daily Operations

### Check service status

```bash
# monitor-lb: monitoring stack
docker ps

# app-node1/2: Flask service
sudo systemctl status ecommerce

# db-node: database and queue
docker ps
```

### View application logs

```bash
# Flask logs
sudo journalctl -u ecommerce -f

# Modular logs
tail -f ~/ecommerce-app/logs/app.log
tail -f ~/ecommerce-app/logs/startup.log
tail -f ~/ecommerce-app/logs/api.log
tail -f ~/ecommerce-app/logs/order.log
```

### Restart services

```bash
# Flask (app-node1/2)
sudo systemctl restart ecommerce

# Nginx (monitor-lb)
sudo systemctl restart nginx

# Monitoring stack (monitor-lb)
cd ~/home-observability-stack && docker compose restart

# Database (db-node)
docker restart shop-db shop-rabbitmq
```

## Troubleshooting

### Website not loading

1. Check Nginx: `curl -I http://192.168.0.154`
2. Check app-node1: `curl http://192.168.0.156:5000/api/products`
3. Check app-node2: `curl http://192.168.0.157:5000/api/products`
4. If one node is down, Nginx routes to the healthy one

### 502 Bad Gateway

Flask is not running. SSH to app-node1/2:

```bash
sudo systemctl status ecommerce
sudo systemctl restart ecommerce
```

### Grafana no data

1. Check Prometheus targets: http://192.168.0.154:9090/targets
2. Confirm ecommerce target is UP
3. If DOWN, check if app nodes are reachable

### Database connection error

1. On db-node: `docker ps`
2. `docker logs shop-db`
3. Check port 5432 is open

### Services not starting after PVE boot

1. VM autostart: `qm config <id> | grep onboot`
2. Flask systemd: `sudo systemctl is-enabled ecommerce`
3. Docker containers: `docker inspect <name> | grep RestartPolicy`

## Cron Jobs

### Auto shutdown/boot (PVE shell)

```bash
# Shutdown at midnight daily
echo "0 0 * * * /sbin/shutdown -h now" | crontab -

# Power on at 9am daily via BIOS
# Dell BIOS -> Power Management -> Auto Power On
```

## Update product data

Run `D:\workspace\PVE\scrape.bat` on Windows to scrape latest joybuy.de products.

## Remote Access (Tailscale)

| Service | Tailscale URL |
|---------|---------------|
| Shop | http://100.125.96.30 |
| Grafana | http://100.125.96.30:3000 |
| app-node1 SSH | ssh devops@100.64.88.3 |
| app-node2 SSH | ssh devops@100.116.57.112 |
| db-node SSH | ssh devops@100.119.22.30 |

Windows: double-click `D:\workspace\PVE\ssh-all.bat` to open 4 SSH tabs.

## Passwords

| Item | Username | Password |
|------|----------|----------|
| VM SSH | devops | Zhang@123 |
| PostgreSQL | shop | shop123 |
| RabbitMQ | guest | guest |
| Grafana | admin | admin |
| PVE Web UI | root | set during install |
