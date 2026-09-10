#!/bin/bash
# FK Agent OS — Stage 2: on-VM bootstrap (run over SSH as root, after VM create).
set -euo pipefail
BRANCH=${BRANCH:-gcp-migration}
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y install docker.io git curl
systemctl enable --now docker
if ! docker compose version >/dev/null 2>&1; then
  apt-get -y install docker-compose-v2 || {
    mkdir -p /usr/lib/docker/cli-plugins
    curl -fsSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/lib/docker/cli-plugins/docker-compose
  }
fi
docker compose version
mkdir -p /opt/secrets && chmod 700 /opt/secrets
if [ ! -d /opt/fk-agent-os ]; then
  git clone -q -b "$BRANCH" https://github.com/krishnaagri/agent-os.git /opt/fk-agent-os
fi
cd /opt/fk-agent-os/gcp
bash harden.sh
[ -f .env ] || cp .env.example .env
grep -q "__KEEP_SAME_AS_RENDER__\|__FROM_SECRETS__" .env && { echo "WARN: .env still has placeholders — fill values + /opt/secrets before compose up"; exit 2; }
docker compose up -d
sleep 30
./health-check.sh
