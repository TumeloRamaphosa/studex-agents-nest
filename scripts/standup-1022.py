import json, urllib.request, os, datetime, sys

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEYS = live_agentmail_keys()
INBOXES = [
    "meat@studex-group.com", "naledi-cmo@studex-group.com", "robusca.romanov@studex-group.com",
    "t-ramaphosa-ceo@studex-group.com", "info@studex-group.com", "sales@studex-group.com",
    "support.superagents@studex-group.com", "t.ramaphosa@agentmail.to",
    "project-2571-studex-agent-2077@agentmail.to", "uglyrestaurant62@agentmail.to",
    "healthyprocess394@agentmail.to", "studex-2571@agentmail.to",
    "tumoragencies@agentmail.to", "phiri@agentmail.to", "t.ramaphosa@agentmail.to",
]
BASE = "https://api.agentmail.to/v0"


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


since = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=30)
seen = {}
for key in KEYS:
    for inbox in INBOXES:
        try:
            data = get(f"{BASE}/inboxes/{inbox}/messages?limit=25", key)
        except Exception:
            continue
        msgs = data.get("messages", []) if isinstance(data, dict) else []
        for m in msgs:
            mid = m.get("message_id") or m.get("id")
            if mid in seen:
                continue
            ts = m.get("timestamp") or m.get("created_at") or ""
            seen[mid] = (inbox, ts, (m.get("subject") or "")[:80], m.get("from") or "", m.get("text") or m.get("preview") or "")
print(f"TOTAL MESSAGES SEEN: {len(seen)}")
print("--- messages newer than 30h ---")
for mid, (inbox, ts, subj, frm, txt) in sorted(seen.items(), key=lambda x: x[1][1]):
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        d = None
    if d and d >= since:
        print(f"[{ts}] inbox={inbox}\n  from={frm}\n  subj={subj}\n  body={txt[:300]}\n")
print("--- newest 8 overall ---")
for mid, (inbox, ts, subj, frm, txt) in sorted(seen.items(), key=lambda x: x[1][1], reverse=True)[:8]:
    print(f"[{ts}] {inbox} | {frm} | {subj}")
