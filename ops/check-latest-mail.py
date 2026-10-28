#!/usr/bin/env python3
"""Canonical read-only probe: what is the newest inbound AgentMail message?

WHY THIS EXISTS
---------------
A hand-rolled mail probe failed three different ways inside a single
heartbeat pass, and every failure printed the same reassuring thing:
"no new mail". The API's real shapes are:

  1. GET /v0/inboxes            -> {"count","limit","inboxes":[...]}
     the list key is "inboxes", NOT "items"
  2. each inbox object          -> {"inbox_id","email","display_name",...}
     the handle is "inbox_id", NOT "address" and NOT "name"
  3. GET /v0/inboxes/{id}/messages -> {"count","limit","messages":[...]}
     the list key is "messages", NOT "items"

Miss (1) or (3) and the list parses as empty. Miss (2) and every per-inbox
fetch is skipped by `if not a: continue` - zero fetches, zero errors, and a
confident "newest: None". That is a FALSE ALL-CLEAR, the same class of bug
as the auth-error sweep documented in scripts/agentmail_keys.py: a checker
that cannot prove the answer must not look like one that found nothing.

So this checker:
  * uses the CANONICAL key resolver (scripts/agentmail_keys.py) - never a
    hand-rolled key list, never a literal
  * parses the shapes the API actually returns
  * counts the messages it ACTUALLY scanned, so a real zero is
    distinguishable from a broken sweep
  * refuses to report "no mail" when it cannot prove it

Exit codes:
  0  the sweep proved the answer (mail found, or a real empty result)
  2  could NOT prove it (no live key, no inboxes, 0 messages scanned,
     or a truncated page) - never a silent pass
  1  reserved for future findings

Usage:
  python3 ops/check-latest-mail.py
  python3 ops/check-latest-mail.py --since 2026-10-26T09:00:07.281Z
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import agentmail_keys as ak  # noqa: E402  (path set above)

BASE = "https://api.agentmail.to/v0"

# Our own domains. Mail from these is internal traffic (warmup, agents,
# standups) and is not an external arrival.
OWN_DOMAINS = (
    "@studex-group.com",
    "@agentmail.to",
    "@studexmeat.com",
)


# ---------------------------------------------------------------- parsing

def parse_inboxes(payload):
    """Return the list of inbox handles from an inbox-list payload.

    The API returns {"count","limit","inboxes":[...]}. Each object carries
    the handle as "inbox_id" (it also repeats it as "email").
    """
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = (payload.get("inboxes") or payload.get("data")
                 or payload.get("items") or [])
    else:
        items = []
    out = []
    for it in items:
        if isinstance(it, str):
            a = it
        elif isinstance(it, dict):
            a = it.get("inbox_id") or it.get("address") or it.get("email")
        else:
            a = None
        if a:
            out.append(a)
    return out


def parse_messages(payload):
    """Return the list of message objects from a messages payload.

    The API returns {"count","limit","messages":[...]}.
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for k in ("messages", "items", "data"):
            if isinstance(payload.get(k), list):
                return payload[k]
    return []


def ts_of(m):
    if not isinstance(m, dict):
        return ""
    return str(m.get("sent_at") or m.get("created_at") or "")


def sender_of(m):
    if not isinstance(m, dict):
        return ""
    return str(m.get("from") or m.get("from_address") or "")


def subject_of(m):
    if not isinstance(m, dict):
        return None
    return m.get("subject")


def is_external(sender):
    """True when the sender is NOT one of our own domains."""
    if not sender:
        return False
    return not any(d in sender for d in OWN_DOMAINS)


# ------------------------------------------------------------------ sweep

def _get(url, key, timeout=25):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def sweep(limit=1000):
    """Sweep every live key. Returns (inboxes, messages).

    Raises SystemExit with a 'could not prove' message if the sweep cannot
    establish an answer (no live key, unreachable API, truncated page).
    """
    keys = ak.live_agentmail_keys()
    if not keys:
        raise SystemExit("could not prove: no live AgentMail key")

    boxes = {}
    for k in keys:
        try:
            payload = _get(f"{BASE}/inboxes?limit=200", k)
        except urllib.error.HTTPError as e:
            raise SystemExit(f"could not prove: inbox list HTTP {e.code}")
        except Exception as e:
            raise SystemExit(f"could not prove: inbox list unreachable: {e}")
        for a in parse_inboxes(payload):
            boxes.setdefault(a, k)

    msgs = []
    for a, k in boxes.items():
        try:
            payload = _get(f"{BASE}/inboxes/{a}/messages?limit={limit}", k)
        except Exception:
            continue  # a single unreadable inbox does not void the sweep
        if isinstance(payload, dict) and payload.get("count") == limit:
            raise SystemExit(
                f"TRUNCATED: {a} returned count == limit ({limit}). "
                "Raise the limit before trusting this result."
            )
        msgs.extend(parse_messages(payload))
    return boxes, msgs


# ----------------------------------------------------------------- assess

def assess(boxes, msgs, since=None):
    """Pure decision function over a completed sweep.

    Separated from the network so the contract can be regression-tested:
    a sweep that could not read anything must NOT read as 'no mail'.
    """
    n_boxes = len(boxes)
    n_msgs = len(msgs)

    newest = None
    external = []
    for m in msgs:
        ts = ts_of(m)
        if not ts:
            continue
        if newest is None or ts > newest[0]:
            newest = (ts, sender_of(m), subject_of(m))
        if since and ts > since and is_external(sender_of(m)):
            external.append((ts, sender_of(m), subject_of(m)))

    if n_boxes == 0:
        return {
            "rc": 2, "inboxes": 0, "messages": 0, "newest": None,
            "external_since": [],
            "verdict": "COULD NOT PROVE - 0 inboxes visible across every live key. "
                       "This is a broken sweep, NOT an empty mailbox.",
        }
    if n_msgs == 0:
        return {
            "rc": 2, "inboxes": n_boxes, "messages": 0, "newest": None,
            "external_since": [],
            "verdict": f"COULD NOT PROVE - 0 messages scanned across {n_boxes} inbox(es). "
                       "This is almost certainly a response-shape change, NOT an "
                       "empty inbox.",
        }
    if since:
        verdict = (f"VERDICT: CLEAN - no external arrival since {since} "
                   f"({len(external)} found, {n_msgs} message(s) scanned "
                   f"across {n_boxes} inbox(es)).")
    else:
        verdict = (f"VERDICT: OK - {n_msgs} message(s) scanned across "
                   f"{n_boxes} inbox(es).")
    return {
        "rc": 0, "inboxes": n_boxes, "messages": n_msgs, "newest": newest,
        "external_since": external, "verdict": verdict,
    }


# ------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None,
                    help="ISO timestamp: report external arrivals after it")
    ap.add_argument("--limit", type=int, default=1000)
    args = ap.parse_args()

    try:
        boxes, msgs = sweep(limit=args.limit)
    except SystemExit as e:
        print(f"COULD NOT PROVE: {e}")
        print("VERDICT: COULD NOT PROVE - refusing to report 'no mail'.")
        return 2

    r = assess(boxes, msgs, since=args.since)
    print(f"inboxes visible   : {r['inboxes']}")
    print(f"messages scanned  : {r['messages']}")
    n = r["newest"]
    print(f"newest inbound    : {n[0] if n else 'none'}"
          + (f"  from {n[1]}  subject {n[2]!r}" if n else ""))
    if args.since:
        print(f"external arrivals : {len(r['external_since'])}")
        for e in r["external_since"][:10]:
            print(f"   {e[0]}  {e[1]}  {e[2]!r}")
    print()
    print(r["verdict"])
    return r["rc"]


if __name__ == "__main__":
    sys.exit(main())
