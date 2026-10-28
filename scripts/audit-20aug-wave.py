#!/usr/bin/env python3
"""One-shot audit of the 20 Aug 21:57-21:58 outbound wave.

Context: on 2026-08-20 21:57:52 we sent a message to kfschof@gmail.com that arrived with a
subject and NO BODY (429 bytes). At 21:58:14 -- 22 seconds later -- we sent the SAME
"Studex Global Mission 2026 — Partnership Opportunity" email again with a real 1250-byte body.

This script settles whether that retry landed, and produces the full wave inventory so the
"how many blank sends were there really" question has a definitive answer.
"""
import json
import urllib.request

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEY = live_agentmail_keys()[0]
INBOX = "sales@studex-group.com"
BLANK_MAX = 600


def get(path):
    r = urllib.request.Request(
        "https://api.agentmail.to/v0" + path,
        headers={"Authorization": "Bearer " + KEY},
    )
    with urllib.request.urlopen(r, timeout=30) as x:
        return json.load(x)


msgs = get(f"/inboxes/{INBOX}/messages?limit=200").get("messages", [])

print("=" * 74)
print("1) EVERY MESSAGE TO kfschof@gmail.com")
print("=" * 74)
hits = [m for m in msgs if "kfschof" in str(m.get("to") or "")]
for m in sorted(hits, key=lambda x: x.get("timestamp", "")):
    size = m.get("size") or 0
    print(
        f"  {m.get('timestamp')[:23]}  size={size:>5}  "
        f"{'*** BLANK ***' if size < BLANK_MAX else 'has body'}"
    )
    print(f"     subject: {m.get('subject')}")
    print(f"     preview: {(m.get('preview') or '(none)')[:80]!r}")
if not hits:
    print("  (none)")

print()
print("=" * 74)
print("2) EVERY INBOUND MESSAGE FROM kfschof@gmail.com")
print("=" * 74)
backs = [m for m in msgs if "kfschof" in str(m.get("from") or "")]
for m in sorted(backs, key=lambda x: x.get("timestamp", "")):
    print(f"  {m.get('timestamp')[:23]}  size={m.get('size'):>5}  {m.get('subject')}")
    print(f"     preview: {(m.get('preview') or '')[:150]!r}")
if not backs:
    print("  NONE — kfschof never replied to anything we sent.")

print()
print("=" * 74)
print("3) THE 20 AUG 21:57-21:59 WAVE — every send, blank or not")
print("=" * 74)
wave = [
    m
    for m in msgs
    if m.get("timestamp", "").startswith("2026-08-20T21:5")
    or m.get("timestamp", "").startswith("2026-08-25T16:5")
]
blanks = 0
for m in sorted(wave, key=lambda x: x.get("timestamp", "")):
    size = m.get("size") or 0
    is_blank = size < BLANK_MAX
    blanks += is_blank
    to = m.get("to")
    to = to[0] if isinstance(to, list) and to else to
    print(
        f"  {m.get('timestamp')[:23]}  {size:>5}B  {'BLANK' if is_blank else ' ok  '}  "
        f"-> {str(to)[:40]:42} {(m.get('subject') or '')[:34]}"
    )
print(f"\n  blanks in this window: {blanks}")

print()
print("=" * 74)
print("4) VERDICT")
print("=" * 74)
good = [m for m in hits if (m.get("size") or 0) >= BLANK_MAX]
if hits and good:
    print("  kfschof DID receive the real email — the 21:57:52 blank was a failed FIRST attempt,")
    print("  retried successfully 22 seconds later at 21:58:14.")
    print("  -> The 'Test - Studex Global Mission 2026' blank send is a duplicate, not the only copy.")
    print("  -> kfschof received a complete pitch and chose not to reply.")
    print("  -> A reply is still worth making, but as a FOLLOW-UP, not an apology for a blank email.")
elif hits and not good:
    print("  kfschof received ONLY the blank email. An apology + re-send is required.")
else:
    print("  no messages to kfschof found in this inbox.")
