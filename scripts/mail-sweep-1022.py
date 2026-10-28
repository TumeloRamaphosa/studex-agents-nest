#!/usr/bin/env python3
import json, urllib.request, urllib.parse, sys

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEYS = live_agentmail_keys()

def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

# gather all inboxes across keys
seen = {}
for k in KEYS:
    d = get("https://api.agentmail.to/v0/inboxes?limit=50", k)
    for i in d.get("inboxes", []):
        seen[i["email"]] = i.get("display_name", "")
print("INBOXES:", len(seen))
for e in seen: print("  ", e)

print("\n=== RECENT MESSAGES (last 12 per key, all inboxes) ===")
for k in KEYS:
    d = get("https://api.agentmail.to/v0/messages?limit=12&direction=incoming", k)
    msgs = d.get("messages", [])
    print(f"\n-- key {k[:16]} : {len(msgs)} recent incoming")
    for m in msgs:
        print("  ", m.get("timestamp"), "|", m.get("inbox_id"), "|", (m.get("subject") or "")[:70])
        print("      from:", m.get("from"), "-> to:", m.get("to"))
        body = (m.get("preview") or m.get("text") or "")[:300].replace("\n", " ")
        print("      ", body)
