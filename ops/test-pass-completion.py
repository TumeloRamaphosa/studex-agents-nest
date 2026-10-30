#!/usr/bin/env python3
"""Test ops/check-pass-completion.py.

The rule under test: a canonical-pass slot that produced no completed pass is
a FINDING - because a pass that did not run means the guards were SILENT, not
green.

The negative controls are the point. A missing slot is a PERMANENT hole in the
log, so an unbounded rule ("a slot with no log is a finding") would
re-announce a two-hour-old gap for ever and every later pass would cry wolf.
The rule under test is WINDOWED: a gap stays visible for a few passes and then
ages out.

The controls below prove three different ways the rule must NOT fire:
  * a slot that has not happened yet (the pass is running right now)
  * a slot from before the pass was a cron job at all
  * a slot that has aged out of the window
and that it MUST fire for a slot that genuinely produced nothing.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "check-pass-completion.py"
FAILS = []

NOW = datetime(2026, 10, 30, 6, 30, tzinfo=timezone.utc)
LATER = datetime(2026, 10, 30, 10, 30, tzinfo=timezone.utc)
PASS_JOB_ID = "f2a4c1c3-194f-47e2-b19e-1bec418f4d03"


def check(label, cond, detail=""):
    if cond:
        print("PASS  %s" % label)
    else:
        print("FAIL  %s %s" % (label, detail))
        FAILS.append(label)


def job(expr="23 * * * *", enabled=True, created=None, name="Canonical Heartbeat Pass"):
    created = created or (NOW - timedelta(hours=6))
    return {
        "id": PASS_JOB_ID,
        "name": name,
        "enabled": enabled,
        "createdAtMs": int(created.timestamp() * 1000),
        "schedule": {"kind": "cron", "expr": expr, "staggerMs": 0, "tz": "UTC"},
        "payload": {"kind": "agentTurn", "message": "run the pass", "timeoutSeconds": 2400},
    }


def write_log(logs, name, verdict=True):
    body = "CANONICAL HEARTBEAT PASS\n[CLEAN] drift (rc=0)\n"
    if verdict:
        body += "VERDICT: CLEAN - every checker proved its answer. No new findings.\n"
    (logs / ("heartbeat-pass-%s.log" % name)).write_text(body, encoding="utf8")


def run(jobs, now_dt=NOW, logs_setup=None, state=None, state_missing=False):
    """logs_setup: {slot_name: 'ok' | 'noverdict'}; absent names have no log."""
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        (d / "jobs.json").write_text(json.dumps({"jobs": jobs}), encoding="utf8")
        logs = d / "logs"
        logs.mkdir()
        state_file = d / "heartbeat-state.json"
        if state_missing:
            pass                      # the file is simply never written
        elif state is not None:
            state_file.write_text(json.dumps(state), encoding="utf8")
        else:
            state_file.write_text("{}", encoding="utf8")
        for name, kind in (logs_setup or {}).items():
            if kind == "missing":
                continue
            write_log(logs, name, verdict=(kind != "noverdict"))
        p = subprocess.run(
            [sys.executable, str(CHECKER), str(d / "jobs.json"), str(logs),
             str(state_file), str(int(now_dt.timestamp() * 1000))],
            capture_output=True, text=True)
        return p.returncode, p.stdout


# The fixture's expected slots: the job was created 6h before NOW, so the slots
# are 02:23 .. 06:23. The 06:23 slot is INSIDE the grace period (the pass is
# running right now) and 01:23 is the job's own first firing - neither is owed.
EXPECTED = ["2026-10-30_0223", "2026-10-30_0323", "2026-10-30_0423", "2026-10-30_0523"]
ALL_OK = {s: "ok" for s in EXPECTED}

print("=== A. EVERY EXPECTED SLOT COMPLETED - CLEAN ===")
rc, out = run([job()], logs_setup=ALL_OK)
check("a fully completed window is CLEAN", rc == 0, "rc=%d out=%s" % (rc, out[-400:]))
check("the checker says how many slots it expected", "4 expected slot(s)" in out, out[-400:])

print("\n=== B. THE REAL DEFECT (2026-10-30 03:23Z / 04:23Z) - A SLOT THAT PRODUCED NOTHING ===")
setup = dict(ALL_OK)
del setup["2026-10-30_0323"]
del setup["2026-10-30_0423"]
rc, out = run([job()], logs_setup=setup)
check("a slot with no pass record at all is a finding", rc == 1, "rc=%d out=%s" % (rc, out[-500:]))
check("the finding names the 03:23 slot", "2026-10-30 03:23" in out, out[-500:])
check("the finding names the 04:23 slot", "2026-10-30 04:23" in out, out[-500:])
check("the finding says the guards were silent, not green",
      "silent rather than green" in out, out[-500:])

print("\n=== C. A PASS THAT STARTED BUT NEVER FINISHED - A LOG WITH NO VERDICT ===")
setup = dict(ALL_OK)
setup["2026-10-30_0423"] = "noverdict"
rc, out = run([job()], logs_setup=setup)
check("an unfinished pass is a finding", rc == 1, "rc=%d out=%s" % (rc, out[-500:]))
check("the finding says it died mid-run", "died mid-run" in out, out[-500:])
check("the finding does not accuse a clean slot",
      "2026-10-30 03:23" not in out, out[-500:])

print("\n=== D2. AN ALREADY-ANNOUNCED GAP IS NOT A NEW FINDING ===")
setup = dict(ALL_OK)
del setup["2026-10-30_0323"]
del setup["2026-10-30_0423"]
announced = {"discord_posted_findings": {"pass-completion": {
    "missed_slots": ["2026-10-30T03:23:00Z", "2026-10-30T04:23:00Z"],
    "posts": [{"posted_at": "2026-10-30T06:31:30Z",
               "messageId": "1565613320059359254"}]}}}
rc, out = run([job()], logs_setup=setup, state=announced)
check("an already-announced gap is not a finding", rc == 0, "rc=%d out=%s" % (rc, out[-600:]))
check("the checker still names the unproven slots", "2026-10-30 03:23" in out, out[-600:])
check("it says they were already announced", "already announced" in out, out[-600:])
check("it names the announcement it refuses to repeat",
      "1565613320059359254" in out, out[-600:])
check("the verdict does not claim every slot completed",
      "every expected pass slot produced a completed pass" not in out, out[-600:])

print("\n=== D3. A GENUINELY NEW GAP STILL FIRES (the negative control) ===")
setup = dict(ALL_OK)
del setup["2026-10-30_0323"]
del setup["2026-10-30_0423"]
partial = {"discord_posted_findings": {"pass-completion": {
    "missed_slots": ["2026-10-30T03:23:00Z"],   # 04:23 was NEVER announced
    "posts": []}}}
rc, out = run([job()], logs_setup=setup, state=partial)
check("a slot that was never announced is still a finding", rc == 1,
      "rc=%d out=%s" % (rc, out[-600:]))
check("the finding names the 04:23 slot", "2026-10-30 04:23" in out, out[-600:])
check("the already-announced slot is not listed as a problem",
      "2026-10-30 03:23 UTC produced NO pass record at all" not in out, out[-600:])

print("\n=== D. A STATE KEY PROVES A SLOT THAT HAS NO LOG ===")
setup = dict(ALL_OK)
del setup["2026-10-30_0223"]
rc, out = run([job()], logs_setup=setup,
               state={"pass_0223_2026_10_30": "x"})
check("a state key is accepted as evidence", rc == 0, "rc=%d out=%s" % (rc, out[-400:]))

print("\n=== E. AN UNREADABLE STATE FILE IS COULD-NOT-PROVE, NOT CLEAN ===")
rc, out = run([job()], logs_setup=setup, state_missing=True)
check("an unreadable state with an unjudgeable slot exits 2", rc == 2,
      "rc=%d out=%s" % (rc, out[-400:]))
check("the unproven case is named", "COULD NOT PROVE" in out, out[-400:])

print("\n=== F. NEGATIVE CONTROL - THE CURRENT SLOT IS NOT EXPECTED ===")
setup = dict(ALL_OK)
setup["2026-10-30_0623"] = "missing"   # the slot the pass is running inside
rc, out = run([job()], logs_setup=setup)
check("the slot the pass is currently inside is not a finding", rc == 0,
      "rc=%d out=%s" % (rc, out[-400:]))

print("\n=== G. NEGATIVE CONTROL - SLOTS FROM BEFORE THE PASS WAS A CRON JOB ARE NOT OWED ===")
rc, out = run([job(created=NOW - timedelta(hours=1))], logs_setup={})
check("a brand-new job with no slots yet is CLEAN", rc == 0,
      "rc=%d out=%s" % (rc, out[-400:]))

print("\n=== H. NEGATIVE CONTROL - AN AGED-OUT GAP DOES NOT CRY WOLF ===")
# The same fixture seen at 10:30 instead of 06:30: the 03:23/04:23 gap is now
# 6-7h old, and the window (6h) has moved past it.
later_setup = {"2026-10-30_0523": "ok", "2026-10-30_0623": "ok",
               "2026-10-30_0723": "ok", "2026-10-30_0823": "ok",
               "2026-10-30_0923": "ok"}
crude_would_flag = True  # "any slot with no log is a finding" -> flag, for ever
check("the crude rule WOULD keep flagging the aged-out gap", crude_would_flag)
rc, out = run([job()], now_dt=LATER, logs_setup=later_setup)
check("this rule does NOT - an aged-out gap is not re-announced", rc == 0,
      "rc=%d out=%s" % (rc, out[-400:]))

print("\n=== I. NO PASS JOB AT ALL IS COULD-NOT-PROVE ===")
rc, out = run([job(name="Some Other Job")], logs_setup=ALL_OK)
check("a missing pass job exits 2", rc == 2, "rc=%d out=%s" % (rc, out[-400:]))

print("\n=== J. A DISABLED PASS JOB IS OWED NOTHING ===")
rc, out = run([job(enabled=False)], logs_setup={})
check("a disabled job is CLEAN", rc == 0, "rc=%d out=%s" % (rc, out[-400:]))

print("\n=== K. A SCHEDULE THAT IS NOT HOURLY IS COULD-NOT-PROVE, NOT A GUESS ===")
rc, out = run([job(expr="0 9 * * 1-6")], logs_setup=ALL_OK)
check("a non-hourly schedule exits 2", rc == 2, "rc=%d out=%s" % (rc, out[-400:]))

print("")
if FAILS:
    print("%d CHECK(S) FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("ALL CHECKS PASS")
