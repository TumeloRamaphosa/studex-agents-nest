#!/usr/bin/env python3
"""Find BLANK AgentMail sends — the defect that emailed two partners an empty message.

HOW TO READ THE API (learned 2026-10-22, this is easy to get wrong):

  GET /v0/inboxes/{id}/messages  returns a LIST. In that list:
    * `text` is NOT populated at all — it is absent for EVERY message, including
      ones that demonstrably have a body. So "text is empty" is NOT evidence of
      a blank email. That mistake produced a false alarm on 2026-10-22.
    * `preview` is populated for some messages but not others. Also unreliable.
    * `size` IS reliable. A real AgentMail message with a body is ~1200-32000
      bytes. A message that went out with a subject but no body lands at
      ~370-410 bytes (headers + subject only).
  GET /v0/inboxes/{id}/messages/{message_id}  -> HTTP 400 on this API.

SO: a blank send == size < 600 bytes. Use size. Nothing else.

Usage:
  python3 scripts/check-blank-sends.py              # all inboxes, since 2026-08-01
  python3 scripts/check-blank-sends.py --since 2026-09-01
  python3 scripts/check-blank-sends.py --external-only
"""
import argparse
import json
import urllib.request

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEY = live_agentmail_keys()[0]
BASE = "https://api.agentmail.to/v0"

# A message with a body is >= ~1200 bytes. Subject-and-headers-only is ~370-410.
BLANK_MAX_BYTES = 600

OUR_DOMAINS = ("@studex-group.com", "@agentmail.to", "@studexmeat.com")
SELF = ("tumelor001@gmail.com",)

# Inboxes we care about for inbound business traffic.
WATCH = [
    "sales@studex-group.com",
    "info@studex-group.com",
    "meat@studex-group.com",
    "t-ramaphosa-ceo@studex-group.com",
    "naledi-cmo@studex-group.com",
    "robusca.romanov@studex-group.com",
    "support.superagents@studex-group.com",
    "cypher-trace-cto-superagents@studex-group.com",
    "cto-darkfactory@studex-group.com",
]


def get(path):
    req = urllib.request.Request(
        BASE + path, headers={"Authorization": "Bearer " + KEY}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def is_ours(addr):
    a = str(addr or "").lower()
    return any(d in a for d in OUR_DOMAINS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-08-01")
    ap.add_argument("--external-only", action="store_true")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()

    blanks = []
    for iid in WATCH:
        try:
            d = get(f"/inboxes/{iid}/messages?limit={args.limit}")
        except Exception as e:
            print(f"!! {iid}: {e}")
            continue
        for m in d.get("messages", []):
            ts = m.get("timestamp", "")
            if ts < args.since:
                continue
            size = m.get("size") or 0
            if size >= BLANK_MAX_BYTES:
                continue
            frm = m.get("from")
            tos = m.get("to") or []
            to = tos[0] if isinstance(tos, list) and tos else tos
            if not is_ours(frm):
                continue  # a BLANK message we RECEIVED is a different failure
            external = not is_ours(to) and to not in SELF
            if args.external_only and not external:
                continue
            blanks.append(
                {
                    "inbox": iid,
                    "timestamp": ts,
                    "size": size,
                    "to": to,
                    "subject": m.get("subject", ""),
                    "external": external,
                }
            )

    blanks.sort(key=lambda b: b["timestamp"])
    ext = [b for b in blanks if b["external"]]
    internal = [b for b in blanks if not b["external"]]

    print(f"=== BLANK SENDS (size < {BLANK_MAX_BYTES}) since {args.since} ===\n")
    print(f"EXTERNAL (a real person received an empty email): {len(ext)}")
    for b in ext:
        print(
            f"  🔴 {b['timestamp'][:19]}  {b['size']:>4}B  -> {b['to']}\n"
            f"       from {b['inbox']}\n"
            f"       subject: {b['subject'][:80]}"
        )
    print(f"\nINTERNAL (blank emails to Tumelo/own inboxes): {len(internal)}")
    for b in internal:
        print(
            f"  ⚠️  {b['timestamp'][:19]}  {b['size']:>4}B  -> {b['to']}"
            f"  | {b['subject'][:60]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
