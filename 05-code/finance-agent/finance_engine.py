#!/usr/bin/env python3
"""
Flipkart Agent OS — FINANCE AGENT ENGINE (Agent C: Aapka Wallet)
================================================================
Sellers ka GMV + aapka % rate → daily/weekly/monthly income digests.

Usage:
  python3 finance_engine.py --demo            # sample data seed (test ke liye)
  python3 finance_engine.py --today           # aaj ka digest (kal ka data)
  python3 finance_engine.py --date 2026-09-07 # specific din ka digest
  python3 finance_engine.py --weekly          # last 7 din, per-seller
  python3 finance_engine.py --monthly 2026-09 # monthly P&L

Data files:
  ../data/sellers.csv     — rate card (seller_id, name, rate_pct, rate_status, ...)
  ../data/daily-gmv.csv   — date, seller_id, gross_orders, cancelled_value, returns_resolved_value

Output:
  ../output/digest-YYYY-MM-DD.txt
"""
import csv
import sys
import datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # flipkart-agent-os/
DATA = BASE / "data"
OUT = BASE / "output"
SELLERS_CSV = DATA / "sellers.csv"
GMV_CSV = DATA / "daily-gmv.csv"

# ── Config (env se nahi, simple defaults — .env optional) ──
try:
    import os
    COST_MONTHLY = float(os.environ.get("AVG_SYSTEM_COST_MONTHLY", "5000"))
except Exception:
    COST_MONTHLY = 5000.0
COST_DAILY = COST_MONTHLY / 30.0

INR = lambda v: f"₹{v:,.0f}"


# ─────────────────────────── DATA LAYER ───────────────────────────
def load_sellers():
    """Rate card load karo."""
    sellers = {}
    if not SELLERS_CSV.exists():
        return sellers
    with open(SELLERS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sellers[row["seller_id"].strip()] = {
                "name": row["name"].strip(),
                "category": row.get("category", "").strip(),
                "rate_pct": float(row.get("rate_pct", "4") or 4),
                "rate_status": row.get("rate_status", "TENTATIVE").strip().upper(),
                "ad_cap": float(row.get("ad_budget_cap_daily", "0") or 0),
            }
    return sellers


def load_gmv(d: dt.date):
    """Ek din ka GMV data: {seller_id: {...}}"""
    rows = {}
    if not GMV_CSV.exists():
        return rows
    with open(GMV_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["date"] == d.isoformat():
                rows[r["seller_id"].strip()] = {
                    "gross": float(r.get("gross_orders", 0) or 0),
                    "cancelled": float(r.get("cancelled_value", 0) or 0),
                    "returns_resolved": float(r.get("returns_resolved_value", 0) or 0),
                    "units": int(float(r.get("units", 0) or 0)),
                }
    return rows


def net_gmv(rec):
    """Net GMV = gross - cancellations - returns resolved (returns included until resolved)."""
    return rec["gross"] - rec["cancelled"] - rec["returns_resolved"]


def compute_day(d: dt.date, sellers: dict):
    """Ek din ka full calculation."""
    gmv = load_gmv(d)
    detail, tot_gmv, tot_share = [], 0.0, 0.0
    for sid, s in sorted(sellers.items()):
        rec = gmv.get(sid, {"gross": 0, "cancelled": 0, "returns_resolved": 0, "units": 0})
        ng = net_gmv(rec)
        share = ng * s["rate_pct"] / 100.0
        tot_gmv += ng
        tot_share += share
        detail.append({"id": sid, **s, **rec, "net": ng, "share": share})
    return detail, tot_gmv, tot_share


def last7_avg_gmv(d: dt.date, sellers: dict):
    """Last 7 din (d excluded) ka seller-wise avg daily net GMV."""
    sums = {sid: 0.0 for sid in sellers}
    for i in range(1, 8):
        day = d - dt.timedelta(days=i)
        for sid, rec in load_gmv(day).items():
            if sid in sums:
                sums[sid] += net_gmv(rec)
    return {sid: v / 7.0 for sid, v in sums.items()}


# ─────────────────────────── FORMATTING ───────────────────────────
def money(v):
    return f"₹{v:,.0f}"


def fmt_digest(d: dt.date, detail, tot_gmv, tot_share):
    L = []
    L.append(f"📊 AGENT OS — DAILY FINANCE | {d.strftime('%d %b %Y')}")
    L.append("─" * 40)
    for r in detail:
        flag = "⚠️" if r["rate_status"] == "TENTATIVE" else "✅"
        L.append(f"{flag} {r['id']} {r['name'][:18]:<18} GMV {money(r['net']):>9} | aapka {money(r['share']):>8} ({r['rate_pct']}%)")
    L.append("─" * 40)
    L.append(f"TOTAL GMV: {money(tot_gmv)}   |   AAPKA CUT: {money(tot_share)}")
    net = tot_share - COST_DAILY
    L.append(f"System cost (daily): {money(COST_DAILY)}   →   NET: {money(net)}")
    return "\n".join(L)


def fmt_weekly(d: dt.date, sellers: dict):
    """Last 7 din per-seller breakdown."""
    L = [f"📈 AGENT OS — WEEKLY (7 DIN) | ends {d.strftime('%d %b %Y')}", "─" * 52]
    L.append(f"{'Seller':<20} {'GMV(₹)':>10} {'Rate':>5} {'Aapka(₹)':>10}")
    tot_share = 0.0
    for sid, s in sorted(sellers.items()):
        g = sh = 0.0
        for i in range(7):
            rec = load_gmv(d - dt.timedelta(days=i)).get(sid)
            if rec:
                g += net_gmv(rec)
                sh += net_gmv(rec) * s["rate_pct"] / 100.0
        tot_share += sh
        L.append(f"{sid} {s['name'][:16]:<20} {g:>10,.0f} {s['rate_pct']:>4}% {sh:>10,.0f}")
    L.append("─" * 52)
    L.append(f"TOTAL AAPKA (week): {money(tot_share)}")
    return "\n".join(L)


def fmt_monthly(y, m, sellers: dict):
    """Monthly P&L."""
    d0 = dt.date(y, m, 1)
    if m == 12:
        d1 = dt.date(y, 12, 31)
    else:
        d1 = dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    g = {sid: 0.0 for sid in sellers}
    d = d0
    while d <= d1:
        for sid, rec in load_gmv(d).items():
            if sid in g:
                g[sid] += net_gmv(rec)
        d += dt.timedelta(days=1)
    L = [f"💰 AGENT OS — MONTHLY P&L | {d0.strftime('%B %Y')}", "═" * 52]
    L.append(f"{'Seller':<20} {'GMV(₹)':>12} {'Rate':>5} {'Aapka(₹)':>10}")
    tot_gmv = tot_share = 0.0
    for sid, s in sorted(sellers.items()):
        sh = g[sid] * s["rate_pct"] / 100.0
        tot_gmv += g[sid]
        tot_share += sh
        L.append(f"{sid} {s['name'][:16]:<20} {g[sid]:>12,.0f} {s['rate_pct']:>4}% {sh:>10,.0f}")
    L.append("─" * 52)
    L.append(f"Total GMV: {money(tot_gmv)}    Total Aapka: {money(tot_share)}")
    L.append(f"System costs (month): {money(COST_MONTHLY)}")
    net = tot_share - COST_MONTHLY
    L.append(f"════════════════════════ NET PROFIT: {money(net)}")
    return "\n".join(L)


# ─────────────────────────── ALERTS ───────────────────────────
def build_alerts(d: dt.date, detail, tot_share):
    alerts = []
    if tot_share < 0:
        alerts.append(" Daily net negative hai — cost check karo")
    # GMV drop check vs 7-day avg
    try:
        avg = last7_avg_gmv(d, {r["id"]: r for r in detail})
        for r in detail:
            a = avg.get(r["id"], 0)
            if a > 5000 and r["net"] < 0.8 * a and r["net"] > 0:
                alerts.append(f"⚠️ {r['id']} {r['name']}: GMV {money(r['net'])} — 7-day avg {money(a)} se 20%+ neeche")
            elif a > 5000 and r["net"] == 0:
                alerts.append(f"🚨 {r['id']} {r['name']}: aaj GMV ZERO (avg {money(a)/1}) — order flow/API check karo")
    except Exception:
        pass
    for r in detail:
        if r["rate_status"] == "TENTATIVE":
            alerts.append(f"📌 {r['id']} {r['name']}: rate abhi TENTATIVE ({r['rate_pct']}%) — seller se confirm karo")
    return alerts


def write_output(text, name):
    OUT.mkdir(exist_ok=True)
    p = OUT / name
    p.write_text(text, encoding="utf-8")
    return p


# ─────────────────────────── DEMO SEED ───────────────────────────
DEMO_SELLERS = [
    ("S01", "Aman Electronics", "Electronics", 5, "CONFIRMED", 200000, 800),
    ("S02", "Priya Fashion", "Fashion", 4, "TENTATIVE", 150000, 500),
    ("S03", "HomeWorld Decor", "Home", 3, "CONFIRMED", 100000, 300),
    ("S04", "GadgetZone", "Electronics", 4, "CONFIRMED", 180000, 600),
    ("S05", "StyleCraft", "Fashion", 5, "CONFIRMED", 90000, 400),
    ("S06", "Beverage Co", "Grocery", 3, "CONFIRMED", 120000, 200),
    ("S07", "ToyBox Kids", "Toys", 4, "CONFIRMED", 80000, 250),
    ("S08", "MediCare Plus", "Health", 4, "TENTATIVE", 110000, 350),
    ("S09", "PetPal India", "Pet Care", 5, "CONFIRMED", 70000, 200),
    ("S10", "BookNook", "Books", 3, "CONFIRMED", 60000, 150),
]
BASE_GMV = {"S01": 14000, "S02": 9500, "S03": 6200, "S04": 11500, "S05": 4800,
            "S06": 7800, "S07": 4100, "S08": 6900, "S09": 3600, "S10": 2900}


def seed_demo(days=8, end=None):
    """Sample sellers + 8 din ka GMV data (S05 ko girawat ke saath — alert test)."""
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    with open(SELLERS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seller_id", "name", "category", "rate_pct", "rate_status",
                    "monthly_gmv_target", "ad_budget_cap_daily", "cost_sheet_updated"])
        for s in DEMO_SELLERS:
            w.writerow([s[0], s[1], s[2], s[3], s[4], s[5], s[6], (end or dt.date.today()).isoformat()])
    end = end or dt.date.today()
    rows = []
    for i in range(days, 0, -1):
        d = end - dt.timedelta(days=i)
        for sid, base in BASE_GMV.items():
            # weekday effect + noise (deterministic)
            f = 1 + 0.15 * ((i * 7 + ord(sid[1])) % 5 - 2) / 5
            g = base * f
            if sid == "S05" and i <= 2:
                g *= 0.45  # recent drop → trigger alert
            cancelled = g * 0.03
            ret = g * 0.01
            rows.append([d.isoformat(), sid, f"{g:.0f}", f"{cancelled:.0f}", f"{ret:.0f}", int(g / 800)])
    with open(GMV_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "seller_id", "gross_orders", "cancelled_value", "returns_resolved_value", "units"])
        w.writerows(rows)
    return end


# ─────────────────────────── MAIN ───────────────────────────
def main():
    args = sys.argv[1:]

    if "--demo" in args:
        end = seed_demo()
        print(f"✅ Demo data seeded: {len(DEMO_SELLERS)} sellers, 8 din GMV (ends {end})")
        print("Ab chalao: python3 finance_engine.py --today")
        return

    sellers = load_sellers()
    if not sellers:
        print("No sellers found. Run --demo first to seed sample data.")
        sys.exit(1)

    if "--weekly" in args:
        d = dt.date.today()
        text = fmt_weekly(d, sellers)
        print(text)
        write_output(text, f"weekly-{d.isoformat()}.txt")
        return

    if "--monthly" in args:
        ym = args[args.index("--monthly") + 1] if len(args) > args.index("--monthly") + 1 else dt.date.today().strftime("%Y-%m")
        y, m = map(int, ym.split("-"))
        text = fmt_monthly(y, m, sellers)
        print(text)
        write_output(text, f"monthly-{ym}.txt")
        return

    if "--date" in args:
        d = dt.date.fromisoformat(args[args.index("--date") + 1])
    else:
        d = dt.date.today() - dt.timedelta(days=1)  # "today ka digest" = kal ka data

    detail, tot_gmv, tot_share = compute_day(d, sellers)
    digest = fmt_digest(d, detail, tot_gmv, tot_share)
    alerts = build_alerts(d, detail, tot_share)
    if alerts:
        digest += "\n\n🔔 ALERTS:\n" + "\n".join(alerts)
    print(digest)
    p = write_output(digest, f"digest-{d.isoformat()}.txt")
    print(f"\n[saved → {p}]")


if __name__ == "__main__":
    main()
