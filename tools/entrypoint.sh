#!/bin/sh
# ============================================================
# Supervisor entrypoint (Render free tier resilience)
# - Runs n8n in a loop: a native crash (segfault) no longer
#   kills the container → SQLite data on disk SURVIVES crashes.
# - Every crash is logged with its exit code (137=OOM, 139=SEGV,
#   143=SIGTERM, 1=JS error) so the kill cause is visible in
#   the app logs.
# - Node diagnostic reports (--report-on-signal) from the
#   previous crash are dumped into the app log for analysis.
# ============================================================
DIAG=/tmp/n8n-diagnostics
mkdir -p "$DIAG"

dump_reports() {
  # dump the native-stack parts of any crash report, then archive
  for r in "$DIAG"/report.*.json; do
    [ -f "$r" ] || continue
    echo "=== CRASH REPORT: $r ==="
    python3 - "$r" <<'PY' 2>/dev/null | head -60
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    js = d.get('javascriptStack', {})
    print('JS stack:', js.get('trigger') or js.get('message') or '?')
    for f in (js.get('stack') or [])[:10]:
        print('  ', f.get('funcName'), f.get('fileName'), f.get('lineNumber'))
    nat = d.get('resourceUsage') or {}
    print('resourceUsage:', nat)
    info = d.get('systemInfo') or {}
    print('system:', info.get('cpuModel'), info.get('operatingSystem'))
    # walk process states for native frames
    for k in ('environmentVariables',):
        pass
except Exception as e:
    print('report parse error:', e)
PY
    rm -f "$r"
  done
}

FIRST=1
while true; do
  if [ "$FIRST" = "1" ]; then
    echo "[entry] HOME=$HOME N8N_USER_FOLDER=${N8N_USER_FOLDER:-<unset>} USER=$(id -un 2>/dev/null)"
    find /home/node/.n8n -maxdepth 1 -name 'database.sqlite*' 2>/dev/null | while IFS= read -r f; do
      echo "[entry] db: $f ($(stat -c%s "$f" 2>/dev/null) bytes)"
    done
    FIRST=0
  fi

  dump_reports

  # shellcheck disable=SC2086
  NODE_OPTIONS="--report-on-signal --report-on-fatalerror --diagnostic-dir=$DIAG $NODE_OPTIONS" n8n start
  CODE=$?
  echo "[entry] !!! n8n exited with code $CODE — restarting in 5s"
  sleep 5
done
