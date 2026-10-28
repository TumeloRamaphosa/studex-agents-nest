#!/usr/bin/env python3
"""Verify the CIIE outreach breach count independently of any prior claim.

THE CLAIM (outbound-corrections/ciie-correction-recipients.json):
  29 emails to 12 recipients, sent 2026-09-25 .. 2026-10-03, by TWO engines:
    send-sequence.js  -> 23 emails / 9 recipients  (source: ciie-nurture/prospects.json)
    dist/cli.js        ->  6 emails / 3 recipients  (source: ciie-nurture/data/state.json)
  The 3 state.json-only leads were previously uncounted, so the old "21 emails to 9 buyers"
  figure was wrong.

THREE WAYS A NAIVE VERIFICATION REPORTS A FALSE ZERO (all of which bit us):
  1. WRONG ACCOUNT.  The CIIE sender is `project-2571-studex-agent-2077@agentmail.to`,
     which lives on a DIFFERENT AgentMail account. It 404s under the main key and is
     NOT in GET /v0/inboxes for the main key. Sweeping one account cannot see the
     other. -> This script tries EVERY live key against every inbox.
  2. TRUNCATION.  `GET /v0/inboxes/{id}/messages?limit=N` silently truncates at N,
     newest-first. A limit=200 sweep on a 392-message inbox never sees the CIIE
     window at all. -> limit=1000, and we ASSERT the count is below the limit.
  3. FIELD NAMES.  The message schema exposes `sent_at`/`from`/`to` and the
     older `timestamp`/`from_`/`to` variants. We read both, so a renamed field
     cannot silently zero the count.

A checker that reports "0" because it looked in the wrong place is worse than
no checker — it manufactures false reassurance.

Usage: python3 scripts/verify-ciii-breach-count.py
"""
import json
import sys
import pathlib
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys, assert_not_truncated

KEYS = live_agentmail_keys()
BASE = "https://api.agentmail.to/v0"
LIMIT = 1000

# Inboxes the list endpoint does not expose but that we know exist.
EXTRA_INBOXES = ["project-2571-studex-agent-2077@agentmail.to", "studex-2571@agentmail.to"]

# The 12 recipients named in the correction-recipients file.
TARGETS = [
    "buyer@luckincoffee.com",
    "procurement.cn@timhortons.com",
    "purchasing@pacificcoffee.com",
    "food.import@jd.com",
    "info@smartsquare.ae",
    "info@dhiranifoodstuff.ae",
    "trade@bmc-overseas.ae",
    "green@coffeeplanet.ae",
    "info@thirdlinecoffee.com",
    "li.wei@luckincoffee.cn",
    "c.jie@timhortonschina.com",
    "sarah@eurotrading.co.za",
]


def get(path, key):
    """Return (status, payload). Never raises on HTTP error."""
    r = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(r, timeout=90) as x:
            return x.status, json.load(x)
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)[:90]}


def field(m, *names):
    for n in names:
        v = m.get(n)
        if v:
            return v
    return ""


def main():
    # 1. Collect every inbox any live key can list, plus the known-but-unlisted ones.
    inbox_key = {}
    for k in KEYS:
        code, d = get("/inboxes", k)
        if code != 200:
            print(f"  !! key {k[:12]}... could not list inboxes (HTTP {code})")
            continue
        for ib in d.get("inboxes", []):
            iid = ib.get("inbox_id") or ib.get("id")
            if iid and iid not in inbox_key:
                inbox_key[iid] = (ib.get("address") or iid, k)

    print(f"=== {len(inbox_key)} inboxes from {len(KEYS)} live keys "
          f"@ limit={LIMIT} (asserted untruncated) ===\n")

    # 2. For every known inbox, try EVERY live key until one answers.
    hits = {t: [] for t in TARGETS}
    total_msgs = 0
    unreadable = []
    for extra in EXTRA_INBOXES:
        if extra not in inbox_key:
            inbox_key[extra] = (extra, None)

    for iid, (addr, preferred) in inbox_key.items():
        order = ([preferred] if preferred else []) + [k for k in KEYS if k != preferred]
        msgs = None
        for k in order:
            code, d = get(f"/inboxes/{iid}/messages?limit={LIMIT}", k)
            if code == 200:
                msgs = d.get("messages") or d.get("items") or []
                break
        if msgs is None:
            unreadable.append(addr)
            print(f"  !! {addr}: no live key could read this inbox")
            continue
        # A truncated sweep does not error - it just returns a smaller world.
        assert_not_truncated(len(msgs), LIMIT)
        total_msgs += len(msgs)
        found = 0
        for m in msgs:
            to = str(field(m, "to", "to_addresses", "recipients", "recipient"))
            ts = str(field(m, "sent_at", "timestamp", "created_at"))
            for t in TARGETS:
                if t in to:
                    hits[t].append({
                        "ts": ts,
                        "size": field(m, "size"),
                        "subject": field(m, "subject"),
                        "inbox": addr,
                    })
                    found += 1
        if found:
            print(f"  {addr}: {len(msgs)} msgs, {found} CIIE target send(s)")

    print(f"\ntotal messages swept: {total_msgs}")
    if unreadable:
        print(f"!! {len(unreadable)} inbox(es) unreadable by any live key: {unreadable}")

    print("\n=== PER-RECIPIENT ===")
    total = 0
    reached = 0
    for t in TARGETS:
        h = sorted(hits[t], key=lambda x: x["ts"] or "")
        total += len(h)
        if h:
            reached += 1
        print(f"  {len(h)}x  {t:34} {h[0]['ts'][:10] if h else '-'} .. {h[-1]['ts'][:10] if h else '-'}")
        for m in h:
            print(f"        {m['ts']}  {m['size']}B  {str(m['subject'])[:56]}")

    print("\n=== VERDICT ===")
    print(f"  recipients reached : {reached} / {len(TARGETS)}")
    print(f"  total CIIE emails  : {total}")
    claim = json.load(open("outbound-corrections/ciie-correction-recipients.json"))
    print(f"  claimed by file    : {claim['totalEmails']} emails to {claim['totalRecipients']} recipients")
    if total == claim["totalEmails"] and reached == claim["totalRecipients"]:
        print(f"  -> MATCH: the correction note's {claim['totalEmails']}/{claim['totalRecipients']} "
              "figures are confirmed independently.")
        return 0
    print("  -> MISMATCH: the correction note's figures need revising before it goes out.")
    print(f"     verified: {total} emails to {reached} recipients")
    return 1


if __name__ == "__main__":
    sys.exit(main())
