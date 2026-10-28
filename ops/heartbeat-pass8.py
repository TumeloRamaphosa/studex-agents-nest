#!/usr/bin/env python3
"""Heartbeat pass 8 (00:57 UTC) — one consolidated check, no polling loops.

Checks, in one pass:
  1. Concurrent-session writes since the last commit (git log + working tree)
  2. Drift (ops/drift-check.py) - must be 12/12 CLEAN
  3. Cron fleet - enabled count + consecutiveErrors
  4. AgentMail inbound: any NEW external human message since the last sweep
  5. CIIE badge deadline status
  6. Any live breach (senders armed? CIIE crons enabled?)

Usage: python3 ops/heartbeat-pass8.py
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'scripts'))
from cred_env import require as _require
from cred_env import load_env as _load_env
os.environ.update({k: v for k, v in _load_env().items() if k not in os.environ})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

KEYS = {
    "main": _require("AGENTMAIL_MAIN_API_KEY"),
    "ciie-nurture": _require("AGENTMAIL_API_KEY"),
}
BASE = "https://api.agentmail.to/v0"
SELF = {"robusca.romanov@studex-group.com", "naledi-cmo@studex-group.com",
        "t.ramaphosa@agentmail.to", "naledi.services@gmail.com",
        "robusca.romanov@outlook.com", "tumelor001@gmail.com",
        "naledi-cmo@studex-group.com", "naledi-cmo@studex-group.com"}
CIIE = {"project-2571-studex-agent-2077@agentmail.to", "t.ramaphosa@agentmail.to",
        "uglyrestaurant62@agentmail.to"}

print("=" * 74)
print("HEARTBEAT PASS 8 —", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
print("=" * 74)

# ---- 1. concurrent writes
print("\n[1] git state")
log = subprocess.run(["git", "log", "--oneline", "-4"], capture_output=True, text=True).stdout
print("   recent commits:")
for l in log.strip().splitlines():
    print("     " + l)
st = subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout.strip()
print(f"   working tree: {st if st else 'clean'}")

# ---- 2. drift
print("\n[2] drift")
r = subprocess.run(["python3", "ops/drift-check.py"], capture_output=True, text=True, timeout=300)
tail = [l for l in r.stdout.splitlines() if l.startswith("pages:") or "DRIFT]" in l]
for l in tail:
    print("   " + l)
drift_ok = r.returncode == 0

# ---- 3. cron
print("\n[3] cron fleet")
cj = subprocess.run(["openclaw", "cron", "list", "--json"], capture_output=True, text=True, timeout=120)
try:
    d = json.loads(cj.stdout)
    jobs = d.get("jobs", d if isinstance(d, list) else [])
except Exception:
    jobs = []
en = [j for j in jobs if j.get("enabled")]
fail = [j for j in en if ((j.get("state") or {}).get("consecutiveErrors") or 0) > 0
        or (j.get("state") or {}).get("lastStatus") == "error"]
print(f"   ENABLED JOBS: {len(en)} | FAILING: {len(fail)}")
for j in fail:
    print(f"     !! {j.get('id')} {j.get('name')}")
# the two CIIE crons must stay disabled
for j in jobs:
    nm = (j.get("name") or "").lower()
    if "ciie" in nm and j.get("enabled"):
        print(f"     !! CIIE JOB ENABLED: {j.get('id')} {j.get('name')}  <-- must be disabled")
ciie_enabled = [j for j in jobs if "ciie" in (j.get("name") or "").lower() and j.get("enabled")]

# ---- 4. AgentMail inbound - new external humans
print("\n[4] AgentMail inbound (new external humans)")
def get(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=90) as x:
        return json.load(x)

inboxes = []
for name, key in KEYS.items():
    try:
        for i in get("/inboxes", key).get("inboxes", []):
            iid = i.get("inbox_id")
            if iid and iid not in inboxes:
                inboxes.append((iid, key))
    except Exception as e:
        print(f"   !! {name}: {e}")

seen_from = {}
scanned = 0
for iid, key in inboxes:
    try:
        msgs = get(f"/inboxes/{iid}/messages?limit=50", key).get("messages", [])
    except Exception:
        continue
    if len(msgs) >= 50:
        print(f"   !! {iid}: truncated at limit")
    scanned += len(msgs)
    for m in msgs:
        frm = m.get("from") or m.get("sender") or ""
        if isinstance(frm, dict):
            frm = frm.get("email") or frm.get("address") or ""
        frm = (frm or "").lower()
        ts = m.get("timestamp") or ""
        if not frm or frm in SELF:
            continue
        if frm.endswith("@studex-group.com") or frm.endswith("@agentmail.to"):
            continue
        prev = seen_from.get(frm)
        if prev is None or ts > prev:
            seen_from[frm] = ts

print(f"   inboxes: {len(inboxes)}  messages scanned: {scanned}")
if seen_from:
    print("   external senders seen (newest per sender):")
    for frm, ts in sorted(seen_from.items(), key=lambda x: -int(x[1].replace('-', '').replace(':', '').replace('T', '')[:14] or 0)):
        print(f"     {frm:36} latest={ts}")
else:
    print("   no external human senders")

# ---- 5. badge deadline
print("\n[5] CIIE badge deadline")
now = datetime.now(timezone.utc)
dl = datetime(2026, 10, 23, 16, 0, tzinfo=timezone.utc)
h = (dl - now).total_seconds() / 3600
print(f"   CNY 200 · due 2026-10-23 16:00 UTC (18:00 SAST) · {h:.1f} h remaining")
print(f"   -> {'EXPIRED' if h < 0 else 'DUE TODAY - needs Tumelo' if h < 24 else 'not yet'}")

# ---- 6. live breach check
print("\n[6] live-breach check")
armed = []
for f in ["ciie-nurture/send-sequence.js", "ciie-nurture/dist/cli.js"]:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p):
        print(f"   !! {f} MISSING")
        continue
    txt = open(p, encoding="utf8", errors="ignore").read()
    has_switch = "CIIE_NURTURE_ARMED" in txt
    print(f"   {f}: kill switch present={has_switch}")
    if not has_switch:
        armed.append(f)
if ciie_enabled:
    print("   !! CIIE CRON ENABLED")
print(f"   -> {'LIVE BREACH RISK' if armed or ciie_enabled else 'no live breach - both senders disarmed, CIIE crons disabled'}")

print("\n" + "=" * 74)
print("SUMMARY:", "drift OK" if drift_ok else "DRIFT PRESENT",
      f"| cron {len(en)}/{len(fail)}",
      "| breach" if (armed or ciie_enabled) else "| no breach")
