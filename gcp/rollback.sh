#!/bin/bash
# FK Agent OS — rollback to previous good image (run on VM as root).
set -euo pipefail
cd /opt/fk-agent-os/gcp
docker tag fk-n8n:rolledback fk-n8n:prod 2>/dev/null || { echo "no previous image tagged"; exit 1; }
docker compose up -d
sleep 25
./health-check.sh
