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


def policy_failures(caption):
    """Return a list of policy failures for a caption. Empty == publishable."""
    failures = []
    if not caption:
        return ["FAIL: Empty caption"]
    if PRICE_RE.search(caption):
        failures.append("FAIL: Price published on public feed")
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
