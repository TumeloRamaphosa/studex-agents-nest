#!/usr/bin/env python3
"""Flag a cron job whose LAST run was killed by a timeout its CURRENT budget cannot avoid.

WHY THIS EXISTS
---------------
The canonical pass cannot see a cron job that DIED. `cron-times` asks "does
this job fire when its name promises?", `cron-payload-claims` asks "does this
payload hardcode a status claim?", and `cron-timeouts` asks "is this budget an
outlier against its siblings?" - none of them reads whether the job's last run
survived. On 2026-10-29 the 09:00 CEO Standup was killed by its own
300-second budget and **nobody noticed for a day**: the job was "supposed to"
work, so its run record was never read. Tumelo did not get his standup and
nothing said so.

THE RULE
--------
For each enabled job with a declared budget:

  * take the job's MOST RECENT run record (the last thing that happened to it)
  * if that run was NOT a timeout kill, the job is fine - one bad hour is not
    a pattern, and the next run is the proof
  * if it WAS a timeout kill, compare the run's duration against the job's
    CURRENT budget:
      - duration >= current budget  => FINDING. The same budget would kill it
        again tomorrow. Raise the budget or cut the work.
      - duration <  current budget  => the budget has since been raised past
        the kill point, so the kill is unlikely to repeat. NOT a finding - the
        fix is waiting for its next run to prove itself, not for a checker to
        announce it.

That second branch is the whole point. A checker that reports "this job timed
out" forever would cry wolf on every job that has already been fixed and
still awaits its next run - and a guard that cries wolf gets switched off.

Freshness: a last run older than 7 days is not actionable (the job may not
even run that often). The rule answers "would it die again", and a month-old
kill is not that question.

Usage: python3 ops/check-cron-timeout-kills.py [jobs.json] [runs_dir]
Exit:  0 = no recurring kill, 1 = a job would be killed again by the same budget,
       2 = could not prove (a timed-out run with no duration to measure against)
"""
import json
import pathlib
import sys
import time

DEFAULT_JOBS = "/root/.openclaw/cron/jobs.json"
DEFAULT_RUNS = "/root/.openclaw/cron/runs"
MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000  # a week


def load_jobs(path):
    d = json.loads(pathlib.Path(path).read_text(encoding="utf8"))
    jobs = d.get("jobs", d if isinstance(d, list) else [])
    out = {}
    for j in jobs:
        if not j.get("enabled"):
            continue
        payload = j.get("payload") or {}
        t = payload.get("timeoutSeconds")
        if isinstance(t, bool) or not isinstance(t, (int, float)):
            continue
        out[j.get("id")] = {"name": j.get("name", ""), "timeout": int(t)}
    return out


def last_record(runs_dir, jid):
    """The most recent run record for a job, or None if it has never run."""
    p = pathlib.Path(runs_dir) / ("%s.jsonl" % jid)
    if not p.exists():
        return None
    best = None
    for line in p.read_text(encoding="utf8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if not isinstance(rec, dict):
            continue
        ts = rec.get("ts")
        if not isinstance(ts, (int, float)):
            continue
        if best is None or ts > best.get("ts", 0):
            best = rec
    return best


def timed_out(rec):
    if not rec:
        return False
    if rec.get("status") != "error":
        return False
    err = str(rec.get("error") or "").lower()
    return "timed out" in err or "timeout" in err


def main():
    jobs_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JOBS
    runs_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_RUNS
    jobs = load_jobs(jobs_path)
    now = time.time() * 1000

    findings = []
    unproven = []
    considered = 0
    kills = 0

    for jid, meta in jobs.items():
        rec = last_record(runs_dir, jid)
        if not rec:
            continue
        age = now - (rec.get("ts") or 0)
        if age > MAX_AGE_MS:
            continue
        considered += 1
        if not timed_out(rec):
            continue
        kills += 1
        dur = rec.get("durationMs")
        if not isinstance(dur, (int, float)) or isinstance(dur, bool):
            unproven.append((meta["name"], jid, meta["timeout"], None))
            continue
        if dur >= meta["timeout"] * 1000:
            findings.append((meta["name"], jid, meta["timeout"], int(dur)))

    print("cron timeout-kill check: %d job(s) with a budget, %d ran in the last 7 days, "
          "%d last-run timeout kill(s)" % (len(jobs), considered, kills))
    if unproven:
        print("\n%d COULD NOT PROVE - a timed-out run with no duration to measure:" % len(unproven))
        for name, jid, timeout, dur in unproven:
            print("  - %r (%s) has a current budget of %ds and its last run has no durationMs"
                  % (name, jid, timeout))
    if findings:
        print("\n%d RECURRING KILL(S) - the current budget would kill the job again:" % len(findings))
        for name, jid, timeout, dur in findings:
            print("  - %r (%s) was killed at %ds with a budget of %ds - the same budget "
                  "would kill it again, and a killed job arrives with an empty summary "
                  "and no announcement" % (name, jid, dur // 1000, timeout))
        return 1
    if unproven:
        return 2
    print("no job's last run was killed by a timeout its current budget could not have avoided")
    return 0


if __name__ == "__main__":
    sys.exit(main())
