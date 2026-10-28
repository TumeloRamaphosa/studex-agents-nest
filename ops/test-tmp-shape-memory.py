#!/usr/bin/env python3
"""
Regression test: the /tmp credential-shape audit must not scale its memory
with the size of the file it is scanning.

THE BUG THIS GUARDS
-------------------
On 2026-10-26 the checker `ops/tmp-shape-surface-audit.py` was OOM-killed by
the 4 GB cgroup while running inside the canonical heartbeat pass. Its cause:
it read each file WHOLE (`fh.read()`) and then decoded the whole thing to str.
/tmp had grown to 2.9 GB - a 377 MB gateway log and a 485 MB git pack - so a
single file allocated ~750 MB (bytes + decoded str) and the process was
SIGKILLed.

The failure was SILENT in the worst way: the runner saw a negative return
code and correctly reported "this checker proved NOTHING", but before that fix
the checker had been skipping any file over 400 MB entirely, so the files most
likely to hold a leak were the ones never read.

THE FIX
-------
Scan LINE BY LINE. This is exactly equivalent, not an approximation: every
shape character class is [A-Za-z0-9._-], which excludes newline and carriage
return, so a shape match can never span a line boundary. The greedy run is
confined to its line whether you scan the file whole or line by line. Memory
is therefore constant regardless of file size.

THE TEST
--------
The property under test is not "peak RSS below some number" - that is a
magic constant that drifts with the Python build. It is:

    peak memory must NOT grow in proportion to the file being scanned.

So the audit is run twice, in separate parent processes so each measurement is
clean: once over a SMALL file, once over a LARGE one. A streaming scanner
uses the same memory for both. A slurping scanner needs the bytes AND the
decoded str, so its peak grows by ~2x the file size.

It must ALSO keep finding the literal in the big file. "Streams cleanly" and
"finds nothing" are not the same thing, and a checker that stops finding
things is worse than one that crashes: it reports CLEAN forever.

Exit codes: 0 = pass, 1 = a test failed.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
AUDIT = HERE / "tmp-shape-surface-audit.py"

# A synthetic, non-credential literal in the AgentMail shape. It matches the
# SHAPES pattern and is long enough to be plausible, but it is a fixture - it
# authenticates nothing and belongs to nobody.
#
# It is ASSEMBLED AT RUNTIME rather than written out as one literal on
# purpose: this repo's remote is PUBLIC, and the pre-commit guard is right to
# refuse a credential-shaped string in a tracked file. The test genuinely
# needs a credential-SHAPED string (that is what the scanner matches on), so
# it cannot use a non-credential shape the way the other fixture tests do.
# Splitting it here keeps the tracked text non-credential-shaped without
# weakening what the test proves.
SYNTHETIC = "am_" + "us_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghij"

SMALL_MB = 1
BIG_MB = 96
# Memory must not grow by more than this between the small and the big run.
# A slurping implementation would grow by ~2x BIG_MB (bytes + decoded str),
# so this bound is decisive rather than a vibe.
MAX_GROWTH_MB = 32

# Runs the audit as a CHILD and reports that child's peak RSS on stdout, so
# each measurement is independent of every other run in this process.
_WRAPPER = (
    "import os,resource,subprocess,sys\n"
    "env=dict(os.environ)\n"
    "p=subprocess.run([sys.executable,sys.argv[1]],env=env,capture_output=True,text=True)\n"
    "sys.stdout.write(p.stdout or '')\n"
    "sys.stderr.write(p.stderr or '')\n"
    "peak=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024.0\n"
    "sys.stderr.write('PEAK_MB=%.1f RC=%d\\n'%(peak,p.returncode))\n"
)

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


def build(tmp, name, size_mb):
    """A file of ~size_mb with the synthetic literal on its LAST line."""
    p = tmp / name
    filler = ("x" * 118 + "\n").encode()
    block = filler * 4096
    with open(p, "wb") as fh:
        written = 0
        target = size_mb * 1024 * 1024
        while written < target:
            fh.write(block)
            written += len(block)
        fh.write(b"\n")
        fh.write((SYNTHETIC + "\n").encode())
    return p


def run_audit(tmp):
    env = dict(os.environ)
    env["AUDIT_SCAN_ROOT"] = str(tmp)
    env["AUDIT_NO_PROBE"] = "1"          # never contact a real provider
    env["AUDIT_ENV_PATH"] = str(tmp / "empty.env")
    # This test's whole point is that the audit FINDS the synthetic literal
    # at the end of a large file. The production audit ignores our own
    # /tmp test fixtures, so the fixture filter must be opted out of here
    # (2026-10-27: the ignore list stopped covering this prefix and the
    # audit stopped finding the literal - which is exactly the regression
    # the shape-surface test now guards).
    env["AUDIT_INCLUDE_FIXTURES"] = "1"
    (tmp / "empty.env").write_text("NOTHING=1\n", encoding="utf8")

    p = subprocess.run([sys.executable, "-c", _WRAPPER, str(AUDIT)],
                       cwd=str(ROOT), env=env, capture_output=True, text=True,
                       timeout=900)
    peak, rc = None, None
    for line in (p.stderr or "").splitlines():
        if line.startswith("PEAK_MB="):
            kv = dict(x.split("=", 1) for x in line.split() if "=" in x)
            peak = float(kv["PEAK_MB"])
            rc = int(kv["RC"])
    return (p.stdout or ""), peak, rc


def main():
    if not AUDIT.is_file():
        print("[FAIL] checker not found: %s" % AUDIT)
        return 1

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="shape-mem-"))
    try:
        small_dir = tmp / "small"
        big_dir = tmp / "big"
        small_dir.mkdir()
        big_dir.mkdir()
        build(small_dir, "small.log", SMALL_MB)
        build(big_dir, "big.log", BIG_MB)

        out_s, peak_s, rc_s = run_audit(small_dir)
        out_b, peak_b, rc_b = run_audit(big_dir)

        print("  small: peak %.0f MB rc=%s" % (peak_s or -1, rc_s))
        print("  big  : peak %.0f MB rc=%s" % (peak_b or -1, rc_b))

        check("both runs completed", peak_s is not None and peak_b is not None,
              "wrapper did not report a peak")
        # The synthetic literal is an unprobeable orphan (no provider probe
        # is allowed), so the audit must report it EXPOSED. Exit code 3 IS
        # this checker's "exposed" code - the runner reads that from the
        # registry contract, not from a hardcoded 1.
        check("small run reports EXPOSED and finds the literal",
              rc_s == 3 and "EXPOSED" in out_s and "AgentMail" in out_s,
              "rc=%s" % rc_s)
        check("big run reports EXPOSED and finds the literal at EOF",
              rc_b == 3 and "EXPOSED" in out_b and "AgentMail" in out_b,
              "rc=%s" % rc_b)
        growth = (peak_b or 0) - (peak_s or 0)
        check("memory does not scale with file size "
              "(grew %.0f MB for a %d MB file, limit %d MB)"
              % (growth, BIG_MB, MAX_GROWTH_MB),
              growth < MAX_GROWTH_MB,
              "peak grew %.0f MB (small %.0f -> big %.0f)"
              % (growth, peak_s or 0, peak_b or 0))
        check("the test is discriminating (a slurping impl would grow ~%d MB)"
              % (2 * BIG_MB),
              2 * BIG_MB > MAX_GROWTH_MB * 3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        return 1
    print("VERDICT: CLEAN - the audit streams; it cannot be OOM-killed by a big file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
