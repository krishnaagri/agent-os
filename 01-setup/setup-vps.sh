#!/usr/bin/env bash
# Flipkart Agent OS — One-click VPS setup (Ubuntu 22.04/24.04)
# Run as root: bash setup-vps.sh
set -euo pipefail

echo "=== [1/6] System updates ==="
apt-get update -y && apt-get upgrade -y

echo "=== [2/6] Install Docker + Compose ==="
if ! command -v docker &>/dev/null; then
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker
usermod -aG docker $USER 2>/dev/null || true

echo "=== [3/6] Project structure ==="
mkdir -p /opt/agent-os /backup
cd /opt/agent-os
# Note: apna project laptop se pehle scp karo:
#   scp -r flipkart-agent-os/* root@<IP>:/opt/agent-os/
[ -f .env ] || echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" > .env

echo "=== [4/6] Python deps ==="
apt-get install -y python3 python3-pip cron
pip3 install --quiet openpyxl python-telegram-bot 2>/dev/null || true

echo "=== [5/6] Start n8n ==="
cd /opt/agent-os/01-setup
docker compose up -d

echo "=== [6/6] Backup cron ==="
CRON_LINE="0 2 * * * tar czf /backup/agent-os-\$(date +\%F).tar.gz /opt/agent-os/data /opt/agent-os/.env 2>/dev/null"
( crontab -l 2>/dev/null | grep -v "agent-os-" ; echo "$CRON_LINE" ) | crontab -

echo ""
echo "=============================================="
echo " SETUP COMPLETE ✅"
echo " n8n:  http://<VPS_IP>:5678"
echo " Ab karo:"
echo "  1. n8n khولو, owner account banao (TZ: Asia/Kolkata)"
echo "  2. /opt/agent-os/.env mein apni API keys bharo"
echo "  3. Telegram bot live karo (SETUP-GUIDE.md STEP 4-6)"
echo "=============================================="
