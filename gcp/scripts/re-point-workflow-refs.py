#!/usr/bin/env python3
"""After fresh reseed: workflow JSONs reference credential ids that no longer exist.
Re-point telegramApi/httpHeaderAuth refs to the freshly imported credentials by type."""
import glob, json, os, sqlite3, sys

DB = os.path.join(os.environ.get("N8N_USER_FOLDER", "/home/node/.n8n"), "database.sqlite")
con = sqlite3.connect(DB)
creds = {t: i for (i, n, t) in con.execute("SELECT id, name, type FROM credentials").fetchall()}
con.close()
print("[refs] creds by type:", creds)
changed = 0
for f in glob.glob("/opt/state/workflows/*.json"):
    d = json.load(open(f))
    dirty = False
    for node in d.get("nodes", []):
        for ctype, cdata in (node.get("credentials") or {}).items():
            if ctype in creds and cdata.get("id") != creds[ctype]:
                cdata["id"] = creds[ctype]
                dirty = True
    if dirty:
        json.dump(d, open(f, "w"), separators=(",", ":"))
        changed += 1
        print("[refs] re-pointed", os.path.basename(f))
print("[refs] files changed:", changed)
