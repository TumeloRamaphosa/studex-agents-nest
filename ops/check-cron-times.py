#!/usr/bin/env python3
"""Check that every cron job fires at the time its own NAME promises.

WHY THIS EXISTS
---------------
Six jobs were running two hours off their names. The root cause was not the
cron expression - it was that `openclaw cron edit <id> --cron <expr>` RESETS
the job's timezone to UTC when --tz is not passed with it. So an edit that
looked correct (the expr hour now reads 09:00) moved the job from 09:00 SAST
to 09:00 UTC = 11:00 SAST. The expr alone cannot tell you when a job fires.

The ONLY trustworthy signal is nextRunAtMs in the job's own state, read back
from jobs.json after the edit.

This checker therefore:
  1. extracts the clock time from each enabled job's NAME
  2. converts that job's nextRunAtMs to SAST
  3. fails if they differ
  4. fails if an enabled job has a null timezone (the --cron trap)

Usage: python3 ops/check-cron-times.py [path/to/jobs.json]
Exit:  0 = all good, 1 = at least one job is off
"""
import json
import pathlib
import re
import sys
from datetime import datetime, timezone, timedelta

SAST = timezone(timedelta(hours=2))
DEFAULT = "/root/.openclaw/cron/jobs.json"


def name_time(name):
    """The clock time a job's NAME promises, as "HH:MM".

    A RANGE name ("Research Hour — 10-11 PM SAST") promises its START time.
    A job named "10-11 PM" begins at 10 PM and runs for an hour - it does not
    begin at 11 PM. Parsing the range's END made the checker validate 23:00
    against a job that was supposed to start at 22:00, so the wrong schedule
    looked correct and the checker could not catch it.
    """
    # A RANGE first: "10-11 PM SAST" / "9 AM - 11 AM SAST" -> take the START.
    m = re.search(r"(\d{1,2})(?:\s*[-–]\s*\d{1,2})\s*(AM|PM)\s*SAST", name, re.I)
    if m:
        return f"{(int(m.group(1)) % 12) + (12 if m.group(2).upper() == 'PM' else 0):02d}:00"
    m = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", name)
    if m:
        h = int(m.group(1)) % 12 + (12 if m.group(3).upper() == "PM" else 0)
        return f"{h:02d}:{m.group(2)}"
    m = re.search(r"(\d{1,2})\s*PM\s*SAST", name)
    if m:
        return f"{(int(m.group(1)) % 12) + 12:02d}:00"
    m = re.search(r"(\d{1,2})\s*AM\s*SAST", name)
    if m:
        return f"{int(m.group(1)) % 12:02d}:00"
    m = re.search(r"(\d{1,2}):(\d{2})\s*SAST", name)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    # "Midnight" and "Noon" are clock times too - without this the checker
    # silently skipped the Vault Sync EOD job entirely.
    if re.search(r"\bMIDNIGHT\b", name, re.I):
        return "00:00"
    if re.search(r"\bNOON\b", name, re.I):
        return "12:00"
    return None

def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(DEFAULT)
    d = json.loads(path.read_text(encoding="utf8"))
    jobs = d.get("jobs", d if isinstance(d, list) else [])

    issues = []
    checked = 0
    for j in jobs:
        if not j.get("enabled"):
            continue
        sched = j.get("schedule") or {}
        if sched.get("kind") != "cron":
            continue
        name = j.get("name", "")
        jid = j.get("id", "")
        tz = sched.get("tz")
        st = j.get("state") or {}
        nr = st.get("nextRunAtMs")

        if not tz:
            issues.append(f"{name!r} ({jid}) - enabled job has NO timezone (tz={tz!r}); "
                          f"`cron edit --cron` without --tz silently clears it")
            continue

        want = name_time(name)
        if not want or not nr:
            continue
        actual = datetime.fromtimestamp(nr / 1000, tz=timezone.utc).astimezone(SAST).strftime("%H:%M")
        checked += 1
        if actual != want:
            issues.append(f"{name!r} ({jid}) - name promises {want} SAST but nextRunAtMs "
                          f"fires at {actual} SAST (expr={sched.get('expr')!r}, tz={tz!r})")
        elif "SAST" in name and "Johannesburg" not in str(tz):
            # The stored next-run matches the name, but the job is scheduled in
            # UTC while its name promises SAST. That means the expr hours are
            # being read as UTC - so the moment the engine RECOMPUTES the next
            # run (after any edit, or a restart) the job silently shifts by two
            # hours. Flag it now rather than discover it then.
            issues.append(f"{name!r} ({jid}) - name promises {want} SAST but the job is scheduled "
                          f"in tz={tz!r}; the expr hours will be re-read as UTC and the job will "
                          f"shift by 2 hours on the next recompute")

    print(f"cron time check: {checked} time-named job(s) verified against nextRunAtMs")
    if issues:
        print(f"\n{len(issues)} PROBLEM(S):")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("all time-named jobs fire at the time their name promises")
    return 0


if __name__ == "__main__":
    sys.exit(main())
