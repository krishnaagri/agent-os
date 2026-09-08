#!/bin/sh
# Diagnostic entrypoint (temporary): reveal the real runtime paths
echo "[entry] HOME=$HOME N8N_USER_FOLDER=${N8N_USER_FOLDER:-<unset>} USER=$(id -un 2>/dev/null) UID=$(id -u 2>/dev/null)"
echo "[entry] --- /home/node ---"
ls -la /home/node 2>/dev/null | head -15
echo "[entry] --- /root ---"
ls -la /root 2>/dev/null | head -10
echo "[entry] --- database.sqlite files ---"
find /home /root /tmp -maxdepth 4 -name 'database.sqlite*' 2>/dev/null | while IFS= read -r f; do
  echo "[entry] found: $f ($(stat -c%s "$f" 2>/dev/null) bytes)"
done
echo "[entry] --- disk ---"
df -h /home/node 2>/dev/null | tail -2
echo "[entry] launching n8n..."
exec n8n start
