# Secrets on the GCP VM — what goes where

Secrets live ONLY in `/opt/secrets/` on the VM (chmod 700, files 600).
Never in git, never in images, never in logs, never in Telegram.

## Files to create on the VM (Stage 2, via secure transfer — scp or console paste)
| File | Contents |
|---|---|
| `/opt/secrets/creds.env` | `TELEGRAM_BOT_TOKEN=...` + `GEMINI_API_KEY=...` (used by re-seed import) |
| `/opt/secrets/telegram_token` | bot token (watchdog alerts) |
| `/opt/secrets/admin_chat_id` | your admin chat id (watchdog alerts) |
| `/opt/secrets/razorpay_webhook_secret` | webhook signing secret (self-heal script) |
| `gcp/.env` | full env (see .env.example) — includes RAZORPAY_KEY_ID/SECRET, MONGODB_URI, N8N_ENCRYPTION_KEY |

## Transfer options (no secrets in chat)
1. `scp` from your laptop to `root@<vm-ip>`
2. GCP console → Serial Console → paste files manually
3. GitHub Actions secret + a one-time fetch workflow (if preferred later)

## Rotation queue (already chat-exposed — rotate after migration is stable)
- Razorpay LIVE key pair
- MongoDB Atlas user/password
- n8n owner password (yours to set in UI)
- n8n public API key
- Telegram bot token (optional — low risk)
- Gemini/Groq keys (inline in wf JSONs today — move to credentials in Phase 2)
