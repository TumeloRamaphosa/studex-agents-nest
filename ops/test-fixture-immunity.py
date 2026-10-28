#!/usr/bin/env python3
"""Prove the rule-proving tests cannot poison the LIVE directories they check.

Two tests prove drift-check's rules fire by writing a deliberately-bad file
and checking that drift-check flags it:

  - `ops/test-correction-rules.py` -> wrote into LIVE `outbound-corrections/`
  - `ops/test-draft-rules.py`       -> wrote into LIVE `outbound-drafts/`

An interrupted run (timeout, kill, crash) left those fixtures behind, and then:

  1. the real drift check cried wolf on a test artefact, and
  2. the tests' own "MUST PASS" cases failed for the wrong reason.

`outbound-drafts/` is worse than a false alarm: it holds REAL email drafts
that go out to REAL external partners. A stray test file there is one stray
approval away from being sent to a buyer.

The fix is structural: both tests now work on a SANDBOX and point drift-check
at it via DRIFT_CHECK_CORRECTION_DIR / DRIFT_CHECK_DRAFT_DIR, so the live
directories are never written to.

This test proves, for BOTH directories:
  A. the live dir is byte-identical before and after the test runs
  B. the test still PROVES the rules fire (it is not a test that skips itself)
  C. a real forbidden claim is STILL caught - the sandbox did not blindfold
     the checker, it only moved the fixture
  D. the sandbox is cleaned up

Run: python3 ops/test-fixture-immunity.py
"""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path("/workspace")
LIVE_CORR = ROOT / "outbound-corrections"
LIVE_DRAFTS = ROOT / "outbound-drafts"
SANDBOX = pathlib.Path("/tmp/fixture-immunity-sandbox")

FAIL = []


def check(label, cond, detail=""):
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label,
                           (" -> " + detail) if detail and not cond else ""))
    if not cond:
        FAIL.append(label)


def snapshot(d):
    """Hash every file in a directory - content AND names."""
    out = {}
    if not d.exists():
        return out
    for f in sorted(d.iterdir()):
        if f.is_file():
            out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def run_drift(corr_dir=None, draft_dir=None):
    env = dict(os.environ)
    if corr_dir:
        env["DRIFT_CHECK_CORRECTION_DIR"] = str(corr_dir)
    if draft_dir:
        env["DRIFT_CHECK_DRAFT_DIR"] = str(draft_dir)
    r = subprocess.run([sys.executable, "ops/drift-check.py"], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=300, env=env)
    return r.stdout


# The two tests that write fixtures, and the live dir each one owns.
CASES = [
    ("ops/test-correction-rules.py", LIVE_CORR, "DRIFT_CHECK_CORRECTION_DIR",
     "outbound-corrections"),
    ("ops/test-draft-rules.py", LIVE_DRAFTS, "DRIFT_CHECK_DRAFT_DIR",
     "outbound-drafts"),
]

for test_rel, live_dir, env_var, rel_label in CASES:
    print("\n--- %s -> %s ---" % (test_rel, rel_label))

    # ---------------------------------------------------------- A + B + D
    before = snapshot(live_dir)
    r = subprocess.run([sys.executable, test_rel], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=400)
    after = snapshot(live_dir)

    check("the test itself passes", r.returncode == 0,
          "exit=%d %s" % (r.returncode, (r.stdout or "")[-400:]))
    check("A. the LIVE dir is byte-identical after the test",
          before == after,
          "before=%s after=%s" % (sorted(before), sorted(after)))
    check("A. no fixture was left behind in the live dir",
          "ok.md" not in after,
          "the live dir now contains ok.md")
    check("D. the sandbox was cleaned up",
          not pathlib.Path("/tmp/corr-rules-sandbox").exists()
          and not pathlib.Path("/tmp/drafts-sandbox").exists(),
          "a sandbox directory was left behind")

    # ---------------------------------------------------------- C
    # Negative control: a REAL file with a REAL forbidden claim must still be
    # caught. If the sandbox had blinded the checker, this would pass silently.
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    shutil.copytree(live_dir, SANDBOX)
    try:
        (SANDBOX / "real-test-file.md").write_text(
            "# Real file\n\n## Draft body\n\n```\n"
            "Dear buyer, our coffee is PROWTC certified and available at USD 4,200/MT.\n"
            "```\n", encoding="utf8")
        kw = {env_var: str(SANDBOX.resolve())}
        if env_var == "DRIFT_CHECK_CORRECTION_DIR":
            out = run_drift(corr_dir=SANDBOX.resolve())
        else:
            out = run_drift(draft_dir=SANDBOX.resolve())
        check("C. NEGATIVE CONTROL: a real forbidden claim is STILL caught",
              "DRIFT DETECTED" in out, "the checker was blinded")
        check("C. it names the offending file", "real-test-file.md" in out,
              "the offending file was not named")
    finally:
        shutil.rmtree(SANDBOX, ignore_errors=True)

# The live tree must still be clean right now.
out_live = run_drift()
check("the live tree is CLEAN right now", "DRIFT DETECTED" not in out_live,
      "the live tree has drift:\n" + out_live[-800:])

print()
if FAIL:
    print("RESULT: %d FAILURE(S): %s" % (len(FAIL), FAIL))
    sys.exit(1)
print("RESULT: neither test can poison a live directory, and the checker is not blinded")
