#!/usr/bin/env python3
"""Which AgentMail inbox can we actually SEND the CIIE correction FROM?

The draft note says 'Send from: sales@studex-group.com (the inbox they were
contacted from)'. Two things need checking:
  1. Does sales@studex-group.com exist as an inbox on EITHER AgentMail account?
  2. Which inbox did the CIIE sends ACTUALLY come from?

The 29 CIIE emails came from project-2571-studex-agent-2077@agentmail.to
(ciie-nurture/src/agentmail-client.ts FROM_INBOX). If the correction goes from
a different address than the false email, buyers see an unknown sender
apologising - which reads as phishing, and undermines the correction.

Usage: python3 scripts/check-send-inbox.py
"""
import json
import urllib.request
import urllib.error

BASE = "https://api.agentmail.to/v0"
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

_live = live_agentmail_keys()
KEYS = {"main": _live[0], "ciie-nurture": _live[-1], "general": _live[-1]}
CANDIDATES = [
    "sales@studex-group.com",
    "project-2571-studex-agent-2077@agentmail.to",
    "robusca.romanov@studex-group.com",
    "studex-2571@agentmail.to",
    "t.ramaphosa@agentmail.to",
]


def get(path, key):
    r = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(r, timeout=60) as x:
        return json.load(x)


def main():
    print("=== inboxes listed per account ===")
    listed = {}
    for name, key in KEYS.items():
        try:
            ibs = [i.get("inbox_id") for i in get("/inboxes", key).get("inboxes", [])]
        except Exception as e:
            print(f"  {name:14} !! {e}")
            ibs = []
        listed[name] = ibs
        print(f"  {name:14} {len(ibs):>2}  {ibs}")

    print("\n=== can we READ each candidate inbox? ===")
    readable = {}
    for cand in CANDIDATES:
        row = []
        for name, key in KEYS.items():
            try:
                m = get(f"/inboxes/{cand}/messages?limit=1", key).get("messages", [])
                row.append(f"{name}=OK({len(m)})")
                readable.setdefault(cand, []).append(name)
            except urllib.error.HTTPError as e:
                row.append(f"{name}={e.code}")
            except Exception as e:
                row.append(f"{name}=ERR")
        print(f"  {cand:42} {row}")

    print("\n=== VERDICT ===")
    for cand in CANDIDATES:
        accs = readable.get(cand, [])
        print(f"  {cand:42} readable via: {accs if accs else 'NONE'}")

    sales = readable.get("sales@studex-group.com", [])
    ciie = readable.get("project-2571-studex-agent-2077@agentmail.to", [])
    print()
    if not sales:
        print("  !! sales@studex-group.com is NOT readable on any account.")
        print("     -> the draft note's 'Send from:' line names an inbox we cannot send from.")
    if ciie:
        print(f"  -> the correction MUST go from project-2571-studex-agent-2077@agentmail.to "
              f"({', '.join(ciie)}) — the same address the false email came from.")


if __name__ == "__main__":
    main()
