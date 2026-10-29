#!/usr/bin/env python3
"""Recount the CIIE outreach breach from the verified send records.

INPUT: the AgentMail send records for the CIIE sender inbox
       project-2571-studex-agent-2077@agentmail.to (a SEPARATE AgentMail account from
       sales@studex-group.com — it needs the ciie-nurture key, **************..., and it
       404s for the main key).

WHY THE ORIGINAL COUNTS DISAGREED:
  * "21 emails to 9 buyers" (vault/MEMORY, 22 Oct) counted only ciie-nurture/prospects.json.
  * "26 emails to 12 recipients" (outbound-corrections/ciie-correction-recipients.json,
    23:58 UTC) added the 3 leads that live only in ciie-nurture/data/state.json —
    but counted each of them as 1 email.
  * The truth: each of those 3 state.json leads received **2** emails (a 24 Sep
    "Welcome — Studex Meat Co. Catalogue & Introduction" and a 2 Oct custom quote),
    not 1. And the 2 Oct email went out with a **literal, uninterpolated ${lead.company}**
    in the subject line.

Run:  python3 scripts/ciii-breach-recount.py
It reads the cached send records from /tmp/ciii-sends.json (written by the fetcher) so that
the count can be re-derived without touching the API again.
"""
import json
import os
import re
from collections import defaultdict

CACHE = "/tmp/ciii-sends.json"

# The 12 recipients, grouped by the engine that produced their sends.
STATE_ONLY = [
    "li.wei@luckincoffee.cn",
    "c.jie@timhortonschina.com",
    "sarah@eurotrading.co.za",
]
PROSPECTS = [
    "buyer@luckincoffee.com",
    "procurement.cn@timhortons.com",
    "purchasing@pacificcoffee.com",
    "food.import@jd.com",
    "info@smartsquare.ae",
    "info@dhiranifoodstuff.ae",
    "trade@bmc-overseas.ae",
    "green@coffeeplanet.ae",
    "info@thirdlinecoffee.com",
]

# Subjects that actually carried the false CIIE booth/meeting claim.
BOOTH_CLAIM = re.compile(
    r"CIIE|Booth|Meeting Request|PROWTC|Custom Quote|Special Pricing", re.I
)


def main():
    if not os.path.exists(CACHE):
        print(f"missing cache {CACHE} — run the fetcher first")
        return 1
    recs = json.load(open(CACHE))

    by_recipient = defaultdict(list)
    for r in recs:
        for t in r["targets"]:
            by_recipient[t].append(r)

    print("=" * 76)
    print("VERIFIED CIIE OUTREACH — recount")
    print("=" * 76)
    total = 0
    broken = 0
    booth_claim = 0
    for t in PROSPECTS + STATE_ONLY:
        h = sorted(by_recipient.get(t, []), key=lambda x: x["timestamp"])
        if not h:
            print(f"  {t:34}  NO SENDS FOUND")
            continue
        engine = "state.json only" if t in STATE_ONLY else "prospects.json"
        print(f"\n  {t}   ({engine}) — {len(h)} email(s)")
        for r in h:
            total += 1
            subj = r["subject"]
            is_broken = "${lead" in subj
            if is_broken:
                broken += 1
            has_claim = bool(BOOTH_CLAIM.search(subj))
            if has_claim:
                booth_claim += 1
            flag = "  <<< BROKEN SUBJECT" if is_broken else ""
            print(
                f"      {r['timestamp'][:19]}  {r['size']:>5}B  "
                f"{'CIIE-CLAIM' if has_claim else 'no-claim '}  {subj[:60]}{flag}"
            )

    print()
    print("=" * 76)
    print("VERDICT")
    print("=" * 76)
    reached = sum(1 for t in PROSPECTS + STATE_ONLY if by_recipient.get(t))
    print(f"  recipients reached        : {reached} / 12")
    print(f"  total emails sent         : {total}")
    print(f"  emails carrying a CIIE claim subject : {booth_claim}")
    print(f"  emails with a BROKEN subject (literal ${{lead.*}}) : {broken}")
    print()
    print("  Prior figures:")
    print("    '21 emails to 9 buyers'  — counted prospects.json only; missed 3 recipients")
    print("    '26 emails to 12 recipients' — right recipients, but each state.json lead")
    print("                                 was counted as 1 email when it received 2")
    print(f"  CORRECTED FIGURE: {total} emails to {reached} recipients")
    print()
    print("  Recipients needing a correction note (received a CIIE claim):")
    for t in PROSPECTS + STATE_ONLY:
        h = by_recipient.get(t, [])
        if any(BOOTH_CLAIM.search(r["subject"]) for r in h):
            print(f"    - {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
