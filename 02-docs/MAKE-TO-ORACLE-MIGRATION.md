# 🔄 PHASED SETUP PLAN — n8n on LAPTOP (ABHI) → n8n on ORACLE (BAAD MEIN)

> Decision (09 Sep 2026): Make.com hata. **Seedha n8n.**
> Abhi: n8n aapke **laptop pe** (₹0, bina card). Baad mein: **wahi n8n, Oracle free VM pe** (24/7).
> Kaam dobara nahi karna padega — workflow ek hi, sirf "ghar" badlega.

---

## 🧠 KYSSE YEH KAAM KARTA HAI: "EK HI SYSTEM, DO GHAAR"

| Hissa | Kya | Badlega? |
|-------|-----|---------|
| **BRAIN** | data/ CSV files, SOP rules, prompts, formulas, rate card | ❌ Kabhi nahi |
| **WORKFLOWS** | n8n ke 5-8 workflows (digest, alerts, KPI, weekly, listing) | ❌ Same (laptop se Oracle) |
| **CODE** | finance_engine.py, bot.py (n8n ke Execute Command node se chalte hain) | ❌ Same files |
| **GHAR** | Phase 0: aapka laptop → Phase 1: Oracle free VM | ✅ Sirf yeh badlega |

**n8n ke isliye best:** Make mein Python chalana mushkil tha, n8n mein **Execute Command node** se aapke finance engine + bot directly machine pe chalte hain. Matlab laptop pe hi almost full system milega.

---

## 📌 PHASE 0: n8n ON LAPTOP (ABHI — ₹0, No Card)

### Kya Milega:
- ✅ Saare workflows live (digest, alerts, KPI, weekly, listing generation)
- ✅ Finance engine + Telegram bot — n8n ke saath, same machine
- ✅ Unlimited runs (koi ops limit nahi — yahi Make se n8n ka asli farq hai)
- ✅ Gemini free + Telegram free + Sheets free = **₹0**

### Honest Constraint (Important):
- ⚠️ **Laptop ON ho toh hi schedules chalti hain.** Laptop band (raat) → uska waqt ka job miss (n8n missed runs ko catch-up nahi karta)
- **Solution:** Phase 0 mein saare important jobs **working hours mein** set karo:
  - Digest: **09:30 AM** (aap office/kaam pe aao, tab aaye)
  - Alerts check: **10:00 AM + 6:00 PM**
  - KPI: **6:30 PM**
  - Weekly: **Friday 5 PM**
- Laptop pe kaam karte ho toh din bhar system "jaagta" hai — 10 sellers ka 90% kaam din mein hi hota hai

### Laptop Setup (30 min):
1. **Node.js LTS** install karo (nodejs.org) — ya **Docker Desktop** (docker.com)
2. n8n chalao (main aapko exact command OS ke hisaab se dunga — Windows/Mac)
3. Browser kholo: **localhost:5678** → owner account banao → Timezone: **Asia/Kolkata**
4. `04-n8n-workflows/` ke 3 JSONs import karo
5. Credentials lagao: Telegram token, Gemini key
6. Har workflow ka 1 test run → sab green

### Daily Routine (Phase 0):
| Time | Kya |
|------|-----|
| Subah laptop on hote hi | Digest + alerts Telegram pe (09:30 job) |
| Roz 5 min | Seller Hub se CSV downloads → data/ folder |
| Din bhar | On-demand: listings (Gemini workflow), queries |
| 6:30 PM | KPI check report |
| Raat | Laptop band = system soya (koi baat nahi, Phase 0 hai) |

---

## 🚀 PHASE 1: n8n → ORACLE VM (Jab Card + Approval Ready Ho)

### Migration (15-30 min — kaam dobara NAHI):
| Step | Kaam |
|------|------|
| 1 | Oracle VM ready (setup guide complete) |
| 2 | n8n VM pe start (docker compose — file ready) |
| 3 | **Laptop ka n8n data folder VM pe copy karo** (`.n8n` folder — isme saare workflows + credentials hain) — ya workflows export/import |
| 4 | `.env` keys VM pe bharo |
| 5 | 1 din parallel verify (laptop wala n8n inactive) |
| 6 | Done — ab system 24/7 Oracle pe |

### Phase 1 Mein Milega (jo Phase 0 mein nahi tha):
- ✅ **24/7** — 7:00 AM ka asli digest (laptop soya nahi)
- ✅ Hourly/30-min jobs (stock check, SLA monitoring)
- ✅ Flipkart Seller API real-time order feed
- ✅ Koi laptop dependency nahi

---

## 📊 WHY N8N (Final Reasoning)

| | Make.com | **n8n** ✅ |
|---|----------|-----------|
| Free limit | 1000 ops/mo (Phase 1 mein bhi ceiling) | **Unlimited** (self-hosted) |
| Python/code | Mushkil | **Execute Command node — direct** |
| Workflow editor | Chhota | **Best-in-class (nodes, sub-workflows, error paths)** |
| Error handling | Basic | **Retry, error workflows, webhooks** |
| Data privacy | Make ke servers pe | **Aapke paas (laptop/VM)** |
| 10→50 sellers scale | Limit ke kareeb | **Bina problem ke** |

---

## 💰 TOTAL COST — PHASE 0 (Abhi)

| Item | Cost |
|------|------|
| n8n (laptop pe self-hosted) | ₹0 |
| Node.js / Docker | ₹0 |
| Gemini free tier | ₹0 |
| Telegram | ₹0 |
| Google Sheets | ₹0 |
| Personal WhatsApp (manual, sellers) | ₹0 |
| **TOTAL** | **₹0** |

## 📱 WhatsApp Rule (unchanged)
System interface = Telegram (₹0). Sellers se baat = aapka personal WhatsApp, manually (₹0). Official WhatsApp API = Phase 3 (jab commission ₹25k+/mo).
