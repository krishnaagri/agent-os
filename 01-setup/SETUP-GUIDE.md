# 🛠️ Complete Setup Guide — Flipkart Agent OS

> Kya-kya chahiye aur kaise — step by step. Estimated total time: **4-6 ghante** (Din 1-2 mein).

---

## STEP 0: Shopping List (Pehle Ye Le Lo)

| # | Item | Recommended | Cost |
|---|------|-------------|------|
| 1 | VPS | Hostinger VPS 2 / DigitalOcean 4GB (2vCPU, 4GB RAM, Mumbai/Singapore region) | ₹500-800/mo |
| 2 | LLM API key | OpenAI (api.openai.com) ya Anthropic (console.anthropic.com) | Usage-based |
| 3 | Dedicated phone number | Koi bhi SIM (WhatsApp Business API ke liye) | — |
| 4 | Telegram account | Aapka personal | FREE |
| 5 | Google account | Dashboard/sheets/backup ke liye | FREE |

---

## STEP 1: VPS Setup (30 min)

VPS kharidte hi aapko milta hai: IP address, root password.

```bash
# Aapke laptop se:
ssh root@<YOUR_VPS_IP>

# VPS pe ye script chalao (file pehle upload karo: scp setup-vps.sh root@<IP>:/root/):
cd /root
bash setup-vps.sh
```

`setup-vps.sh` kya karega:
- Ubuntu updates
- Docker + Docker Compose install
- Project folder `/opt/agent-os` create (yahan poora project rakhna hai)
- n8n start (port 5678)
- Auto-restart on reboot enable

**Verify:** Browser mein kholo `http://<YOUR_VPS_IP>:5678` → n8n setup page aayega.
**Important:** n8n setup mein apna **owner account** banao + apna timezone `Asia/Kolkata` set karo.

---

## STEP 2: Project Deploy VPS Pe (15 min)

```bash
# Laptop se poora project VPS pe bhejo:
scp -r flipkart-agent-os root@<IP>:/opt/agent-os

# VPS pe:
cd /opt/agent-os
cp 01-setup/.env.example .env
nano .env    # Apni keys yahan bharo (STEP 3 ke baad)
```

`.env` mein yeh chahiye:
```
OPENAI_API_KEY=sk-...
# ya ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=123456:ABC-...
TELEGRAM_CHAT_ID=123456789        # aapka chat id (bot ko /start bhejne pe milega)
FLIPKART_APP_KEY=...
FLIPKART_APP_SECRET=...
```

---

## STEP 3: LLM API Key (10 min)

1. **OpenAI** (recommended start): api.openai.com → Sign in → API Keys → Create
2. Ya **Anthropic**: console.anthropic.com → API Keys → New key
3. **$5-10 credit** lagao ($5 = ~₹415 — shuruat ka kaafi hai)
4. Key ko `.env` mein daalo

> ⚠️ Key kisi ko share mat karo. Agar leak ho jaye, turban regenerate karo.

---

## STEP 4: Telegram Bot Banao (10 min, FREE)

1. Telegram mein **@BotFather** kholo
2. `/newbot` → naam do (e.g., `MyAgentOSBot`) → username do (`my_agentos_bot`)
3. **Bot Token** milega → `.env` mein `TELEGRAM_BOT_TOKEN`
4. Ab bot ko `/start` bhejo → aapka **Chat ID** milega (ya `https://api.telegram.org/bot<TOKEN>/getUpdates` kholo) → `.env` mein `TELEGRAM_CHAT_ID`
5. Bot code chalao (STEP 6)

**Security:** `bot.py` mein `ALLOWED_CHAT_IDS` mein sirf aapka ID daalna hai — koi aur bot use nahi kar sakta.

---

## STEP 5: WhatsApp Business API (Option 2 — Jab Volume Badhe)

Shuruat mein **Telegram hi kaafi hai** (free + reliable). WhatsApp tab lagao jab:
- Daily messages > 50 ho jayen
- Aap WhatsApp pe hi business karte ho

Options (kaunsa bhi ek):
- **WATI** — free tier available, WhatsApp Business API
- **Interakt** — free trial
- **A2P approved provider** (Agoo/LeadSquared)

Number: dedicated SIM ka number register karo → bot se connect karo → `.env` mein API details.

---

## STEP 6: Telegram Bot Live Karo (20 min)

```bash
cd /opt/agent-os/05-code/telegram-bot
pip install -r requirements.txt
# Bot background mein chalo:
nohup python3 bot.py > bot.log 2>&1 &
```

Test: Telegram mein `/status`, `/income`, `/schedule` bhejo.

**Auto-restart** ke liye systemd service banao (SOP-MANUAL.md mein template hai).

---

## STEP 7: Flipkart API Keys (Har Seller Se)

Har seller se maangna hai (onboarding packet mein script hai):

1. Seller apna **Seller Hub → API Access** section kholta hai
2. App register karta hai (ya aapki existing app ko apne account se authorize karta hai)
3. Aapko milta hai: **App Key + App Secret + Seller ID + Location IDs**
4. Plus: apna naam se **User role** (Operations Manager + Catalog Manager)

Keys `.env` ya dedicated `data/api-keys.json` mein (encrypted storage mein, plain file nahi).

> Phase 1 (pilot) mein API key ke bina bhi 60% kaam ho sakta hai — manual CSV exports (Sales Report, Orders Report Seller Hub se download) + finance engine. API keys Phase 2 mein live karo.

---

## STEP 8: n8n Workflows Import (30 min)

1. n8n login → **Workflows** → **Import from File**
2. `04-n8n-workflows/` ke 3 JSON files import karo
3. Har workflow mein **TODO** marked nodes pe credentials connect karo:
   - Telegram node → apna bot token
   - OpenAI node → apna LLM key
   - Google Sheets / HTTP nodes → apna data + Flipkart keys
4. **Test** (n8n ka test mode) → phir **Active** on karo

Detail: `04-n8n-workflows/IMPORT-INSTRUCTIONS.md`

---

## STEP 9: Finance Engine Live (15 min)

```bash
cd /opt/agent-os/05-code/finance-agent
python3 finance_engine.py --demo      # Sample data se test
# Ab real: data/sellers.csv + data/daily-gmv.csv mein apna data daalo
python3 finance_engine.py --today     # Aaj ka digest → output/ + Telegram
```

n8n WF-01 isko har subah 7 baje auto-chalaata hai.

---

## STEP 10: Kill Switch + Backup (10 min)

```bash
# Kill switch (emergency freeze):
touch /opt/agent-os/data/KILL    # system monitoring-only mode mein chala jayega
rm /opt/agent-os/data/KILL       # wapas normal

# Daily backup (crontab -e mein add karo):
0 2 * * * tar czf /backup/agent-os-$(date +\%F).tar.gz /opt/agent-os/data /opt/agent-os/.env
```

Backup VPS se alag storage pe push karo (Google Drive rclone se — guide `SOP-MANUAL.md` §11).

---

## ✅ Final Checklist

- [ ] `http://<VPS_IP>:5678` — n8n open ho raha hai
- [ ] Telegram `/status` ka reply aa raha hai
- [ ] `finance_engine.py --demo` digest bana raha hai
- [ ] 3 workflows imported + test pass
- [ ] Backup crontab chala, archive bana
- [ ] Kill switch test kiya (touch → verify freeze → rm)

**Sab tick? Aap live ho. 🎉 Ab 2 pilot sellers se onboarding (02-docs/SELLER-ONBOARDING-PACKET.md)**
