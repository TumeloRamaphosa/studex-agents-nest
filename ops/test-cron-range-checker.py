#!/usr/bin/env python3
"""Negative-test the cron-time checker for RANGE names.

A green checker that cannot fail is worse than no checker, because it is
trusted. This proves the checker catches a job whose name promises a TIME
RANGE and which fires at the wrong end of that range.

THE BUG THIS GUARDS
-------------------
`ops/check-cron-times.py` parses the clock time out of each job's NAME.
`Research Hour — 10-11 PM SAST` is a RANGE: it begins at 10 PM and runs for
an hour. The old parser took the range's END (11 PM -> 23:00), so it
validated a job that fired at 23:00 as "correct" - while the job's own
payload said "It is 10:00 PM SAST - RESEARCH HOUR begins NOW", and it
collided with `Build Hour — 11 PM SAST` on the same minute. Build Hour
consumes the research brief Research Hour is supposed to produce.

So the checker was not merely blind to the bug - it was CONFIRMING it.

Cases proven here:
  A. a range-named job firing at the range's END is caught
  B. a range-named job firing at the range's START passes
  C. "Midnight" is understood as 00:00 (it was silently skipped before)

Usage: python3 ops/test-cron-range-checker.py
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAST = timezone(timedelta(hours=2))
SRC = pathlib.Path("/root/.openclaw/cron/jobs.json")
CHECKER = ROOT / "ops" / "check-cron-times.py"

fails = []


def check(label, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", label,
                           (" -> " + detail) if detail and not ok else ""))
    if not ok:
        fails.append(label)


def run_checker(path):
    return subprocess.run([sys.executable, str(CHECKER), str(path)],
                          capture_output=True, text=True)


def sast_ms(hour, minute=0):
    """nextRunAtMs for a given SAST clock time on 2026-10-23."""
    dt = datetime(2026, 10, 23, hour, minute, tzinfo=SAST)
    return int(dt.timestamp() * 1000)


def fixture(expr, tz, next_ms, name="Research Hour — 10-11 PM SAST"):
    return {
        "id": "range-victim",
        "name": name,
        "enabled": True,
        "schedule": {"kind": "cron", "expr": expr, "tz": tz},
        "state": {"nextRunAtMs": next_ms},
        "payload": {"kind": "agentTurn", "message": "x"},
    }


# ---- control: the REAL jobs.json must pass
with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / "jobs.json"
    shutil.copy(SRC, p)
    r = run_checker(p)
    check("control (the live jobs.json) passes", r.returncode == 0,
          (r.stdout or "")[-700:])

# ---- A: a range-named job firing at the range's END must be CAUGHT
with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps({"jobs": [fixture("0 23 * * 0-6", "Africa/Johannesburg",
                                              sast_ms(23))]}), encoding="utf8")
    r = run_checker(p)
    caught = r.returncode != 0 and "promises 22:00" in r.stdout
    check("A. a range-named job firing at the range's END is caught", caught,
          "exit=%d out=%s" % (r.returncode, (r.stdout or "")[-300:]))
    check("A. it says which time was promised",
          "22:00" in (r.stdout or ""), (r.stdout or "")[-300:])

# ---- B: the same job firing at the range's START must PASS
with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps({"jobs": [fixture("0 22 * * 0-6", "Africa/Johannesburg",
                                              sast_ms(22))]}), encoding="utf8")
    r = run_checker(p)
    check("B. the same job firing at the range's START passes", r.returncode == 0,
          "exit=%d out=%s" % (r.returncode, (r.stdout or "")[-300:]))

# ---- C: "Midnight" means 00:00
with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps({"jobs": [
        fixture("0 0 * * 1-6", "Africa/Johannesburg", sast_ms(0),
                name="Vault Sync — Midnight SAST (EOD)")]}), encoding="utf8")
    r = run_checker(p)
    check("C. 'Midnight' is checked as 00:00 (not silently skipped)",
          "1 time-named job(s) verified" in r.stdout,
          (r.stdout or "")[-300:])

# ---- D: NEGATIVE CONTROL - the OLD parser would have passed the wrong job.
#      This proves the NEW parser is what makes case A catchable, rather than
#      the checker catching it for some unrelated reason.
old_parser = re.compile(r"(\d{1,2})\s*PM\s*SAST")
m = old_parser.search("Research Hour — 10-11 PM SAST")
old_want = f"{(int(m.group(1)) % 12) + 12:02d}:00"
check("D. NEGATIVE CONTROL: the OLD parser read the range's END (23:00)",
      old_want == "23:00", "old parser gave %s" % old_want)
check("D. so the OLD parser would have PASSED the wrong 23:00 job",
      old_want == "23:00", "the old parser did not read 23:00")

# And the live (new) parser must read the range's START.
import importlib.util
spec = importlib.util.spec_from_file_location("cronchk", CHECKER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
new_want = mod.name_time("Research Hour — 10-11 PM SAST")
check("D. the NEW parser reads the range's START (22:00)",
      new_want == "22:00", "new parser gave %s" % new_want)
check("D. and the two parsers DISAGREE - so the fix is what closed the hole",
      old_want != new_want,
      "old=%s new=%s (if equal, case A would not be a real test)" % (old_want, new_want))

print()
if fails:
    print("RESULT: %d FAILURE(S): %s" % (len(fails), fails))
    sys.exit(1)
print("RESULT: the cron-time checker provably catches a range-named job off its range")
