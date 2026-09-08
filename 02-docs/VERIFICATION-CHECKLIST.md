# ✅ VERIFICATION CHECKLIST — "System Sahi Chal Raha Hai" Test

> Har component ka ek simple test. Kabhi bhi confusion ho toh yahi chalao.
> Rule: ek test fail = aage mat jao, usi ko fix karo.

---

## 1. SERVER (Oracle VM)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| VM live hai | Oracle console → instance status | **RUNNING** (not STOPPED) |
| SSH kaam karta hai | `ssh ubuntu@<VPS_IP>` | Terminal khulti hai |
| Auto-restart | VM restart karo → 5 min baad n8n check | n8n khud wapas aa gaya |
| Space | `df -h` | / partition 80% se neeche |

## 2. AUTOMATION (n8n)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| n8n khulta hai | `http://<VPS_IP>:5678` | Login page |
| Timezone sahi | Settings | **Asia/Kolkata** |
| 3 workflows imported | Workflows list | 3 workflows dikhte hain |
| WF-01 manual run | "Execute workflow" | Telegram pe digest message |
| WF-01 schedule active | Workflow → Active toggle ON | Kal 7:00 pe khud message aaya |
| WF-02 test | Manual execute | Koi breach na ho toh silent, ho toh alert |

## 3. AI (Gemini)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| Key kaam karti hai | aistudio.google.com pe key active dikhe | Status: active |
| Data use OFF | Key details | "Improve products" = **Off** |
| WF-03 (listing) test | Ek sample product do | 30 sec mein Flipkart-format listing aati hai |
| Pacing rule | 10 listings ka batch chala | Batch ke beech 10-min gap hua (cap safe) |

## 4. DATA (Sheets + CSV)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| sheets.csv data sahi | `data/sellers.csv` kholo | 10 sellers, rate % sahi |
| Daily log aa raha | `data/daily-gmv.csv` | Aaj/kal ki rows hain |
| Sheets mirror | Google Sheet kholo | DAILY-LOG mein naye entries aaye (agar sync workflow active hai) |
| % calculation | Ek seller ka number manually mat karo vs digest | **Dono match hain** (sabse important test) |

## 5. INTERFACE (Telegram)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| Bot reply deta hai | `/status` bhejo | 5 sec mein status aaya |
| Income command | `/income` | Latest digest aaya |
| Koi aur ka ID kaam nahi karta | Dose ke phone se bot ko message | "Not authorized" |
| WhatsApp down scenario | (socho: WhatsApp app update aaye) | Telegram se system accessible hai ✅ |

## 6. BACKUP (Drive)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| Aaj ki backup hai | Drive → AgentOS-Backups | Aaj/kaal ka file hai |
| Restore test (weekly) | Ek file download karo, kholo | File intact hai |
| Cron chala | VPS: `crontab -l` | Backup line hai |

## 7. SECURITY

| Test | Kaise | Pass Agar |
|------|-------|----------|
| .env protected | `ls -l .env` | Permission 600 |
| 2FA Google | Google account security | 2FA ON |
| Kill switch test | `touch data/KILL` → WF run karo | Koi publish/price action NAHI hua, sirf alerts |
| Firewall | Oracle network rules | Sirf 22 + 5678 open |

## 8. BUSINESS (Pilot)

| Test | Kaise | Pass Agar |
|------|-------|----------|
| Aapka % sahi | Manually: GMV × rate = digest ka number | **Match** |
| Tentative rate alert | Ek seller ka rate TENTATIVE rakhke dekho | Digest mein 📌 alert aaya |
| GMV drop alert | Ek seller ka GMV aadha karke dekho | "20%+ neeche" alert aaya |
| Weekly report | Friday 6 baje | 10 sellers ki reports ready |
| Seller ka response | Pilot seller ko pehli report dikhao | "Yeh toh achha hai" mile ☺️ |

---

## 📋 WEEKLY 5-MIN HEALTH CHECK (Har Sunday)

```
☐ 7:00 ka digest aaya?
☐ Koi open P0/P1 incident?
☐ Aaj ki backup Drive mein?
☐ Aapka tentative rate abhi bhi tentative?
☐ Koi seller ka GMV 2 hafte se gir raha?
```

5 ticks = system healthy. Koi tick miss = uska test upar se chala.
