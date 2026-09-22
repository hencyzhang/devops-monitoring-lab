# Runbook — Alert Handling Guide

## HighCPU (CPU > 80% for 1 min)

1. SSH into the VM
2. Run `top` to find the process consuming CPU
3. Investigate:
   - Is it expected (build job, backup)?
   - Is it a runaway process? `kill <PID>`
4. If it's a container: `docker stats` to find the container, then `docker restart <name>`
5. Alert auto-resolves within 1-2 minutes after CPU drops.

## InstanceDown (target unreachable for 1 min)

1. Check if the VM is powered on
2. Check network: `ping <target-ip>`
3. Check Docker: `docker ps` — is the container running?
4. If container stopped: `docker compose up -d`
5. Check logs: `docker compose logs <service>`

## DiskAlmostFull (disk > 90% for 5 min)

1. Check disk usage: `df -h`
2. Find large files: `du -h --max-depth=1 / | sort -h`
3. Clean up:
   - Docker: `docker system prune -a`
   - Old logs: `journalctl --vacuum-size=100M`
4. Alert auto-resolves within 5 min after cleanup.

## Useful Commands

| Task | Command |
|------|---------|
| View running containers | `docker compose ps` |
| View logs | `docker compose logs -f <service>` |
| Restart service | `docker compose restart <service>` |
| Stop stack | `docker compose down` |
| Start stack | `docker compose up -d` |
| Check Prometheus targets | `curl -s localhost:9090/api/v1/targets | jq` |
