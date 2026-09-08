# 💰 RATE CARD & REVENUE LOGIC (Aapka % Model)

> Aapka revenue = sellers ke GMV ka 3-5%. Is document mein exactly defined kiya hai
> ki calculation kaise hoga — taaki Finance Agent, aap, aur sellers teeno ka ek hi number aaye.

---

## 1. BASIC DEFINITIONS (Sabse Important)

| Term | Definition |
|------|-----------|
| **Gross Orders** | Approve hui orders ka total value (MRP/selling price se) |
| **Cancellations** | Seller/Flipkart/buyer kisi bhi taraf se cancel hui orders |
| **Returns** | Delivered hokar wapas aaye orders (refund pending until resolved) |
| **NET GMV (commission base)** | `Gross Orders − Cancellations` (Returns **included** until final resolution) |
| **Aapka Revenue** | `NET GMV × Seller ka rate_pct` |
| **Net Profit (aapka)** | `Aapka Revenue − System Costs` |

### Kyun Yehi Definition?
- Cancellations minus karni hain — wo kamaai nahi hui
- Returns included rakhni hain (final tak) — kyunki COD returns mein actual refund 7-15 din baad confirm hota hai; jaise hi resolve hua, Finance Agent adjust karta hai
- Yeh standard marketplace commission practice se bhi milta hai

---

## 2. RATE CARD STRUCTURE

`data/sellers.csv` mein har seller ke liye:

```csv
seller_id,name,category,rate_pct,rate_status,monthly_gmv_target,ad_budget_cap_daily,cost_sheet_updated
S01,Aman Electronics,Electronics,5,CONFIRMED,200000,800,2026-09-01
S02,Priya Fashion,Fashion,4,TENTATIVE,150000,500,2026-09-03
S03,HomeWorld Decor,Home,3,CONFIRMED,100000,300,2026-09-05
...
```

### Rate Status
- **TENTATIVE** — seller se abhi final confirm nahi hua → Finance Agent weekly reminder deta hai
- **CONFIRMED** — agreement signed pe

### Rate Band Suggestions (aapke liye)
| Seller Type | Suggested % | Kyun |
|-------------|-------------|------|
| High volume (GMV >₹1L/mo), low effort categories | 3% | Volume pe kamao |
| Medium volume, active management chahiye | 4% | Balance |
| Low volume / naya seller / high-touch (fashion, returns zyada) | 5% | Effort premium |

> **Pro move:** Seller ko do options do: "Flat 4%" vs "3% + sales target hit pe bonus 0.5%". Yeh unhe growth ke saath align karta hai aur aapka revenue bhi upar jaata hai.

---

## 3. SYSTEM COSTS (Aapka Kharcha — Net P&L Se Minus)

| Item | ₹/Month |
|------|---------|
| VPS | 500-2000 |
| LLM API | 1500-6000 |
| WhatsApp API | 0-3000 |
| Backup/other | 0-500 |
| **Total (typical)** | **~3,000-9,000** |

Daily allocation = `Monthly / 30` — Finance Agent isse har din ke digest mein "net" dikhata hai.

**Breakeven math:** 4% average rate pe, ₹5,000 system cost recover karne ke liye sellers ka combined **monthly GMV ≈ ₹1.25 lakh** chahiye. 10 sellers x ₹1L avg GMV = aapka gross ~₹40-50k/month, net ₹35k+.

---

## 4. MONTHLY P&L FORMAT (Finance Agent Generate Karega)

```
══════════════════════════════════════════
  AGENT OS — MONTHLY P&L (AUGUST 2026)
══════════════════════════════════════════
Seller          GMV(₹)    Rate  Aapka(₹)
S01 Aman        2,10,000   5%    10,500
S02 Priya       1,42,000   4%     5,680
...
TOTAL                     →     38,450
System costs                  →  -5,200
────────────────────────────────────
NET PROFIT                  →   33,250
══════════════════════════════════════════
Trend: GMV +8% vs July | Aapka +6%
Attention: S05 GMV -22% | S02 rate abhi TENTATIVE
```

---

## 5. EDGE CASES (Rules Clear, Taaki Dispute Na Ho)

| Case | Rule |
|------|------|
| Sale season (BBD) ka GMV spike | Same rate — season mein aapka bonus hai, seller ko transparent raho |
| Seller ne apna ad budget badhaya aur usse aaya sales | Wahi rate — ad spend seller ka hai, credit bhi unka, commission normal |
| Return final reject (refund nahi hua) | Wapis GMV mein count (original treatment se koi change nahi — originally included hi thi) |
| Return final accept (refund hua) | Wahi din se GMV minus |
| Seller ne mid-month rate badla (agreed) | Change date se naya rate, month-wise proration |
| Seller ne account pause kiya (10 din) | Pause days bhi normal — bas uska GMV 0 aayega |
| Seller ne agreement terminate kiya | Last settlement tak wahi rules, transition 7 din |

---

## 6. RATE REVISION POLICY (Professional)

- Review: **quarterly** (30 din pehle notice)
- Increase ka legitimate basis: GMV growth, expanded services, seller score improvement aapne kara
- Format: *"Aapka account 2x grow hua, services expand hue — naya rate 4%→4.5% se 1 Oct. Ya same 4% pe bonus structure rakh sakte hain."*
- Kabhi bhi: mid-month surprise rate change NAHI
