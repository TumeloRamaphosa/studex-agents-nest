#!/usr/bin/env python3
import json, urllib.request, urllib.error

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

_live = live_agentmail_keys()
KEYS = {
    "AGENTMAIL_MAIN_API_KEY": _live[0],
    "AGENTMAIL_API_KEY": _live[1],
}
def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

rows = []
for key, boxes in KEYS.items():
    for ib in boxes:
        d = get(f"https://api.agentmail.to/v0/inboxes/{ib}/messages?limit=40", key)
        for m in d.get("messages", []):
            ts = m.get("timestamp") or ""
            if ts >= "2026-10-19":
                rows.append((ts, ib, (m.get("subject") or "")[:65], (m.get("from") or "")[:45], (m.get("to") or ""), (m.get("preview") or m.get("text") or "")[:400].replace("\n"," ")))
rows.sort(reverse=True)
print("MESSAGES SINCE 2026-10-19:", len(rows))
for r in rows:
    print(f"\n{r[0]} | {r[1]}\n   subj: {r[2]}\n   from: {r[3]} -> {r[4]}\n   {r[5][:300]}")
