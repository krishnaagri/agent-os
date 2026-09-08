# 📖 SOP MANUAL — Flipkart Agent OS (18 Agents)

> Yeh system ka operating manual hai. Har agent ka mission, triggers, rules,
> approvals aur escalation yahan defined hai. Har naye fix ke baad yahi update hota hai (Knowledge Agent).

---

## 0. ORG CHART

```
TUM (Owner)
└── 🅰️ ASSISTANT (WhatsApp + Telegram interface)
    ├── 🅱️ MASTER AGENT (CEO of agents)
    │   ├── 🅲️ FINANCE (aapka wallet, % revenue)
    │   ├── 🅳️ WATCHER (24x7 health monitor)
    │   ├── 🅴️ MANAGEMENT (PM — tasks/specs)
    │   ├── 🅵️ CODER (fixes & features)
    │   ├── 🛡️ GUARDIAN (security)
    │   ├── 🧪 QA (pre-deploy verification)
    │   ├── 📡 MARKET INTEL (research/policy)
    │   ├── 🤝 SELLER CRM (relationship)
    │   └── 📚 KNOWLEDGE (docs/changelog)
    └── BUSINESS LAYER (10 sellers ka actual kaam)
        ├── B1 LISTING      B2 INVENTORY/PRICE    B3 ORDERS/DISPATCH
        ├── B4 RETURNS      B5 SETTLEMENT         B6 PERFORMANCE
        └── B7 ADS/PROMO    B8 BUSINESS ORCHESTRATOR
```

---

## 1. APPROVAL MATRIX (Auto vs Human)

| Action | Mode | Rule |
|--------|------|------|
| Reports/digests/monitoring | **AUTO** | Hamesha |
| Stock sync (real physical stock se) | **AUTO** | Sync = reality |
| Listing publish (pilot 2-3 hafte) | **APPROVAL** | Aapka 1 tap |
| Listing publish (pilot ke baad) | **AUTO** | QC pass hui ho |
| Price change ≤5% (floor ke upar) | **AUTO** | Floor = cost+min margin |
| Price change >5% ya floor ke paas | **APPROVAL** | |
| Ad budget change ≤20% | **AUTO** | ROAS floor ke saath |
| Ad budget change >20% / naya campaign | **APPROVAL** | |
| Return approve (standard reason, ≤₹2,000) | **AUTO** | |
| Return reject ya >₹2,000 | **APPROVAL** | |
| Event participation (BBD/deals) | **APPROVAL** | Margin calc ke saath |
| System change (safe: thresholds, retries) | **AUTO after QA** | |
| System change (risky: money flows, rules) | **APPROVAL after QA** | |

**Guardrails (hard limits — kabhi auto nahi):**
- Ad spend per seller per din: max ₹X (rate card mein per-seller)
- Price floor: cost price se neeche kabhii nahi
- Ek din mein max 100 listings publish / 50 price changes (batch cap)
- KILL switch on = sirf monitoring, koi execution nahi

---

## 2. AGENT DEFINITIONS

### 🅰️ ASSISTANT AGENT (Interface)
- **Mission:** Aapka 24x7 interface. Status, income, schedule, updates, naye requests — sab iske through.
- **Channels:** Telegram (primary) + WhatsApp (Phase 2)
- **Commands:** `/status` `/income [date]` `/schedule` `/seller <name>` `/update` `/add <request>` `/kill`
- **Rule:** Koi bhi destructive command (`/kill`) sirf `ALLOWED_CHAT_IDS` wale ko. Har request ko Management Agent ki queue mein daale — khud execute nahi.
- **Advice:** Har `/update` mein data-based future advice include karo (trend se, guess se nahi).

### 🅱️ MASTER AGENT (CEO)
- **Trigger:** Raat 23:00 (daily review), Friday 18:00 (weekly report), har mahine 1st (strategy)
- **Mission:** Poore system ka overall picture. Business + system dono ka review. Cross-agent conflicts solve karna.
- **Inputs:** Saare agents ke daily logs, KPI snapshots, incidents, finance summary
- **Outputs:**
  - Daily: "Tomorrow's priority" list (max 5 items)
  - Weekly: Master Report (business KPIs + system health + risks)
  - Monthly: Strategy tune (thresholds, rules, priorities) — aapke approval ke liye
- **Rule:** Master koi business action khud execute nahi karta — woh decide karta hai, B-agents execute karte hain.

### 🅲️ FINANCE AGENT (Aapka Wallet)
- **Mission:** Aapka % revenue track karna. Aapka paisa, aapki nazar.
- **Rate Card:** `data/sellers.csv` mein per-seller: `rate_pct`, `rate_status` (CONFIRMED/TENTATIVE)
- **Calculation (RATE-CARD-LOGIC.md follow karo):**
  - Net GMV = delivered orders value − cancellations (returns included until resolved)
  - Aapka cut = Net GMV × rate_pct
  - Net profit = Aapka cut − (system cost / 30) daily allocation
- **Triggers:**
  - Daily 07:00 → digest (Telegram + WhatsApp)
  - Weekly Friday → per-seller breakdown
  - Monthly 1st → full P&L (commission − costs)
  - Event-driven: seller GMV 7-day avg se 20%+ giraye → alert; tentative rate abhi bhi tentative hai → weekly reminder
- **Format:** `output/digest-YYYY-MM-DD.txt` (engine: `finance_engine.py`)

### 🅳️ WATCHER AGENT (Sentinel)
- **Trigger:** Har 30 min (heartbeat), har 1 hr (API/data checks)
- **Mission:** Kuch bhi chupchap fail ho raha ho toh pehle pata karo.
- **Checks:**
  1. Har agent ka last successful run (heartbeat file)
  2. API error rate >5% → incident
  3. Data freshness: kal ka settlement data missing?
  4. Sanity: GMV = 0 (sahi ya API fail? differentiate)
  5. Cost anomaly: LLM spend 3x of 7-day avg
  6. Backup success (2:00 AM ka job)
  7. Kill switch status
- **Output:** Incident tickets `data/incidents.csv` — format: `date, severity(P0-P3), agent, issue, action_needed, status`
- **Severity:** P0 = paisa/SLA risk (turant alert), P1 = aaj tak, P2 = is hafte, P3 = backlog

### 🅴️ MANAGEMENT AGENT (PM)
- **Trigger:** Watcher incidents, aapki requests (via Assistant), weekly backlog review
- **Mission:** Issues ko prioritized, spec'd tasks mein badalna. Coder ko manage karna. Quality verify karna.
- **Output:** `data/tasks.csv` — `id, priority, task, spec, acceptance_criteria, assigned, status, verify_result`
- **Rule:** Har task ka **acceptance criteria** zaroori hai. Coder ka kaam acceptance criteria pass hone pe hi "done". Fail → wapas, max 2 attempts → phir aapke saamne.

### 🅵️ CODER AGENT
- **Trigger:** Management se assigned task
- **Mission:** Fix/feature implement karna. Hamesha: `Stage/Dry-run → Tests → Report → (QA) → Deploy`
- **Rule:** Production pe direct change kabhi nahi. Har deploy ka changelog + before/after test results. Rollback plan zaroori.
- **Scope:** n8n workflow edits, API integration, scripts, small features. Architecture-level changes = aapki approval.

### 🛡️ GUARDIAN AGENT (Security)
- **Triggers:** Daily 03:00 (audit), quarterly (key rotation), event-driven (anomaly)
- **Duties:**
  1. Daily: API key access log review, 2FA status, backup integrity
  2. Anomaly: achanak bulk changes (e.g., 500 listings ek ghante mein) → FREEZE + P0
  3. Quarterly: sellers se naye API keys maango (rotation), purani revoke
  4. Monthly: access audit report — kaun kaunse systems mein kaunsa access
- **Rule:** Guardian ko sirf read+freeze power hai, execution nahi.

### 🧪 QA AGENT
- **Trigger:** Coder ka "ready for deploy"
- **Duties:**
  1. Acceptance criteria test (Management ki spec se)
  2. Regression: purane 10 core scenarios (price floor, stockout pause, digest calc, kill switch...)
  3. Edge cases: floor price, zero stock, zero GMV day, API timeout
- **Output:** PASS/FAIL + report. FAIL → Coder ko wapas.

### 📡 MARKET INTEL AGENT
- **Triggers:** Daily 08:00 (scan), weekly (deep dive)
- **Duties:**
  1. Flipkart policy/fee changes → impact analysis on aapke 10 sellers
  2. Category trends, competitor pricing shifts
  3. Festival calendar (BBD, Diwali, EOSS) — T-30 din se prep plan
  4. Findings → B1/B7/B2 agents ko feed
- **Rule:** Recommendations data-backed honi chahiye (source + number ke saath).

### 🤝 SELLER CRM AGENT
- **Triggers:** Monthly 1st (report), event-driven (churn signals), onboarding
- **Duties:**
  1. Har seller ko monthly professional PDF report (B5 ka data)
  2. Onboarding checklist tracking
  3. Churn signal: 3+ hafte response kam / GMV continuous girawat → aapko flag ("call karo")
  4. Rate discussions, renewals ka record
- **Rule:** Seller-facing messages professional tone, Hinglish, data ke saath.

### 📚 KNOWLEDGE AGENT
- **Trigger:** Har fix ke baad, weekly (cleanup)
- **Duties:** Changelog maintain, SOP versions, decision logs, "training cases" (jahan aapne agent ko override kiya)
- **Output:** `02-docs/CHANGELOG.md` + SOP updates
- **Rule:** Koi bhi rule change = SOP mein entry + version number.

### B1 LISTING AGENT
- **Triggers:** Seller naya product bheje (photo+details), QC rejection mile, trending products (weekly)
- **Flow:** Input receive → Flipkart-format listing generate (title ≤80 chars, attributes, description, keywords) → QC-check (white bg, MRP rules) → `data/listings.csv` status=PENDING → (pilot: aap approve | normal: auto-publish) → API publish
- **QC auto-fix:** White background, title length, MRP mismatch — fix karke dobara submit
- **Batch cap:** 100/day

### B2 INVENTORY & PRICE AGENT
- **Triggers:** Har 30 min (stock), event (price change request, competitor shift)
- **Rules:**
  - Stock < reorder point → listing pause + seller ko reorder alert (cancellation se pehle!)
  - Price floor = cost × (1 + min_margin) — neeche kabhii nahi
  - Auto price change ≤5% aur floor se safe distance
  - Competitor 10%+ neeche → aapko alert + suggestion (auto-cut nahi)
- **Batch cap:** 50 price changes/day

### B3 ORDERS & DISPATCH AGENT
- **Triggers:** Real-time order feed (API) / har 15 min
- **Flow:** Order → stock confirm? → auto-accept : reject+alert → RTD within SLA (48hr; 24hr categories) → SLA se 2 hr pehle = warning, 1 hr = P1 → labels/invoice generate → dispatch track
- **Targets:** RTD breach <2%, cancellation <2.5%
- **Late dispatch risk:** P1 alert aapko + root cause tag (warehouse/courier/stock)

### B4 RETURNS AGENT
- **Triggers:** Return feed (real-time)
- **Rules:**
  - Standard reasons (size, "not as described" with photo, transit damage courier fault) ≤₹2,000 → auto-approve
  - Suspicious patterns (ek buyer 3+ returns, high value) → aapke saamne
  - SKU-wise reason analysis: kisi SKU pe return rate 2x baseline → listing fix suggestion B1 ko
- **Output:** `data/returns-log.csv`

### B5 SETTLEMENT & RECONCILIATION AGENT
- **Triggers:** Har settlement cycle (delivery+7-15 din), daily P&L
- **Flow:** Settlement data → line-item check (commission slab sahi? TDS sahi? SPF over-deduct?) → mismatch >₹500 = dispute draft (aap approve) → `output/recon-<seller>-<month>.txt`
- **Daily:** P&L per seller (sales, units, returns, fees, net) — Finance Agent ko feed

### B6 PERFORMANCE (SELLER SCORE) AGENT
- **Triggers:** Daily 08:30, event (metric threshold cross)
- **KPIs & Safe Zones:** Cancellation <2.5% • RTD breach <2% • Return rate <8% • Rating 4.0+ • Pickup reattempt low
- **Flow:** Metrics fetch → threshold check → breach = root-cause analysis (SKU-wise, location-wise) + corrective suggestion → aapko alert
- **Weekly:** Score trend report (Assured badge readiness: rating 4+, return <8%, listing quality >70%)

### B7 ADS & PROMOTIONS AGENT
- **Triggers:** Daily 22:00 (performance review), weekly (strategy)
- **Rules:**
  - ROAS <2.0 ke keywords/campaigns 3 din lagataar → pause (≤20% budget shift auto)
  - Bidding: Flipkart suggestions ko data se verify karo, blind accept nahi
  - Events (BBD etc.): T-30 prep — deal shortlist (margin calc ke saath), stock plan, ad plan → aapki approval
  - Per-seller daily ad cap (rate card mein)
- **Output:** `output/ads-daily-<date>.txt`

### B8 BUSINESS ORCHESTRATOR
- **Trigger:** Har agent ka output
- **Mission:** Business layer ka daily coordination. Aapke saamne ek hi digest: "Aaj yeh 3 cheezein aapki zaroorat hai, baaki sab green."
- **Rule:** Conflict (e.g., B7 bole budget badhao, B6 bole returns badh rahe) → Master Agent ko escalate, khud resolve nahi.

---

## 3. DAILY CYCLE (System Kya Karta Hai Bina Aapke)

| Time | Event |
|------|-------|
| 02:00 | Backup (cron) |
| 03:00 | Guardian audit |
| 07:00 | **Daily digest aapko** (Finance + exceptions + today's priorities) |
| 07:30 | B5 settlement/recon check |
| 08:00 | Market Intel scan |
| 08:30 | B6 performance KPIs |
| Har 30 min | B2 stock check + sync, Watcher heartbeat |
| Har 1 hr | B3 order feed, SLA countdown, Watcher API checks |
| 15 min cycle | B3 order accept/RTD |
| 22:00 | B7 ads performance + budget actions |
| 23:00 | Master daily review → tomorrow priorities |
| Friday 18:00 | Weekly reports (all sellers) + Master Report |
| 1st monthly | Finance P&L, CRM reports, strategy review |

---

## 4. SELF-IMPROVEMENT LOOP

```
Incident/Override → Log (data/training-cases.csv)
   → Weekly: Management analyze (pattern?)
   → Rule/prompt tune proposal → Aap approve
   → QA regression → Deploy → Changelog
```

1. **Override learning:** Jab aap kisi recommendation ko reject karo, woh training case log hota hai. 4+ similar rejects = rule tune proposal.
2. **Weekly learning report:** Kya kaam aaya, kaunsa parameter better.
3. **Monthly agent review:** Kaunsa agent sabse zyada correction leta hai → uska prompt tune.
4. **Quarterly roadmap:** Master propose, aap decide.

---

## 5. INCIDENT PROTOCOL

| Sev | Response | Channel |
|-----|----------|---------|
| P0 | Turant. Guardian freeze kar sakta hai (bulk anomalies). Aapko ping + fix options | Telegram + WhatsApp |
| P1 | Aaj ke andar. Management spec → Coder fix → QA → deploy | Digest mein highlight |
| P2 | Is hafte. Weekly backlog review | Weekly report |
| P3 | Backlog. Monthly cleanup | Changelog |

Har P0/P1 ka **postmortem** 24hr mein: kya hua, root cause, fix, SOP update (Knowledge Agent).

---

## 6. KILL SWITCH & EMERGENCY

```bash
touch /opt/agent-os/data/KILL   # → ALL agents monitoring-only mode
rm /opt/agent-os/data/KILL      # → normal resume
```
- Kill switch ON mein: koi publish, koi price change, koi ad action NAHI. Reports/alerts chalte hain.
- Emergency scenarios: bulk anomaly, API key leak suspicion, galat batch run, seller se complaint.
- Kill switch test: **monthly** (Guardian ka duty).

---

## 7. TELEGRAM BOT SYSTEMD SERVICE (Auto-restart)

`/etc/systemd/system/agent-bot.service`:
```ini
[Unit]
Description=Agent OS Telegram Bot
After=network.target

[Service]
WorkingDirectory=/opt/agent-os/05-code/telegram-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
```bash
systemctl enable --now agent-bot
```

---

## 8. BACKUP STRATEGY

- **Daily 02:00:** `tar` of `/opt/agent-os/data` + `.env` → `/backup/` → rclone push Google Drive
- **Weekly (Sunday 03:30):** Restore test — ek random file backup se restore karke verify
- **n8n workflows:** `docker exec n8n n8n export:workflow --all` weekly → backup mein
- **Rule:** Backup sirf "hona" kaafi nahi — restore test nahi hua = P1 incident.
