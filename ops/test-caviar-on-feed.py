#!/usr/bin/env python3
"""
Tests for ops/check-caviar-on-feed.py - the LIVE caviar audit.

The rule this checker enforces is simple ("does a live public post offer
caviar?"), but the ways it can be WRONG are not, so each check below targets
one specific way:

  1. the shipped caption (the one that actually went live) is caught
  2. a clean biltong post is not flagged
  3. a NEGATED mention ("caviar-free") is not flagged  <- the destructive
     false positive: the remedy here is "a human deletes a live post", and our
     2026 product IS a caviar-free box
  4. a cue far away from the word does not negate it
  5. the predicate is the publish path's own function, so it cannot drift
  6. the negation carve-out is AUDIT-ONLY: the publish path still refuses any
     caption that mentions caviar at all
  7. an empty feed is COULD-NOT-PROVE (rc=2), never "clean" - a checker that
     can report CLEAN without looking at the live feed is a false all-clear
  8. a post on ANOTHER brand's account (laisa_aesthetics) is never flagged -
     the remedy is a deletion, so a false positive would push a human into
     deleting someone else's post

Run: python3 ops/test-caviar-on-feed.py
"""

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def post(text, pid="123", platform="threads", account="7701"):
    return {"id": pid, "text": text, "postTime": "2026-10-30T06:56:13.268Z",
            "account": {"platform": platform, "id": account}}


def main():
    # Load the policy ONCE and register it in sys.modules BEFORE the checker
    # is loaded, so the checker's `from caption_policy import caviar_offer`
    # resolves to this very module object - that is what makes check 5 a real
    # test of coupling rather than a test of import luck.
    policy = load(os.path.join(ROOT, "scripts", "caption_policy.py"), "caption_policy")
    sys.modules["caption_policy"] = policy
    checker = load(os.path.join(ROOT, "ops", "check-caviar-on-feed.py"), "caviar_feed")

    checks = 0
    fails = []

    def ok(label, cond):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(label)
            print("  FAIL  %s" % label)
        else:
            print("  ok    %s" % label)

    def scan(items):
        return checker.scan_items(items)[0]

    # 1. the caption that actually shipped, verbatim in substance
    shipped = ("Some moments deserve more than champagne - they deserve caviar. "
               "Our Oscietra Imperial Caviar is the richest, most sought-after tier we "
               "carry: deep, nutty, with a clean finish and a long, savoury finish.")
    hits = scan([post(shipped, "8676561")])
    ok("the shipped caviar caption is caught", len(hits) == 1)
    ok("the caught post keeps its id", hits and hits[0]["postId"] == "8676561")

    # 1b. the OTHER two live caviar posts the checker found on its first run
    hits = scan([post("Take our caviar import. The DAFF veterinary import permit must be "
                      "applied for at least four weeks before shipment.", "8634450",
                      "instagram", "76978")])
    ok("the live 'caviar import' post is caught", len(hits) == 1)
    hits = scan([post("Caviar imported and distributed on a 7-14 day lead, priced per 100g "
                      "so the shelf and the table agree.", "8592075", "instagram", "76978")])
    ok("the live 'caviar priced per 100g' post is caught", len(hits) == 1)

    # 2. a clean biltong post
    ok("a clean biltong post is not flagged",
       len(scan([post("Wagyu Biltong Gold 1kg - slow-dried, ready to slice.")])) == 0)

    # 3. NEGATED mentions - the destructive false positive
    for label, text in [
        ("caviar-free", "Our Christmas box is CAVIAR-FREE this year - biltong and coffee only."),
        ("no caviar", "Wagyu biltong, no caviar, nothing you cannot slice."),
        ("without caviar", "A gift box without caviar, just Wagyu biltong."),
        ("free of caviar", "Corporate gifting that is free of caviar this season."),
    ]:
        ok("negated mention (%s) is not flagged" % label, len(scan([post(text)])) == 0)

    # 4. a cue far away must not negate the offer
    ok("a distant 'no other' does not negate the offer",
       len(scan([post("No other product we carry compares. Our Oscietra caviar does.")])) == 1)

    # 5. the predicate is shared, not copied
    ok("the checker uses the publish path's own caviar_offer()",
       checker.caviar_offer is policy.caviar_offer)

    # 6. the carve-out is AUDIT-ONLY: the publish path still refuses any mention
    ok("the publish path still refuses a caviar-free caption",
       len(policy.policy_failures("Our Christmas box is CAVIAR-FREE this year.")) > 0)

    # 7. an empty feed is could-not-prove, never clean
    def boom(path, key):
        return {"items": []}
    orig_get = checker.get
    checker.get = boom
    try:
        rc_empty = checker.main()
        rc_fail = None

        def fail(path, key):
            raise RuntimeError("network down")
        checker.get = fail
        rc_fail = checker.main()
    finally:
        checker.get = orig_get
    ok("an empty feed returns rc=2 (could NOT prove), not 0 (clean)", rc_empty == 2)
    ok("a network failure returns rc=2, not 0", rc_fail == 2)

    # 8. another brand's account is NEVER flagged - the remedy is a deletion
    other = post(shipped, "9999999", "instagram", "55765")  # laisa_aesthetics
    hits, skipped = checker.scan_items([other])
    ok("a caviar post on laisa_aesthetics (55765) is not flagged", len(hits) == 0)
    ok("the non-ours account is reported as skipped", "55765" in skipped)
    ok("laisa_aesthetics is not in the accounts we own",
       "55765" not in checker.our_accounts())

    print()
    if fails:
        print("FAILED %d of %d checks:" % (len(fails), checks))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("ALL CHECKS PASS (%d)" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
