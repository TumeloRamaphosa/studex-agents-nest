#!/usr/bin/env python3
"""
Check that no cron payload hardcodes a system-status claim.

WHY THIS EXISTS
---------------
On 2026-10-24 the Discord Ops Morning Summary published this to #ops:

    **🛒 Shopify:** 🔴 77+ days dark — Admin API token expired.
    **✅ Systems live:** Discord ✅ | AgentMail ✅ | Orgo VM 47.236.124.79 ✅ | Composio MCP ✅

Both halves are false. The storefront was live and selling (only the Admin API
is dark), and 47.236.124.79 is the *Alibaba Cloud VM*, which was down - and
which is not Orgo.

The 2026-10-22 fix had already made `discord-ops-bot/src/sendSummary.js` probe
every system live at send time, and the drift checker already scanned that
file. The fix was correct and complete. It never fired - because the cron
PAYLOAD was not calling the script at all. It was publishing its own
hard-coded copy of the briefing, and the checker was scanning the script.

The rule that was broken, stated generally: **a checker that only checks what
it was told to check.** The guarded surface and the publishing surface were
different files. This checker covers the publishing surface.

THE INVARIANT
-------------
An enabled job's payload must not assert the live status of a system. Status
is probed at send time by the script; a payload that hardcodes it will be
wrong the moment the world changes, and it will be wrong *silently*.

We express this as "a system name and a status marker on the same line"
rather than as a list of banned sentences, because a banned-sentence list
only catches the sentences we already know about - which is exactly how the
previous guard let a paraphrase through.

EXIT CODES
----------
0  CLEAN
1  DRIFT (a payload hardcodes a status claim)
2  UNCHECKED (the cron file could not be read - NOT a pass)
"""

import json
import os
import re
import sys

JOBS_FILE = os.environ.get("CRON_JOBS_FILE", "/root/.openclaw/cron/jobs.json")

# Systems whose live status the briefing reports on.
SYSTEM_NAMES = [
    "shopify",
    "alibaba",
    "orgo",
    "hub",
    "gitea",
    "blotato",
    "feedhive",
    "agentmail",
    "meta",
]

# Emoji / glyph markers that turn a mention into a STATUS CLAIM.
STATUS_MARKERS = ["✅", "❌", "🔴", "🟡", "🟢", "🔵", "⚠️", "🚨", "❗"]

# How far from the system NAME a status marker may sit and still count as
# asserting that system's status. A warning about a DEAD inbox 250 characters
# away is not a claim that AgentMail is up - and a rule that reads it as one
# will get switched off, and then it will protect nothing.
MARKER_WINDOW = 60

# Specific banned phrasings from the incident, kept as belt-and-braces.
BANNED_PATTERNS = [
    (r"Orgo\s+VM\s+47\.236\.124\.79", "Orgo mislabelled with the Alibaba Cloud VM IP"),
    (r"Orgo\s+VM\s*\(\s*Alibaba", "Alibaba Cloud VM described as Orgo"),
    (r"\d+\s*\+\s*days\s+dark", "a stale 'N+ days dark' count"),
    (r"Storefront:\*\*\s*dark", "the Shopify storefront declared dark"),
    (r"✅\s*Systems\s+live", "the old hard-coded 'Systems live' template"),
]


def iter_strings(node):
    """Yield every string anywhere under a node."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from iter_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_strings(v)


def scan_text(text):
    """Return a list of (reason, line) for every status claim found."""
    hits = []
    for i, line in enumerate(text.split("\n"), 1):
        low = line.lower()
        for name in SYSTEM_NAMES:
            for m in re.finditer(re.escape(name), low):
                start, end = m.span()
                window = line[max(0, start - MARKER_WINDOW): end + MARKER_WINDOW]
                if any(sym in window for sym in STATUS_MARKERS):
                    hits.append(("hardcoded status for '%s'" % name, i, line.strip()[:160]))
                    break
            else:
                continue
            break
    for pat, why in BANNED_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            line_no = text[: m.start()].count("\n") + 1
            hits.append((why, line_no, m.group(0)[:160]))
    return hits


def main():
    if not os.path.exists(JOBS_FILE):
        print("UNCHECKED - cron file not found: %s" % JOBS_FILE)
        print("A missing file is not a pass. Nothing was asserted.")
        return 2
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print("UNCHECKED - cron file unreadable: %s (%s)" % (JOBS_FILE, exc))
        return 2

    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    if not isinstance(jobs, list):
        print("UNCHECKED - unexpected jobs shape in %s" % JOBS_FILE)
        return 2

    issues = []
    disabled_notes = []
    scanned = 0
    for job in jobs:
        if not isinstance(job, dict):
            continue
        jid = job.get("id", "?")
        name = job.get("name", "?")
        enabled = job.get("enabled", True)
        payload = job.get("payload") or {}
        text = "\n".join(iter_strings(payload))
        if not text.strip():
            continue
        scanned += 1
        hits = scan_text(text)
        if not hits:
            continue
        if not enabled:
            disabled_notes.append((jid, name, hits))
            continue
        for why, line_no, snippet in hits:
            issues.append("DRIFT  job %s (%s) line %d: %s | %s" % (jid, name, line_no, why, snippet))

    for jid, name, hits in disabled_notes:
        for why, line_no, snippet in hits:
            print("note    DISABLED job %s (%s) line %d: %s | %s" % (jid, name, line_no, why, snippet))

    if issues:
        print("RESULT: DRIFT")
        for i in issues:
            print("  " + i)
        print("%d payload(s) scanned, %d issue(s)." % (scanned, len(issues)))
        return 1

    print("CLEAN   %d payload(s) scanned - no hardcoded system-status claims" % scanned)
    return 0


if __name__ == "__main__":
    sys.exit(main())
