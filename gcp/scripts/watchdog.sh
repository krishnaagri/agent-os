#!/bin/bash
# FK Agent OS — Watchdog-001 (cron */5). Alerts via Telegram admin chat. Deduped 2h per key.
set -u
TOKEN=$(cat /opt/secrets/telegram_token 2>/dev/null || true)
CHAT=$(cat /opt/secrets/admin_chat_id 2>/dev/null || true)
[ -z "$TOKEN" ] || [ -z "$CHAT" ] && exit 0
STATE=/var/lib/fk-watchdog
mkdir -p "$STATE"
alert() { # key message
  local f="$STATE/$1"
  [ -f "$f" ] && [ $(( $(date +%s) - $(cat "$f") )) -lt 7200 ] && return
  echo "$(date +%s)" > "$f"
  curl -s -m 15 "https://api.telegram.org/bot$TOKEN/sendMessage" \
    -d "chat_id=$CHAT" -d "text=$2" >/dev/null 2>&1
}
# containers
for c in fk-n8n fk-backend fk-caddy; do
  docker ps --filter name="$c" --format '{{.Names}}' | grep -q "$c" || { alert "ctr-$c" "🚨 $c container DOWN — checking auto-restart"; }
done
# n8n health
curl -fsS -m 10 http://127.0.0.1:5678/healthz >/dev/null 2>&1 || alert "n8n-health" "🚨 n8n /healthz failing"
# disk
DISK=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
[ "$DISK" -gt 80 ] && alert disk "⚠️ disk ${DISK}% — cleanup needed"
# RAM
RAM=$(free -m | awk '/Mem/{printf "%d", $3/$2*100}')
[ "$RAM" -gt 90 ] && alert ram "⚠️ RAM ${RAM}% — swap in use, check containers"
# monthly egress estimate (eth0 tx since boot — conservative monthly proxy)
TX=$(cat /sys/class/net/eth0/statistics/tx_bytes 2>/dev/null || echo 0)
TB=$(( TX / 1048576 ))
[ "$TB" -gt 800 ] && alert egress "⚠️ network tx ${TB}MB — approaching 1GB free egress cap"
exit 0
