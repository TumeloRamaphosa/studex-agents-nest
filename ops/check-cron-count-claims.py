#!/usr/bin/env python3
"""
Check that a cron payload's COUNT claims match the registry they describe.

WHY THIS EXISTS (2026-10-31)
---------------------------
The `cta-on-feed` checker was registered as the 26th checker at ~02:20Z. The
canonical pass's own payload still said:

    It is 25 READ-ONLY checkers and takes about 4 minutes.

So the pass would run 26 checkers while its instructions told the agent it
was running 25. The number in the instructions is a CLAIM about the thing the
instructions describe, and a claim that is one behind is a lie that reads like
a number.

🔑 WHY NOTHING CAUGHT IT
The registry test (`ops/test-heartbeat-registry.py`) verifies that every
checker ON DISK is classified and every registered checker EXISTS. Neither
direction is the same question as "does the payload's number match the
registry's number". The payload-claims checker
(`ops/check-cron-payload-claims.py`) verifies that a payload does not assert
a FALSE STATUS - "25 checkers" was not a false status, just a stale number.
🔑 *A claim can be wrong without being false-sounding, and a guard that only
catches false-sounding claims will not catch a stale number.*

THE RULE
--------
If a payload says "N checkers" (or names a checker COUNT), that N must equal
the number of checkers the registry says will run. A payload that is merely
silent about the count is fine - the rule only bites on a number that is
stated, because a stated number is the one an agent will quote back.

The count is derived from the registry: rows whose class is PASS (i.e. the
checkers that actually RUN in the pass) - SCOPE rows are libraries or
one-shot tools that are invoked by something else, and counting them would
make the rule wrong in the other direction.

EXIT CODES
----------
0  CLEAN (no count claim, or every count claim matches)
1  DRIFT (a payload states a checker count that the registry contradicts)
2  UNCHECKED (the registry or the cron file could not be read - NOT a pass)
"""

import json
import os
import re
import sys

JOBS_FILE = os.environ.get("CRON_JOBS_FILE", "/root/.openclaw/cron/jobs.json")
REGISTRY = os.environ.get(
    "HEARTBEAT_CHECKERS_TSV",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "heartbeat-checkers.tsv"),
)

# "25 READ-ONLY checkers", "25 checkers", "It is 26 checkers and takes...".
# The number must be immediately followed by the word, so a payload saying
# "the 2026-10-25 checkers" is not read as a count claim.
#
# Two details that the real payload forced:
#   * the word between the number and "checkers" can be HYPHENATED
#     ("25 READ-ONLY checkers") - a plain \w+ does not match "READ-ONLY",
#     which silently made the rule never fire on the very payload it was
#     written for.
#   * a number that is part of a DATE or an ID must not be read as a count
#     ("2026-10-25 checkers" is not a claim of 25 checkers) - hence the
#     lookbehind, which refuses a number preceded by a digit or a hyphen.
COUNT_CLAIM_RE = re.compile(
    r"(?<![\d-])(\d{1,3})\s+(?:[\w'-]+\s+){0,3}?checkers?\b", re.I)

# A payload that says "25 checkers" is a count claim. One that says "checkers"
# alone is not. This also keeps out lines that mention a checker BY NAME with
# a number next to it ("checker 25") - that is an id, not a count.
COUNT_BY_NAME_RE = re.compile(r"\bchecker\s+(\d{1,3})\b", re.I)


def registry_count(path=REGISTRY):
    """The number of checkers that actually RUN in the pass.

    PASS rows run. SCOPE rows are libraries or one-shot tools invoked by
    something else. Anything else (a blank line, a comment) does not count.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            rows = [ln for ln in fh.read().splitlines() if ln.strip()]
    except Exception as exc:
        return None, "cannot read the registry (%s)" % exc
    n = 0
    for ln in rows:
        if ln.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) >= 3 and parts[2].upper() == "PASS":
            n += 1
    if n == 0:
        return None, "the registry lists no PASS checkers - cannot prove the count"
    return n, None


def jobs_from_file(path=JOBS_FILE):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            data = json.load(fh)
    except Exception as exc:
        return None, "cannot read the cron file (%s)" % exc
    if isinstance(data, dict):
        for key in ("jobs", "items"):
            if isinstance(data.get(key), list):
                return data[key], None
        return None, "the cron file has no job list"
    if isinstance(data, list):
        return data, None
    return None, "the cron file has an unexpected shape"


def payload_text(job):
    p = job.get("payload")
    if isinstance(p, dict):
        return p.get("message") or ""
    if isinstance(p, str):
        return p
    return job.get("message") or ""


def claims_in(text):
    """Every checker-count claim in a payload, as (value, line) pairs."""
    out = []
    for i, line in enumerate(text.splitlines()):
        if COUNT_BY_NAME_RE.search(line):
            continue  # "checker 25" is an id, not a count
        for m in COUNT_CLAIM_RE.finditer(line):
            out.append((int(m.group(1)), line.strip()))
    return out


def main():
    n, err = registry_count()
    if n is None:
        print("UNCHECKED: %s" % err)
        return 2
    print("registry checkers that run: %d" % n)

    jobs, err = jobs_from_file()
    if jobs is None:
        print("UNCHECKED: %s" % err)
        return 2

    drift = []
    for job in jobs:
        if not job.get("enabled", True):
            continue
        text = payload_text(job)
        if not text:
            continue
        for value, line in claims_in(text):
            if value != n:
                drift.append((job.get("name") or job.get("id") or "?",
                              value, n, line))
    if drift:
        print("DRIFT: %d payload count claim(s) contradict the registry" % len(drift))
        for name, said, actual, line in drift:
            print("  [%s] says %d, the registry has %d" % (name, said, actual))
            print("      %s" % line[:150])
        print("REMEDY: update the payload's number to match the registry - a stated")
        print("        count is a claim the agent will quote back.")
        return 1
    print("VERDICT: CLEAN - every payload count claim matches the registry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
