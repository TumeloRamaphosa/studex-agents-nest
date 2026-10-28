#!/usr/bin/env python3
"""Negative-test ops/check-cron-times.py — prove it can actually FAIL.

A green checker that cannot fail is worse than no checker, because it is
trusted. This builds doctored copies of jobs.json and asserts the checker
catches each failure mode:

  A. a job whose nextRunAtMs is 2 hours off its name
  B. an enabled job with tz cleared (the `cron edit --cron` trap)
  C. a job whose tz is UTC while its name promises SAST hours

Usage: python3 ops/test-cron-times-checker.py
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


def run_checker(path):
    return subprocess.run([sys.executable, str(CHECKER), str(path)],
                          capture_output=True, text=True)


base = json.loads(SRC.read_text(encoding="utf8"))
jobs = base.get("jobs", base if isinstance(base, list) else [])

def re_time(name):
    m = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", name) or re.search(r"(\d{1,2}):(\d{2})\s*SAST", name)
    return bool(m)


# pick a victim job that has a time in its name and a nextRunAtMs
victim = next((j for j in jobs
               if j.get("enabled") and "SAST" in (j.get("name") or "")
               and (j.get("state") or {}).get("nextRunAtMs")
               and re_time(j.get("name", ""))), None)


if not victim:
    print("  !! no suitable victim job found in jobs.json - cannot negative-test")
    sys.exit(1)

print(f"  victim job: {victim.get('name')!r} ({victim.get('id')})")

# ---- control: unmodified copy must PASS
with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps(base), encoding="utf8")
    r = run_checker(p)
    ok = r.returncode == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] control (unmodified copy) passes        exit={r.returncode}")
    if not ok:
        fails.append("control")
        print(r.stdout[-600:])

# ---- A: nextRunAtMs shifted by 2 hours
with tempfile.TemporaryDirectory() as td:
    d = json.loads(json.dumps(base))
    for j in d.get("jobs", []):
        if j.get("id") == victim.get("id"):
            nr = j["state"]["nextRunAtMs"]
            j["state"]["nextRunAtMs"] = nr + 2 * 3600 * 1000
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps(d), encoding="utf8")
    r = run_checker(p)
    caught = r.returncode != 0 and "promises" in r.stdout
    print(f"  [{'PASS' if caught else 'FAIL'}] A. nextRunAtMs 2h off its name caught   exit={r.returncode}")
    if not caught:
        fails.append("A")
    for l in r.stdout.splitlines():
        if l.strip().startswith("- "):
            print(f"          {l.strip()[:130]}")
            break

# ---- B: tz cleared
with tempfile.TemporaryDirectory() as td:
    d = json.loads(json.dumps(base))
    for j in d.get("jobs", []):
        if j.get("id") == victim.get("id"):
            j["schedule"]["tz"] = None
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps(d), encoding="utf8")
    r = run_checker(p)
    caught = r.returncode != 0 and "NO timezone" in r.stdout
    print(f"  [{'PASS' if caught else 'FAIL'}] B. cleared timezone caught            exit={r.returncode}")
    if not caught:
        fails.append("B")
    for l in r.stdout.splitlines():
        if l.strip().startswith("- "):
            print(f"          {l.strip()[:130]}")
            break

# ---- C: tz flipped to UTC while the name promises SAST
with tempfile.TemporaryDirectory() as td:
    d = json.loads(json.dumps(base))
    for j in d.get("jobs", []):
        if j.get("id") == victim.get("id"):
            j["schedule"]["tz"] = "UTC"
    p = pathlib.Path(td) / "jobs.json"
    p.write_text(json.dumps(d), encoding="utf8")
    r = run_checker(p)
    caught = r.returncode != 0
    print(f"  [{'PASS' if caught else 'FAIL'}] C. tz flipped to UTC caught            exit={r.returncode}")
    if not caught:
        fails.append("C")
    for l in r.stdout.splitlines():
        if l.strip().startswith("- "):
            print(f"          {l.strip()[:130]}")
            break

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): {fails}")
    sys.exit(1)
print("RESULT: the cron-time checker provably fails on every failure mode")
