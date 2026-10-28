#!/usr/bin/env python3
"""
Studex AgentMail inbound sweep — CORRECTED 2026-10-22.

WHY THIS FILE EXISTS
--------------------
The old sweeps (scripts/mail-sweep2.py, scripts/mail-all.py) used:
    GET /v0/messages?inbox_id=...
That route **404s** on the AgentMail v0 API ("Route not found"). The old
scripts swallowed the exception and printed "0 messages", which reads
exactly like "no inbound mail" — a false negative. Every past heartbeat
that reported "0 external inbound" was actually reporting a 404.

The correct route is per-inbox:
    GET /v0/inboxes/{inbox_id}/messages?limit=N
and the inbox list is:
    GET /v0/inboxes

Usage:  python3 scripts/mail-sweep3.py
Exit 0 = sweep ran (errors are printed, not swallowed)
"""
import json, sys, urllib.request, urllib.error

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEYS = live_agentmail_keys()

# Inboxes that legitimately receive external (buyer/prospect) mail.
# The watch list is a SHARED source of truth (scripts/agentmail_watch.py) so the
# sweep and the badge-payment sweep can never drift apart - and so the
# documented unreachable inboxes are visible to both.
from agentmail_watch import WATCH  # noqa: E402


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf8", "replace")[:200]}
    except Exception as e:
        return "ERR", {"error": str(e)[:200]}


def main():
    seen_inboxes = {}
    for key in KEYS:
        code, d = get("https://api.agentmail.to/v0/inboxes", key)
        if code != 200:
            print(f"[key {key[:16]}…] /v0/inboxes -> {code} {d.get('error','')[:120]}")
            continue
        for ib in d.get("inboxes", []):
            iid = ib.get("inbox_id")
            if iid and iid not in seen_inboxes:
                seen_inboxes[iid] = key
        print(f"[key {key[:16]}…] {d.get('count')} inboxes")

    print("\nknown inboxes:")
    for iid in sorted(seen_inboxes):
        print("  ", iid, "<-- WATCH" if iid in WATCH else "")

    external = []
    print("\n--- recent messages ---")
    for iid, key in seen_inboxes.items():
        code, d = get(f"https://api.agentmail.to/v0/inboxes/{iid}/messages?limit=100", key)
        if code != 200:
            print(f"  {iid}: HTTP {code} {d.get('error','')[:100]}")
            continue
        msgs = d.get("messages", [])
        print(f"  {iid}: {len(msgs)}")
        for m in msgs:
            frm = str(m.get("from"))
            to = str(m.get("to"))
            subj = (m.get("subject") or "")[:70]
            print(f"    {m.get('timestamp')} | {subj}")
            print(f"       from: {frm[:110]}  to: {to[:110]}")
            if iid in WATCH and "tumelor001@gmail.com" not in frm and "@agentmail.to" not in frm and "@studex-group.com" not in frm:
                external.append((iid, m.get("timestamp"), frm, subj))

    print("\n=== EXTERNAL INBOUND (watched inboxes, non-self senders) ===")
    if external:
        for e in external:
            print("  *", e)
    else:
        print("  none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
