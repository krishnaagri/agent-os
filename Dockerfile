# ============================================================
# FK AGENT OS — n8n + Python finance engine (Render free tier)
# Base: Debian slim (apt) + Node 24 + n8n via npm + python3
# KEY TRICK: SQLite DB is pre-migrated AT BUILD TIME so the
# service boots in seconds (free tier 0.1 CPU + Render health
# check would kill slow first-boot migrations, causing a loop).
# NOTE: kill by PID (pkill -f would match the build shell's own
# command line and self-terminate the step).
# ============================================================
FROM node:24-slim

# python3 for the finance engine; build tools for native npm modules
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 build-essential \
 && rm -rf /var/lib/apt/lists/*

# n8n
RUN npm install -g n8n@latest

# ── Pre-migrate SQLite at build time (one-time, ~1-2 min) ──
ENV N8N_USER_FOLDER=/home/node/.n8n
RUN mkdir -p /home/node/.n8n \
 && n8n start > /tmp/n8n_boot.log 2>&1 & \
 BOOTPID=$!; \
 for i in $(seq 1 90); do \
   grep -q "Editor is now accessible" /tmp/n8n_boot.log 2>/dev/null && break; \
   sleep 2; \
 done; \
 if grep -q "Editor is now accessible" /tmp/n8n_boot.log 2>/dev/null; then \
   kill $BOOTPID 2>/dev/null || true; \
   wait $BOOTPID 2>/dev/null || true; \
 else \
   kill $BOOTPID 2>/dev/null || true; \
   echo "=== BOOT FAILED — last 60 lines ==="; \
   tail -60 /tmp/n8n_boot.log; \
   exit 1; \
 fi \
 && test -f /home/node/.n8n/database.sqlite \
 && echo "SQLite pre-migrated at build time"

# Project code + demo data (no secrets here)
WORKDIR /home/node/agent-os
COPY 05-code/ ./05-code/
COPY data/ ./data/

ENV TZ=Asia/Kolkata \
    GENERIC_TIMEZONE=Asia/Kolkata \
    N8N_PORT=8080 \
    N8N_DIAGNOSTICS_ENABLED=false \
    NODE_OPTIONS=--max-old-space-size=300

EXPOSE 8080
CMD ["n8n", "start"]
