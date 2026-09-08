#!/usr/bin/env python3
"""
Flipkart Agent OS — Master Dashboard Builder
Runs: python3 build_dashboard.py  →  master-dashboard.xlsx
Reads: ../data/sellers.csv, ../data/daily-gmv.csv, ../data/schedule.csv
"""
import csv
import datetime as dt
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUT = BASE / "03-dashboard" / "master-dashboard.xlsx"

GREEN = "C6EFCE"; YELLOW = "FFEB9C"; RED = "FFC7CE"
HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(bold=True, size=16, color="111827")
SUB_FONT = Font(bold=True, size=11, color="374151")
THIN = Border(*[Side(style="thin", color="D1D5DB")] * 4)


def load_csv(p):
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN


def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main():
    sellers = load_csv(DATA / "sellers.csv")
    gmv = load_csv(DATA / "daily-gmv.csv")
    sched = load_csv(DATA / "schedule.csv")
    wb = Workbook()

    # ── 1. DASHBOARD ─────────────────────────────────────────
    ws = wb.active
    ws.title = "DASHBOARD"
    ws["B2"] = "FLIPKART AGENT OS — MASTER DASHBOARD"
    ws["B2"].font = TITLE_FONT
    ws["B3"] = f"10-seller portfolio control center | Generated: {dt.date.today().isoformat()}"
    ws["B3"].font = SUB_FONT

    ws["B5"] = "TODAY AT A GLANCE"
    ws["B5"].font = SUB_FONT
    gl = [
        ("Sellers Live", '=COUNTA(SELLERS!A2:A11)', ""),
        ("GMV (kal)", "=SUM(DAILY-LOG!G:G)", "₹#,##0"),
        ("Aapka Cut (kal)", "=SUM(DAILY-LOG!I:I)", "₹#,##0"),
        ("Open Incidents (P0/P1)", '=COUNTIF(INCIDENTS!F:F,"OPEN")', "0"),
        ("Active Tasks", '=COUNTIF(TASKS!F:F,"ASSIGNED")+COUNTIF(TASKS!F:F,"IN_PROGRESS")', "0"),
        ("Kill Switch", "OFF (check data/KILL file)", ""),
    ]
    for i, (label, formula, fmt) in enumerate(gl):
        r = 6 + i
        ws.cell(row=r, column=2, value=label).font = Font(bold=True)
        c = ws.cell(row=r, column=3, value=formula)
        if fmt:
            c.number_format = fmt

    ws["B14"] = "WEEKLY P&L (LAST 7 DAYS)"
    ws["B14"].font = SUB_FONT
    hdr = ["Seller", "Name", "Rate %", "Net GMV (₹)", "Aapka (₹)", "Trend"]
    for c, h in enumerate(hdr, 2):
        ws.cell(row=15, column=c, value=h)
    style_header(ws, 15, 7)
    dates = sorted({g["date"] for g in gmv})[-7:]
    for i, s in enumerate(sellers):
        r = 16 + i
        sid = s["seller_id"]
        ws.cell(row=r, column=2, value=sid)
        ws.cell(row=r, column=3, value=s["name"])
        ws.cell(row=r, column=4, value=float(s["rate_pct"]))
        ws.cell(row=r, column=5, value=f'=SUMIF(DAILY-LOG!B:B,B{r},DAILY-LOG!G:G)').number_format = "₹#,##0"
        ws.cell(row=r, column=6, value=f'=SUMIF(DAILY-LOG!B:B,B{r},DAILY-LOG!I:I)').number_format = "₹#,##0"
        ws.cell(row=r, column=7, value="—")
    set_widths(ws, [2, 14, 22, 12, 16, 16, 10])

    # ── 2. SELLERS ───────────────────────────────────────────
    ws = wb.create_sheet("SELLERS")
    cols = ["ID", "Name", "Category", "Rate %", "Rate Status", "GMV Target (₹/mo)", "Ad Cap (₹/day)", "Contact", "Onboarded", "Status"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    for s in sellers:
        ws.append([
            s["seller_id"], s["name"], s.get("category", ""), float(s["rate_pct"]),
            s.get("rate_status", "TENTATIVE"), int(float(s.get("monthly_gmv_target", 0) or 0)),
            int(float(s.get("ad_budget_cap_daily", 0) or 0)), "", s.get("cost_sheet_updated", ""), "LIVE"
        ])
    for r in range(2, len(sellers) + 2):
        ws.cell(row=r, column=4).number_format = "0"
        ws.cell(row=r, column=6).number_format = "₹#,##0"
        ws.cell(row=r, column=7).number_format = "₹#,##0"
    ws.conditional_formatting.add(f"E2:E{len(sellers)+1}",
        CellIsRule(operator="equal", formula=['"TENTATIVE"'], fill=PatternFill("solid", fgColor=YELLOW)))
    ws.conditional_formatting.add(f"E2:E{len(sellers)+1}",
        CellIsRule(operator="equal", formula=['"CONFIRMED"'], fill=PatternFill("solid", fgColor=GREEN)))
    set_widths(ws, [8, 20, 14, 9, 13, 16, 14, 18, 14, 10])

    # ── 3. DAILY-LOG ─────────────────────────────────────────
    ws = wb.create_sheet("DAILY-LOG")
    cols = ["Date", "Seller", "Gross (₹)", "Cancelled (₹)", "Returns Resolved (₹)", "Units", "Net GMV (₹)", "Rate %", "Aapka Cut (₹)"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    rows = sorted(gmv, key=lambda g: (g["date"], g["seller_id"]))
    r = 2
    for g in rows:
        ws.cell(row=r, column=1, value=g["date"])
        ws.cell(row=r, column=2, value=g["seller_id"])
        ws.cell(row=r, column=3, value=float(g["gross_orders"])).number_format = "₹#,##0"
        ws.cell(row=r, column=4, value=float(g["cancelled_value"])).number_format = "₹#,##0"
        ws.cell(row=r, column=5, value=float(g["returns_resolved_value"])).number_format = "₹#,##0"
        ws.cell(row=r, column=6, value=int(float(g["units"])))
        ws.cell(row=r, column=7, value=f"=C{r}-D{r}-E{r}").number_format = "₹#,##0"
        ws.cell(row=r, column=8, value=f"=IFERROR(VLOOKUP(B{r},SELLERS!A:D,4,FALSE),4)").number_format = "0"
        ws.cell(row=r, column=9, value=f"=G{r}*H{r}/100").number_format = "₹#,##0"
        r += 1
    set_widths(ws, [12, 9, 13, 14, 18, 8, 14, 9, 14])

    # ── 4. KPI-TRACKER ───────────────────────────────────────
    ws = wb.create_sheet("KPI-TRACKER")
    cols = ["Seller", "Cancellation %", "RTD Breach %", "Return Rate %", "Rating", "Stockout SKUs", "Score Status", "Notes"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    demo = {
        "S01": (1.8, 1.2, 6.1, 4.3, 2), "S02": (3.4, 2.8, 7.2, 4.0, 5),
        "S03": (2.1, 0.9, 8.4, 4.2, 1), "S04": (1.5, 1.1, 5.8, 4.4, 0),
        "S05": (4.2, 3.1, 9.1, 3.9, 7), "S06": (2.8, 1.6, 6.9, 4.1, 3),
        "S07": (1.2, 0.8, 4.9, 4.5, 0), "S08": (2.5, 2.2, 7.8, 4.0, 4),
        "S09": (1.9, 1.4, 6.4, 4.3, 2), "S10": (2.2, 1.0, 5.2, 4.6, 1),
    }
    for i, s in enumerate(sellers):
        r = 2 + i
        sid = s["seller_id"]
        c1, c2, c3, rt, sk = demo.get(sid, (2, 1, 6, 4.2, 0))
        ws.cell(row=r, column=1, value=sid)
        ws.cell(row=r, column=2, value=c1).number_format = "0.0"
        ws.cell(row=r, column=3, value=c2).number_format = "0.0"
        ws.cell(row=r, column=4, value=c3).number_format = "0.0"
        ws.cell(row=r, column=5, value=rt).number_format = "0.0"
        ws.cell(row=r, column=6, value=sk)
        ws.cell(row=r, column=7, value=f'=IF(OR(B{r}>2.5,C{r}>2,D{r}>8,E{r}<4),"🔴 RED","✅ GREEN")')
        ws.cell(row=r, column=8, value="sample data — real KPIs API se aayenge")
    ws.conditional_formatting.add(f"B2:B{len(sellers)+1}",
        CellIsRule(operator="greaterThan", formula=["2.5"], fill=PatternFill("solid", fgColor=RED)))
    ws.conditional_formatting.add(f"C2:C{len(sellers)+1}",
        CellIsRule(operator="greaterThan", formula=["2"], fill=PatternFill("solid", fgColor=RED)))
    ws.conditional_formatting.add(f"D2:D{len(sellers)+1}",
        CellIsRule(operator="greaterThan", formula=["8"], fill=PatternFill("solid", fgColor=RED)))
    ws.conditional_formatting.add(f"E2:E{len(sellers)+1}",
        CellIsRule(operator="lessThan", formula=["4"], fill=PatternFill("solid", fgColor=RED)))
    set_widths(ws, [9, 15, 13, 13, 9, 13, 14, 34])

    # ── 5. PNL-MONTHLY ───────────────────────────────────────
    ws = wb.create_sheet("PNL-MONTHLY")
    cols = ["Month", "Total Net GMV (₹)", "Total Aapka (₹)", "System Costs (₹)", "NET PROFIT (₹)", "Avg Rate %"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    for i in range(6):
        r = 2 + i
        ws.cell(row=r, column=1, value=f"=IF(DAILY-LOG!A{2+40*i}=\"\",\"\",TEXT(DATE(2026,{1+i},1),\"MMM YYYY\"))")
        ws.cell(row=r, column=2, value=f"=SUMIF(DAILY-LOG!A:A,A{r},DAILY-LOG!G:G)").number_format = "₹#,##0"
        ws.cell(row=r, column=3, value=f"=SUMIF(DAILY-LOG!A:A,A{r},DAILY-LOG!I:I)").number_format = "₹#,##0"
        ws.cell(row=r, column=4, value=5000).number_format = "₹#,##0"
        ws.cell(row=r, column=5, value=f"=C{r}-D{r}").number_format = "₹#,##0"
        ws.cell(row=r, column=6, value=f"=IF(B{r}=0,0,C{r}/B{r}*100)").number_format = "0.0"
    set_widths(ws, [14, 18, 17, 16, 16, 12])

    # ── 6. COSTS ─────────────────────────────────────────────
    ws = wb.create_sheet("COSTS")
    cols = ["Item", "Provider", "₹/Month", "Notes"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    for item in [
        ("Server (VPS)", "Oracle Cloud Always Free", 0, "A1 ARM 4 OCPU/24GB — free forever"),
        ("Automation (n8n)", "Self-hosted Docker", 0, "MIT/fair-code — free internal use"),
        ("AI (LLM)", "Google Gemini API free tier", 0, "~₹415 upgrade optional (OpenAI)"),
        ("Interface", "Telegram bot", 0, "Free"),
        ("Backup", "Google Drive (rclone)", 0, "15GB free"),
        ("WhatsApp (Phase 2)", "WATI/Interakt", 0, "Free tiers available"),
    ]:
        ws.append([*item])
    ws.append(["TOTAL", "", "=SUM(C2:C7)", "FREE STACK"])
    ws.cell(row=8, column=1).font = Font(bold=True)
    ws.cell(row=8, column=3).number_format = "₹#,##0"
    set_widths(ws, [20, 28, 12, 40])

    # ── 7. INCIDENTS ─────────────────────────────────────────
    ws = wb.create_sheet("INCIDENTS")
    cols = ["Date", "Severity", "Agent", "Issue", "Action Needed", "Status", "Resolved Date"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    ws.append(["(sample)", "P1", "B5 SETTLEMENT", "S03 May settlement mein ₹4,300 extra commission", "Dispute draft approve karo", "OPEN", ""])
    ws.conditional_formatting.add("B2:B200", CellIsRule(operator="equal", formula=['"P0"'], fill=PatternFill("solid", fgColor=RED)))
    ws.conditional_formatting.add("B2:B200", CellIsRule(operator="equal", formula=['"P1"'], fill=PatternFill("solid", fgColor=YELLOW)))
    set_widths(ws, [12, 10, 18, 46, 34, 12, 14])

    # ── 8. TASKS ─────────────────────────────────────────────
    ws = wb.create_sheet("TASKS")
    cols = ["ID", "Priority", "Task", "Spec/Acceptance Criteria", "Assigned", "Status", "Verify Result"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    for t in [
        ("T-001", "P2", "Listing auto-publish on karo (pilot S01, S04)", "2 hafte manual approval se koi QC reject na ho", "CODER", "ASSIGNED", ""),
        ("T-002", "P3", "S02 rate confirm karo (4% tentative)", "Seller se written confirm milna", "CRM", "OPEN", ""),
    ]:
        ws.append(list(t))
    set_widths(ws, [8, 10, 44, 40, 10, 14, 16])

    # ── 9. SCHEDULE ──────────────────────────────────────────
    ws = wb.create_sheet("SCHEDULE")
    cols = ["Time", "Agent", "Kaam", "Frequency"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    for srow in sched:
        ws.append([srow.get("time", ""), srow.get("agent", ""), srow.get("what", ""), srow.get("frequency", "")])
    set_widths(ws, [12, 26, 60, 12])

    wb.save(OUT)
    print(f"✅ Dashboard saved → {OUT}")
    print(f"   Sheets: {wb.sheetnames}")


if __name__ == "__main__":
    main()
