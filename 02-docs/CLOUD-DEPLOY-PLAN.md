# FK AGENT OS — CLOUD DEPLOY PLAN (Render free, ₹0/month)

_Date: 08 Sep 2026 · Status: READY TO DEPLOY (keys required)_

## 1. Architecture

```
┌────────────────────────────┐        ┌─────────────────────────────────────────┐
│ GitHub repo: agent-os      │  push  │ RENDER (free, no card)                  │
│  ├─ Dockerfile (n8n+python)│ ──────►│  fk-agent-os.onrender.com (web service) │
│  ├─ 05-code/ (engine)      │  auto  │  ├─ n8n 2.x (webhook + workflows)       │
│  ├─ data/ (sellers, GMV)   │ deploy │  └─ finance_engine.py (Execute Command) │
│  └─ .github/workflows/     │        │  fk-agent-os-db (free Postgres 256MB)   │
│     n8n-pinger.yml (cron)  │        └─────────────────────────────────────────┘
└────────────────────────────┘                          ▲
                                                        │ wake + trigger (09:30 IST)
        ┌──────────────────────┐                        │
        │ GitHub Actions (free)│────────────────────────┘
        └──────────────────────┘
                                                        n8n API key
        ┌──────────────────────┐                        │
        │ AURA (Arena.ai agent)│────────────────────────┘
        │ → credentials,      │
        │ workflows, tests,   │  (sab kuch API se, user 0 clicks)
        │ monitoring          │
        └──────────────────────┘
```

## 2. Stack Decisions (research: Sep 2026)

| Option | Free? | Card? | 24/7? | Verdict |
|---|---|---|---|---|
| **Render free** (chosen) | ✅ ₹0, permanent | ❌ NAHI | ⚠️ 15-min sleep (pinger se solve) | **Phase 0 cloud** — fastest, no card |
| GCP e2-micro | ✅ always-free | ✅ Visa/MC chahiye | ✅ true 24/7 | Option B — card ho toh migration easy (code same) |
| AWS/Azure | ⚠️ 12-month/credits | ✅ | 12 months | Expiry risk, card required |
| Oracle A1 | ✅ | ✅ | ✅ | PARKED (user decision) — Phase 1 (Watcher) |
| GratisVPS/VPSWala | ✅ | ❌ | ❌ unstable | Rejected — unprofessional |

**DB:** n8n sirf **PostgreSQL/SQLite** support karta hai (MongoDB ❌ — n8n support nahi karta).
Render free Postgres (256MB) use hoga. Fuse: 30–90 din expiry → tab main API se
2 min mein poora data re-import kar deta hoon (workflows repo mein + credentials ke values mere paas).

**"n8n Cloud" clarification:** n8n ka official SaaS ($20+/mo) is plan mein NAHI hai —
usme shell access nahi hoti (Python engine nahi chalega). Yahan "cloud" = self-hosted
n8n pe free server, jo hamesha ₹0 rahega.

## 3. Sleep Problem ka Solution

Render free service 15 min idle pe spin-down hoti hai (wake = 30–60s).
n8n internal cron sleeping mein fire NAHI hota. Isliye:

- WF-01/WF-02 ke trigger = **Webhook nodes** (n8n schedule node cloud pe use nahi hota)
- **GitHub Actions cron** (public repo = free, unlimited) har 09:30 IST ko
  webhook POST karta hai → service wake → workflow run → digest phone pe
- WF-03 (listing pipeline) = user-triggered → user ka apna message hi wake karta hai
- Cold start (30–60s) matlab digest ~09:32 pe aayega. Acceptable.
- GitHub Actions cron kabhi-kabhi 5–10 min late fire ho sakta hai (congestion) —
  digest same din hi aayega. Backup manual trigger: GitHub repo → Actions →
  "n8n Schedule Pinger" → Run workflow → daily/weekly.

## 4. Division of Work

### User ek baar (total ~10 min, phir HAMESHA 0 clicks):
1. render.com → free signup (Google/GitHub login) → **API Key** banao (Account → API Keys) → de do
2. github.com → repo **agent-os** (public) banao → fine-grained token (Contents: Read & Write) → de do
3. Deploy ke baad: n8n URL kholo → owner account banao (name/email/password)
4. n8n UI → Settings (gear) → **n8n API** → API key banao → de do

### Aura (API se, user ke bina):
- Code push (repo), Postgres + web service create, env vars, deploy, health check
- n8n credentials create (Telegram + Gemini)
- 3 workflows import (webhook triggers ke saath), activate
- Test run → digest verify → schedule verify
- Future: naya agent = naya workflow = main API se bana deta hoon (user ko batana bas itna ki "kaam karo")

## 5. Failure Modes & Recovery

| Failure | Impact | Recovery |
|---|---|---|
| Render Postgres expiry (30–90d) | n8n data wipe | User: owner account re-bana (1 min) → main: credentials + workflows re-import (2 min) |
| GitHub Actions cron late/miss | Digest late/missed | Manual trigger (Actions → Run workflow) ya kal ka digest + main backup pinger set kar sakta hoon |
| Service OOM (512MB) | Restart | Health check se Render auto-restart; heavy agents Phase 1 (GCP/Oracle) pe |
| Repo deleted | Deploy source gone | Poora code + data is project mein (workspace) backup hai |
| Render account issue | Downtime | Code same → 15 min mein GCP e2-micro pe migrate |

## 6. Security

- Repo public hai par sirf **fake/demo data** hai (real seller data push hoga toh repo private bana lena)
- Tokens/keys repo mein KABHI nahi — sab n8n credentials ke andar (encrypted DB)
- 3 keys (Render API, GitHub token, n8n API) sensitive hain → setup complete hone ke baad
  ek baar rotate kar lena chahiye (main batayunga kab kya)
- Telegram bot token → `/revoke` in BotFather setup complete hone ke baad (purana token chat mein shared hua tha)

## 7. Deployment Checklist (Aura executes)

- [ ] User: Render account + API key
- [ ] User: GitHub repo `agent-os` + fine-grained token
- [ ] Aura: code push (Dockerfile, engine, data, pinger workflow)
- [ ] Aura: Render API → Postgres `fk-agent-os-db` (free, singapore)
- [ ] Aura: Render API → web service `fk-agent-os` (docker, free, healthz)
- [ ] Aura: deploy complete → https://fk-agent-os.onrender.com live
- [ ] User: n8n owner account (1 min)
- [ ] User: n8n API key
- [ ] Aura: n8n API → credentials (Telegram Bot, Gemini)
- [ ] Aura: n8n API → WF-01 (webhook `fk-daily-9f4e2a`), WF-02 (webhook `fk-weekly-7b3d1c`), WF-03 import + activate
- [ ] Aura: pinger webhook test → digest user ke phone pe ✅ = **SYSTEM LIVE**
