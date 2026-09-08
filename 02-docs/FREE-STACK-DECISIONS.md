#  FREE STACK — FINAL DECISIONS (₹0/month)

> Yeh document selection ka permanent record hai. Har component ka winner, uska pro-con,
> aur jo options reject hue unka reason.

## 🚀 EXECUTION PLAN (2 PHASES — Decision: 09 Sep 2026, Updated)

| Phase | Kya | Kab |
|-------|-----|-----|
| **PHASE 0 (ABHI)** | **n8n on LAPTOP** (₹0, no card) — unlimited runs, saare workflows + finance engine + Telegram bot. Jobs working-hours mein set. 2-3 pilot sellers | Din 1 se |
| **PHASE 1 (BAAD MEIN)** | **Wahi n8n → Oracle free VM** (24/7, hourly jobs, API real-time) | Jab card ready + Oracle approval aaye |
| Migration | Laptop n8n data folder → Oracle VM | **15-30 min** (workflows/credentials/data sab same) |

**Design rule:** Brain (data CSVs + docs + prompts) + workflows kabhi nahi badalte; sirf n8n ka "ghar" badalta hai. Full flow + setup + migration: **`MAKE-TO-ORACLE-MIGRATION.md`** (ab n8n laptop→Oracle plan)

**WhatsApp decision:** Personal WhatsApp (manual, ₹0) sellers ke saath. System interface = Telegram (₹0). Official WhatsApp API = Phase 3 (jab commission ₹25k+/mo).

---

## ✅ CHOSEN STACK

| # | Component | USE KAREIN | ✅ PRO | ❌ CON (dhyan) |
|---|-----------|------------|--------|----------------|
| 1 | Server (24/7) | **Oracle Cloud Always Free** — A1 ARM, 4 OCPU + 24GB RAM, **Mumbai region** | Free FOREVER; itni RAM ki n8n + bot + backup sab ek saath; Mumbai = low latency | Signup pe card verification (₹0 charge, sirf KYC); account approval 1-2 din lag sakta hai |
| 2 | Automation | **n8n self-hosted** (Oracle VM pe, Docker se) | **Unlimited** workflows — 10 se 50 sellers tak bina limit ke; data aapke server pe | Setup mein 1 ghanta (script ready hai); backup zaroori (ho chuka plan mein) |
| 3 | AI Brain | **Google Gemini API — free tier** (AI Studio) | ~250 requests/din FREE; aapke daily 50-150 calls ka 2-4x headroom; quality top | Daily cap — bulk listing days pe batch pacing (SOP rule); key create karte waqt "data use for improvement" OFF karna hai |
| 4 | Database | **Google Sheets** | Phone pe khud kholo/dekho/edit karo; n8n directly read/write | 10,000+ rows pe slow — 10 sellers ke volume mein saalon tak nahi aayega |
| 5 | Interface | **Telegram Bot** | 100% free, unlimited messages, 24/7 reliable, commands + alerts | WhatsApp jaisa feel nahi — internal tool hai, baat nahi. WhatsApp = Phase 2 |
| 6 | Backup | **Google Drive** (rclone auto-push, daily 2 AM) | 15GB free; daily backup <500MB; Drive se phone pe bhi dekh sakte ho | Drive account pe 2FA ON zaroori |
| 7 | Flipkart Data | Phase 1: **Seller Hub manual CSV exports** → Phase 2: **Flipkart Seller API** (dono FREE) | Pilot bina API friction ke shuru | Phase 1 mein data 15-60 min laggy (manual download) — pilot ke liye theek |

**TOTAL MONTHLY COST: ₹0**

---

## ❌ REJECTED OPTIONS (Aur Kyun Nahi)

| Option | Kyun Reject |
|--------|-------------|
| Make.com free (1000 ops/mo) | 10 sellers ka FULL volume (hourly/30-min jobs) ke liye chhota hai — **par Phase 1 pilot (2-3 sellers, daily jobs) ke liye PERFECT** — isliye abhi yahi use ho raha hai (no card) |
| Zapier free (100 tasks/mo) | 2-3 din ka kaam. Demo hi nahi chalega |
| Google Cloud e2-micro free | 1GB RAM (n8n ke liye chhota) + US regions only (India latency 150ms+) |
| AWS / Azure free tier | **Sirf 12 months** free — phir bill + migration dard |
| Apna laptop 24/7 | Laptop band = system band. Net fail = system fail. 10 sellers ke data ke liye unprofessional |
| Unofficial WhatsApp automation bots | **Number ban ka real risk** — business kabhi bhi unofficial tool pe nahi |
| Airtable free | 1,000 records ki deewar — 1 mahine mein full |
| OpenAI/ChatGPT API | Paisa wala — free stack mein Gemini free tier kaafi hai; ₹415 upgrade sirf jab cap consistently touch ho |

---

## ⚠️ "FREE" KE 3 HONEST NOTES

1. **Oracle card verification:** Charge ₹0 hai, par card details leni padti hai. Comfortable nahi ho toh **Plan B**: Phase 1 Make.com free tier (pilot 2 sellers ke liye 1000 ops kaafi), Oracle approval aate hi migrate.
2. **Gemini 250 calls/din cap:** Normal din mein 50-150 calls aati hain — safe zone. Bulk listing day (50+ listings) pe n8n pacing: 10 min mein 10 listings ka batch. Cap regularly touch hua toh **ek hi upgrade point: $10/month (~₹415)** — aapke commission ka ~1%.
3. **Scale limit:** Yeh stack **10-15 sellers tak zero-cost** comfortable hai. 20+ sellers pe LLM cost shuru (₹500-1,000/mo) — tab bhi aapke 4% commission model mein negligible.

---

## 📅 TIMING NOTE (Updated 09 Sep 2026)

**Phase 1 (Make.com) aaj hi start hota hai — card ka wait nahi.**
Oracle signup tab karo jab card (Visa/MC logo wala) ready ho — approval aate hi Phase 2 migration (15-30 min). Phase 1-2 ke beech koi kaam block nahi hota.
