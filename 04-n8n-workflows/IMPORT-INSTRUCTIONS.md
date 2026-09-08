# 📥 n8n Workflows Import Guide (Windows)

> n8n localhost:5678 pe khula hua hona chahiye. Yeh 3 workflows import karo.

## PRE-REQUISITES (Import Se Pehle)

1. Project folder **`C:\agent-os`** mein extracted hai (zip se)
2. **Python** installed hai — cmd mein `python --version` se verify (v3.9+)
3. Finance engine test ho gaya — cmd mein chalao:
   `cd C:\agent-os && python 05-code\finance-agent\finance_engine.py --today`
   (agar digest print ho gaya = ✅)
4. **Telegram Bot Token** ready hai (@BotFather se)
5. **Gemini API Key** ready hai (aistudio.google.com se)

## CREDENTIALS BANAO (2)

**1. Telegram:**
1. n8n left sidebar → **Credentials** → **New** → search "Telegram" → **Telegram API**
2. **Telegram Bot Token** paste karo
3. Name: `Telegram Bot` → Save

**2. Google Gemini:**
1. **Credentials** → **New** → search "Google Gemini" → **Google Gemini API**
2. **API Key** paste karo
3. Name: `Gemini` → Save

## IMPORT (3 Files)

Har file ke liye: **Workflows** → **Import from File** → file select karo

| File | Kya Karta Hai |
|------|---------------|
| `wf-01-daily-finance-digest.json` | Har Monday-Friday 09:30 — aapka income digest Telegram pe |
| `wf-02-weekly-report.json` | Har Friday 17:00 — 10 sellers ka weekly breakdown |
| `wf-03-listing-pipeline.json` | Form bharo → Gemini listing banata hai → aapko approval ke liye bhejta hai |

## IMPORT KE BAAD — TODOs FIX KARO (Har Workflow Mein)

Import ke baad har workflow kholo, nodes pe **yellow/orange TODO** nazar aayenge:

**WF-01 aur WF-02 (2-2 nodes):**
- "Send to Telegram" node kholo:
  - **Credential** dropdown → `Telegram Bot` select
  - **Chat ID** mein apna chat ID paste karo (jo bot ne /start pe diya tha)
- "Run Finance Engine" node: command mein path check karo — `C:\agent-os` sahi hai toh kuch nahi karna

**WF-03 (3 nodes):**
- "Send for Approval" node → credential `Telegram Bot` + chat ID
- "Gemini Model" node → credential `Gemini` select
- "Product Form" node → pehli baar **Active** on karte hi n8n ek **form URL** dega — wohi URL aap kholo toh product details ka form khulega

## TEST (Sabse Important)

Har workflow ke liye:
1. **WF-01:** workflow page pe **"Execute Workflow"** button dabao → 10 sec → Telegram pe digest aana chahiye
2. **WF-02:** same → weekly table aani chahiye
3. **WF-03:** **Active** toggle on karo → form URL kholo → ek sample product bharo (e.g., "Cotton Kurti Set, Brand: Priya Fashion, Category: Women's Ethnic Wear, Price 1299, Cost 650, Features: pure cotton / machine washable / 5 sizes") → Telegram pe listing aani chahiye

**Teesron mein se koi bhi Telegram pe message aaya = system ka pehla loop close. 🎉**

## SCHEDULES (Laptop Phase — Working Hours Mein)

| Workflow | Time | Kyun |
|----------|------|------|
| WF-01 Digest | Mon-Fri 09:30 | Laptop phase mein subah laptop on hote hi |
| WF-02 Weekly | Fri 17:00 | Hafta ka wrap |
| WF-03 Listing | Form-based (jab bhi bhara) | — |

> Phase 1 (Oracle) mein WF-01 ko 07:00 pe shift kar denge (24/7 server pe).

## COMMON ISSUES (Windows)

| Problem | Fix |
|---------|-----|
| Execute Command node error: "python not recognized" | Python install karte waqt **"Add python.exe to PATH"** tick karna bhool gaye — reinstall karo tick ke saath |
| Path error | Project `C:\agent-os` mein hona chahiye — koi aur jagah nahi (spaces wale folder bhi nahi) |
| Telegram "Unauthorized" | chat ID galat hai — bot ko phir /start bhejo, naya ID lo |
| Gemini 429 error | Free tier rate limit — thodi der baad dobara try (SOP mein pacing rule hai) |
| Form URL nahi dikhta | WF-03 ko **Active** on karo, phir node pe click karo — URL wahan dikhega |
