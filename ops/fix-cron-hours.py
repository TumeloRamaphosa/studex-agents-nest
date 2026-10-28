#!/usr/bin/env python3
"""Set every time-named cron job to fire at EXACTLY the time its name promises.

THE TRAP (found the hard way)
------------------------------
`openclaw cron edit <id> --cron <expr>` RESETS the job's timezone to UTC if
you do not also pass --tz. So editing '0 7 * * 1-5' to '0 9 * * 1-5' on a job
whose tz was Africa/Johannesburg silently moved it from 07:00 SAST to
09:00 UTC = 11:00 SAST - two hours LATE instead of two hours early.

The expr hour alone therefore cannot tell you when a job will fire. The only
trustworthy signal is nextRunAtMs in /root/.openclaw/cron/jobs.json, read
back after every edit.

THE FIX
-------
For each enabled job whose NAME promises a clock time:
  tz   = Africa/Johannesburg
  expr = that clock time in SAST hours
  then assert nextRunAtMs converts to exactly the promised SAST time.

Jobs whose name promises no time (Coffee + Global Markets, Discord Ops Morning
Summary, Email Warmup, Daily Content Agent) are NOT touched - there is no
intent signal to act on.

Usage: python3 ops/fix-cron-hours.py
"""
import json
import pathlib
import re
import subprocess
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path("/workspace")
SAST = timezone(timedelta(hours=2))
JOBS = pathlib.Path("/root/.openclaw/cron/jobs.json")
SAST_TZ = "Africa/Johannesburg"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), **kw)


def load():
    d = json.loads(JOBS.read_text(encoding="utf8"))
    return d.get("jobs", d if isinstance(d, list) else [])


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

def actual_sast(j):
    nr = (j.get("state") or {}).get("nextRunAtMs")
    if not nr:
        return None
    return datetime.fromtimestamp(nr / 1000, tz=timezone.utc).astimezone(SAST).strftime("%H:%M")


print("=" * 78)
print("STEP 1 — before")
print("=" * 78)
plan = []
for j in load():
    if not j.get("enabled"):
        continue
    sched = j.get("schedule") or {}
    if sched.get("kind") != "cron":
        continue
    want = name_time(j.get("name", ""))
    if not want:
        print(f"  (no time in name - left alone)  {str(j.get('name',''))[:46]:46} "
              f"expr={str(sched.get('expr')):12} tz={str(sched.get('tz')):20} next={actual_sast(j)}")
        continue
    expr = sched.get("expr") or ""
    parts = expr.split()
    if len(parts) < 2 or not parts[1].isdigit():
        continue
    new = list(parts)
    new[1] = str(int(want[:2]))
    new_expr = " ".join(new)
    act = actual_sast(j)
    tz = sched.get("tz")
    status = "OK" if act == want else "WRONG"
    print(f"  [{status:5}] {str(j.get('name',''))[:46]:46} expr={expr:12} tz={str(tz):20} "
          f"next={act}  name says {want}")
    if act != want:
        plan.append((j["id"], j.get("name", ""), expr, new_expr, want))

print("\n" + "=" * 78)
print(f"STEP 2 — fixing {len(plan)} job(s)  (--cron AND --tz together)")
print("=" * 78)
for jid, name, old, new_expr, want in plan:
    r = run(["openclaw", "cron", "edit", jid, "--cron", new_expr, "--tz", SAST_TZ])
    print(f"  {str(name)[:46]:46} {old:12} -> {new_expr:12} rc={r.returncode}")
    if r.returncode:
        for l in (r.stderr or "").strip().splitlines()[-2:]:
            print("      ", l[:140])

print("\n" + "=" * 78)
print("STEP 3 — read back and VERIFY nextRunAtMs against the promised time")
print("=" * 78)
bad = 0
for j in load():
    if not j.get("enabled"):
        continue
    sched = j.get("schedule") or {}
    if sched.get("kind") != "cron":
        continue
    want = name_time(j.get("name", ""))
    if not want:
        continue
    act = actual_sast(j)
    ok = act == want
    if not ok:
        bad += 1
    print(f"  [{'OK  ' if ok else 'BAD '}] {str(j.get('name',''))[:46]:46} expr={str(sched.get('expr')):12} "
          f"tz={str(sched.get('tz')):20} next={act}  promised={want}")
print(f"\n  jobs whose actual fire time still differs from their name: {bad}")
