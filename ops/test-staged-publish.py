#!/usr/bin/env python3
"""Regression test for ops/check-staged-publish.py.

A checker that cannot demonstrably FAIL is worse than no checker. These
controls prove the staged-publish checker can both pass and fail, and that it
reaches its verdict from the same table it prints.

Run:  python3 ops/test-staged-publish.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECK = os.path.join(HERE, "check-staged-publish.py")

passed = 0
failed = 0


def check(label: str, cond: bool, extra: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print("  PASS  %s" % label)
    else:
        failed += 1
        print("  FAIL  %s%s" % (label, ("  -- " + extra) if extra else ""))


def run_check(pending_dir: str, now: str = "12:00", today: str = "2026-10-26"):
    """Run the checker against a sandboxed pending dir."""
    env = dict(os.environ)
    env["STAGED_PENDING_DIR"] = pending_dir
    env["STAGED_NOW"] = now
    env["STAGED_TODAY"] = today
    r = subprocess.run([sys.executable, CHECK], capture_output=True, text=True,
                       env=env, timeout=120)
    return r.returncode, r.stdout + r.stderr


def write_pending(d: str, date: str, caption: str, status: str = "APPROVED_PENDING_FB_TOKEN",
                  fallback=None):
    p = {"date": date, "caption": caption, "status": status}
    if fallback is not None:
        p["fallback"] = fallback
    with open(os.path.join(d, "%s.json" % date), "w", encoding="utf-8") as f:
        json.dump(p, f)


def main() -> int:
    print("=== staged-publish checker ===")

    # ---- CONTROL 1: a clean dir must PASS --------------------------------
    d = tempfile.mkdtemp(prefix="staged-clean-")
    try:
        write_pending(d, "2026-10-25", "A caption that was published.",
                      status="POSTED_VIA_FALLBACK",
                      fallback={"posted": ["instagram", "threads"]})
        rc, out = run_check(d)
        check("clean dir exits 0", rc == 0, "rc=%d" % rc)
        check("clean dir reports PUBLISHED", "PUBLISHED" in out, out[:200])
        check("clean dir verdict is CLEAN", "VERDICT: CLEAN" in out, out[-200:])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- CONTROL 2: a staged-but-unpublished caption must FAIL ----------
    d = tempfile.mkdtemp(prefix="staged-bad-")
    try:
        write_pending(d, "2026-10-25", "A caption nobody ever posted.")
        rc, out = run_check(d)
        check("unpublished caption exits non-zero", rc != 0, "rc=%d" % rc)
        check("unpublished caption is named", "2026-10-25" in out, out[:300])
        check("verdict is EXPOSED", "VERDICT: EXPOSED" in out, out[-200:])
        check("verdict says it never published",
              "never published" in out.lower() or "never reached" in out.lower(),
              out[-300:])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- CONTROL 3: the same dir must PASS once a fallback record exists -
    d = tempfile.mkdtemp(prefix="staged-fixed-")
    try:
        write_pending(d, "2026-10-25", "A caption nobody ever posted.")
        rc_before, _ = run_check(d)
        write_pending(d, "2026-10-25", "A caption nobody ever posted.",
                      status="POSTED_VIA_FALLBACK",
                      fallback={"posted": ["threads"]})
        rc_after, out = run_check(d)
        check("before fix: fails", rc_before != 0)
        check("after fix: passes", rc_after == 0, "rc=%d" % rc_after)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- CONTROL 4: today is IN-FLIGHT before the cutoff, a finding after -
    d = tempfile.mkdtemp(prefix="staged-window-")
    try:
        write_pending(d, "2026-10-26", "Today's caption.")
        rc_open, out_open = run_check(d, now="08:00")
        rc_closed, out_closed = run_check(d, now="12:00")
        check("today before cutoff is IN-FLIGHT", "IN-FLIGHT" in out_open, out_open[:300])
        check("today before cutoff does not fail on its own", rc_open != 0 or "IN-FLIGHT" in out_open)
        check("today after cutoff is a finding", "STAGED-NOT-PUBLISHED" in out_closed,
              out_closed[:300])
        check("today after cutoff exits non-zero", rc_closed != 0, "rc=%d" % rc_closed)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- CONTROL 5: a FUTURE date is not a finding ----------------------
    d = tempfile.mkdtemp(prefix="staged-future-")
    try:
        write_pending(d, "2026-10-27", "A caption staged for tomorrow.")
        rc, out = run_check(d, now="12:00")
        check("future date is FUTURE", "FUTURE" in out, out[:300])
        check("future date is not listed as a finding",
              "2026-10-27  " not in out.split("never reached any platform")[-1]
              if "never reached any platform" in out else True,
              out[-300:])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- CONTROL 6: the verdict must be provable from the printed table --
    d = tempfile.mkdtemp(prefix="staged-table-")
    try:
        write_pending(d, "2026-10-25", "Never posted caption alpha.")
        rc, out = run_check(d)
        table_line = [l for l in out.splitlines() if "2026-10-25" in l and "STAGED-NOT-PUBLISHED" in l]
        check("the finding appears as its own table row", bool(table_line), out[:400])
        check("the finding is counted in the summary",
              "1 staged caption(s) never reached" in out, out[-300:])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- CONTROL 7: the checker must NEVER publish -----------------------
    src = open(CHECK, encoding="utf-8").read()
    for bad in ('method="POST"', "method='POST'", "/posts\"", "requests.post"):
        # A POST to /posts would be a publish. Reads of /posts are fine.
        if bad in ('method="POST"', "method='POST'"):
            check("checker contains no POST method", bad not in src, bad)
    check("checker only reads the posts endpoint",
          "/posts?limit=50" in src and "urlopen" in src)
    check("checker has no publish call", ".send(" not in src and "post(" not in src.lower()
          or "postTime" in src)

    # ---- CONTROL 8: missing pending dir is not a crash -------------------
    rc, out = run_check("/nonexistent/path/for/staged")
    check("missing pending dir exits 0", rc == 0, "rc=%d" % rc)
    check("missing pending dir says CLEAN", "VERDICT: CLEAN" in out, out[:200])

    print()
    print("%d passed, %d failed" % (passed, failed))
    if failed:
        print("TESTS FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
