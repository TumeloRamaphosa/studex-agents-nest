#!/usr/bin/env python3
"""
A public post with NO call to action - the live check.

WHY THIS EXISTS (2026-10-31):
The feed was reaching people and asking for nothing. Measured on the LIVE
feed (Blotato /posts -> state.analytics.latest.metrics), 10 posts:

    Instagram  5/5 carry a CTA ("Connect with our team: info@studexmeat.com")
               1060-1239 chars, never truncated.
    Threads   0/5 carry a CTA - every one exactly 500 chars (TRUNCATED).
    Threads: 3 likes across 5 posts.  Instagram: 47 likes.
    Every post on both platforms: 0 comments, 0 follows, 0 shares.
    Best post: 841 views, 489 reach, 12 likes, 5 profile visits, 0 follows.

THE ROOT CAUSE was a truncation, not a strategy:
  * Threads captions are capped at 500 chars.
  * BOTH publish paths cut at 497 chars + "..." (`scripts/daily-post.py` and
    `studex-content-automation/scripts/blotato-fallback.js`).
  * The CTA lives at the END of a caption, so the cut deleted exactly the
    CTA - and the generator's validator ("no closing question/CTA") had
    ALREADY APPROVED the caption, because it validates the PRE-truncation
    text. Every gate read green and the CTA went out the window.
🔑 *A validator that checks the text BEFORE the transform is not checking the
text that ships.*

The fix is in `scripts/caption_policy.py` (`truncate_for_platform`), which
now cuts the PROSE and keeps the CTA + hashtags. THIS checker is the other
half: it proves whether a CTA-less post is ALREADY sitting on a public feed,
so the live ones stay visible until a human fixes them (Blotato exposes no
edit or delete route, so the remedy is owner-side).

THE PREDICATE IS SHARED, NOT COPIED:
this checker imports `has_cta()` from the same policy module the publish path
uses. If the policy changes, this checker follows it automatically - a second
copy of the rule could drift and then report "clean" against a rule that no
longer exists.

WHY A LIVE CHECK AND NOT JUST THE FIX:
the fix stops the NEXT post from losing its CTA, but the 5 Threads posts
already published are still CTA-less. A guard that only looked at the source
would say "clean" while the live feed still had the defect.

WHOSE POSTS MAY BE FLAGGED:
allow-listed, exactly like the caviar checker - this Blotato key carries
several brands including `laisa_aesthetics` (55765), which is NOT ours. The
remedy here is "a human edits a live post", so a false positive would push a
human into editing another brand's post. Unknown accounts are SKIPPED, not
flagged.

CONTRACT: 0 = every live post carries a CTA (clean) · 1 = a live post with no
CTA (finding) · 2 = could NOT prove (no key / API error / empty feed - never
reported as clean, because a checker that can report CLEAN without looking at
the live feed is a false all-clear).

Registered in ops/heartbeat-checkers.tsv as a KNOWN escalation: the live posts
are an already-raised condition, so they must not be re-announced every hour,
but they must stay in the pass's output until they are fixed.
"""

import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# The publish path's own predicate - not a copy of it.
from caption_policy import has_cta  # noqa: E402

BASE = "https://backend.blotato.com/v2"
ENV = os.path.join(ROOT, ".env")

# The StudEx accounts on this Blotato key. 55765 (Instagram laisa_aesthetics)
# is a DIFFERENT brand and is deliberately absent.
DEFAULT_ACCOUNTS = ["38744", "41593", "76978", "26628", "7701", "48423"]
ACCOUNTS_FILE = os.path.join(ROOT, "ops", "blotato-studex-accounts.txt")


def env_key(name):
    """Read one key from the workspace .env without printing it."""
    try:
        with open(ENV, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == name:
                    return v.strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def our_accounts():
    """The account ids this checker is allowed to flag."""
    ids = set(DEFAULT_ACCOUNTS)
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                ids.add(line.split()[0].strip())
    except Exception:
        pass
    return ids


def get(path, key):
    req = urllib.request.Request(
        BASE + path, headers={"blotato-api-key": key, "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp)


def scan_items(items, accounts=None):
    """Return (hits, skipped_accounts) for the live posts we own.

    A post with no CTA is a HIT. A post whose account is not ours is
    SKIPPED, never flagged.
    """
    allowed = our_accounts() if accounts is None else set(accounts)
    hits = []
    skipped = set()
    for p in items or []:
        acct = p.get("account") or {}
        aid = str(acct.get("id") or "")
        if aid and aid not in allowed:
            skipped.add("%s (%s)" % (acct.get("name") or "?", aid))
            continue
        text = p.get("text") or ""
        if not has_cta(text):
            hits.append({
                "id": p.get("id"),
                "platform": p.get("platform"),
                "postTime": p.get("postTime"),
                "chars": len(text),
            })
    return hits, sorted(skipped)


def main():
    key = env_key("BLOTATO_API_KEY")
    if not key:
        print("ERROR: BLOTATO_API_KEY not set in %s - cannot prove what published." % ENV)
        print("       Refusing to report a clean feed without live evidence.")
        return 2
    try:
        data = get("/posts?limit=50", key)
    except urllib.error.HTTPError as e:
        print("ERROR: posts HTTP %s (wrong header or expired key)" % e.code)
        return 2
    except Exception as e:
        print("ERROR: posts request failed: %s" % e)
        return 2

    items = data.get("items") if isinstance(data, dict) else data
    if not items:
        print("ERROR: post list came back empty - cannot prove what published")
        return 2

    hits, skipped = scan_items(items)
    print("scanned: %d" % len(items))
    print("skipped_accounts: %s" % json.dumps(skipped))
    if hits:
        print("VERDICT: FINDING - %d live public post(s) carry NO call to action." % len(hits))
        for h in hits:
            print("  %s %s %s (%d chars) - %s"
                  % (h["id"], h["platform"], h["postTime"], h["chars"],
                     "no CTA" if h["platform"] == "threads"
                     else "no CTA - the post reaches people and asks for nothing"))
        print("REMEDY: edit the caption to end with an ask (owner-side - Blotato has no")
        print("        edit route). A post with a CTA is the difference between reach")
        print("        and a conversation.")
        return 1
    print("VERDICT: CLEAN - every live public post carries a call to action.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
