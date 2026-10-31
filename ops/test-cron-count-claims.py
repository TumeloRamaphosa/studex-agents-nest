#!/usr/bin/env python3
"""Test ops/check-cron-count-claims.py.

THE DEFECT (2026-10-31): the `cta-on-feed` checker was registered as the 26th
checker, but the canonical pass's payload still said "It is 25 READ-ONLY
checkers" - so the pass ran 26 while its instructions said 25.

🔑 WHY NOTHING CAUGHT IT
  * `ops/test-heartbeat-registry.py` checks that every checker ON DISK is
    classified and every registered checker EXISTS. Neither direction is the
    question "does the payload's number match the registry's number".
  * `ops/check-cron-payload-claims.py` checks that a payload does not assert
    a FALSE STATUS. "25 checkers" was not a false status, just a stale
    number. A guard that only catches false-sounding claims will not catch a
    stale number.

🔑 WHY THE NEGATIVE CONTROLS ARE THE POINT
A count check is trivially satisfiable by a rule that never fires. So the
controls below pin down BOTH edges:
  * a payload stating the RIGHT count must pass
  * a payload stating the WRONG count must be caught - including the exact
    real-world case (payload says 25, registry has 26)
  * a payload that says nothing about the count must NOT be flagged (the rule
    only bites on a stated number)
  * "checker 25" (an ID, not a count) must NOT be read as a count claim
  * a DISABLED job must not be flagged
  * a missing cron file must be UNCHECKED, never CLEAN
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "check-cron-count-claims.py"
REGISTRY = REPO / "ops" / "heartbeat-checkers.tsv"
FAILS = []


def check(cond, label):
    if cond:
        print("  PASS  %s" % label)
    else:
        print("  FAIL  %s" % label)
        FAILS.append(label)


def run_with(jobs_payload, registry_text=None):
    """Run the checker against a synthetic cron file (and optionally registry)."""
    with tempfile.TemporaryDirectory() as td:
        jf = os.path.join(td, "jobs.json")
        with open(jf, "w", encoding="utf-8") as fh:
            json.dump(jobs_payload, fh)
        env = dict(os.environ)
        env["CRON_JOBS_FILE"] = jf
        if registry_text is not None:
            rf = os.path.join(td, "reg.tsv")
            with open(rf, "w", encoding="utf-8") as fh:
                fh.write(registry_text)
            env["HEARTBEAT_CHECKERS_TSV"] = rf
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True,
                           text=True, env=env, timeout=60)
        return r.returncode, r.stdout


def job(msg, enabled=True, name="Canonical Heartbeat Pass"):
    return {"name": name, "enabled": enabled,
            "payload": {"message": msg}}


def main():
    # A registry with a known PASS-row count.
    reg = ("# header\n"
           "a-checker | ops/a.py | PASS | 0,1,2 | no | thing one |\n"
           "b-checker | ops/b.py | PASS | 0,1,2 | yes | thing two |\n"
           "a-scope  | ops/lib.py | SCOPE | 0,1,- | no | a library |\n"
           "a-note   | ops/n.py  | PASS | 0,1,- | no | thing three |\n")
    # => 3 PASS rows (SCOPE does not count).

    print("=== A. the registry count is derived correctly ===")
    rc, out = run_with([job("It is 3 READ-ONLY checkers and takes about 4 minutes.")], reg)
    check(rc == 0, "a payload naming the right count passes (rc=0)")
    check("registry checkers that run: 3" in out,
          "the count comes from PASS rows only (SCOPE excluded)")

    print("\n=== B. a STALE count is caught (the real defect) ===")
    rc, out = run_with([job("It is 25 READ-ONLY checkers and takes about 4 minutes.")], reg)
    check(rc == 1, "a payload naming the wrong count is DRIFT (rc=1)")
    check("says 25" in out and "the registry has 3" in out,
          "the drift names both numbers: %s" % out.strip().splitlines()[1][:90])

    print("\n=== C. a payload SILENT about the count is not flagged ===")
    rc, out = run_with([job("Run the canonical heartbeat pass and report on a change.")], reg)
    check(rc == 0, "a payload with no count claim passes")

    print("\n=== D. 'checker 25' is an ID, not a count ===")
    rc, out = run_with([job("checker 25 raised a finding last night.")], reg)
    check(rc == 0, "a payload naming a checker BY ID is not read as a count claim")

    print("\n=== E. a DISABLED job is not flagged ===")
    rc, out = run_with([job("It is 25 READ-ONLY checkers."), ], reg)
    check(rc == 1, "the enabled job IS flagged")
    rc, out = run_with([job("It is 25 READ-ONLY checkers.", enabled=False)], reg)
    check(rc == 0, "a disabled job is not flagged")

    print("\n=== F. missing inputs are UNCHECKED, never CLEAN ===")
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ)
        env["CRON_JOBS_FILE"] = os.path.join(td, "nope.json")
        env["HEARTBEAT_CHECKERS_TSV"] = os.path.join(td, "nope.tsv")
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True,
                           text=True, env=env, timeout=60)
        check(r.returncode == 2, "a missing cron file -> rc=2 (unchecked), not clean")
    rc, out = run_with([job("It is 3 checkers.")], "not a registry at all\n")
    check(rc == 2, "a registry with no PASS rows -> rc=2 (unchecked), not clean")

    print("\n=== G. the LIVE cron file and the LIVE registry agree ===")
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True,
                       text=True, timeout=60)
    check(r.returncode == 0,
          "the live check is CLEAN (rc=0): %s" % r.stdout.strip().splitlines()[-1][:80])

    print("\n=== H. the negative control is NOT vacuous ===")
    # Prove the rule can actually fire against the REAL registry: a payload
    # claiming a number that is one behind must be DRIFT.
    real_reg_lines = REGISTRY.read_text(encoding="utf-8").splitlines()
    real_n = sum(1 for ln in real_reg_lines
                 if ln.strip() and not ln.lstrip().startswith("#")
                 and len(ln.split("|")) >= 3
                 and ln.split("|")[2].strip().upper() == "PASS")
    check(real_n >= 20, "the live registry has a real count to contradict (%d)" % real_n)
    rc, out = run_with([job("It is %d READ-ONLY checkers." % (real_n - 1))],
                        REGISTRY.read_text(encoding="utf-8"))
    check(rc == 1,
          "the LIVE registry + a one-behind payload -> DRIFT (the rule fires)")

    print("\n" + "=" * 66)
    if FAILS:
        print("FAILED (%d):" % len(FAILS))
        for f in FAILS:
            print("  - %s" % f)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
