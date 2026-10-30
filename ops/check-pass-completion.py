#!/usr/bin/env python3
"""Flag a canonical-pass slot that produced NO completed pass.

WHY THIS EXISTS
---------------
The canonical pass became a cron job on 2026-10-29 (hourly, :23 UTC). On
2026-10-30 the 03:23Z and 04:23Z slots NEVER RAN: both cron turns died after
~24 seconds with "API rate limit reached", before the runner was ever invoked.
No log file was written, no state key was added, no note was recorded, and
`delivered: false` sent nothing to Discord either.

**The guards were silent, not green.** Nothing in the pass could see it:
  * `cron-times` asks "does this job FIRE when its name promises?" - it fired
    on time and then died of an upstream rate limit. Perfectly healthy to that
    checker.
  * `cron-kills` asks "was the last run killed by its own TIMEOUT budget?" -
    these runs were not killed by a timeout; they were killed by a provider.
    Perfectly healthy to that checker too.
  * every other checker reads the state of the WORLD (live pages, feeds,
    credentials). None of them reads whether THE PASS ITSELF ran.

There was no checker for "the pass completed", and that is a hole in the pass
rather than a criticism of any individual checker.

THE RULE
--------
The pass is scheduled hourly at a fixed minute. For every slot in a recent
window the checker asks a single question: **is there a record that this slot
produced a COMPLETED pass?**

Evidence of a completed pass, any one of:
  * ops/logs/heartbeat-pass-<date>_<hhmm>.log containing a column-0 VERDICT
    line - the runner only prints that line after every checker has run
  * ops/logs/pass-record-<date>_<hhmm>.json - the pass record the pass writes
  * a `pass_<hhmm>_YYYY_MM_DD` key in memory/heartbeat-state.json

A slot with NO evidence at all is a MISSED pass: the guards did not run.
A slot whose log exists but never printed a VERDICT is an INCOMPLETE pass:
the runner started and died mid-way. Both are findings - a pass that did not
finish proves nothing, which is exactly the "could not prove" rule applied to
the pass itself.

WHY THE WINDOW
--------------
A missed slot is a permanent hole in the log, so an unbounded window would
re-announce a two-hour-old gap forever. The window is deliberately short
(6 hours): a gap stays visible for a few passes and then ages out, which is
the difference between a finding and a guard that cries wolf.

Slots are only EXPECTED once they are older than a 30-minute grace period:
the pass takes minutes to run, and the slot the pass is currently inside must
never be reported as missing by the pass itself.

Slots before the job was CREATED are not expected - the pass did not exist
then, and the cron job's own creation time is the honest start of the
obligation.

Usage: python3 ops/check-pass-completion.py [jobs.json] [logs_dir] [state.json] [now_ms]
Exit:  0 = every expected slot produced a completed pass
       1 = a slot was missed or the pass did not finish
       2 = could not prove (no such job / unreadable state / unsupported schedule)
"""
import json
import os
import pathlib
import sys
import time
from datetime import datetime, timedelta, timezone

DEFAULT_JOBS = "/root/.openclaw/cron/jobs.json"
DEFAULT_LOGS = "/workspace/ops/logs"
DEFAULT_STATE = "/workspace/memory/heartbeat-state.json"
PASS_JOB_HINT = "canonical heartbeat pass"
WINDOW_HOURS = 6
GRACE_MIN = 30
# A slot is expected only from the job's SECOND firing onward: the first
# firing is the one the job was created for, and its record may predate the
# naming convention every later slot follows.
SKIP_FIRST_SLOT = True


def parse_minute(expr):
    """Return the minute-of-hour for an hourly cron expr, or None if unsupported.

    Only `M * * * *` is supported. Anything else (a daily expr, a range in the
    minute field, a list) means the expected-slot set cannot be derived, and
    the honest answer is "could not prove" rather than a guess.
    """
    if not isinstance(expr, str):
        return None
    parts = expr.split()
    if len(parts) != 5:
        return None
    minute, hour, dom, month, dow = parts
    if hour != "*" or dom != "*" or month != "*" or dow != "*":
        return None
    if not minute.isdigit():
        return None
    m = int(minute)
    return m if 0 <= m <= 59 else None


def find_pass_job(jobs):
    for j in jobs:
        name = str(j.get("name") or "")
        if PASS_JOB_HINT in name.lower():
            return j
    return None


def slot_times(job, minute, now):
    """Every scheduled slot from the job's creation to now, newest last."""
    created = job.get("createdAtMs")
    if not isinstance(created, (int, float)) or isinstance(created, bool):
        return None
    start = datetime.fromtimestamp(created / 1000.0, tz=timezone.utc)
    # first slot at or after creation
    cur = start.replace(minute=minute, second=0, microsecond=0)
    if cur < start:
        cur += timedelta(hours=1)
    slots = []
    step = timedelta(hours=1)
    while cur <= now:
        slots.append(cur)
        cur += step
    return slots


def log_has_verdict(path):
    """True if the pass log contains a column-0 VERDICT line (the runner's own).

    The runner prints its summary and only THEN prints the column-0 VERDICT
    line, so a VERDICT line is proof the pass reached its end. A log with no
    VERDICT line is a pass that started and never finished.
    """
    try:
        text = path.read_text(encoding="utf8", errors="replace")
    except OSError:
        return False
    for line in text.splitlines():
        if line.startswith("VERDICT"):
            return True
    return False


def main():
    jobs_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JOBS
    logs_dir = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LOGS)
    state_path = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else DEFAULT_STATE)
    now_ms = int(sys.argv[4]) if len(sys.argv) > 4 else int(time.time() * 1000)

    try:
        raw = json.loads(pathlib.Path(jobs_path).read_text(encoding="utf8"))
    except Exception as e:
        print("pass-completion check: COULD NOT PROVE - cannot read %s (%s)"
              % (jobs_path, e))
        print("VERDICT: COULD NOT PROVE - the cron job list is unreadable")
        return 2
    jobs = raw.get("jobs", raw if isinstance(raw, list) else [])
    job = find_pass_job(jobs)
    if job is None:
        print("pass-completion check: COULD NOT PROVE - no job matching %r"
              % PASS_JOB_HINT)
        print("VERDICT: COULD NOT PROVE - the canonical pass job is not in the "
              "cron list, so its slots cannot be derived")
        return 2
    if not job.get("enabled"):
        print("pass-completion check: the canonical pass job is DISABLED - no slot is expected")
        print("VERDICT: CLEAN - the pass job is disabled, so no pass slot is owed")
        return 0

    sched = job.get("schedule") or {}
    minute = parse_minute(sched.get("expr"))
    if minute is None:
        print("pass-completion check: COULD NOT PROVE - schedule %r is not an hourly "
              "'M * * * *' expr" % (sched.get("expr"),))
        print("VERDICT: COULD NOT PROVE - the pass schedule cannot be turned into "
              "expected slots")
        return 2

    now = datetime.fromtimestamp(now_ms / 1000.0, tz=timezone.utc)
    slots = slot_times(job, minute, now)
    if not slots:
        print("pass-completion check: COULD NOT PROVE - the job has no creation time")
        print("VERDICT: COULD NOT PROVE - no job creation time, so no start of obligation")
        return 2
    if SKIP_FIRST_SLOT and len(slots) > 1:
        slots = slots[1:]

    grace = timedelta(minutes=GRACE_MIN)
    window_start = now - timedelta(hours=WINDOW_HOURS)
    expected = [s for s in slots
                if s <= now - grace and s >= window_start]

    state = None
    state_ok = True
    try:
        state = json.loads(state_path.read_text(encoding="utf8"))
        if not isinstance(state, dict):
            state = {}
    except Exception:
        state_ok = False
        state = {}

    missed = []
    incomplete = []
    unproven = []
    proved = 0
    for slot in expected:
        date_str = slot.strftime("%Y-%m-%d")
        hhmm = slot.strftime("%H%M")
        log = logs_dir / ("heartbeat-pass-%s_%s.log" % (date_str, hhmm))
        rec = logs_dir / ("pass-record-%s_%s.json" % (date_str, hhmm))
        key = "pass_%s_%s" % (hhmm, date_str.replace("-", "_"))

        if rec.exists() or (state_ok and key in state):
            proved += 1
            continue
        if log.exists():
            if log_has_verdict(log):
                proved += 1
            else:
                incomplete.append((slot, log))
            continue
        if not state_ok:
            unproven.append(slot)
            continue
        missed.append(slot)

    print("pass-completion check: %d expected slot(s) in the last %dh (from %s), "
          "%d proved complete, %d missed, %d incomplete, %d unproven"
          % (len(expected), WINDOW_HOURS,
             expected[0].strftime("%Y-%m-%d %H:%MZ") if expected else "n/a",
             proved, len(missed), len(incomplete), len(unproven)))

    problems = []
    for slot in missed:
        problems.append("slot %s UTC produced NO pass record at all - the pass did "
                        "not run, so the guards were silent rather than green"
                        % slot.strftime("%Y-%m-%d %H:%M"))
    for slot, log in incomplete:
        problems.append("slot %s UTC started (log %s exists) but never printed a "
                        "VERDICT line - the pass died mid-run and proved nothing"
                        % (slot.strftime("%Y-%m-%d %H:%M"), log.name))
    if unproven:
        print("\n%d COULD NOT PROVE - the slot(s) below cannot be judged:" % len(unproven))
        for slot in unproven:
            print("  - slot %s UTC - %s is unreadable and no log or record exists"
                  % (slot.strftime("%Y-%m-%d %H:%M"), state_path))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems:
            print("  - %s" % p)
        print("VERDICT: %d expected pass slot(s) did not complete - the guards did "
              "not run for that window" % len(problems))
        return 1
    if unproven:
        print("VERDICT: COULD NOT PROVE - %d slot(s) could not be judged" % len(unproven))
        return 2
    print("VERDICT: CLEAN - every expected pass slot produced a completed pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
