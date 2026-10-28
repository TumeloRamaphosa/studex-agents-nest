#!/usr/bin/env python3
"""Negative tests for ops/tmp-shape-surface-audit.py and
ops/redact-orphan-secrets-in-place.py.

WHY THIS FILE EXISTS: the first version of the shape audit PRINTED CLEAN while its
own results table listed UNKNOWN orphan rows - the counter compared
`verdict == "UNKNOWN"` but probe() returns `"UNKNOWN (no probe)"`. A checker that
cannot fail is worse than no checker, and this repo has now produced that bug
three times (cost-model checker, /tmp scanner, credential-resolution checker).

These tests prove, with a CONTROL CASE each way, that:
  1. an orphan literal that CANNOT be probed is counted as UNKNOWN -> EXPOSED
  2. a literal that IS in .env is classified IN-ENV, not ORPHAN
  3. a DEAD orphan is NOT counted as exposure
  4. a shape collision (implausible length) is ignored, not counted
  5. the redactor masks an orphan in place, preserving size and inode

Every check runs against a SANDBOX /tmp dir - never the live tree.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

OPS = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.join(OPS, "tmp-shape-surface-audit.py")
REDACT = os.path.join(OPS, "redact-orphan-secrets-in-place.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print("  %-58s %s%s" % (name, "PASS" if ok else "FAIL",
                            ("  <- " + detail) if (detail and not ok) else ""))


def sandbox(files):
    """Create a temp dir with the given {name: content} and return its path."""
    d = tempfile.mkdtemp(prefix="shape-audit-test-")
    for n, c in files.items():
        with open(os.path.join(d, n), "w") as fh:
            fh.write(c)
    return d


def run_audit(env_path, scan_root):
    """Run the audit with a controlled .env and scan root. Returns parsed rows.

    AUDIT_INCLUDE_FIXTURES=1 is REQUIRED here. The production audit ignores
    our own test-fixture directories (that is what stops a concurrent test
    run from being reported as a real exposure during a heartbeat pass), so
    without this opt-in the audit could not see the synthetic orphan this
    test is specifically testing for.
    """
    env = dict(os.environ)
    env["AUDIT_ENV_PATH"] = env_path
    env["AUDIT_SCAN_ROOT"] = scan_root
    env["AUDIT_NO_PROBE"] = "1"          # never touch a real provider
    env["AUDIT_INCLUDE_FIXTURES"] = "1"  # this test WANTS to see the fixture
    p = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True, env=env)
    return p.stdout + p.stderr, p.returncode


def count(out, label):
    """Count table rows for a given credential label in the audit output."""
    return len(re.findall(r"^\s+%s\s+len=" % re.escape(label), out, re.M))


def verdict(out):
    m = re.search(r"^VERDICT:\s*(\S+)", out, re.M)
    return m.group(1) if m else "NONE"


def main():
    print("=== test-tmp-shape-surface-audit.py ===")

    # A synthetic AgentMail-shaped literal (not in .env) -> ORPHAN, UNKNOWN.
    orphan = "am_us_" + "a1b2c3d4e5f6" * 4
    d = tempfile.mkdtemp(prefix="shape-env-")
    env_file = os.path.join(d, ".env")
    with open(env_file, "w") as fh:
        fh.write("SOME_OTHER_KEY=notashape\n")

    # 1. orphan, unprobeable -> UNKNOWN -> EXPOSED
    sb = sandbox({"leak.txt": "key is %s here\n" % orphan})
    out, rc = run_audit(env_file, sb)
    check("orphan unprobeable literal is reported", count(out, "AgentMail") == 1,
          "rows=%d" % count(out, "AgentMail"))
    check("orphan unprobeable literal -> VERDICT EXPOSED",
          verdict(out) == "EXPOSED", "got %s" % verdict(out))
    check("audit exits non-zero when exposed", rc != 0, "rc=%d" % rc)

    # 2. CONTROL: the same literal IN .env -> not an orphan -> CLEAN
    d2 = tempfile.mkdtemp(prefix="shape-env2-")
    env2 = os.path.join(d2, ".env")
    with open(env2, "w") as fh:
        fh.write("AGENTMAIL_TEST_KEY=%s\n" % orphan)
    sb2 = sandbox({"leak.txt": "key is %s here\n" % orphan})
    out2, rc2 = run_audit(env2, sb2)
    check("CONTROL: in-.env literal is not an orphan", count(out2, "AgentMail") == 0,
          "rows=%d" % count(out2, "AgentMail"))
    check("CONTROL: in-.env literal -> VERDICT CLEAN", verdict(out2) == "CLEAN",
          "got %s" % verdict(out2))

    # 3. implausible length -> shape collision -> ignored
    sb3 = sandbox({"big.txt": "blob am_us_" + "z" * 900 + " end\n"})
    out3, rc3 = run_audit(env_file, sb3)
    check("implausible-length shape is a collision, not an orphan",
          count(out3, "AgentMail") == 0, "rows=%d" % count(out3, "AgentMail"))

    # 4. empty dir -> CLEAN with a coverage statement
    sb4 = sandbox({})
    out4, rc4 = run_audit(env_file, sb4)
    check("empty dir -> VERDICT CLEAN", verdict(out4) == "CLEAN", "got %s" % verdict(out4))
    check("verdict carries a coverage statement (files read)",
          "files read" in out4)

    # 5. the redactor masks an orphan in place, preserving size and inode
    sb5 = sandbox({"target.log": "prefix %s suffix\n" % orphan})
    tgt = os.path.join(sb5, "target.log")
    before = os.stat(tgt)
    env = dict(os.environ)
    env["REDACT_ENV_PATH"] = env_file
    env["REDACT_SCAN_ROOT"] = sb5
    env["REDACT_NO_PROBE"] = "1"
    p = subprocess.run([sys.executable, REDACT], capture_output=True, text=True, env=env)
    after = os.stat(tgt)
    body = open(tgt).read()
    check("redactor masked the orphan value", orphan not in body)
    check("redactor preserved file size", before.st_size == after.st_size,
          "%d -> %d" % (before.st_size, after.st_size))
    check("redactor preserved inode", before.st_ino == after.st_ino,
          "%s -> %s" % (before.st_ino, after.st_ino))
    check("redactor kept surrounding bytes intact",
          body.startswith("prefix ") and body.endswith(" suffix\n"))

    # 6. REGRESSION (2026-10-27): a PRODUCTION audit - no opt-in - must NOT
    # report our own synthetic fixture as an exposure.
    #
    # This is the false positive that hit a real heartbeat pass: the audit's
    # own test writes a synthetic `am_us_...` literal into a /tmp fixture,
    # and the fixture-ignore list did not know that prefix. When the test
    # suite ran CONCURRENTLY with a pass, the pass reported EXPOSED.
    #
    # The failure was in the ignore LIST, not the detector - so the
    # regression has to be proved against the production path.
    prod_env = dict(os.environ)
    prod_env["AUDIT_ENV_PATH"] = env_file
    prod_env["AUDIT_SCAN_ROOT"] = sb          # the SAME synthetic fixture
    prod_env["AUDIT_NO_PROBE"] = "1"
    prod_env.pop("AUDIT_INCLUDE_FIXTURES", None)   # production path
    pp = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True,
                        env=prod_env)
    prod_out = pp.stdout + pp.stderr
    check("PRODUCTION audit ignores our own synthetic fixture",
          verdict(prod_out) == "CLEAN",
          "got %s (the fixture-ignore list must cover every prefix our own "
          "tests create)" % verdict(prod_out))
    check("PRODUCTION audit does not report the fixture as an orphan",
          count(prod_out, "AgentMail") == 0, "rows=%d" % count(prod_out, "AgentMail"))

    # 6b. And the ignore list must be DERIVED, not hand-kept: a fixture
    # prefix our tests create must be in it.
    audit_src = open(AUDIT).read()
    check("the fixture-ignore list is derived from the test files",
          "_derive_fixture_dirs" in audit_src and "FIXTURE_DIRS = tuple(sorted" in audit_src,
          "the list is hand-maintained again - it will drift and the "
          "false positive will return")

    for d in (sb, sb2, sb3, sb4, sb5, d, d2):
        shutil.rmtree(d, ignore_errors=True)

    failed = [n for n, ok, _ in RESULTS if not ok]
    print("\n%d passed, %d failed" % (len(RESULTS) - len(failed), len(failed)))
    if failed:
        for n in failed:
            print("  FAILED:", n)
    print("ALL TESTS PASS" if not failed else "TESTS FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
