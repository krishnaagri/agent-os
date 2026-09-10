#!/bin/bash
# FK Agent OS — deploy from GitHub (run on VM as root).
# Pipeline: git(main) -> build -> up -> health. QA gate: only main is deployed.
set -euo pipefail
cd /opt/fk-agent-os
git fetch origin
git checkout main
git pull --ff-only origin main
cd gcp
[ -f .env ] || { echo "ERROR: gcp/.env missing (see .env.example + SECRETS.md)"; exit 1; }
docker compose build --pull
# keep previous image for rollback
docker tag fk-n8n:prev fk-n8n:rolledback 2>/dev/null || docker tag fk-n8n:prod fk-n8n:prev 2>/dev/null || true
docker compose up -d
sleep 25
python3 scripts/re-point-workflow-refs.py || true
./health-check.sh
