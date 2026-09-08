# ============================================================
# FK AGENT OS — n8n + Python finance engine (Render free tier)
# Base: Debian slim (apt) + Node 24 + n8n via npm + python3
# KEY TRICK: SQLite DB is pre-migrated AT BUILD TIME (via
# tools/bake-db.js) so the service boots in seconds — the free
# tier's 0.1 CPU + Render health check kill slow first-boot
# migrations (infinite restart loop). N8N_USER_FOLDER is set in
# BOTH the bake and the runtime ENV so they use the same data
# root (/home/node).
# ============================================================
FROM node:24-slim

# python3 for the finance engine; build tools for native npm modules
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 build-essential \
 && rm -rf /var/lib/apt/lists/*

# n8n
RUN npm install -g n8n@latest

# ── Pre-migrate SQLite at build time (one-time, ~1-3 min) ──
COPY tools/bake-db.js /tmp/bake-db.js
RUN node /tmp/bake-db.js

# Project code + demo data (no secrets here)
WORKDIR /home/node/agent-os
COPY 05-code/ ./05-code/
COPY data/ ./data/

ENV TZ=Asia/Kolkata \
    GENERIC_TIMEZONE=Asia/Kolkata \
    N8N_PORT=8080 \
    N8N_USER_FOLDER=/home/node \
    N8N_DIAGNOSTICS_ENABLED=false \
    NODE_OPTIONS=--max-old-space-size=300

EXPOSE 8080
COPY tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
