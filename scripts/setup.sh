#!/bin/bash
set -e

echo "=== DevOps Monitoring Lab Setup ==="

if ! command -v docker &> /dev/null; then
    echo "[1/3] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
else
    echo "[1/3] Docker already installed."
fi

echo "[2/3] Starting monitoring stack..."
docker compose up -d

echo "[3/3] Waiting for services..."
sleep 10

echo ""
echo "=== Done! ==="
echo "Grafana:      http://$(hostname -I | awk '{print $1}'):3000  (admin/admin)"
echo "Prometheus:   http://$(hostname -I | awk '{print $1}'):9090"

