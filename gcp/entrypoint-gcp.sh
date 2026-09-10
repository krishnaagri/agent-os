#!/bin/sh
# FK Agent OS — GCP entrypoint: re-seed aware boot + webhook self-heal.
set -eu
export N8N_USER_FOLDER=${N8N_USER_FOLDER:-/home/node/.n8n}
DB="$N8N_USER_FOLDER/database.sqlite"

if [ ! -f "$DB" ]; then
  echo "[reseed] fresh instance — importing workflows"
  mkdir -p /opt/state/workflows
  cp /opt-state-workflows/*.json /opt/state/workflows/ 2>/dev/null || true
  for f in /opt/state/workflows/*.json; do
    [ -f "$f" ] || continue
    n8n import:workflow "$f" >/dev/null 2>&1 && echo "[reseed] imported $(basename "$f")" || echo "[reseed] WARN: $(basename "$f") import failed"
  done
  echo "[reseed] importing credentials (from /opt/secrets)"
  if [ -f /opt/secrets/creds.env ]; then
    . /opt/secrets/creds.env
    python3 - <<'PY'
import json, os
tg = os.environ.get('TELEGRAM_BOT_TOKEN', '')
gem = os.environ.get('GEMINI_API_KEY', '')
if tg:
    json.dump({"name": "Telegram Bot (FK Agent OS)", "type": "telegramApi", "data": {"accessToken": tg}}, open('/tmp/cred_tg.json', 'w'))
if gem:
    json.dump({"name": "Gemini API Key", "type": "httpHeaderAuth", "data": {"name": "x-goog-api-key", "value": gem}}, open('/tmp/cred_gem.json', 'w'))
PY
    [ -f /tmp/cred_tg.json ] && n8n import:credential /tmp/cred_tg.json >/dev/null 2>&1 && echo "[reseed] telegram cred" || true
    [ -f /tmp/cred_gem.json ] && n8n import:credential /tmp/cred_gem.json >/dev/null 2>&1 && echo "[reseed] gemini cred" || true
  else
    echo "[reseed] WARN: /opt/secrets/creds.env missing — telegram/gemini creds NOT imported"
  fi
  # NOTE: imported credential ids differ from baked refs. deploy.sh runs
  # re-point-workflow-refs.py to sync node credential refs after import.
  python3 - <<PY
import sqlite3
c = sqlite3.connect("$DB")
c.execute("UPDATE workflow_entity SET active=1 WHERE name LIKE 'FK%' AND name NOT LIKE '%Master Map%'")
print('[reseed] workflows activated:', c.total_changes)
c.commit(); c.close()
PY
fi

# self-heal external webhook URLs (e2-micro ephemeral IP)
[ -f /entrypoint-scripts/update-webhooks.sh ] && /entrypoint-scripts/update-webhooks.sh || true

echo "[boot] starting n8n (production)"
exec n8n start
