# 🏢 Flipkart Agent OS — Multi-Seller AI Portfolio Management System

> Ek professional 18-agent system jo 10+ Flipkart sellers ka poora portfolio
> (listings, orders, pricing, inventory, returns, settlements, ads, performance)
> automate karta hai — aap sirf approvals + strategy karte ho.

---

## 📁 Project Structure

```
flipkart-agent-os/
├── README.md                        ← AAP YAHAN HAIN (quick start)
├── 01-setup/
│   ├── SETUP-GUIDE.md               ← VPS + n8n + Telegram, step-by-step
│   ├── docker-compose.yml           ← n8n self-host config
│   ├── setup-vps.sh                 ← One-click VPS setup script
│   └── .env.example                 ← API keys template (copy → .env)
├── 02-docs/
│   ├── SOP-MANUAL.md                ← 18 agents ka complete operating manual
│   ├── SELLER-ONBOARDING-PACKET.md  ← Seller se kya maangna hai + scripts
│   ├── AGREEMENT-TEMPLATE.md        ← Aap ↔ Seller agreement
│   └── RATE-CARD-LOGIC.md           ← Aapka % revenue kaise calculate hoga
├── 03-dashboard/
│   ├── build_dashboard.py           ← Dashboard generator (run karo)
│   └── master-dashboard.xlsx        ← 10-seller operations dashboard
├── 04-n8n-workflows/
│   ├── IMPORT-INSTRUCTIONS.md
│   ├── wf-01-daily-finance-digest.json
│   ├── wf-02-seller-score-monitor.json
│   └── wf-03-listing-pipeline.json
├── 05-code/
│   ├── finance-agent/
│   │   └── finance_engine.py        ← WORKING — aapka wallet engine
│   └── telegram-bot/
│       ├── bot.py                   ← Aapka 24x7 assistant interface
│       └── requirements.txt
├── 06-prompts/
│   └── AGENT-PROMPTS-PACK.md        ← Har agent ka ready system prompt
├── data/                            ← Sellers, GMV, rate card (CSV)
└── output/                          ← Generated digests & reports
```

---

## 🚀 QUICK START (7 Din Ka Plan)

| Din | Kaam | File |
|-----|------|------|
| **1** | **Oracle Cloud signup (Pehle! approval 1-2 din leta hai)** + Gemini key + Telegram bot + Sheets master file | `01-setup/SETUP-GUIDE-FREE.md` |
| **2-3** | Oracle approval aate hi: project deploy + n8n live + 3 workflows import | `01-setup/SETUP-GUIDE-FREE.md` |
| **4** | Backup (Drive) + first live test + security hardening → **SYSTEM LIVE** | `02-docs/VERIFICATION-CHECKLIST.md` |
| **5-8** | Pilot: 2 sellers ka real data live, digests + weekly test | `02-docs/BUILD-CALENDAR-14-DAY.md` |
| **9-12** | Baaki 8 sellers ka onboarding (2/din) | `02-docs/SELLER-ONBOARDING-PACKET.md` |
| **13-14** | Full system review + Month 1 plan | `02-docs/BUILD-CALENDAR-14-DAY.md` |

---

## 💰 Monthly Cost — FREE STACK (₹0/month)

| Item | Provider | Cost |
|------|----------|------|
| Server (24/7) | **Oracle Cloud Always Free** (Mumbai, 4 CPU/24GB) | ₹0 |
| Automation | **n8n** self-hosted (unlimited) | ₹0 |
| AI Brain | **Google Gemini API** free tier (~250 calls/din) | ₹0 |
| Database | **Google Sheets** | ₹0 |
| Interface | **Telegram Bot** | ₹0 |
| Backup | **Google Drive** (rclone, daily) | ₹0 |
| **TOTAL** | | **₹0/month** |

> Details + rejected options (Make/Zapier/AWS etc.) + 3 honest notes:
> `02-docs/FREE-STACK-DECISIONS.md`
> Complete step-by-step: `01-setup/SETUP-GUIDE-FREE.md`
> Daily plan: `02-docs/BUILD-CALENDAR-14-DAY.md` | Tests: `02-docs/VERIFICATION-CHECKLIST.md`
>
> **Note:** Oracle approval 1-2 din leta hai → Din 1 pehla kaam = Oracle signup.
> Optional upgrade (sirf jab zaroorat): Gemini $10/mo (~₹415) — tab tak mat socho.

---

## 🔐 Security Rules (Non-Negotiable)

1. API keys sirf `.env` / Vault mein — kabhi sheets/chat mein nahi
2. 2FA on: VPS, n8n, LLM, WhatsApp tool
3. Daily auto-backup + weekly restore test
4. Quarterly API key rotation (sellers se naye keys)
5. Kill switch: `touch /opt/agent-os/data/KILL` → pura auto system freeze (monitoring-only mode)
6. Har agent action ka log — audit trail

---

## ✅ System Health Check (Weekly 5 min)

- [ ] Kya aaj ka 7 baje digest aaya?
- [ ] Kya incidents log mein koi open P0/P1 hai?
- [ ] Kya aapka tentative rate abhi bhi tentative hai?
- [ ] Kya backup kal raat bana?

---

*Built for: Portfolio Managers managing 10+ Flipkart sellers on % revenue model (3-5%).*
