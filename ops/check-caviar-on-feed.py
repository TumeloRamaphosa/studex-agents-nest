#!/usr/bin/env python3
"""
Caviar offered on a PUBLIC feed - the live check.

WHY THIS EXISTS (2026-10-30):
A retail Oscietra caviar offer went live on Threads (`DfG_M2bEd5U`,
published 06:56Z) and **every gate read GREEN**, because:
  * the caption carried NO price, so the price guard (`check-price-on-feed.py`)
    never fired - and
  * NO checker looked at the PRODUCT at all.
The caviar rule now lives in the publish path (`scripts/caption_policy.py`
-> `caviar_offer()`), which stops a NEW caviar post. This checker closes the
other half: it proves whether a caviar offer is ALREADY sitting on a public
feed, so the ones that are live stay visible in the hourly pass until a human
deletes them. Blotato exposes no delete route, so the remedy is owner-side.

WHEN IT RAN FOR THE FIRST TIME it found THREE live posts, not one:
  * Threads 8676561 (`DfG_M2bEd5U`, 30 Oct) - the retail Oscietra offer
  * IG    8634450 (29 Oct) - "Take our caviar import. The DAFF veterinary import
    permit must be applied for..." - a public caviar-import capability while
    the permit stack (DFFE -> ITAC -> DAFF -> SARS -> CITES) is NOT assembled
  * IG    8592075 (28 Oct) - "Caviar imported and distributed on a 7-14 day lead,
    priced per 100g" - a public caviar offer with a pricing framing (no number,
    which is why the price guard never fired)

THE PREDICATE IS SHARED, NOT COPIED:
this checker imports `caviar_offer()` from the same policy module the publish
path uses. If the policy changes, this checker follows it automatically - a
second copy of the regex could drift and then report "clean" against a rule
that no longer exists.

WHOSE POSTS MAY BE FLAGGED - and why this is allow-listed, not deny-listed:
this Blotato key carries several brands, including `laisa_aesthetics`
(account 55765), which is NOT ours. The remedy this checker proposes is
"a human deletes a live post", so a false positive is DESTRUCTIVE: it would
push a human into deleting another brand's post. Therefore the check scans
ONLY the accounts we own (below), and an unknown account is skipped rather
than flagged. Adding an account is a deliberate act.

CONTRACT: 0 = no live caviar offer (clean) · 1 = a live caviar offer (finding)
· 2 = could NOT prove (no key / API error / empty feed - never reported as
clean, because a checker that can report CLEAN without looking at the live feed
is a false all-clear).

Registered in ops/heartbeat-checkers.tsv as a KNOWN escalation: the live posts
are an already-raised condition, so they must not be re-announced every hour,
but they must stay in the pass's output until they are gone.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# The publish path's own predicate - not a copy of it.
from caption_policy import caviar_offer  # noqa: E402

BASE = "https://backend.blotato.com/v2"
ENV = os.path.join(ROOT, ".env")

# The StudEx accounts on this Blotato key. 76978 + 7701 = ramaphosatumelo
# (Instagram + Threads), 38744 = Facebook, 26628 = LinkedIn, 48423 = TikTok
# (studexwildlife), 41593 = YouTube. 55765 (Instagram laisa_aesthetics) is a
# DIFFERENT brand and is deliberately absent.
DEFAULT_ACCOUNTS = ["38744", "41593", "76978", "26628", "7701", "48423"]
ACCOUNTS_FILE = os.path.join(ROOT, "ops", "blotato-studex-accounts.txt")

# A NEGATED mention of caviar is not an offer - "caviar-free gift box",
# "no caviar, just biltong". This matters MORE here than in the publish path:
# the publish path can afford to be fail-closed (refusing a caption that
# merely mentions caviar costs us a post), but THIS checker's remedy is
# "a human deletes a live post" - so a false positive here would push a human
# into deleting a legitimate post. And a negated mention could only have been
# published by a human: our own publish path refuses ANY caption containing
# the word (caviar_offer is a bare mention test), so we cannot have published
# "caviar-free" ourselves.
NEG_BEFORE = re.compile(r"\b(no|not|without|zero|excluding|minus|never|free of)\s+$", re.I)
NEG_AFTER = re.compile(r"^[\s\-]*(free|less)\b", re.I)


def env_key(name):
    """Read one key from the workspace .env without printing it."""
    try:
        with open(ENV, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() == name:
                    return v.strip().strip('"').strip("'")
    except OSError:
        return None
    return None


def our_accounts():
    """The account ids this checker is allowed to flag."""
    ids = list(DEFAULT_ACCOUNTS)
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if line:
                    ids.append(line)
    except OSError:
        pass
    return set(ids)


def get(path, key):
    req = urllib.request.Request(
        BASE + path,
        headers={"blotato-api-key": key, "accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp)


def un_negated(text):
    """True when the text mentions caviar as an OFFER rather than a denial."""
    for m in re.finditer(r"caviar|oscietra|kaluga|sevtruga|beluga", text or "", re.I):
        before = text[:m.start()]
        after = text[m.end():]
        if NEG_BEFORE.search(before[-14:]):
            continue
        if NEG_AFTER.match(after):
            continue
        return True
    return False


def scan_items(items, accounts=None):
    """Return the live posts whose text offers caviar.

    Kept separate from main() so the rule can be tested against synthetic
    posts with no network at all. `accounts` defaults to the accounts we own;
    posts on any other account are skipped (see the module docstring).
    """
    allowed = our_accounts() if accounts is None else set(accounts)
    hits = []
    skipped = []
    for it in items:
        if not isinstance(it, dict):
            continue
        acct = it.get("account")
        acc = acct if isinstance(acct, dict) else {}
        aid = str(acc.get("id") or "")
        if aid and aid not in allowed:
            skipped.append(aid)
            continue
        text = it.get("text") or it.get("content") or ""
        if not caviar_offer(text):
            continue
        if not un_negated(text):
            # mentions caviar only to deny it - not an offer, not a finding
            continue
        hits.append({
            "platform": acc.get("platform") or acc.get("type") or "",
            "account": aid,
            "postId": it.get("id") or it.get("postId") or "",
            "postTime": str(it.get("postTime") or it.get("publishedAt") or "")[:19],
            "text": str(text)[:120],
        })
    return hits, sorted(set(skipped))


def main():
    args = sys.argv[1:]
    key = env_key("BLOTATO_API_KEY")
    if not key:
        print("ERROR: BLOTATO_API_KEY not set in %s - cannot prove what published." % ENV)
        print("       Refusing to report a clean feed without live evidence.")
        return 2

    try:
        d = get("/posts?limit=50", key)
    except urllib.error.HTTPError as e:
        print("ERROR: posts HTTP %s (wrong header or expired key)" % e.code)
        return 2
    except Exception as e:  # noqa: BLE001
        print("ERROR: posts request failed: %s" % e)
        return 2

    items = d if isinstance(d, list) else (d.get("items") or d.get("posts") or [])
    if not items:
        # An empty list must never read as "nothing published".
        print("ERROR: post list came back empty - cannot prove what published")
        return 2

    allowed = our_accounts()
    hits, skipped = scan_items(items, allowed)

    if "--json" in args:
        print(json.dumps({"scanned": len(items), "accounts": sorted(allowed),
                          "skipped_accounts": skipped, "hits": hits}, indent=2))
        return 1 if hits else 0

    print("  live posts scanned : %d (accounts we own: %s)"
          % (len(items), ",".join(sorted(allowed))))
    if skipped:
        print("  accounts skipped   : %s (not ours - a delete-remedy check must not flag them)"
              % ",".join(skipped))
    if hits:
        print("  [FINDING] caviar offered on a public feed")
        for h in hits:
            print("     %-10s acct=%-6s %-14s %s :: %s" % (
                h["platform"], h["account"], h["postId"], h["postTime"], h["text"]))
        print("VERDICT: FINDING - %d live public post(s) offer caviar." % len(hits))
        print("         2026 policy: caviar is TRADE-ONLY, 2027 season. The SA permit stack")
        print("         (DFFE -> ITAC -> DAFF -> SARS -> CITES) is NOT assembled and 0 caviar")
        print("         products are purchasable. Blotato has NO delete route - a human must")
        print("         delete the post in Threads / Instagram / the Blotato dashboard.")
        return 1

    print("VERDICT: OK - %d live public post(s) scanned, none offers caviar." % len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
