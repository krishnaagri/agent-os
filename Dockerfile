# ============================================================
# FK AGENT OS — n8n + Python finance engine (Render free tier)
# Base: Debian slim (apt works) + n8n via npm + python3
# (official n8nio/n8n image is a minimal build with no package
#  manager, so we build n8n from npm on a standard base)
# Secrets NOT in repo — credentials live inside n8n (created via API)
# ============================================================
FROM node:22-slim

# python3 for the finance engine; build tools as fallback for native npm modules
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 build-essential \
 && rm -rf /var/lib/apt/lists/*

# n8n
RUN npm install -g n8n@latest

# Project code + demo data (no secrets here)
WORKDIR /home/node/agent-os
COPY 05-code/ ./05-code/
COPY data/ ./data/

ENV TZ=Asia/Kolkata \
    GENERIC_TIMEZONE=Asia/Kolkata \
    N8N_PORT=8080 \
    N8N_DIAGNOSTICS_ENABLED=false \
    NODE_OPTIONS=--max-old-space-size=448

EXPOSE 8080
CMD ["n8n", "start"]
