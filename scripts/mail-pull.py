#!/usr/bin/env python3
"""Pull one message body from a watched inbox and flag risky claims."""
import json, sys, urllib.request, urllib.error

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEY = live_agentmail_keys()[0]
INBOX = sys.argv[1]
SUBJECT_MATCH = sys.argv[2] if len(sys.argv) > 2 else ""

FORBIDDEN = [
    "booth", "Hall B", "pavilion", "PROWTC", "Rainforest Alliance",
    "attend", "meeting", "Luckin", "hall",
]


def get(url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


d = get(f"https://api.agentmail.to/v0/inboxes/{INBOX}/messages?limit=40")
for m in d.get("messages", []):
    subj = (m.get("subject") or "")
    if SUBJECT_MATCH and SUBJECT_MATCH.lower() not in subj.lower():
        continue
    body = m.get("text") or m.get("preview") or ""
    print("=" * 70)
    print(m.get("timestamp"), "|", subj)
    print("from:", m.get("from"), "-> to:", m.get("to"))
    print("-" * 70)
    print(body[:2500])
    hits = [w for w in FORBIDDEN if w.lower() in (subj + " " + body).lower()]
    print("\n>>> RISK WORDS:", hits)
