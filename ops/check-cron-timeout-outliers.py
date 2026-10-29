#!/usr/bin/env python3
"""Flag a cron job whose timeout is an OUTLIER against its own siblings.

WHY THIS EXISTS
---------------
On 2026-10-29 the 09:00 CEO Standup (`ceo-standup-0900`) was killed by its own
300-second budget - 3.5 seconds past the line - with an empty summary and
`deliveryStatus: unknown`. Tumelo simply did not get his standup, and nothing
said so: the job was "supposed to" work, so nobody read its run record.

Every sibling had 1800-3600 seconds. The 22 Oct round that raised the fleet's
timeouts never included this job: it was ONE NUMBER away from working, and
nobody diffed the fleet against itself.

So the defect is not "a timeout is too short" - a short timeout is a perfectly
legitimate choice for a quick job. The defect is a timeout that is an OUTLIER
in its own family: the same kind of job, the same name, the same channel,
carrying a budget an order of magnitude smaller than its siblings.

THE RULE
--------
Group the enabled jobs by NAME FAMILY (the words before the time part). For a
family with two or more members, a member whose timeout is less than a quarter
of the family's maximum is flagged.

One-sided on purpose: a LARGER budget is harmless, a smaller one silently
kills the job and reports nothing.

The threshold is 25% because the real defect was 300s against 1800s (17%). A
family whose members sit within 4x of each other is left alone - a guard that
cries wolf on working jobs gets switched off, and that is exactly how the
PLACEHOLDER it exists to catch slips through.

WHAT THIS CHECKER DOES NOT DO
-----------------------------
It does not read run history and it does not call any provider. It answers ONE
question: "is any job's budget an outlier against its own siblings?" A green
answer says nothing about whether the jobs ran - that is the `cron-times`
checker's question, and the gap this checker leaves (a fleet member that DIED
rather than one that was mis-budgeted) is recorded in HEARTBEAT.md.

Usage: python3 ops/check-cron-timeout-outliers.py [path/to/jobs.json]
Exit:  0 = no outlier, 1 = at least one outlier
"""
import json
import pathlib
import re
import sys

DEFAULT = "/root/.openclaw/cron/jobs.json"

# A member below this fraction of its family's maximum is an outlier.
OUTLIER_FRACTION = 0.25


def family(name):
    """The name of the KIND of job, without the time it runs at.

    "CEO Standup - 9:00 AM SAST" and "CEO Standup - 10:00 PM SAST" are the
    same kind of job and must be compared against each other; a "Midday
    Nudge" is not.
    """
    head = re.split(
        r"\s[\u2014\u2013-]\s"
        r"|\s+\d{1,2}:\d{2}"
        r"|\s+\d{1,2}\s?(?:AM|PM)"
        r"|\s+MIDNIGHT\b"
        r"|\s+NOON\b",
        name or "",
        maxsplit=1,
        flags=re.I,
    )[0]
    words = re.findall(r"[A-Za-z0-9']+", head)[:3]
    return " ".join(w.lower() for w in words)


def timeout_of(job):
    """The job's declared budget in seconds, or None if it declares none."""
    payload = job.get("payload") or {}
    t = payload.get("timeoutSeconds")
    if isinstance(t, bool) or not isinstance(t, (int, float)):
        return None
    return int(t)


def collect(jobs):
    """-> {family: [(name, id, timeout), ...]} for enabled cron jobs with a budget."""
    groups = {}
    for j in jobs:
        if not j.get("enabled"):
            continue
        sched = j.get("schedule") or {}
        if sched.get("kind") != "cron":
            continue
        t = timeout_of(j)
        if t is None:
            continue
        groups.setdefault(family(j.get("name", "")), []).append(
            (j.get("name", ""), j.get("id", ""), t)
        )
    return groups


def outliers(groups):
    """-> [(name, id, timeout, family_max, family)] for every budget that is an outlier."""
    out = []
    for fam, members in groups.items():
        if len(members) < 2:
            continue
        fmax = max(m[2] for m in members)
        for name, jid, t in members:
            if t < fmax * OUTLIER_FRACTION:
                out.append((name, jid, t, fmax, fam))
    return out


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(DEFAULT)
    d = json.loads(path.read_text(encoding="utf8"))
    jobs = d.get("jobs", d if isinstance(d, list) else [])
    groups = collect(jobs)
    issues = outliers(groups)

    compared = sum(len(v) for v in groups.values() if len(v) > 1)
    print("cron timeout outlier check: %d enabled job(s) with a budget, %d family(ies), "
          "%d comparable in a family of 2+" % (sum(len(v) for v in groups.values()),
                                               len(groups), compared))
    if issues:
        print("\n%d OUTLIER(S) - a job budgeted far below its own siblings:" % len(issues))
        for name, jid, t, fmax, fam in issues:
            print("  - %r (%s) has %ds where its family %r max is %ds (%.0f%%) - "
                  "a job killed by its own budget arrives with an empty summary and "
                  "no announcement" % (name, jid, t, fam, fmax, 100.0 * t / fmax))
        return 1
    print("no job's timeout is an outlier against its own siblings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
