# 🆓 FREE SETUP MASTER GUIDE — ₹0/month
> Oracle Cloud + n8n + Gemini + Google Sheets + Telegram + Google Drive
> Total time: **~3-4 ghante active work** (Oracle approval wait alag)
> Rule: koi paid cheez nahi. Har step mein "expected result" hai — wahi nahi aaya toh aage mat jao.

---

## STEP 0: Jo Chahiye (Sab Free)

| Cheez | Kyun |
|-------|------|
| Koi bhi email (Gmail best) | Sab accounts isi pe |
| Debit/Credit card (Sirf Oracle verification) | ₹0 charge hota hai |
| Phone with Telegram | Interface ke liye |
| Laptop | Setup ke liye |

---

## STEP 1: Oracle Cloud Account (DIN 1 — Pehle Yehi Karo, Approval Time Lagta Hai)

1. **cloud.oracle.com** kholo → "Start for free"
2. Sign up: email, password, **region: Mumbai (IN)** choose karo — important, low latency
3. **Always Free** tier select karo (koi paid plan NAHI)
4. **Card verification** aayegi — card daalo. ⚠️ Balance pe ₹0 chuta hai, sirf verification.
5. **Instance request** (ya approval ke baad):
   - Shape: **Ampere A1** — "Up to 4 OCPUs / 24GB RAM" wala always-free
   - Image: **Ubuntu 22.04 LTS (ARM)**
   - Key pair: generate karo (yeh SSH ke liye hoga — .pem file save karo)
6. Account/instance **approval** aayega — **1-2 din** lag sakta hai. Email notification aayega.

✅ **Expected:** Approval email + instance RUNNING status.
💡 *Approval wait hote hue STEP 2-4 kar lo — parallel work.*

---

## STEP 2: Gemini API Key (DIN 1, 5 min, FREE)

1. **aistudio.google.com** kholo → apne Google account se sign in
2. Left menu: **API Key** → "Create API Key"
3. Key copy karo → `01-setup/.env.example` mein copy karke bharo (file `01-setup/.env` banao)
4. **Zaroori:** key ke details mein **"Data usage: Improve Google's products" = OFF** karo (privacy)

✅ **Expected:** Key copy ho gayi, `.env` mein `GOOGLE_GEMINI_API_KEY=...`

---

## STEP 3: Telegram Bot (DIN 1, 10 min, FREE)

1. Telegram mein **@BotFather** kholo
2. `/newbot` → Bot ka naam do (e.g., `Agent OS`) → username do (e.g., `my_agent_os_bot`)
3. **Bot Token** milega → `.env` mein `TELEGRAM_BOT_TOKEN`
4. Bot ko **/start** bhejo → bot aapka **Chat ID** dikhayega (ya `https://api.telegram.org/bot<token>/getUpdates` kholo)
5. Chat ID → `.env` mein `TELEGRAM_CHAT_ID` aur `ALLOWED_CHAT_IDS` dono mein

✅ **Expected:** Bot se welcome message + aapka chat ID.

---

## STEP 4: Google Sheets Master File (DIN 1, 15 min, FREE)

1. Google Drive mein new **Google Sheet** banao → naam: `Flipkart Agent OS - Master`
2. In tabs (sheets) banao:
   | Tab | Kya Rahega |
   |-----|-----------|
   | SELLERS | 10 sellers: ID, name, category, rate %, rate status, GMV target, ad cap, contact |
   | DAILY-LOG | Date, Seller, Gross, Cancelled, Returns Resolved, Units, Net GMV, Rate, Aapka Cut |
   | KPI-TRACKER | Seller-wise: cancellation %, RTD breach %, return rate %, rating, status |
   | INCIDENTS | Date, Severity, Agent, Issue, Action, Status |
   | TASKS | ID, Priority, Task, Spec, Assigned, Status |
   | SCHEDULE | Time, Agent, Kaam, Frequency |
3. File ko **Share** setting: "Anyone with link — Viewer" OFF rakho (private)
4. File ka **URL** note karo (n8n connect ke liye chahiye)

✅ **Expected:** 6 tabs wali sheet, private.

---

## STEP 5: Project Deploy VM Pe (DIN 2-3, jab Oracle approval aaye)

1. Apne laptop se poora project VPS pe bhejo (terminal mein, ek baar):
   - `scp -r flipkart-agent-os root@<VPS_IP>:/opt/agent-os`
2. VPS pe setup script chala (yeh sab install karta hai — Docker, n8n, backup cron):
   - `cd /opt/agent-os/01-setup && bash setup-vps.sh`
3. Browser mein kholo: `http://<VPS_IP>:5678`
4. n8n **owner account** banao → Settings mein timezone: **Asia/Kolkata**
5. `01-setup/.env.example` copy karke `01-setup/.env` banao → apni 3 keys bharo (Gemini, Telegram token, chat ID)

✅ **Expected:** n8n dashboard khulta hai, timezone Kolkata set hai.

---

## STEP 6: n8n Workflows Import (DIN 3, 30 min)

1. n8n → **Workflows** → **Import from File** → `04-n8n-workflows/` ke 3 files:
   - `wf-01-daily-finance-digest.json`
   - `wf-02-seller-score-monitor.json`
   - `wf-03-listing-pipeline.json`
2. Har workflow mein **TODO** marked nodes pe credentials lagao:
   - Telegram node → apna bot token
   - Gemini node → apni Gemini key (model: `gemini-2.5-flash`)
   - Execute Command node → path check: `/opt/agent-os`
3. Har workflow ka **Test** (n8n ke "Execute workflow" button se) — 1 baar manually
4. Sab green → **Active** on

✅ **Expected:** Test mein Telegram pe message aata hai.

---

## STEP 7: Backup to Google Drive (DIN 3, 15 min, FREE)

1. VPS pe rclone install + Google Drive authenticate karo (rclone.com se official guide — 2 minute ka flow, browser mein Google login)
2. Daily backup cron `setup-vps.sh` mein pehle se hai (2 AM) — manually ek baar test chala:
   - `tar czf /backup/test.tar.gz /opt/agent-os/data`
3. Drive folder `AgentOS-Backups` mein test file push ho jaaye

✅ **Expected:** Drive mein `AgentOS-Backups` folder, andar aaj ki backup.

---

## STEP 8: First Live Test (DIN 3-4)

1. `wf-01` ko manually trigger karo (n8n mein "Execute")
2. **Telegram pe aapko daily digest message aana chahiye**
3. `data/sellers.csv` mein pehle 2 real sellers daalo (naam, rate %, target)
4. Unka kal ka GMV `data/daily-gmv.csv` mein ek row daalo → digest phir chala → **aapka % sahi nikaalne chahiye**

✅ **Expected:** Telegram pe REAL numbers wala digest. **System LIVE. 🎉**

---

## STEP 9: Security Hardening (DIN 4, 20 min)

- [ ] Oracle VM: firewall mein sirf **22 (SSH) + 5678 (n8n)** open; n8n pe strong password
- [ ] Google Drive + Google account: **2FA ON**
- [ ] Telegram: `ALLOWED_CHAT_IDS` mein sirf aapka ID
- [ ] `.env` file: `chmod 600`
- [ ] Kill switch test: `touch /opt/agent-os/data/KILL` → verify monitoring-only → `rm`

✅ **Expected:** Sab ticks. System secured.

---

## 🚨 Agar Oracle Approval Na Aaye (Plan B — 48hr+)

1. **Make.com free tier** (1000 ops/mo) pe Phase 1 chala do — pilot 2 sellers ke liye kaafi
2. Oracle signup dobara try karo (different card / verification details)
3. Approval aate hi n8n pe migrate karo (workflows export/import hoti hain — 15 min)
4. Make pe daily digest + Sheets + Telegram — yehi combo 1000 ops mein chalta hai (sirf stock-sync hourly nahi chalegi)

---

## ✅ FINAL: System Live Hone Ke Baad

- **Din 5 se:** Pilot 2 sellers ka real data daily
- **Week 2:** Baaki 8 sellers onboarding (2 per din) — onboarding packet: `02-docs/SELLER-ONBOARDING-PACKET.md`
- **Din 14:** Pehla full month-prep review

Full daily breakdown: `02-docs/BUILD-CALENDAR-14-DAY.md`
Har step ka test: `02-docs/VERIFICATION-CHECKLIST.md`
