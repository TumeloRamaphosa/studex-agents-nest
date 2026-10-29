#!/usr/bin/env python3
"""Test ops/check-cron-timeout-outliers.py.

The rule under test: a job whose timeout is far below its own family's
maximum is an outlier and must be flagged; a job that is merely SHORT is not.

The negative controls matter more than the positive ones here. A checker that
flags "any timeout under X seconds" would have caught the real defect and
would ALSO have cried wolf on every legitimately quick job - and a guard that
cries wolf gets switched off, which is how the PLACEHOLDER it exists to catch
slips through. So the test pins the SHARPNESS, not just the finding.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "check-cron-timeout-outliers.py"

FAILS = []


def job(jid, name, timeout=None, enabled=True):
    j = {
        "id": jid,
        "name": name,
        "enabled": enabled,
        "schedule": {"kind": "cron", "expr": "0 9 * * 1-6", "tz": "Africa/Johannesburg"},
        "payload": {"kind": "agentTurn", "message": "x"},
    }
    if timeout is not None:
        j["payload"]["timeoutSeconds"] = timeout
    return j


def run(jobs):
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "jobs.json"
        p.write_text(json.dumps({"jobs": jobs}), encoding="utf8")
        r = subprocess.run([sys.executable, str(CHECKER), str(p)],
                           capture_output=True, text=True)
        return r.returncode, r.stdout


def check(label, cond, detail=""):
    if cond:
        print("PASS  %s" % label)
    else:
        print("FAIL  %s %s" % (label, detail))
        FAILS.append(label)


print("=== A. THE REAL DEFECT (2026-10-29) — 300s against its own siblings ===")
rc, out = run([
    job("ceo-standup-0900", "CEO Standup — 9:00 AM SAST", 300),
    job("ceo-standup-1700", "CEO Standup — 17:00 SAST", 1800),
    job("ceo-standup-2200", "CEO Standup — 10:00 PM SAST", 1800),
])
check("the 300s standup is flagged", rc == 1, "rc=%d" % rc)
check("the finding names the job", "ceo-standup-0900" in out, out[-300:])
check("the finding names both budgets", "300" in out and "1800" in out, out[-300:])
check("the finding names the family", "ceo standup" in out, out[-300:])

print("\n=== B. A HEALTHY FAMILY IS NOT FLAGGED ===")
rc, out = run([
    job("a", "CEO Standup — 9:00 AM SAST", 1800),
    job("b", "CEO Standup — 17:00 SAST", 1800),
    job("c", "CEO Standup — 10:00 PM SAST", 2400),
])
check("a healthy family is CLEAN", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== C. A LONE SHORT JOB IS NOT FLAGGED (nothing to compare it to) ===")
rc, out = run([
    job("quick", "Quick Health Ping", 300),
    job("slow", "Nightly Reconciliation", 3600),
])
check("a single-member family is not an outlier", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== D. THE BOUNDARY — exactly 25% of the family max is NOT an outlier ===")
rc, out = run([
    job("a", "Standup — 9:00 AM SAST", 450),
    job("b", "Standup — 17:00 SAST", 1800),
])
check("exactly 25% is left alone", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))
rc, out = run([
    job("a", "Standup — 9:00 AM SAST", 449),
    job("b", "Standup — 17:00 SAST", 1800),
])
check("below 25% IS flagged", rc == 1, "rc=%d" % rc)

print("\n=== E. A JOB WITH NO DECLARED BUDGET IS SKIPPED, NOT GUESSED AT ===")
rc, out = run([
    job("a", "Standup — 9:00 AM SAST", None),
    job("b", "Standup — 17:00 SAST", 1800),
])
check("a job with no timeoutSeconds does not create an outlier", rc == 0,
      "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== F. DISABLED JOBS DO NOT SET THE FAMILY CEILING ===")
rc, out = run([
    job("a", "Standup — 9:00 AM SAST", 1800),
    job("b", "Standup — 17:00 SAST", 1800),
    job("c", "Standup — Retired (old)", 120, enabled=False),
])
check("a disabled job is ignored", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== G. NEGATIVE CONTROL — THE CRUDER RULE WOULD HAVE CRIED WOLF ===")
# "Every timeout must be >= 600s" catches the real defect too. It also flags
# the legitimate 300s Quick Health Ping, which is why the rule is relative.
crude_flags_300 = 300 < 600
check("the crude rule WOULD flag a legitimate 300s job", crude_flags_300)
rc, out = run([job("quick", "Quick Health Ping", 300)])
check("this rule does NOT flag it", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== H. THE FIXED FLEET IS CLEAN (the 2026-10-29 job was raised to 1800s) ===")
rc, out = run([
    job("ceo-standup-0900", "CEO Standup — 9:00 AM SAST", 1800),
    job("ceo-standup-1700", "CEO Standup — 17:00 SAST", 1800),
    job("ceo-standup-2200", "CEO Standup — 10:00 PM SAST", 1800),
])
check("the repaired fleet is CLEAN", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("")
if FAILS:
    print("%d CHECK(S) FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("ALL CHECKS PASS")
