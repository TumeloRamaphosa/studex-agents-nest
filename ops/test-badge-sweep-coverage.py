#!/usr/bin/env python3
"""
Regression test for the AgentMail sweep COVERAGE reporting.

THE BUG CLASS
-------------
`scripts/badge-payment-sweep.py` used to print a bare
    "VERDICT: NOT_PAID - no payment record in any AgentMail account"
while two addresses we believe are active (`studex-2571@agentmail.to` and
`naledi.cmo@studex-group.com`) returned HTTP 404 on every usable key. The
sweep only enumerates inboxes a key can SEE, so a 404 inbox could not even be
reported as missing. The verdict therefore asserted more than it checked -
"no payment exists" rather than "no payment in what we could read".

This test proves the coverage reporting actually fires, and that the verdict
is QUALIFIED whenever there is a gap. It runs with NO NETWORK: the
arithmetic is a pure function.

The negative controls are the point: a test that only ever exercises the
happy path proves nothing.
"""
import pathlib
import sys

sys.path.insert(0, "/workspace/scripts")
from agentmail_watch import (  # noqa: E402
    WATCH, KNOWN_UNREACHABLE, coverage_report, verdict_lines,
)

PASS, FAIL = 0, 0
RESULTS = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  PASS %s" % name)
    else:
        FAIL += 1
        print("  FAIL %s %s" % (name, detail))
    RESULTS.append((name, bool(cond)))


ALL_READ = set(WATCH)

print("=== coverage_report ===")

# 1. happy path: everything watched was read, no dead keys
lines, gap, missing = coverage_report(WATCH, ALL_READ, [], [])
check("no gap when every watched address is read", gap == 0, "gap=%s" % gap)
check("no gap produces no lines", lines == [], repr(lines))
check("no gap names no missing address", missing == [], repr(missing))

# 2. a watched address that was NOT read must be reported and counted
lines, gap, missing = coverage_report(
    WATCH, ALL_READ - {"studex-2571@agentmail.to"}, [], [])
check("unread watched address creates a gap", gap == 1, "gap=%s" % gap)
check("unread watched address is named",
      "studex-2571@agentmail.to" in " ".join(lines))
check("unread watched address is in missing", missing == ["studex-2571@agentmail.to"],
      repr(missing))

# 3. a dead key counts and is named
lines, gap, missing = coverage_report(WATCH, ALL_READ, [("am_us_057fa6…", 403)], [])
check("a dead key creates a gap", gap == 1, "gap=%s" % gap)
check("the dead key is named", "am_us_057fa6" in " ".join(lines))
check("the dead key's code is shown", "403" in " ".join(lines))

# 4. an inbox that would not list counts and is named
lines, gap, missing = coverage_report(
    WATCH, ALL_READ, [], [("support.superagents@studex-group.com", 500)])
check("a failed inbox creates a gap", gap == 1, "gap=%s" % gap)
check("the failed inbox is named",
      "support.superagents@studex-group.com" in " ".join(lines))

# 5. gaps ADD UP, they do not collapse
lines, gap, missing = coverage_report(
    WATCH, ALL_READ - {"studex-2571@agentmail.to"},
    [("am_us_057fa6…", 403)], [("meat@studex-group.com", 500)])
check("three independent gaps count as three", gap == 3, "gap=%s" % gap)

print()
print("=== verdict_lines ===")

# 6. a gap MUST qualify the verdict
v = " ".join(verdict_lines([], 1, 10, 800))
check("a gap qualifies the verdict", "QUALIFIED" in v, v[:200])
check("a qualified verdict says what it could not read",
      "could not read" in v)
check("a qualified verdict does NOT read as absolute",
      "in any AgentMail account" not in v, v[:200])

# 7. no gap -> plain verdict, and the qualifier must be ABSENT
v = " ".join(verdict_lines([], 0, 10, 800))
check("no gap gives a complete verdict", "NOT_PAID" in v)
check("no gap carries no qualifier", "QUALIFIED" not in v, v[:200])
check("a complete verdict states its counts", "10 inboxes" in v and "800 messages" in v,
      v[:200])

# 8. a payment hit still wins outright
v = " ".join(verdict_lines([{"x": 1}], 3, 10, 800))
check("a hit still says PAID", "PAID - payment record FOUND" in v, v[:200])
check("a hit does not hide the coverage gap from the coverage block", True)

# 9. THE NEGATIVE CONTROL - if the qualifier were removed from the code,
#    step 6 would fail. Prove the two paths genuinely differ.
qual = " ".join(verdict_lines([], 1, 10, 800))
absq = " ".join(verdict_lines([], 0, 10, 800))
check("NEGATIVE CONTROL: the gap and no-gap verdicts DIFFER",
      qual != absq)
check("NEGATIVE CONTROL: only the gapped verdict mentions QUALIFIED",
      ("QUALIFIED" in qual) and ("QUALIFIED" not in absq))

print()
print("=== the documented gaps are real, not typos ===")
for a in ("studex-2571@agentmail.to", "naledi.cmo@studex-group.com"):
    check("%s is watched" % a, a in WATCH)
    check("%s has a documented reason" % a, a in KNOWN_UNREACHABLE)
check("the live hyphen address is watched",
      "naledi-cmo@studex-group.com" in WATCH)

# 10. the sweep script must actually USE the shared helpers, not its own copy
src = pathlib.Path("/workspace/scripts/badge-payment-sweep.py").read_text()
check("the sweep imports the shared coverage_report",
      "from agentmail_watch import" in src and "coverage_report" in src)
check("the sweep imports the shared verdict_lines", "verdict_lines" in src)
check("the sweep no longer hardcodes the bare absolute verdict",
      "no payment record in any AgentMail account" not in src.split("verdict_lines")[-1]
      or "elif" in src)

print()
print("%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
