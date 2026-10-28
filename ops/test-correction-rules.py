#!/usr/bin/env python3
"""Prove the outbound correction-note rules actually FIRE.

A checker that can never fail is worthless. This proves each rule rejects a
deliberately bad correction note, and that a correct one stays clean.

WHY A SANDBOX
-------------
This test proves drift-check's correction rules work by writing a
deliberately-bad note and checking that drift-check flags it. When that note
was written into the LIVE `outbound-corrections/` directory, an interrupted
run (timeout, kill, crash) left the fixture behind - and then drift-check
reported DRIFT on that fixture for EVERY subsequent run. Two failures followed:

  1. the real drift check cried wolf on a test artefact, and
  2. this test's own "MUST PASS" cases failed for the wrong reason.

A test that writes into the live tree can poison the tree it then checks.
So this test works on a SANDBOX copy and points drift-check at it with
DRIFT_CHECK_CORRECTION_DIR. The live directory is never written to.

Run: python3 ops/test-correction-rules.py
"""
import os
import pathlib
import shutil
import subprocess
import sys

# The LIVE corrections directory. This test must never write into it.
LIVE_CORR = pathlib.Path("outbound-corrections")

# A SANDBOX copy. The fixture is written here and drift-check is pointed at it.
SANDBOX = pathlib.Path("/tmp/corr-rules-sandbox")
CORR = SANDBOX
BACKUP = pathlib.Path("/tmp/corr-rules-backup")

# NOTE: build the fixture WITHOUT nested triple-backticks - a fence inside the
# fixture body would be swallowed by the outer heredoc. This exact mistake
# made a passing fixture look like a failing one.
GOOD_BODY = (
    'Dear buyer, I am writing to correct my earlier email. I wrote '
    '"PROWTC (Rainforest Alliance) certified" and that was wrong - it is not ours. '
    'I also quoted USD 4.60/kg, which was an error; the correct price is USD 4,200/MT. '
    'I withdraw the earlier claim and I apologise. '
    'Sheet: https://hhsmhunf1xci.space.mcode.io'
)

CASES = [
    ("asserted claim, no withdrawal context",
     "Dear buyer, our coffee is PROWTC certified and available at USD 4,200/MT.\n", True),
    ("price not in registry",
     'Dear buyer, I wrote "old figures" and that was wrong; the correct price is USD 9,999/MT. '
     "I apologise.\n", True),
    ("superseded URL",
     'Dear buyer, I wrote "old figures" and that was wrong. '
     "Sheet: https://z7p9urw22jwb.space.mcode.io\n", True),
    ("non-canonical URL",
     'Dear buyer, I wrote "old figures" and that was wrong. '
     "Sheet: https://zzznotcanonical99.space.mcode.io\n", True),
    ("silent correction, no withdrawal language",
     "Dear buyer, here is our new sheet https://hhsmhunf1xci.space.mcode.io\n", True),
    ("clean correction", GOOD_BODY + "\n", False),
]

# Any fixture left in the LIVE directory by an OLD interrupted run of this
# test must be removed, or the real drift check keeps tripping over it.
STALE_LIVE_FIXTURE = LIVE_CORR / "ok.md"
if STALE_LIVE_FIXTURE.exists():
    STALE_LIVE_FIXTURE.unlink()
    print("  (removed a stale test fixture left in the LIVE dir by an interrupted run)")

if BACKUP.exists():
    shutil.rmtree(BACKUP)
shutil.copytree(LIVE_CORR, BACKUP)

# Build the SANDBOX: a copy of the live corrections dir (including the
# recipients JSON, which drift-check reads from the SAME directory).
if SANDBOX.exists():
    shutil.rmtree(SANDBOX)
shutil.copytree(LIVE_CORR, SANDBOX)

FAIL = []


def run():
    # Point drift-check at the SANDBOX, not the live directory.
    env = dict(os.environ)
    env["DRIFT_CHECK_CORRECTION_DIR"] = str(SANDBOX.resolve())
    r = subprocess.run([sys.executable, "ops/drift-check.py"], capture_output=True,
                       text=True, timeout=300, env=env)
    return r.stdout


def write_fixture(body):
    (CORR / "ok.md").write_text(
        "# DRAFT - test\n\n## Draft body\n\n" + chr(96) * 3 + "\n" + body + chr(96) * 3 + "\n",
        encoding="utf8")


try:
    for label, body, expect_drift in CASES:
        for f in CORR.glob("*.md"):
            f.unlink()
        for f in BACKUP.glob("*.md"):
            shutil.copy(f, CORR / f.name)
        write_fixture(body)
        out = run()
        drift = "DRIFT DETECTED" in out
        ok = drift == expect_drift
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:<46} drift={drift} expected={expect_drift}")
        if not ok:
            FAIL.append(label)
        for l in [x.strip() for x in out.splitlines() if x.strip().startswith("- outbound-corrections/ok.md")][:2]:
            print(f"          {l[:140]}")
finally:
    # Clean up the SANDBOX only. The live directory was never written to, so
    # there is nothing to restore here - and nothing to leak.
    shutil.rmtree(SANDBOX, ignore_errors=True)

print("\nlive corrections dir (untouched by this test):",
      sorted(p.name for p in LIVE_CORR.iterdir()))
if FAIL:
    print(f"RESULT: {len(FAIL)} FAILURE(S): {FAIL}")
    sys.exit(1)
print("RESULT: all correction rules proven to fire")
