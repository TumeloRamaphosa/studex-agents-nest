#!/usr/bin/env python3
"""Test ops/check-cron-timeout-kills.py.

The rule under test: a job whose LAST run was killed by a timeout must be
flagged only when its CURRENT budget would kill it again.

The negative controls are the whole point of this checker. A checker that
reported "this job timed out" - full stop - would have been RIGHT on
2026-10-29 and would have cried wolf forever after, because a fixed job stays
fixed until its next run and a checker that ignores the budget would keep
announcing the repair as a defect.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "check-cron-timeout-kills.py"
FAILS = []
NOW_MS = int(time.time() * 1000)


def check(label, cond, detail=""):
    if cond:
        print("PASS  %s" % label)
    else:
        print("FAIL  %s %s" % (label, detail))
        FAILS.append(label)


def job(jid, name, timeout):
    return {
        "id": jid,
        "name": name,
        "enabled": True,
        "schedule": {"kind": "cron", "expr": "0 9 * * 1-6", "tz": "Africa/Johannesburg"},
        "payload": {"kind": "agentTurn", "message": "x", "timeoutSeconds": timeout},
    }


def rec(jid, status="error", error="cron: job execution timed out", duration=None, age_min=60):
    r = {"jobId": jid, "ts": NOW_MS - age_min * 60 * 1000, "status": status,
         "error": error, "durationMs": duration, "deliveryStatus": "unknown"}
    return r


def run(jobs, records):
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        (d / "jobs.json").write_text(json.dumps({"jobs": jobs}), encoding="utf8")
        rd = d / "runs"
        rd.mkdir()
        for jid, recs in records.items():
            (rd / ("%s.jsonl" % jid)).write_text(
                "\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf8")
        p = subprocess.run([sys.executable, str(CHECKER), str(d / "jobs.json"), str(rd)],
                           capture_output=True, text=True)
        return p.returncode, p.stdout


print("=== A. THE REAL DEFECT (2026-10-29) — killed at 300s, budget still 300s ===")
rc, out = run(
    [job("ceo-standup-0900", "CEO Standup — 9:00 AM SAST", 300)],
    {"ceo-standup-0900": [rec("ceo-standup-0900", duration=303478)]},
)
check("the job is flagged", rc == 1, "rc=%d out=%s" % (rc, out[-300:]))
check("the finding names the job", "ceo-standup-0900" in out, out[-300:])
check("the finding names the budget", "300" in out, out[-300:])

print("\n=== B. THE FIXED JOB — budget raised past the kill point is NOT a finding ===")
rc, out = run(
    [job("ceo-standup-0900", "CEO Standup — 9:00 AM SAST", 1800)],
    {"ceo-standup-0900": [rec("ceo-standup-0900", duration=303478)]},
)
check("a repaired job is CLEAN", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== C. A JOB WHOSE LAST RUN WAS FINE IS NOT A FINDING ===")
rc, out = run(
    [job("a", "Standup — 9:00 AM SAST", 300)],
    {"a": [rec("a", status="ok", error="", duration=12000),
           rec("a", duration=310000, age_min=1440)]},
)
check("only the MOST RECENT run counts", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== D. A NON-TIMEOUT ERROR IS NOT A KILL ===")
rc, out = run(
    [job("a", "Vault Sync — Midnight SAST", 1200)],
    {"a": [rec("a", error="API rate limit reached. Please try again later.", duration=5000)]},
)
check("a provider rate limit is not a timeout kill", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== E. A TIMEOUT KILL WITH NO DURATION IS UNPROVEN, NOT CLEAN AND NOT A FINDING ===")
rc, out = run(
    [job("a", "Standup — 9:00 AM SAST", 300)],
    {"a": [rec("a", duration=None)]},
)
check("could-not-prove exits 2", rc == 2, "rc=%d out=%s" % (rc, out[-300:]))
check("the unproven case is named", "COULD NOT PROVE" in out, out[-300:])

print("\n=== F. A MONTH-OLD KILL IS NOT ACTIONABLE ===")
rc, out = run(
    [job("a", "Standup — 9:00 AM SAST", 300)],
    {"a": [rec("a", duration=303478, age_min=60 * 24 * 40)]},
)
check("a stale record is ignored", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== G. A DISABLED JOB IS NOT CONSIDERED ===")
j = job("a", "Retired — old job", 300)
j["enabled"] = False
rc, out = run([j], {"a": [rec("a", duration=303478)]})
check("a disabled job is ignored", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== H. NEGATIVE CONTROL — THE CRUDE RULE WOULD CRY WOLF ON A FIXED JOB ===")
crude_flags_fixed_job = True  # "the last run timed out" -> flag, whatever the budget is
check("the crude rule WOULD flag the repaired standup", crude_flags_fixed_job)
rc, out = run(
    [job("ceo-standup-0900", "CEO Standup — 9:00 AM SAST", 1800)],
    {"ceo-standup-0900": [rec("ceo-standup-0900", duration=303478)]},
)
check("this rule does NOT", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("\n=== I. A JOB THAT HAS NEVER RUN IS NOT A FINDING ===")
rc, out = run([job("a", "Brand New Job — 09:00 SAST", 1800)], {})
check("a job with no run record is CLEAN", rc == 0, "rc=%d out=%s" % (rc, out[-300:]))

print("")
if FAILS:
    print("%d CHECK(S) FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("ALL CHECKS PASS")
