#!/bin/bash
# FK Agent OS — health report (run on VM as root). PASS/FAIL per component.
set -u
FAIL=0
ck() { if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; else echo "FAIL  $1"; FAIL=1; fi; }
ck "caddy container up"     "docker ps --filter name=fk-caddy --format '{{.Names}}' | grep -q fk-caddy"
ck "n8n container up"       "docker ps --filter name=fk-n8n --format '{{.Names}}' | grep -q fk-n8n"
ck "backend container up"   "docker ps --filter name=fk-backend --format '{{.Names}}' | grep -q fk-backend"
ck "n8n /healthz (200)"     "curl -fsS -m 10 http://127.0.0.1:5678/healthz"
ck "backend /health (200)"  "curl -fsS -m 10 http://127.0.0.1:8000/health"
ck "public web (80)"        "curl -fsS -m 15 http://127.0.0.1:80/"
DISK=$(df -h / | awk 'NR==2{print $5}' | tr -d %)
RAM=$(free -m | awk '/Mem/{printf "%d", $3/$2*100}')
SWAP=$(free -m | awk '/Swap/{printf "%d", ($2?$3/$2*100:0)}')
echo "INFO  disk ${DISK}% | ram ${RAM}% | swap ${SWAP}%"
[ "$DISK" -gt 80 ] && { echo "WARN  disk > 80%"; FAIL=1; }
[ "$RAM" -gt 90 ] && { echo "WARN  ram > 90% (swap headroom check)"; }
exit $FAIL
