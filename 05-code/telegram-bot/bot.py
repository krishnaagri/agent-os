"""
Flipkart Agent OS — TELEGRAM ASSISTANT BOT (Agent A: Aapka Interface)
=====================================================================
Aapka 24x7 personal window. Yeh koi AI chatbot nahi — yeh SYSTEM ka interface hai:
jo data agents/system bana rahe hain (output/, data/), usse aapke saamne pesh karta hai.

Commands:
  /start            — welcome + aapka chat id
  /status           — system health snapshot
  /income [date]    — aapka wallet (default: latest digest)
  /weekly           — 7-din per-seller breakdown
  /schedule         — aage ke scheduled runs
  /seller S01       — ek seller ka drill-down
  /update           — complete system update + recent incidents/tasks
  /add <request>    — naya feature/fix request → Management Agent queue
  /kill             — KILL SWITCH (sirf allowed chat ids)

Setup:
  1. pip install -r requirements.txt
  2. .env mein TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID + ALLOWED_CHAT_IDS
  3. python3 bot.py
"""
import csv
import datetime as dt
import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BASE = Path(__file__).resolve().parent.parent.parent  # flipkart-agent-os/
DATA = BASE / "data"
OUT = BASE / "output"
KILL_FILE = DATA / "KILL"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED = {x.strip() for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip()}


def authorized(update: Update) -> bool:
    return str(update.effective_chat.id) in ALLOWED or not ALLOWED  # dev mode: empty = allow all


# ────────────────────── DATA READERS ──────────────────────
def read_csv(p: Path):
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sellers():
    return {r["seller_id"].strip(): r for r in read_csv(DATA / "sellers.csv")}


def latest_digest():
    files = sorted(OUT.glob("digest-*.txt"))
    if not files:
        return None
    return files[-1].read_text(encoding="utf-8")


def last_lines(p: Path, n=8):
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    return lines[-n:]


# ────────────────────── HANDLERS ──────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Agent OS Assistant online.\n\n"
        "Commands:\n"
        "/status — system health\n"
        "/income — aapka wallet (latest digest)\n"
        "/weekly — 7-din breakdown\n"
        "/schedule — aage ke runs\n"
        "/seller S01 — seller drill-down\n"
        "/update — full system update\n"
        "/add <text> — naya request (Management queue)\n"
        "/kill — kill switch\n\n"
        f"✅ Aapka chat id: {update.effective_chat.id}\n(Isse .env ke TELEGRAM_CHAT_ID mein daalo)"
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    s = sellers()
    kill = "🛑 KILL SWITCH ON" if KILL_FILE.exists() else "🟢 Normal"
    inc = read_csv(DATA / "incidents.csv")
    open_inc = [i for i in inc if i.get("status", "OPEN").upper() in ("OPEN", "IN_PROGRESS")]
    tasks = read_csv(DATA / "tasks.csv")
    open_tasks = [t for t in tasks if t.get("status", "OPEN").upper() in ("OPEN", "IN_PROGRESS", "ASSIGNED")]
    lines = [
        f"🖥️ SYSTEM STATUS — {dt.datetime.now().strftime('%d %b %Y %H:%M')}",
        f"Mode: {kill}",
        f"Sellers onboard: {len(s)}",
        f"Open incidents: {len(open_inc)} (P0/P1: {sum(1 for i in open_inc if i.get('severity','') in ('P0','P1'))})",
        f"Open tasks (Coder/PM): {len(open_tasks)}",
    ]
    latest = latest_digest()
    if latest:
        lines.append("Latest digest: ✅ present")
    else:
        lines.append("Latest digest: ⚠️ abhi tak nahi bana")
    await update.message.reply_text("\n".join(lines))


async def cmd_income(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    d = ctx.args[0] if ctx.args else None
    if d:
        p = OUT / f"digest-{d}.txt"
        if p.exists():
            await update.message.reply_text(p.read_text(encoding="utf-8"))
            return
        await update.message.reply_text(f"Digest {d} nahi mila. Available: {[f.name for f in sorted(OUT.glob('digest-*.txt'))][-5:]}")
        return
    t = latest_digest()
    await update.message.reply_text(t or "Abhi koi digest nahi bana. Finance engine run karo.")


async def cmd_weekly(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    t = latest_weekly()
    await update.message.reply_text(t)


def latest_weekly():
    files = sorted(OUT.glob("weekly-*.txt"))
    return files[-1].read_text(encoding="utf-8") if files else "Weekly report abhi nahi bani."


async def cmd_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    rows = read_csv(DATA / "schedule.csv")
    if not rows:
        await update.message.reply_text("Schedule data nahi mila (data/schedule.csv).")
        return
    lines = ["📅 SCHEDULED RUNS:"]
    for r in rows:
        lines.append(f"• {r.get('time','?'):>7} {r.get('agent','?'):<28} {r.get('what','')}")
    await update.message.reply_text("\n".join(lines))


async def cmd_seller(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    sid = (ctx.args[0].upper() if ctx.args else "")
    s = sellers()
    if sid not in s:
        await update.message.reply_text(f"{sid} nahi mila. Available: {', '.join(s.keys())}")
        return
    r = s[sid]
    await update.message.reply_text(
        f"👤 {r.get('name','?')} ({sid})\n"
        f"Category: {r.get('category','?')}\n"
        f"Rate: {r.get('rate_pct','?')}% [{r.get('rate_status','?')}]\n"
        f"GMV target: ₹{r.get('monthly_gmv_target','?')}\n"
        f"Ad cap: ₹{r.get('ad_budget_cap_daily','?')}/day"
    )


async def cmd_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    parts = ["🔄 FULL SYSTEM UPDATE\n"]
    d = latest_digest()
    if d:
        parts.append("💰 LATEST FINANCE:\n" + d.split("\n🔔")[0] + "\n")
    inc = [i for i in read_csv(DATA / "incidents.csv") if i.get("status", "OPEN").upper() in ("OPEN", "IN_PROGRESS")][-5:]
    if inc:
        parts.append("🚨 OPEN INCIDENTS:\n" + "\n".join(
            f"• [{i.get('severity','?')}] {i.get('agent','?')}: {i.get('issue','?')}" for i in inc) + "\n")
    else:
        parts.append("✅ Koi open incident nahi\n")
    tasks = [t for t in read_csv(DATA / "tasks.csv") if t.get("status", "OPEN").upper() in ("OPEN", "IN_PROGRESS", "ASSIGNED")][-5:]
    if tasks:
        parts.append("📋 ACTIVE TASKS:\n" + "\n".join(
            f"• [{t.get('priority','?')}] {t.get('task','?')} ({t.get('status','?')})" for t in tasks) + "\n")
    cl = last_lines(BASE / "02-docs" / "CHANGELOG.md", 5)
    if cl:
        parts.append("📚 RECENT CHANGES:\n" + "\n".join("• " + c for c in cl))
    await update.message.reply_text("\n".join(parts))


async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    text = " ".join(ctx.args) if ctx.args else ""
    if not text:
        await update.message.reply_text("Usage: /add <aapki request>")
        return
    p = DATA / "inbox.csv"
    new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "request", "status"])
        w.writerow([dt.datetime.now().isoformat(timespec="seconds"), text, "OPEN"])
    await update.message.reply_text(
        f"✅ Request queue mein add ho gayi:\n\"{text}\"\n\n"
        "Management Agent ise next review mein spec bana ke Coder Agent ko dega. "
        "Progress ke liye /update karo."
    )


async def cmd_kill(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("⛔ Not authorized.")
        return
    if KILL_FILE.exists():
        KILL_FILE.unlink()
        await update.message.reply_text("🟢 KILL SWITCH off — system normal mode mein.")
    else:
        KILL_FILE.touch()
        await update.message.reply_text(
            "🛑 KILL SWITCH ON — saare execution agents freeze (monitoring-only).\n"
            "Wapas: /kill phir se, ya: rm data/KILL"
        )


def main():
    if not BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN missing — .env set karo (SETUP-GUIDE STEP 4)")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("income", cmd_income))
    app.add_handler(CommandHandler("weekly", cmd_weekly))
    app.add_handler(CommandHandler("schedule", cmd_schedule))
    app.add_handler(CommandHandler("seller", cmd_seller))
    app.add_handler(CommandHandler("update", cmd_update))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("kill", cmd_kill))
    print("🤖 Agent OS Assistant bot running... (Ctrl+C to stop)")
    app.run_polling()


if __name__ == "__main__":
    main()
