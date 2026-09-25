# 运维手册

## 日常操作

### 查看服务状态

```bash
# monitor-lb: 监控栈
docker ps

# app-node1/2: Flask 服务
sudo systemctl status ecommerce

# db-node: 数据库和消息队列
docker ps
```

### 查看应用日志

```bash
# Flask 日志（app-node1 或 app-node2）
sudo journalctl -u ecommerce -f

# 分模块日志
tail -f ~/ecommerce-app/logs/app.log
tail -f ~/ecommerce-app/logs/startup.log
tail -f ~/ecommerce-app/logs/api.log
tail -f ~/ecommerce-app/logs/order.log
```

### 重启服务

```bash
# 重启 Flask（app-node1/2）
sudo systemctl restart ecommerce

# 重启 Nginx（monitor-lb）
sudo systemctl restart nginx

# 重启监控栈（monitor-lb）
cd ~/home-observability-stack && docker compose restart

# 重启数据库（db-node）
docker restart shop-db shop-rabbitmq
```

## 故障排查

### 网站打不开

1. 检查 Nginx: `curl -I http://192.168.0.154`
2. 检查 app 节点: `curl http://192.168.0.156:5000/api/products`
3. 检查 app 节点2: `curl http://192.168.0.157:5000/api/products`
4. 如果一台挂了，Nginx 会自动只转发到正常的那台

### 502 Bad Gateway

Flask 没启动。SSH 到 app-node1/2:
```bash
sudo systemctl status ecommerce
sudo systemctl restart ecommerce
```

### Grafana 没数据

1. 检查 Prometheus targets: http://192.168.0.154:9090/targets
2. 确认 ecommerce target 是 UP
3. 如果是 DOWN，检查 app 节点是否在线

### 数据库连不上

1. db-node 上: `docker ps` 看 postgres 容器
2. `docker logs shop-db`
3. 确认防火墙没挡 5432 端口

### PVE 开机后服务没起来

1. VM 是否开机自启: `qm config <id> | grep onboot`
2. Flask 是否 systemd 自启: `sudo systemctl is-enabled ecommerce`
3. Docker 容器是否 `restart: always`: `docker inspect <容器名> | grep RestartPolicy`

## 定时任务

### 定时关机/开机（PVE Shell）

```bash
# 每天 00:00 关机
echo "0 0 * * * /sbin/shutdown -h now" | crontab -

# BIOS 中设置每天 09:00 自动开机
# Dell BIOS → Power Management → Auto Power On
```

### 日志清理

日志自动按天轮转，保留 7 天，无需手动清理。

## 更新商品数据

在 Windows 上双击 `D:\workspace\PVE\scrape.bat`，自动爬取 joybuy.de 最新商品并写入数据库。详见《Joybuy 爬虫手册》。

## 外网访问

所有服务通过 Tailscale 访问：

| 服务 | Tailscale 地址 |
|------|---------------|
| 电商 | http://100.125.96.30 |
| Grafana | http://100.125.96.30:3000 |
| app-node1 SSH | ssh devops@100.64.88.3 |
| app-node2 SSH | ssh devops@100.116.57.112 |
| db-node SSH | ssh devops@100.119.22.30 |

Windows 上双击 `D:\workspace\PVE\ssh-all.bat` 一键打开 4 个 SSH 标签页。

## 密码清单

| 项目 | 用户名 | 密码 |
|------|--------|------|
| VM SSH | devops | Zhang@123 |
| PostgreSQL | shop | shop123 |
| RabbitMQ | guest | guest |
| Grafana | admin | admin |
| PVE Web UI | root | 安装时设置 |
