# 📅 14-DIN BUILD CALENDAR (Free Stack)

> Goal: Din 4-5 pe system LIVE, Din 14 pe 10 sellers ke saath full pilot.
> Aapka daily effort: **1-1.5 ghante** (Din 1-5), uske baad **30 min**.

---

## PHASE A: INFRA (DIN 1-4)

| Din | Kaam | Kitna Time | Done Kab? |
|-----|------|-----------|-----------|
| **1** | Oracle signup + instance request (approval lagta hai — bas request karke chhodo) • Gemini API key • Telegram bot • Sheets master file (6 tabs) | 1.5 ghante | ☐ |
| **2** | Oracle approval wait. Is beech: SOP manual padho (`02-docs/SOP-MANUAL.md`) • Rate card decide karo (3/4/5% kaunse sellers ke liye) • 2 pilot sellers ki list banao | 1 ghanta | ☐ |
| **3** | Oracle approval aaya? → Project deploy + setup script + n8n account + .env keys • Workflows import + credentials | 1.5 ghante | ☐ |
| **4** | Backup (Drive) • First live test (digest Telegram pe) • Security hardening checklist | 1 ghanta | ☐ |

**Din 4-5 end pe system LIVE hona chahiye — Telegram pe digest aa raha ho.**

---

## PHASE B: PILOT 2 SELLERS (DIN 5-8)

| Din | Kaam | Kitna Time | Done Kab? |
|-----|------|-----------|-----------|
| **5** | Pilot sellers ka onboarding shuru: docs maango (onboarding packet se WhatsApp script) • Unka real data daalo (sellers.csv + cost sheet) | 1 ghanta | ☐ |
| **6** | Seller 1 ka data live: 7 din ka GMV history daalo → weekly digest check karo • Listings pipeline pe 2-3 listings test (manual approve mode) | 1 ghanta | ☐ |
| **7** | Seller 2 ka data live • Dono ka daily digest 7 baje aane laga (auto) • KPI tracker mein initial values | 45 min | ☐ |
| **8** | **Pilot review:** Kya digest sahi? Kya % sahi? Kya alerts aaye? Issues note karo • Unhe fix karo (SOP update) | 45 min | ☐ |

---

## PHASE C: SCALE 10 SELLERS (DIN 9-14)

| Din | Kaam | Kitna Time | Done Kab?
|-----|------|-----------|-----------|
| **9** | Onboarding: Seller 3-4 (onboarding packet scripts se) | 1 ghanta | ☐ |
| **10** | Onboarding: Seller 5-6 • Pilot sellers ka pehla "weekly" dekho — seller ko bhi report bhejo (first wow moment) | 1 ghanta | ☐ |
| **11** | Onboarding: Seller 7-8 | 1 ghanta | ☐ |
| **12** | Onboarding: Seller 9-10 • Sabka data DAILY-LOG mein aa raha hai? Verify | 1 ghanta | ☐ |
| **13** | **Full system week review:** 10 sellers ke digests, incidents, tasks • KPI tracker full update • Jo rules tight/khule the unhe tune karo | 1 ghanta | ☐ |
| **14** | **Month 1 plan:** Kaunse 3 improvements agle mahine (e.g., API keys live karna = Phase 2) • Self-review: aapka time ab kitna? (target: daily 30 min) | 30 min | ☐ |

---

## 📊 Din 14 Ke Aakhri Target State

- [ ] 10 sellers ka data system mein live
- [ ] Subah 7 baje auto digest aapke Telegram pe
- [ ] Friday ko auto weekly reports
- [ ] Koi bhi seller ka number gire toh alert aayega
- [ ] Aapka daily time: **≤30 min** (sirf approvals + digest padhna)
- [ ] Aapka kharcha: **₹0**

---

## ⏰ Daily Routine (System Live hone ke baad, din 15+)

| Time | Aap ka kaam |
|------|------------|
| 7:00 AM | Digest padho (2 min) — red flags ho toh handle karo |
| Subah kabhi bhi | Approvals ka queue check karo (Telegram se, 10 min) |
| 8:00 PM | Koi baaki approval? (5 min) |
| **Total** | **~20-30 min/din** |
