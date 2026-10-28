#!/usr/bin/env python3
"""What did the concurrent session find? (badge payment + breach status)
Plus a PROPER non-truncated inbound sweep — my pass-8 script used limit=50 and
flagged 3 inboxes as truncated, which is the mistake I documented at pass 7.

Usage: python3 ops/heartbeat-pass8b.py
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

print("=== concurrent commits 301dd640 / cccef31e ===")
for c in ["301dd640", "cccef31e"]:
    r = subprocess.run(["git", "show", "--stat", "--format=%h %s%n%b", c],
                       capture_output=True, text=True)
    print(r.stdout[:1400])
    print("-" * 70)

KEYS = {
    "main": _require("AGENTMAIL_MAIN_API_KEY"),
    "ciie-nurture": _require("AGENTMAIL_API_KEY"),
}
BASE = "https://api.agentmail.to/v0"
SELF_SUFFIX = ("@studex-group.com", "@agentmail.to")


def get(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=120) as x:
        return json.load(x)


print("\n=== NON-TRUNCATED inbound sweep (limit=1000, assert count < limit) ===")
inboxes = []
for name, key in KEYS.items():
    try:
        for i in get("/inboxes", key).get("inboxes", []):
            iid = i.get("inbox_id")
            if iid and iid not in inboxes:
                inboxes.append((iid, key))
    except Exception as e:
        print(f"  !! {name}: {e}")

CANDIDATES = ["kfschof@gmail.com", "rz@sc-ee.com", "obelyakova@sv-tech.ru",
              "africabiz.r@yandex.com"]
found = {}
all_external = {}
truncated = []
for iid, key in inboxes:
    try:
        msgs = get(f"/inboxes/{iid}/messages?limit=1000", key).get("messages", [])
    except Exception:
        continue
    if len(msgs) >= 1000:
        truncated.append(iid)
    for m in msgs:
        frm = m.get("from") or m.get("sender") or ""
        if isinstance(frm, dict):
            frm = frm.get("email") or frm.get("address") or ""
        frm = (frm or "").strip().lower()
        ts = m.get("timestamp") or ""
        subject = m.get("subject") or ""
        if not frm:
            continue
        if not frm.endswith(SELF_SUFFIX) and frm not in ("no-reply@mail.privy.io",):
            if frm not in all_external or ts > all_external[frm][0]:
                all_external[frm] = (ts, subject, iid)
        for c in CANDIDATES:
            if c in frm:
                if c not in found or ts > found[c][0]:
                    found[c] = (ts, subject, iid, len(m.get("text") or m.get("preview") or ""))

print(f"  inboxes: {len(inboxes)}  truncated: {truncated if truncated else 'none'}")
print("\n  -- the 4 external leads (sent-side sweep) --")
for c in CANDIDATES:
    if c in found:
        ts, subj, iid, ln = found[c]
        print(f"    {c:26} latest={ts}  in={iid}  subj={subj[:56]!r}")
    else:
        print(f"    {c:26} NOT SEEN in any inbox (limit=1000, untruncated)")

print("\n  -- ALL external (non-studex) senders, newest first --")
def keyof(v):
    try:
        return int(v[0].replace("-", "").replace(":", "").replace("T", "")[:14])
    except Exception:
        return 0
for frm, (ts, subj, iid) in sorted(all_external.items(), key=lambda x: -keyof(x[1])):
    print(f"    {frm:34} {ts}  {subj[:48]!r}")

print("\n=== badge payment evidence check ===")
for iid, key in inboxes:
    try:
        msgs = get(f"/inboxes/{iid}/messages?limit=1000", key).get("messages", [])
    except Exception:
        continue
    for m in msgs:
        s = (m.get("subject") or "").lower()
        body = (m.get("text") or m.get("preview") or "").lower()
        if any(k in s or k in body for k in ["badge", "cnie", "ciie", "shanghai", "nec", "visitor pass", "ciie 2026"]):
            print(f"    {iid}  {m.get('timestamp')}  {m.get('subject')[:70]!r}")
