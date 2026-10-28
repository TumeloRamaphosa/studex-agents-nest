#!/usr/bin/env python3
"""
No live instruction may direct the agent to use a service whose credential is DEAD.

WHY THIS EXISTS
---------------
The 09:00 SAST publish job's payload said "Use the FeedHive API to upload any
images and schedule the post" - and FeedHive's key has been dead since
2026-10-05, with every endpoint returning 404. The posting SKILL repeated it
in its Overview, in its cron payload template, and in a copy-paste Python
block that called https://api.feedhive.com/v1/media/upload. That file even
said "use Blotato as the publish path" and then showed the dead call, so the
copy-paste block won.

The consequence was not an error message - it was a SILENT one: the caption
published with NO image, because the image never got uploaded. Two of the last
ten live posts shipped with no picture.

THE INVARIANT
-------------
1. A cron payload must not name a service whose credential is dead. A payload
   is a bare instruction - it has no room for a warning, so any mention is an
   instruction to use it.
2. The posting skill must not contain EXECUTABLE code that calls a dead
   service. Prose warning that it is dead is fine, and is wanted.

EXIT CODES
----------
0  CLEAN
1  DRIFT
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

JOBS_FILE = os.environ.get("CRON_JOBS_FILE", "/root/.openclaw/cron/jobs.json")
SKILL = os.environ.get("POSTING_SKILL", "/workspace/skills/studex-daily-posting/SKILL.md")

# A service is listed here when its credential is dead AND its API no longer
# answers. The endpoint is PROBED, so a stale entry cannot hide: if the
# service ever comes back, this test fails and the entry must be removed
# deliberately.
DEAD_SERVICES = {"feedhive": "https://api.feedhive.com/v1/accounts"}


def iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from iter_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_strings(v)


def code_blocks(text):
    """The fenced code blocks of a markdown file (odd parts of the split)."""
    parts = text.split("```")
    return [parts[i] for i in range(1, len(parts), 2)]


def mentions_dead_service(text):
    low = text.lower()
    return sorted(s for s in DEAD_SERVICES if s in low)


# A mention that the same line negates is NOT an instruction to use the service.
# "do NOT call FeedHive" is the best instruction we can give; "use the FeedHive
# API to upload" is the bug. So a NEGATED mention is allowed and an affirmative
# one is a violation.
NEGATION_MARKERS = ("not", "never", "don't", "dont", "dead", "404", "instead", "avoid", "no feedhive")


def unnegated_mentions(text):
    """Dead services mentioned AFFIRMATIVELY (i.e. as something to use)."""
    hits = set()
    for line in text.split("\n"):
        low = line.lower()
        for svc in mentions_dead_service(line):
            if not any(marker in low for marker in NEGATION_MARKERS):
                hits.add(svc)
    return sorted(hits)


def service_is_actually_dead(url):
    """True if the endpoint does not answer with success. None = could not tell."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dead-service-check"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status >= 400
    except urllib.error.HTTPError as e:
        return True
    except Exception:
        return None


def main():
    failures = []

    # --- the dead list must still be true ---------------------------------
    for svc, url in DEAD_SERVICES.items():
        dead = service_is_actually_dead(url)
        if dead is False:
            failures.append("STALE: %s answered successfully at %s - it is alive, "
                            "remove it from DEAD_SERVICES and fix the instructions" % (svc, url))
        elif dead is None:
            print("note: could not probe %s (%s) - the list is unverified, the scan still runs"
                  % (svc, url))

    # --- 1. the live cron payloads ----------------------------------------
    if not os.path.exists(JOBS_FILE):
        print("UNCHECKED - cron file not found: %s (a missing file is not a pass)" % JOBS_FILE)
        return 1
    with open(JOBS_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    scanned = 0
    for job in jobs:
        if not isinstance(job, dict) or not job.get("enabled", True):
            continue
        text = "\n".join(iter_strings(job.get("payload") or {}))
        if not text.strip():
            continue
        scanned += 1
        for svc in unnegated_mentions(text):
            failures.append("DRIFT  job %s (%s) tells the agent to use the DEAD service '%s'"
                            % (job.get("id"), job.get("name"), svc))

    # --- 2. the posting skill's EXECUTABLE code ---------------------------
    if not os.path.exists(SKILL):
        print("UNCHECKED - skill not found: %s (a missing file is not a pass)" % SKILL)
        return 1
    with open(SKILL, "r", encoding="utf-8") as fh:
        skill = fh.read()
    blocks = code_blocks(skill)
    for i, block in enumerate(blocks):
        for svc in unnegated_mentions(block):
            failures.append("DRIFT  %s code block %d calls the DEAD service '%s'"
                            % (os.path.basename(SKILL), i, svc))

    # --- NEGATIVE CONTROLS: the scan must be able to fail ------------------
    fake_payload = "Run the skill. Use the FeedHive API to upload any images."
    if not unnegated_mentions(fake_payload):
        failures.append("NEGATIVE CONTROL FAILED: a payload naming 'feedhive' was not detected")
    fake_block = "import requests\nrequests.post('https://api.feedhive.com/v1/media/upload')\n"
    if not unnegated_mentions(fake_block):
        failures.append("NEGATIVE CONTROL FAILED: a code block calling 'feedhive' was not detected")
    # positive control: prose that WARNS about the dead service must NOT trip it
    fake_prose = "The FeedHive key is DEAD - never call it."
    if unnegated_mentions(fake_prose):
        failures.append("POSITIVE CONTROL FAILED: prose warning about 'feedhive' was flagged")
    # positive control 2: the CORRECT instruction - "do NOT call it" - must be allowed
    good_instruction = "Use the '**Media URL:**' line and do NOT call the FeedHive API."
    if unnegated_mentions(good_instruction):
        failures.append("POSITIVE CONTROL FAILED: the correct negated instruction was flagged")

    if failures:
        for f in failures:
            print("FAIL  " + f)
        print("%d failure(s)." % len(failures))
        return 1

    print("%d payload(s) and %d skill code block(s) scanned - no instruction names a dead service."
          % (scanned, len(blocks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
