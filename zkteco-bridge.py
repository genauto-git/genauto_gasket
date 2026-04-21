#!/usr/bin/env python3
"""
ZKTeco ADMS → ERPNext HRMS Employee Checkin Bridge.

Reads incremental JSONL lines from /opt/eSSL-attlog/data/attendance.jsonl,
looks up Employee by attendance_device_id, POSTs to Employee Checkin API.
State (last byte offset) persisted in /var/lib/zkteco-bridge/state.json.

Run as systemd service — loops every POLL_INTERVAL seconds.
"""
from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# ────────────────────────────────────────────────────────
# Config (env-overrideable)
# ────────────────────────────────────────────────────────

ADMS_LOG = Path(os.environ.get("ADMS_LOG", "/opt/eSSL-attlog/data/attendance.jsonl"))
STATE_FILE = Path(os.environ.get("STATE_FILE", "/var/lib/zkteco-bridge/state.json"))
ERP_BASE = os.environ.get("ERP_BASE", "http://127.0.0.1:9080")
ERP_HOST = os.environ.get("ERP_HOST", "erp.genautoindia.com")
API_KEY = os.environ["ERP_API_KEY"]
API_SECRET = os.environ["ERP_API_SECRET"]
DEVICE_SN = os.environ.get("DEVICE_SN", "QJT3253600356")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

# VerifyType → verification text for Employee Checkin.device_id field
VERIFY_MAP = {
    "0": "Password",
    "1": "Fingerprint",
    "4": "Card",
    "15": "Face",
    "20": "Face+Fingerprint",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("zkteco-bridge")

_running = True


def _on_signal(signum, _frame):
    global _running
    log.info("Received signal %s, stopping…", signum)
    _running = False


signal.signal(signal.SIGTERM, _on_signal)
signal.signal(signal.SIGINT, _on_signal)


# ────────────────────────────────────────────────────────
# State persistence
# ────────────────────────────────────────────────────────


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as e:
            log.warning("Could not parse state file: %s — starting fresh", e)
    return {"offset": 0, "last_employee_cache_refresh": 0}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ────────────────────────────────────────────────────────
# Employee lookup cache (device_id → Employee name)
# ────────────────────────────────────────────────────────

_employee_cache: dict[str, str] = {}


def refresh_employee_cache(session: requests.Session) -> None:
    global _employee_cache
    url = f"{ERP_BASE}/api/method/frappe.client.get_list"
    params = {
        "doctype": "Employee",
        "fields": '["name","attendance_device_id"]',
        "filters": '[["status","=","Active"],["attendance_device_id","is","set"]]',
        "limit_page_length": 0,
    }
    r = session.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("message", [])
    _employee_cache = {e["attendance_device_id"]: e["name"] for e in data if e.get("attendance_device_id")}
    log.info("Employee cache refreshed: %d entries", len(_employee_cache))


# ────────────────────────────────────────────────────────
# Checkin POST
# ────────────────────────────────────────────────────────


def post_checkin(session: requests.Session, employee: str, record: dict) -> bool:
    """POST an Employee Checkin. Returns True if created (or idempotent duplicate)."""
    url = f"{ERP_BASE}/api/resource/Employee Checkin"

    # timestamp format: ZKTeco sends "2026-04-21 16:19:12" → Frappe wants ISO
    ts = record["timestamp"].replace(" ", "T")
    verify_type = VERIFY_MAP.get(record.get("verify", ""), f"Type {record.get('verify','?')}")

    payload = {
        "employee": employee,
        "time": ts,
        "log_type": "",  # empty — Frappe Auto-Attendance determines from shift rules
        "device_id": record.get("sn", DEVICE_SN),
        "skip_auto_attendance": 0,
    }

    r = session.post(url, json=payload, timeout=10)
    if r.status_code in (200, 201):
        return True
    # Duplicate (unique index on employee+time+log_type) — treat as success
    if r.status_code == 409 or (r.status_code == 417 and "Duplicate" in r.text):
        return True
    # Other errors
    if r.status_code == 417 and "already has a log" in r.text.lower():
        return True
    log.warning("Checkin POST failed for %s @ %s — %s %s",
                employee, ts, r.status_code, r.text[:200])
    return False


# ────────────────────────────────────────────────────────
# Main loop
# ────────────────────────────────────────────────────────


def sync_tick(session: requests.Session, state: dict) -> int:
    """Read new lines from JSONL, push to ERPNext. Returns count synced."""
    if not ADMS_LOG.exists():
        return 0

    size = ADMS_LOG.stat().st_size
    offset = state.get("offset", 0)

    # File rotated/truncated — reset
    if offset > size:
        log.warning("File truncated (offset %d > size %d) — resetting", offset, size)
        offset = 0

    if offset >= size:
        return 0

    # Refresh employee cache every 10 minutes
    now = time.time()
    if now - state.get("last_employee_cache_refresh", 0) > 600:
        try:
            refresh_employee_cache(session)
            state["last_employee_cache_refresh"] = now
        except Exception as e:
            log.warning("Employee cache refresh failed: %s", e)

    synced = skipped = errors = 0
    with ADMS_LOG.open("r") as f:
        f.seek(offset)
        while _running:
            line = f.readline()
            if not line:
                # EOF
                offset = f.tell()
                break
            stripped = line.strip()
            if not stripped:
                offset = f.tell()
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                errors += 1
                offset = f.tell()
                continue

            user_id = record.get("user_id", "")
            employee = _employee_cache.get(user_id)
            if not employee:
                log.debug("No employee for user_id=%s — skipped", user_id)
                skipped += 1
                offset = f.tell()
            else:
                if post_checkin(session, employee, record):
                    synced += 1
                    offset = f.tell()
                else:
                    errors += 1
                    # Don't advance offset on error — retry next tick
                    break

    state["offset"] = offset
    save_state(state)

    if synced or skipped or errors:
        log.info("Tick: synced=%d skipped=%d errors=%d offset=%d/%d",
                 synced, skipped, errors, offset, size)
    return synced


def main():
    # Session with auth headers
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Host": ERP_HOST,
        "Content-Type": "application/json",
    })

    state = load_state()
    log.info("Starting zkteco-bridge — ADMS=%s ERP=%s Host=%s offset=%d",
             ADMS_LOG, ERP_BASE, ERP_HOST, state.get("offset", 0))

    # Initial cache load
    try:
        refresh_employee_cache(session)
        state["last_employee_cache_refresh"] = time.time()
    except Exception as e:
        log.error("Initial cache load failed: %s", e)
        sys.exit(1)

    while _running:
        try:
            sync_tick(session, state)
        except requests.exceptions.RequestException as e:
            log.warning("Network error in tick: %s", e)
        except Exception as e:
            log.exception("Unexpected error in tick: %s", e)

        # Sleep but wake up on signal
        for _ in range(POLL_INTERVAL):
            if not _running:
                break
            time.sleep(1)

    log.info("Stopped cleanly. Last offset: %d", state.get("offset", 0))


if __name__ == "__main__":
    main()
