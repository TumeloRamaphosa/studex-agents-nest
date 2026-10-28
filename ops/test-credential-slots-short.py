#!/usr/bin/env python3
"""The credential-slot checker must not call a short-but-real credential broken.

2026-10-28: the .env slot for ALIBABA_SSH_PASSWORD holds an 11-character
password - a perfectly real credential. The checker's 16-character length
floor called it BROKEN. That is a false failure on a working credential,
and a checker that cries wolf on real credentials is a checker people learn
to ignore - which is exactly how the PLACEHOLDER it exists to catch slips
through.

A length floor is a guess. The SHAPE is the rule. So:
  * a PLACEHOLDER / EMPTY / NOT-A-CREDENTIAL slot is still BROKEN
  * a TOO-SHORT slot is REPORTED and is not a failure
"""
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile

WS = pathlib.Path("/workspace")
CHECKER = WS / "ops" / "check-credential-slots.py"

spec = importlib.util.spec_from_file_location("ccs", CHECKER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

fails = []

# A credential-SHAPED value with NO vendor prefix. The pre-commit guard
# blocks any file holding a value shaped like a real vendor key (blt_,
# sk_, AIza, ...) - and it was RIGHT to: a file that looks like it holds a
# live key must not reach a PUBLIC remote. The classifier under test is
# shape-based and never needed a vendor prefix, so the repo's own
# convention ("B" * 40, in ops/test-credential-slots.py) is used here.
FIXTURE = "B" * 40


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def run(env_text, tracked=False):
    """Run the checker against a temp env file; return (rc, out)."""
    tmp = tempfile.mkdtemp(prefix="slots-test-")
    envf = pathlib.Path(tmp) / ".env"
    envf.write_text(env_text, encoding="utf-8")
    cmd = [sys.executable, str(CHECKER)]
    if tracked:
        cmd.append("--tracked")
    cmd.append(str(envf))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(WS / "scripts")
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("=== the classifier's own decisions ===")
check("a long alphanumeric token is a CREDENTIAL",
      m.classify(FIXTURE) == "CREDENTIAL")
check("an empty value is EMPTY", m.classify("") == "EMPTY")
check("a redaction artefact is a PLACEHOLDER",
      m.classify('t = t.replace(secret, "***")') == "PLACEHOLDER")
check("a REDACTED marker is a PLACEHOLDER",
      m.classify("REDACTED_CREDENTIAL_XXXX") == "PLACEHOLDER")
check("an 11-character password is TOO-SHORT (reported, not broken)",
      m.classify("11charlongpw") == "TOO-SHORT")

print()
print("=== the checker's VERDICT: a short-but-real credential is not BROKEN ===")
rc, out = run("SSH_PASSWORD=11charlongpw\n")
check("a short-but-real credential does not fail the checker (rc=0)", rc == 0,
      "rc=%d" % rc)
check("and it says CLEAN", "VERDICT: CLEAN" in out, out[-300:])
check("and it REPORTS the slot as short", "short-but-real" in out, out[-300:])
check("and it names the slot", "SSH_PASSWORD" in out, out[-300:])

print()
print("=== NEGATIVE CONTROL: a real placeholder is still BROKEN ===")
rc, out = run("BLOTATO_API_KEY=t = t.replace(secret, \"***\")\n")
check("a redaction artefact FAILS the checker (rc!=0)", rc != 0, "rc=%d" % rc)
check("and it says BROKEN", "VERDICT: BROKEN" in out, out[-300:])
check("and it names the slot", "BLOTATO_API_KEY" in out, out[-300:])

rc, out = run("BLOTATO_API_KEY=\n")
check("an EMPTY slot FAILS the checker (rc!=0)", rc != 0, "rc=%d" % rc)
check("and it says BROKEN", "VERDICT: BROKEN" in out, out[-300:])

rc, out = run("BLOTATO_API_KEY=REDACTED_CREDENTIAL_XXXX\n")
check("a REDACTED marker FAILS the checker (rc!=0)", rc != 0, "rc=%d" % rc)

print()
print("=== POSITIVE CONTROL: a healthy slot is still CLEAN ===")
rc, out = run("BLOTATO_API_KEY=" + FIXTURE + "\n")
check("a healthy slot passes (rc=0)", rc == 0, "rc=%d" % rc)
check("and it says CLEAN", "VERDICT: CLEAN" in out, out[-300:])

print()
print("=== the pre-fix behaviour is what we are fixing ===")
# The pre-fix rule: anything that is not literally "CREDENTIAL" is a problem.
# Written out as the golden reference, so this test does not depend on a
# commit that a history rewrite could delete.
def pre_fix_problems(kind):
    return kind != "CREDENTIAL"


check("NEGATIVE CONTROL: the pre-fix rule called TOO-SHORT a problem",
      pre_fix_problems("TOO-SHORT") is True)
check("and the pre-fix rule called PLACEHOLDER a problem too",
      pre_fix_problems("PLACEHOLDER") is True)
check("POSITIVE CONTROL: the pre-fix rule agreed on a real CREDENTIAL",
      pre_fix_problems("CREDENTIAL") is False)

print()
if fails:
    print("FAILURES: %d -> %s" % (len(fails), fails))
    sys.exit(1)
print("ALL CHECKS PASS")
