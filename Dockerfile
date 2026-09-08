# ============================================================
# FK AGENT OS — n8n + Python finance engine (Render free tier)
# Base: official n8n image (Alpine-based, Node 20+) + python3
# Secrets NOT in repo — credentials live inside n8n (created via API)
# ============================================================
FROM n8nio/n8n:latest

USER root
RUN apk add --no-cache python3

# Project code + demo data (no secrets here)
WORKDIR /home/node/agent-os
COPY 05-code/ ./05-code/
COPY data/ ./data/

USER node

ENV TZ=Asia/Kolkata \
    GENERIC_TIMEZONE=Asia/Kolkata \
    N8N_PORT=8080 \
    N8N_DIAGNOSTICS_ENABLED=false \
    NODE_OPTIONS=--max-old-space-size=448

EXPOSE 8080
CMD ["n8n", "start"]
