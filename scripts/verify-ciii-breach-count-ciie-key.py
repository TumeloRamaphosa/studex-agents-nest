#!/usr/bin/env python3
"""Independently re-verify the CIIE outreach count using the ciie-nurture AgentMail key.

WHY A SEPARATE SCRIPT: scripts/verify-ciii-breach-count.py uses the MAIN key
(am_us_d7922...) and therefore sees ZERO CIIE sends - because the CIIE sender
inbox project-2571-studex-agent-2077@agentmail.to belongs to a DIFFERENT
AgentMail account and 404s for the main key. Its "0 / 12, MISMATCH" verdict is
an artefact of the wrong credential, not evidence that nothing was sent.

This script uses the ciie-nurture key (am_us_e4b30fcc...), asserts that the
message count is BELOW the limit (i.e. NOT truncated), and recounts from the
sent side.

Usage: python3 scripts/verify-ciii-breach-count-ciie-key.py
"""
import json
import urllib.request

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEY = live_agentmail_keys()[-1]
BASE = "https://api.agentmail.to/v0"
CIIE_INBOX = "project-2571-studex-agent-2077@agentmail.to"
LIMIT = 1000

TARGETS = [
    "buyer@luckincoffee.com", "procurement.cn@timhortons.com",
    "purchasing@pacificcoffee.com", "food.import@jd.com",
    "info@smartsquare.ae", "info@dhiranifoodstuff.ae",
    "trade@bmc-overseas.ae", "green@coffeeplanet.ae",
    "info@thirdlinecoffee.com", "li.wei@luckincoffee.cn",
    "c.jie@timhortonschina.com", "sarah@eurotrading.co.za",
]


def get(path):
    r = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(r, timeout=120) as x:
        return json.load(x)


def main():
    print(f"=== {CIIE_INBOX} (ciie-nurture key), limit={LIMIT} ===\n")
    try:
        msgs = get(f"/inboxes/{CIIE_INBOX}/messages?limit={LIMIT}").get("messages", [])
    except Exception as e:
        print(f"  !! {e}")
        return 1

    print(f"  messages returned: {len(msgs)}")
    if len(msgs) >= LIMIT:
        print(f"  !! TRUNCATED (count == limit) - raise the limit, this is not a finished sweep")
        return 1
    print("  not truncated (count < limit) -> this IS the full inbox\n")

    hits = {t: [] for t in TARGETS}
    other = 0
    for m in msgs:
        tgts = m.get("to") or m.get("targets") or []
        tgts = tgts if isinstance(tgts, list) else [tgts]
        tgts = [t.get("email") if isinstance(t, dict) else t for t in tgts]
        matched = False
        for t in TARGETS:
            if t in tgts:
                hits[t].append(m)
                matched = True
        if not matched:
            other += 1

    total = 0
    for t in TARGETS:
        n = len(hits[t])
        total += n
        print(f"  {t:36} {n}")
        for m in sorted(hits[t], key=lambda x: x.get("timestamp", "")):
            print(f"        {m.get('timestamp')}  {str(m.get('subject'))[:70]}")

    print(f"\n  RECIPIENTS REACHED : {sum(1 for t in TARGETS if hits[t])} / 12")
    print(f"  TOTAL CIIE EMAILS  : {total}")
    print(f"  other inbox traffic : {other}")
    print(f"  claimed in file     : 29 emails to 12 recipients")
    ok = total == 29 and sum(1 for t in TARGETS if hits[t]) == 12
    print(f"  -> {'MATCH - 29 emails / 12 recipients CONFIRMED' if ok else 'MISMATCH - file needs revising'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
