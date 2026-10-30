#!/usr/bin/env python3
"""Public-feed caption policy - ONE source of truth for both publish paths.

Path A (scripts/daily-post.py) and path B
(studex-content-automation/scripts/blotato-fallback.js) publish to the SAME
public feeds, so they must enforce the SAME policy. Until now path A had
validate_brand() and path B had NOTHING - the only thing that checked a
path-B caption was the 09:20 pre-flight, which runs ~20 minutes AFTER the
caption was published. That is a post-mortem, not a gate.

The rule at issue: a price must not appear on a public feed
("FAIL: Price published on public feed" in validate_brand()).

THE SECOND RULE, ADDED 2026-10-30: caviar must not appear on a public feed
at all. See CAVIAR_RE below for why the permits decide this rather than a
preference.

CLI:
    caption-policy.py --check-text   "caption here"    -> exit 1 if it violates
    caption-policy.py --check-pending <pending.json>   -> exit 1 if it violates
"""
import json
import re
import sys

# The one pattern. validate_brand() used to hold this inline; both paths
# now read it from here, so the two paths cannot drift apart.
PRICE_RE = re.compile(r"R\s?\d[\d,\.]*")


# 🔑 CAVIAR IS OFF THE PUBLIC FEED - AND THE PERMITS DECIDE THAT, NOT A PREFERENCE.
#   * The SA caviar permit stack (DFFE -> ITAC -> DAFF -> SARS -> CITES) is NOT
#     assembled, so there is no lawful way to sell caviar retail right now.
#   * The live storefront carries 0 caviar products, so a caption offering it
#     cannot be fulfilled either.
#   * The caviar desk itself states "2027 season, trade accounts only, stack
#     not yet assembled". The 2026 product is the CAVIAR-FREE biltong + coffee box.
#
# 🔑 WHY THE PRICE RULE COULD NOT CATCH THIS. The 2026-10-30 caption (Threads
# DfG_M2bEd5U) offered Oscietra caviar and carried NO price, so the price rule
# never fired, every gate read green, and a retail offer for an unpermitted,
# unfulfillable product went live at 08:56 SAST. A guard that only asks "is
# there a price?" cannot see a product problem.
#
# The grade names are matched too, because a caption can say "Oscietra" (or
# "#oscietracaviar") without ever using the word "caviar" - and a hashtag has
# no word boundary to anchor a \b on.
CAVIAR_RE = re.compile(r"caviar|oscietra|kaluga|sevtruga|beluga", re.I)


def caviar_offer(caption):
    """True when a caption offers caviar on a public feed.

    Kept as its own predicate (not only a policy failure) so callers can ask
    the question directly - the pre-flight audits the pending caption and
    needs to know whether the PRODUCT is one we may not offer, separately
    from the price rule that already had its own wording.
    """
    return bool(caption and CAVIAR_RE.search(caption))


def policy_failures(caption):
    """Return a list of policy failures for a caption. Empty == publishable."""
    failures = []
    if not caption:
        return ["FAIL: Empty caption"]
    if PRICE_RE.search(caption):
        failures.append("FAIL: Price published on public feed")
    if caviar_offer(caption):
        failures.append(
            "FAIL: Caviar offered on a public feed - the SA permit stack "
            "(DFFE -> ITAC -> DAFF -> SARS -> CITES) is not assembled, 0 "
            "caviar products are purchasable on the storefront, and caviar "
            "is off the retail path for 2026 (trade desk only, 2027 season). "
            "Do not publish this caption; caviar is advertised on the caviar "
            "trade desk, not on a public feed.")
    return failures


def main(argv):
    if "--check-text" in argv:
        i = argv.index("--check-text")
        caption = argv[i + 1] if i + 1 < len(argv) else ""
    elif "--check-pending" in argv:
        i = argv.index("--check-pending")
        path = argv[i + 1] if i + 1 < len(argv) else ""
        try:
            with open(path, encoding="utf8") as fh:
                pending = json.load(fh)
        except Exception as exc:  # an unreadable pending file is not a violation
            print("caption-policy: cannot read pending file (%s)" % exc,
                  file=sys.stderr)
            return 0
        caption = pending.get("caption") or ""
    else:
        print(__doc__)
        return 2

    failures = policy_failures(caption)
    for f in failures:
        print(f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
