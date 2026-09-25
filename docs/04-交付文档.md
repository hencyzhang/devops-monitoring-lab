# 交付文档

## 项目概述

端到端 DevOps/SRE 实践环境，在一台笔记本上通过 Proxmox VE 虚拟化搭建完整集群电商平台。

## 交付清单

### 基础设施

- [x] Proxmox VE 8.4 虚拟化平台
- [x] 4 台 Ubuntu Server 24.04 虚拟机
- [x] Tailscale VPN 内网组网
- [x] Nginx 负载均衡（轮询）
- [x] 所有 VM 开机自启
- [x] Flask 服务 systemd 自启
- [x] Docker 容器 restart=always

### 电商应用

- [x] 商品列表（1015 个真实 joybuy 商品）
- [x] 分类自动发现
- [x] 搜索功能
- [x] 分页（joybuy 风格：< 1 2 3 4 5 ... 115 >）
- [x] 购物车（抽屉式，加减数量）
- [x] 商品详情页
- [x] "Jetzt kaufen" 配送方式弹窗
- [x] 下单扣库存
- [x] 订单历史（商品图、数量分组、小计）
- [x] 多语言（德/英/中）
- [x] 顶部 toast 通知

### 数据层

- [x] PostgreSQL 16 主库
- [x] RabbitMQ 消息队列
- [x] joybuy.de 爬虫（Windows + Playwright CDP）
- [x] 一键爬取脚本 (scrape.bat)

### 监控告警

- [x] Prometheus 指标采集
- [x] Grafana 看板
- [x] Alertmanager 告警
- [x] ntfy.sh 手机推送
- [x] Flask 业务指标 (HTTP 请求数/延迟)
- [x] 主机指标 (CPU/内存/磁盘)

### 代码管理

- [x] GitHub 仓库: https://github.com/hencyzhang/devops-monitoring-lab
- [x] 目录结构清晰 (ecommerce/, configs/, docs/)
- [x] Mermaid 架构图

## 验证标准

| 验证项 | 方法 | 预期结果 |
|--------|------|---------|
| 电商首页 | 浏览器访问 http://192.168.0.154 | 显示商品网格 |
| 负载均衡 | 连续刷新，对比 app 节点日志 | 请求轮询到两台 |
| 购物车 | 加商品→查看购物车→结算 | 订单写入数据库 |
| 高可用 | 停掉 app-node1，刷新页面 | 网站仍正常 |
| Grafana | 访问 http://192.168.0.154:3000 | 有监控数据 |
| 告警触发 | CPU 压测 | 手机收到 ntfy 推送 |
| 外网访问 | 手机 Tailscale 访问 | 所有服务可用 |

## 技术栈版本

| 组件 | 版本 |
|------|------|
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

## 文件位置

| 文件 | 位置 |
|------|------|
| 电商代码 | GitHub: hencyzhang/devops-monitoring-lab/ecommerce/ |
| 监控配置 | GitHub: hencyzhang/devops-monitoring-lab/configs/ |
| Windows 爬虫 | D:\workspace\PVE\scrape_joybuy.py |
| 一键爬虫 | D:\workspace\PVE\scrape.bat |
| 一键 SSH | D:\workspace\PVE\ssh-all.bat |

## 后续优化方向

- [ ] HTTPS 证书
- [ ] Redis 缓存层
- [ ] CI/CD 自动部署
- [ ] 日志集中收集 (ELK/Loki)
- [ ] Docker 容器化电商应用
- [ ] 多副本 RabbitMQ 高可用
- [ ] PostgreSQL 主从复制
