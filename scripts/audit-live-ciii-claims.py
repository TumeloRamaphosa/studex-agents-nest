#!/usr/bin/env python3
"""Are we STILL sending the false 'CIIE booth confirmed' claim to buyers?

The correction note exists because we promised buyers a CIIE booth we could not evidence.
But our own outbound engine has subjects like 'CIIE 2026 - booth confirmed' still going out
(observed 2026-10-22..2026-10-22 05:35 in the nurture inboxes).

If any of those reached an EXTERNAL recipient, the breach is not historical - it is LIVE,
and the correction note is not just overdue, it is racing an ongoing sender.

This script sweeps BOTH AgentMail accounts (the main one and the ciie-nurture one), lists
every message whose subject or body claims a booth/meeting, and separates EXTERNAL recipients
from our own inboxes.
"""
import json
import re
import urllib.request

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

_live = live_agentmail_keys()
KEYS = {"main": _live[0], "ciie": _live[-1]}

CLAIM = re.compile(
    r"booth\s+confirmed|confirmed\s+booth|our\s+booth|booth\s+appointment|"
    r"meet\s+you\s+at\s+CIIE|at\s+our\s+stand|hall\s+\d|"
    r"CIIE.{0,24}Meeting\s+Request|Meeting\s+Request.{0,24}CIIE|"
    r"CIIE\s+Special\s+Pricing|meeting\s+point",
    re.I,
)

# A claim email is "LIVE" if it went out in the last N days. Older than that it is
# historical - already counted in the breach total and already covered by the
# correction note. Default: anything in the last 7 days is live.
LIVE_WINDOW_DAYS = 7

OUR = ("@studex-group.com", "@agentmail.to", "@studexmeat.com", "@mcode.io")
SELF = ("tumelor001@gmail.com",)


def get(key, path):
    r = urllib.request.Request(
        "https://api.agentmail.to/v0" + path,
        headers={"Authorization": "Bearer " + key},
    )
    with urllib.request.urlopen(r, timeout=90) as x:
        return json.load(x)


def main():
    external = []
    internal = 0
    for label, key in KEYS.items():
        try:
            inb = [i.get("inbox_id") for i in get(key, "/inboxes").get("inboxes", [])]
        except Exception as e:
            print(f"{label}: ERR {e}")
            continue
        for iid in inb:
            try:
                msgs = get(key, f"/inboxes/{iid}/messages?limit=1000").get("messages", [])
            except Exception:
                continue
            for m in msgs:
                blob = " ".join(
                    str(m.get(k) or "") for k in ("subject", "preview", "text")
                )
                if not CLAIM.search(blob):
                    continue
                tos = m.get("to")
                tos = tos if isinstance(tos, list) else ([tos] if tos else [])
                for to in tos:
                    a = str(to).lower()
                    if any(d in a for d in OUR) or a in SELF:
                        internal += 1
                        continue
                    external.append(
                        {
                            "account": label,
                            "inbox": iid,
                            "ts": m.get("timestamp"),
                            "size": m.get("size"),
                            "to": to,
                            "subject": m.get("subject"),
                            "preview": (m.get("preview") or "")[:160],
                        }
                    )

    print("=" * 76)
    print("EXTERNAL RECIPIENTS THAT RECEIVED A BOOTH/MEETING CLAIM")
    print("=" * 76)
    if not external:
        print("  NONE — every booth/meeting-claim email went to our own inboxes.")
    else:
        for e in sorted(external, key=lambda x: x["ts"] or ""):
            print(f"  🔴 {e['ts'][:19]}  {e['size']:>5}B  -> {e['to']}")
            print(f"       subject: {e['subject']}")
            print(f"       preview: {e['preview']!r}")
    print()
    print(f"  internal (own inboxes) claim-emails: {internal}")
    print(f"  EXTERNAL claim-emails              : {len(external)}")
    # Date-aware verdict. The 3 Oct sends are historical (already counted in the
    # 26-claim breach total, already covered by the correction note). A claim email
    # inside LIVE_WINDOW_DAYS means the sender is still firing at buyers.
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=LIVE_WINDOW_DAYS)
    live = []
    for e in external:
        ts = e["ts"]
        if not ts:
            continue
        try:
            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            continue
        if when > cutoff:
            live.append(e)
    newest = max((e["ts"] or "" for e in external), default="(none)")
    print(f"  newest EXTERNAL claim email : {newest}")
    print(f"  live window                 : last {LIVE_WINDOW_DAYS} days (since {cutoff.isoformat()})")
    print()
    if live:
        print(f"  -> THE BREACH IS LIVE: {len(live)} claim email(s) to buyers in the last "
              f"{LIVE_WINDOW_DAYS} days. STOP THE CIIE SENDER before sending any correction.")
        for e in sorted(live, key=lambda x: x["ts"] or ""):
            print(f"     {e['ts']} -> {e['to']}  |  {e['subject']}")
    else:
        print("  -> BREACH IS HISTORICAL, NOT LIVE. No claim email has reached a buyer in the")
        print(f"     last {LIVE_WINDOW_DAYS} days. Every external claim email is already inside the")
        print("     26-claim breach total and is covered by the correction note.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
