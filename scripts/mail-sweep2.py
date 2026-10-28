#!/usr/bin/env python3
import json, urllib.request

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

_live = live_agentmail_keys()
KEY = _live[0]
KEY2 = _live[-1]

def get(url, key=KEY):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

d = get("https://api.agentmail.to/v0/messages?limit=15")
print("no-filter keys:", list(d.keys()))
msgs = d.get("messages", [])
print("count", len(msgs))
for m in msgs:
    print(m.get("timestamp"), "|dir:", m.get("direction"), "|", m.get("inbox_id"), "|", (m.get("subject") or "")[:60])
    print("    from:", m.get("from"), "text:", ((m.get("preview") or m.get("text") or "")[:200]).replace("\n"," "))

print("\n=== per-inbox ===")
for ib in ["meat@studex-group.com","naledi-cmo@studex-group.com","t-ramaphosa-ceo@studex-group.com","sales@studex-group.com","info@studex-group.com","robusca.romanov@studex-group.com"]:
    dd = get(f"https://api.agentmail.to/v0/messages?inbox_id={ib}&limit=6")
    print(f"\n-- {ib}: {len(dd.get('messages',[]))}")
    for m in dd.get("messages", []):
        print("  ", m.get("timestamp"), m.get("direction"), "|", (m.get("subject") or "")[:60], "| from:", m.get("from"))
        print("      ", ((m.get("preview") or m.get("text") or "")[:250]).replace("\n"," "))

print("\n=== key2 inboxes ===")
for ib in ["t.ramaphosa@agentmail.to","project-2571-studex-agent-2077@agentmail.to","uglyrestaurant62@agentmail.to"]:
    dd = get(f"https://api.agentmail.to/v0/messages?inbox_id={ib}&limit=6", KEY2)
    print(f"\n-- {ib}: {len(dd.get('messages',[]))}")
    for m in dd.get("messages", []):
        print("  ", m.get("timestamp"), m.get("direction"), "|", (m.get("subject") or "")[:60], "| from:", m.get("from"))
        print("      ", ((m.get("preview") or m.get("text") or "")[:250]).replace("\n"," "))
