# Render → Google Cloud (e2-micro) Migration

Date: 2026-09-10 · Owner: portfolio-manager (raja.ssk455@gmail.com) · Exec: agent (SSH key gcp-deploy-agent)
Rule (spec §40): **no destructive action without explicit approval. Render stays until GCP verified.**

## 1. Current architecture (audited 2026-09-10)

| Item | Value |
|---|---|
| Host | Render free (Singapore), docker, 512MB, dep-dag50grncjis738nostg lineage |
| n8n | 1.65.2 pinned (single-process; 1.69+ = 700MB → OOM on free) |
| Workflows (live) | Daily digest `9Fc66TvJHTWIiyxk` (active) · Weekly `L7lKcTUTFvKyHOI7` (active) · Master Map `fXEsHGxymxIAFaTL` (inactive) · Payments `i5DZK9p1pgbuFXUH` (active) |
| Credentials | telegramApi `2wRGwP2hapPynuJV` · httpHeaderAuth(Gemini) `DvRdGVWrHit03R2x` · Groq key inline in wf JSONs (rotation pending) |
| Payments lane | Razorpay links (python-in-shell) + webhook `/webhook/fk-razorpay-pay` with **HMAC-SHA256 signature verification** (unverified = dropped) |
| Schedules | GitHub Actions pinger (repo cron): daily 04:00 UTC Mon-Fri → daily webhook; Fri 11:30 UTC → weekly webhook |
| External webhooks | Razorpay webhook `TZuq1tB97xLVX6` → `https://fk-agent-os.onrender.com/webhook/fk-razorpay-pay` (secret exists) |
| Data | n8n SQLite (image layer + container disk) · `data/*.csv` (baked) · payments.csv (runtime, test rows only) |
| MongoDB | Atlas free cluster `flipkartagent` — **BLOCKED**: TLSV1_ALERT_INTERNAL_ERROR from 3 independent networks (sandbox, Render, GitHub runner) → cluster/edge-side, Atlas UI check pending |
| Telegram | bot `8817742347...` (chat 1138783169) via n8n nodes |
| FastAPI backend | **does not exist yet** — Python finance engine runs in n8n executeCommand. GCP deploy creates the v1 backend (health/readiness/metrics + tenant pattern) |

## 2. Target (GCP)

```
e2-micro (1GB RAM + 2GB swap, 30GB std PD)
├─ Caddy (:80/:443)  → n8n :5678 (owner auth on) + backend :8000 (future)
├─ n8n (Docker, 640MB cap, 1.65.2, re-seed entrypoint)
├─ fk-backend (FastAPI v1, 160MB cap)
└─ watchdog cron (*/5, Telegram alerts, dedup 2h)
MongoDB: stays EXTERNAL (Atlas) — not on e2-micro (spec §8)
```
30 agents = logical n8n roles (spec §32/§33) — NOT 30 processes.
RAM budget: system ~150MB + n8n ~400MB + backend ~80MB + caddy ~10MB ≈ 640MB + swap headroom.

## 3. Free-tier compatibility (verified vs GCP 2026 docs)

| Resource | Free limit | Our use | Status |
|---|---|---|---|
| e2-micro | 1/mo, us-west1/us-central1/us-east1 only | 1 VM, **us-central1 preferred** | ✅ |
| Boot disk | 30GB **standard** PD (NOT SSD/balanced) | 30GB standard | ✅ |
| Egress | **1GB/month** NA→world | QR photos ~20KB×10/wk + API JSON ≈ 150-400MB/mo @10 sellers | ✅ but MONITOR (watchdog at 800MB) |
| External IP | free on free-tier VM | 1 ephemeral | ✅ |
| Network tier | Standard (not Premium) | Standard | ✅ |
| Snapshots | 5GB/mo | optional monthly disk snapshot | ✅ |
| Billing account | REQUIRED (even for Always Free) | new GCP account, **$1 budget alert** | ⚠️ user action |
| GPU/TPU/premium LB/managed DB | not free / not used | not used | ✅ |

## 4. Risks (honest)

1. **1GB RAM is tight** — n8n + backend + system fit only with 2GB swap and mem caps; heavy parallel executions may swap-thrash. Mitigation: bounded concurrency, no Redis, agent roles share n8n process. If sustained thrash → growth path = e2-small (paid, ~$20/mo) — decision deferred, monitored by watchdog.
2. **Ephemeral public IP** — VM stop/restart changes IP → webhook URLs break. Mitigation: `update-webhooks.sh` self-heals Razorpay webhook on boot; GitHub pinger target updated at deploy. **Best fix: a custom domain** (DNS A record, Caddy auto-HTTPS) — user to decide.
3. **1GB egress cap** — crossing = charged. Mitigation: watchdog alerts at 800MB; QR size kept 280×280.
4. **GCP billing account** — required for Always Free; accidental non-free config (SSD disk, e2-small, premium tier) = charges. Mitigation: exact free config below + budget alert $1 + only I/user create resources in project.
5. **MongoDB still blocked** (cluster-side TLS) — GCP VM = 4th network test; if it also fails, Atlas UI fix is mandatory before Mongo-backed features. CSV fallback keeps everything working meanwhile.
6. **US region vs India sellers** — latency to Flipkart/Telegram from us-central1 is acceptable (200-300ms); Render Singapore was lower but was a free-tier sleep-prone host (woken by pinger). Acceptable trade.
7. **n8n 1.65 pinned** — no security patches past 1.65 on this size; acceptable for now (owner auth + UFW + fail2ban), revisit on VM growth.

## 5. Required GCP resources (user creates in console — Stage 1)

1. GCP account → new **project** (attach billing — required; set **budget alert at $1**)
2. Enable **Compute Engine API**
3. VM: name `fk-agent-os` · zone **us-central1-a** (fallback us-west1-a, us-east1-a) · machine **e2-micro** · image **Ubuntu 22.04 LTS** · boot disk **Standard persistent 30GB** · network **Standard** tier · external IP **ephemeral** · firewall: allow SSH/HTTP/HTTPS
4. VM metadata → **SSH Keys** → paste agent key:
   `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN2gpLs2Euson9/snNaWe32aVZTEQJa5wOp4aTMEUEv0 gcp-deploy-agent`
5. Report external IP

## 6. Environment variables (gcp/.env — values from /opt/secrets, never in git)

N8N_ENCRYPTION_KEY (carried from Render — credentials stay decryptable), N8N_HOST, WEBHOOK_URL,
GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_ID,
MONGODB_URI, N8N_IMAGE_TAG, SECRETS_DIR, TZ. Template: `gcp/.env.example`.

## 7. Staged execution plan (each stage = health gate before next)

- **Stage 1 — GCP foundation (USER):** project + VM per §5. Gate: VM running + SSH from agent works.
- **Stage 2 — Server (AGENT via SSH):** docker+compose install, harden.sh (ufw/ssh/swap/fail2ban/timezone), repo clone, secrets in place (user transfers), `.env`. Gate: `health-check.sh` infra PASS.
- **Stage 3 — Services (AGENT):** compose up (n8n re-seed entrypoint auto-imports workflows+creds, activates). One-time: user clicks owner setup in UI (1 min). Gate: /healthz, workflows active, creds present.
- **Stage 4 — Verification (AGENT):** signed mock payment (good sig → saved+alerted; bad sig → dropped), daily/weekly webhook triggers, engine run, Telegram digest, Mongo connectivity test (4th network). Gate: all PASS.
- **Stage 5 — Cutover (APPROVAL REQUIRED):** Razorpay webhook → GCP URL · pinger cron → GCP URL · Render workflows → maintenance (pause active) · keep Render up as rollback. Gate: one full operational cycle (a real ₹1 payment).
- **Stage 6 — Render decommission (APPROVAL REQUIRED, later):** only after ≥1 week stable.
- **Rollback at any point:** stop GCP workers, re-activate Render workflows, re-point webhooks back (update-webhooks.sh pattern), verify. **Never two live producers** (spec §31).

## 8. Repo layout added (branch `gcp-migration` — merged to main ONLY after Stage 2-4 pass)

```
gcp/
  docker-compose.yml  Dockerfile.gcp  entrypoint-gcp.sh  Caddyfile
  .env.example  SECRETS.md
  harden.sh  deploy.sh  rollback.sh  health-check.sh
  scripts/update-webhooks.sh  scripts/watchdog.sh  scripts/re-point-workflow-refs.py
  backend/ (app.py, Dockerfile, requirements.txt)
docs/MIGRATION-GCP.md (this file)
```

## 9. Final verification template (filled at cutover)

Project/VM/Region/Machine/Disk/OS/Docker/n8n/Backend/Telegram/MongoDB/Gemini/Flipkart/Razorpay/HTTPS/Monitoring/Backups/Billing-safety/GitHub-deploy/Rollback → each PASS/FAIL/WARNING/NOT-TESTED (no success claimed without test).
