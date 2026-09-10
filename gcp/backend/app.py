"""FK Agent OS — FastAPI backend (v1: health/readiness/metrics + tenant pattern).
Kept intentionally tiny: e2-micro RAM budget. Agent APIs land here in Phase 2+."""
import json
import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request

START = time.time()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fk-backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("backend started | mongodb_uri_present=%s", bool(os.environ.get("MONGODB_URI")))
    yield
    log.info("backend shutting down gracefully")


app = FastAPI(title="FK Agent OS Backend", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    # v1: process up = ready. DB/external checks join in Phase 2.
    return {"status": "ready", "uptime_sec": round(time.time() - START, 1)}


@app.get("/metrics")
def metrics():
    mem = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                k, _, v = line.partition(":")
                if k in ("MemTotal", "MemAvailable"):
                    mem[k] = int(v.strip().split()[0])
    except Exception:
        pass
    return {
        "uptime_sec": round(time.time() - START, 1),
        "mem_total_kb": mem.get("MemTotal"),
        "mem_available_kb": mem.get("MemAvailable"),
        "pid": os.getpid(),
    }


# ── Multi-tenant pattern (spec §16) ─────────────────────────────────────────
# SELLER-FACING endpoints must resolve seller_id ONLY from the authenticated
# Telegram user mapping — never from a client-supplied id.
#
#   authenticated_user -> seller_mapping -> seller_id -> scoped query
#
# Example (when Mongo collections exist):
#   db.orders.find({"seller_id": authenticated_seller_id})
# NEVER: db.orders.find({}) for a seller-facing request.
def require_seller(x_user_id: str | None, x_seller_id: str | None) -> str:
    if not x_user_id:
        raise HTTPException(401, "missing authenticated user")
    # TODO Phase 2: map x_user_id -> seller_id from sellers collection
    # (validated mapping; x_seller_id is advisory/echo only).
    if x_seller_id:
        log.info("seller scoped request for user=%s seller=%s", x_user_id, x_seller_id)
        return x_seller_id
    raise HTTPException(403, "no seller mapping for user")


@app.get("/api/v1/seller/{seller_id}/ping")
def seller_ping(seller_id: str, x_user_id: str | None = Header(default=None)):
    sid = require_seller(x_user_id, seller_id)
    return {"seller_id": sid, "ping": "pong"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=10)
