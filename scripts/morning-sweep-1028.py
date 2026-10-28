#!/usr/bin/env python3
"""Morning nudge inbox sweep for 2026-10-28."""
import json, sys, pathlib, urllib.request, urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEYS = live_agentmail_keys()
print("live keys:", len(KEYS))

INBOXES = [
    "meat@studex-group.com",
    "naledi-cmo@studex-group.com",
    "t-ramaphosa-ceo@studex-group.com",
    "sales@studex-group.com",
    "info@studex-group.com",
    "support.superagents@studex-group.com",
]


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


for inbox in INBOXES:
    got = False
    for key in KEYS:
        try:
            d = get(f"https://api.agentmail.to/v0/inboxes/{inbox}/messages?limit=15", key)
        except urllib.error.HTTPError as e:
            continue
        except Exception as e:
            print(f"{inbox}: ERROR {e}")
            break
        msgs = d.get("messages", [])
        print("=" * 72)
        print(f"INBOX {inbox} -> {len(msgs)} messages (last 15)")
        for m in msgs[:8]:
            print(f"  - {m.get('timestamp')} | {(m.get('subject') or '')[:80]} | from={m.get('from')}")
        got = True
        break
    if not got:
        print(f"{inbox}: 404 / unreachable on all live keys")
