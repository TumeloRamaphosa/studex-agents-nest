"""The single source of truth for which AgentMail inboxes we WATCH, and the
COVERAGE arithmetic that every sweep must report.

WHY THIS IS A SEPARATE MODULE
------------------------------
Before 2026-10-24 there was no shared list. `scripts/mail-sweep3.py` carried
its own `WATCH` dict and `scripts/badge-payment-sweep.py` enumerated only the
inboxes a key could *see*. That second behaviour is the dangerous one: an
inbox that returns 404 cannot be enumerated, so it cannot even be reported as
missing. The sweep said "VERDICT: NOT_PAID - no payment record in any
AgentMail account" while two addresses we believe are active were
unreadable. A verdict that does not state its coverage asserts more than it
checked.

So the list is shared, every sweep compares what it READ against what we
BELIEVE is active, and the difference is reported as a coverage gap.

`coverage_report` and `verdict_lines` are pure functions so they can be
unit-tested with NO NETWORK. A checker that cannot be exercised is a checker
that cannot be trusted.
"""

# Addresses we believe are active and must be read by any sweep.
# `KNOWN_UNREACHABLE` is a DOCUMENTED GAP, not a removal: keep the address
# watched so that the day it comes back we notice, and keep it reported so
# nobody reads "0 messages" as "nothing to worry about".
WATCH = {
    "t.ramaphosa@agentmail.to",
    "project-2571-studex-agent-2077@agentmail.to",
    "uglyrestaurant62@agentmail.to",
    "studex-2571@agentmail.to",
    "robusca.romanov@studex-group.com",
    "naledi.cmo@studex-group.com",
    "naledi-cmo@studex-group.com",
    "sales@studex-group.com",
    "meat@studex-group.com",
    "info@studex-group.com",
    "t-ramaphosa-ceo@studex-group.com",
}

# Documented coverage gaps, verified by GET against every usable key.
# Each was checked on the date recorded; a sweep that finds one readable
# again should drop it from this set.
KNOWN_UNREACHABLE = {
    "studex-2571@agentmail.to": (
        "RE-PROBED 2026-10-26: HTTP 200 on the MAIN key (0 messages), HTTP 404 "
        "on the CIIE key only. The old '404 on all 5 usable keys' note is stale. "
        "It is LIVE-BUT-EMPTY on the main account, not dead: mail sent here is "
        "visible to a main-key sweep. Owner action: confirm which account it "
        "should live on, and whether it should receive."),
    "naledi.cmo@studex-group.com": (
        "RE-PROBED 2026-10-26: still HTTP 404 on the main key. Dotted variant; "
        "the live inbox is naledi-cmo@studex-group.com (hyphen). Stale entry."),
}


def coverage_report(watch, readable, dead_keys, failed_inboxes):
    """Describe what a sweep could NOT read.

    Returns (lines, gap_count, missing_watch).
      watch          - addresses we believe are active
      readable       - addresses the sweep actually read
      dead_keys      - [(key_prefix, http_code)] - keys that answered non-200
      failed_inboxes - [(address, http_code)] - inboxes that would not list
    """
    missing_watch = sorted(a for a in watch if a not in readable)
    lines = []
    if dead_keys:
        lines.append("  DEAD KEYS (%d) - could not enumerate any inbox:" % len(dead_keys))
        for k, c in dead_keys:
            lines.append("    key %s -> HTTP %s" % (k, c))
    if failed_inboxes:
        lines.append("  INBOXES THAT WOULD NOT LIST (%d):" % len(failed_inboxes))
        for a, c in failed_inboxes:
            lines.append("    %s -> HTTP %s" % (a, c))
    if missing_watch:
        lines.append(
            "  WATCH ADDRESSES NOT READ (%d) - a payment record held here would "
            "NOT appear in this verdict:" % len(missing_watch))
        for a in missing_watch:
            why = KNOWN_UNREACHABLE.get(a, "no note")
            lines.append("    %s  [%s]" % (a, why))
    gap = len(dead_keys) + len(failed_inboxes) + len(missing_watch)
    return lines, gap, missing_watch


def verdict_lines(hits, gap, readable_count, total):
    """The verdict text. When there is a coverage gap the verdict MUST say so.

    A bare "NOT_PAID" is indistinguishable from a complete search, and that
    difference is the whole point: "no payment in what we could read" is not
    the same claim as "no payment exists".
    """
    if hits:
        return ["", "VERDICT: PAID - payment record FOUND"]
    if gap:
        return [
            "",
            "VERDICT: NOT_PAID - no payment record across the %d readable "
            "inbox(es) / %d messages." % (readable_count, total),
            "         \u26a0\ufe0f QUALIFIED: this sweep could not read %d watched "
            "place(s) (see COVERAGE). A record held in an" % gap,
            "         unreadable place would NOT appear here. Do not read this as",
            "         'no payment exists' - it is 'no payment in what we could read'.",
        ]
    return [
        "",
        "VERDICT: NOT_PAID - no payment record in any AgentMail account "
        "(%d inboxes, %d messages, no coverage gaps)" % (readable_count, total),
    ]
