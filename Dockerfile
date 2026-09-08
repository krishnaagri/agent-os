# ============================================================
# FK AGENT OS — n8n + Python finance engine (Render free, 512MB)
# Pinned n8n 1.65.2: last major line where task runners are
# OFF by default → SINGLE node process → fits in 512MB free RAM.
# (n8n >=1.69 always spawns main+broker+runner ≈ 700MB → OOM.)
# SQLite DB pre-migrated at build time (tools/bake-db.js).
# ============================================================
FROM node:24-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN npm install -g n8n@1.65.2

# ── Pre-migrate SQLite at build time ──
COPY tools/bake-db.js /tmp/bake-db.js
RUN node /tmp/bake-db.js

WORKDIR /home/node/agent-os
COPY 05-code/ ./05-code/
COPY data/ ./data/

ENV TZ=Asia/Kolkata \
    GENERIC_TIMEZONE=Asia/Kolkata \
    N8N_PORT=8080 \
    N8N_USER_FOLDER=/home/node/.n8n \
    N8N_DIAGNOSTICS_ENABLED=false \
    NODE_OPTIONS=--max-old-space-size=256

EXPOSE 8080
COPY tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
