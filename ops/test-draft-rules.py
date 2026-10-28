"""Fix the draft price regex to handle comma-grouped thousands, and prove the
new draft rules actually FIRE (a checker that can never fail is worthless).
"""
import os, re, shutil, subprocess, sys, pathlib

P = "ops/drift-check.py"
src = open(P, encoding="utf8").read()

# IDEMPOTENT: this script both FIXES and TESTS. The fix it applies was
# committed to ops/drift-check.py by 40c941b6, so on the second run the
# "old" pattern is gone and the original assert fired ("price regex not
# found") - a test that can only pass once, and then reports a FAILURE for
# a source file that is already correct.
#
# A check must be able to run repeatedly and report the CURRENT state.
# If the fix is already in place, say so and carry on to the negative test.
old_re = r'for m in re.finditer(r"\b(?:R|USD)\s?([0-9]+(?:\.[0-9]+)?)", body, re.I):'
new_re = r'for m in re.finditer(r"\b(?:R|USD)\s?([0-9][0-9,]*(?:\.[0-9]+)?)", body, re.I):'
old_cmp = 'amt = m.group(1)\n'
new_cmp = 'amt = m.group(1).replace(",", "")\n'

changed = False
if old_re in src:
    src = src.replace(old_re, new_re)
    changed = True
    print("price regex hardened (comma-grouped thousands)")
else:
    assert new_re in src, "price regex not found in EITHER form - drift-check.py changed shape"

if old_cmp in src and 'replace(",", "")' not in src:
    src = src.replace(old_cmp, new_cmp)
    changed = True
    print("price compare hardened (comma-grouped thousands)")
else:
    assert 'replace(",", "")' in src, "price compare not found in EITHER form"

if changed:
    open(P, "w", encoding="utf8").write(src)
else:
    print("fix already present in ops/drift-check.py - nothing to change")

# ---------------------------------------------------------------- negative test
# The LIVE drafts directory - real email drafts for real external partners.
# This test must never write into it.
LIVE_DRAFTS = pathlib.Path("outbound-drafts")

# A SANDBOX copy. The fixture is written here and drift-check is pointed at it
# via DRIFT_CHECK_DRAFT_DIR, so an interrupted run can never leave a test file
# in the live drafts folder - where it is one approval away from being sent.
SANDBOX = pathlib.Path("/tmp/drafts-sandbox")
DRAFTS = SANDBOX
BACKUP = pathlib.Path("/tmp/drafts-backup")

# A fixture left in the LIVE dir by an OLD interrupted run must be removed, or
# it sits in the approval queue looking like a real draft.
STALE_LIVE_FIXTURE = LIVE_DRAFTS / "ok.md"
if STALE_LIVE_FIXTURE.exists():
    STALE_LIVE_FIXTURE.unlink()
    print("  (removed a stale test fixture left in the LIVE drafts dir)")

if BACKUP.exists():
    shutil.rmtree(BACKUP)
shutil.copytree(LIVE_DRAFTS, BACKUP)

# Build the SANDBOX: a copy of the live drafts dir.
if SANDBOX.exists():
    shutil.rmtree(SANDBOX)
shutil.copytree(LIVE_DRAFTS, SANDBOX)

def run():
    # Point drift-check at the SANDBOX, not the live directory.
    env = dict(os.environ)
    env["DRIFT_CHECK_DRAFT_DIR"] = str(SANDBOX.resolve())
    r = subprocess.run([sys.executable, "ops/drift-check.py"], capture_output=True,
                       text=True, timeout=300, env=env)
    return r.stdout

CASES = {
    "superseded URL": ("ok.md", "Hello. Sheet: https://z7p9urw22jwb.space.mcode.io"),
    "invented price": ("ok.md", "Wagyu ribeye R1,111/kg for you."),
    "forbidden claim": ("ok.md", "Every product we produce is certified Halaal."),
    "non-canonical URL": ("ok.md", "Sheet: https://zzzunknown99.space.mcode.io"),
    "clean control": ("ok.md", "Hi, our Wagyu ribeye is R1,050/kg. Sheet: https://hhsmhunf1xci.space.mcode.io"),
}

try:
    for label, (fname, body) in CASES.items():
        for f in DRAFTS.glob("*.md"):
            f.unlink()
        for f in BACKUP.glob("*.md"):
            shutil.copy(f, DRAFTS / f.name)
        (DRAFTS / fname).write_text(
            "# DRAFT — test\n\n## Draft body\n\n```\n" + body + "\n```\n", encoding="utf8")
        out = run()
        drift = "DRIFT DETECTED" in out
        line = [l.strip() for l in out.splitlines() if l.strip().startswith("- outbound-drafts/ok.md")]
        expect = label != "clean control"
        ok = drift == expect
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:<22} drift={drift} expected={expect}")
        if line:
            print(f"         {line[0][:150]}")
finally:
    # Clean up the SANDBOX only. The live directory was never written to, so
    # there is nothing to restore here - and nothing to leak.
    shutil.rmtree(SANDBOX, ignore_errors=True)

print("\nlive drafts dir (untouched by this test):",
      sorted(p.name for p in LIVE_DRAFTS.iterdir()))

# Check the LIVE tree, not the (now deleted) sandbox. Pointing the final check
# at the deleted sandbox printed "Outbound email drafts CLEAN - no drafts
# directory", which is a FALSE GREEN: the directory did not exist, so nothing
# was asserted. A green tick that asserted nothing is worse than no checker.
live_env = dict(os.environ)
live_env.pop("DRIFT_CHECK_DRAFT_DIR", None)
live_env.pop("DRIFT_CHECK_CORRECTION_DIR", None)
r = subprocess.run([sys.executable, "ops/drift-check.py"], capture_output=True,
                   text=True, timeout=300, env=live_env)
out = r.stdout
for l in out.splitlines():
    if "Outbound email drafts" in l or l.startswith("pages:"):
        print("  " + l.strip())
if "DRIFT DETECTED" in out:
    print("  !! DRIFT DETECTED in the live tree")
    sys.exit(1)
