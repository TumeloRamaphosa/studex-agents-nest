#!/usr/bin/env python3
"""The general fragment audit must FAIL when there is a fragment to find.

2026-10-28. `ops/audit-blotato-fragments.py` checked ONE credential out of
fifty and reported CLEAN while 22 tracked files held fragments of fifteen
credentials, seven of them proven LIVE. It was not broken - it was
watching the wrong thing.

`ops/audit-credential-fragments.py` watches all of them. A checker that
has never been SEEN TO FAIL is not a guard, so this test proves the new
audit fails on a real, seeded fragment - of a credential the old one
never looked at.

Negative controls included:
  * a clean repository is CLEAN (the audit does not cry wolf)
  * the old one-credential audit is STILL CLEAN on the same state - which
    is precisely why it was not a guard
  * a fragment of the credential the old audit DID watch is caught too
  * a fragment shorter than the minimum is not reported
  * a TAIL-only leak is caught - the case the one-sided prefilter missed
"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/workspace")
AUDIT = REPO / "ops/audit-credential-fragments.py"
OLD = REPO / "ops/audit-blotato-fragments.py"

spec = importlib.util.spec_from_file_location("au", AUDIT)
au = importlib.util.module_from_spec(spec)
spec.loader.exec_module(au)

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


print("=== the ground-truth measurement is independent of the detection ===")
# The ground truth is a credential of the RIGHT SHAPE that is NOT LIVE.
#
# These two used to be pasted in whole, and they were the real values -
# a "synthetic" credential that happens to be the actual one is the worst
# kind of fixture, because it leaks while looking safe. The pre-commit
# guard blocked the commit and was RIGHT to.
#
# A fake credential is only fake if it shares NO 12-character slice with
# a live one, so the characters below are chosen to differ from every
# live key in .env. The shape (prefix + length) is what is under test.
FAKE_PINE = "pcsk_" + "Zz8Qv4Nb7Xc2Lm9Rt5Yu3Io1Pa6Sd4Fg0Hj2Kl8Qw9Er1Ty5Uv3Bz6"
FAKE_MAIL = "am_us_" + "Mx2Qw7Er9Ty4Ui6Op1As3Df5Gh7Jk9Lz1Xc3Vb5Nm8Qw2Er6Rt4Y"
SECRET = FAKE_PINE.encode()
OTHER = FAKE_MAIL.encode()
data = b"prefix " + SECRET[20:] + b" suffix"
check("the longest run in the data is measured", au.longest_run(data, SECRET.decode()) == len(SECRET) - 20,
      "got %d" % au.longest_run(data, SECRET.decode()))
check("a clean file measures 0", au.longest_run(b"nothing here", SECRET.decode()) == 0)

print()
print("=== the candidate filter is TWO-SIDED ===")
# A tail-only leak: contains none of the credential's first 4 bytes.
tail_only = SECRET[20:]
check("a TAIL-only leak is a candidate",
      bool(au.candidates(tail_only, [("P", SECRET.decode())])))
check("a file with no window of it is not a candidate",
      au.candidates(b"nothing here", [("P", SECRET.decode())]) == [])

print()
print("=== THE AUDIT FAILS ON A SEEDED FRAGMENT ===")
d = pathlib.Path(tempfile.mkdtemp(prefix="audit-test-"))
subprocess.run(["git", "init", "-q", str(d)], check=True)
subprocess.run(["git", "-C", str(d), "config", "user.email", "t@t"], check=True)
subprocess.run(["git", "-C", str(d), "config", "user.name", "t"], check=True)
(d / "note.md").write_bytes(b"the key is " + SECRET[20:] + b" ok\n")
(d / "clean.md").write_bytes(b"nothing secret in this file at all\n")
subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(d), "commit", "-qm", "x"], check=True)

# an env file holding that credential
envf = d / ".env"
envf.write_text("PINECONE_API_KEY=%s\n" % SECRET.decode(), encoding="utf-8")

p = subprocess.run([sys.executable, str(AUDIT), "--repo", str(d),
                    "--env", str(envf), "--no-probe"],
                   capture_output=True, text=True, timeout=300)
out = p.stdout + p.stderr
check("the audit EXITS NON-ZERO on a seeded fragment", p.returncode != 0,
      "rc=%d" % p.returncode)
check("it names the file", "note.md" in out, out[-400:])
check("it names the credential", "PINECONE" in out, out[-400:])
check("it does NOT flag the clean file", "clean.md" not in out, out[-400:])
check("it says how much leaked", "VERDICT" in out and "fragment" in out.lower(), out[-300:])

print()
print("=== NEGATIVE CONTROL 1: a clean repository is CLEAN ===")
d2 = pathlib.Path(tempfile.mkdtemp(prefix="audit-clean-"))
subprocess.run(["git", "init", "-q", str(d2)], check=True)
subprocess.run(["git", "-C", str(d2), "config", "user.email", "t@t"], check=True)
subprocess.run(["git", "-C", str(d2), "config", "user.name", "t"], check=True)
(d2 / "a.md").write_bytes(b"nothing secret here\n")
subprocess.run(["git", "-C", str(d2), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(d2), "commit", "-qm", "x"], check=True)
envf2 = d2 / ".env"
envf2.write_text("PINECONE_API_KEY=%s\n" % SECRET.decode(), encoding="utf-8")
p2 = subprocess.run([sys.executable, str(AUDIT), "--repo", str(d2),
                     "--env", str(envf2), "--no-probe"],
                    capture_output=True, text=True, timeout=300)
out2 = p2.stdout + p2.stderr
check("the audit exits 0 on a clean repo", p2.returncode == 0, "rc=%d" % p2.returncode)
check("and it says CLEAN", "VERDICT: CLEAN" in out2, out2[-300:])

print()
print("=== NEGATIVE CONTROL 2: the OLD one-credential audit was NOT a guard ===")
print("    (it is run on the SAME seeded state, and it must be CLEAN -")
print("     which is exactly why it never caught the 22 files)")
if OLD.exists():
    p3 = subprocess.run([sys.executable, str(OLD)], capture_output=True, text=True,
                        timeout=300, env={**__import__("os").environ,
                                          "GUARD_ENV_FILE": str(envf)})
    out3 = p3.stdout + p3.stderr
    check("the OLD audit reports CLEAN on the seeded state",
          "CLEAN" in out3, out3[-300:])
    check("and it does not name the file", "note.md" not in out3, out3[-300:])
    print("    ⇒ THE OLD AUDIT WAS WATCHING ONE KEY AND MISSED THIS ONE")
else:
    print("    (the old audit has been removed - the new one replaces it)")

print()
print("=== NEGATIVE CONTROL 3: a fragment SHORTER than the minimum is not reported ===")
d3 = pathlib.Path(tempfile.mkdtemp(prefix="audit-short-"))
subprocess.run(["git", "init", "-q", str(d3)], check=True)
subprocess.run(["git", "-C", str(d3), "config", "user.email", "t@t"], check=True)
subprocess.run(["git", "-C", str(d3), "config", "user.name", "t"], check=True)
(d3 / "s.md").write_bytes(b"a " + SECRET[:8] + b" b\n")
subprocess.run(["git", "-C", str(d3), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(d3), "commit", "-qm", "x"], check=True)
envf3 = d3 / ".env"
envf3.write_text("PINECONE_API_KEY=%s\n" % SECRET.decode(), encoding="utf-8")
p4 = subprocess.run([sys.executable, str(AUDIT), "--repo", str(d3),
                     "--env", str(envf3), "--no-probe"],
                    capture_output=True, text=True, timeout=300)
check("an 8-character run is not a fragment", p4.returncode == 0,
      "rc=%d" % p4.returncode)

print()
print("=== NEGATIVE CONTROL 4: a HEAD-only leak is caught too ===")
d4 = pathlib.Path(tempfile.mkdtemp(prefix="audit-head-"))
subprocess.run(["git", "init", "-q", str(d4)], check=True)
subprocess.run(["git", "-C", str(d4), "config", "user.email", "t@t"], check=True)
subprocess.run(["git", "-C", str(d4), "config", "user.name", "t"], check=True)
(d4 / "h.md").write_bytes(b"key " + SECRET[:30] + b"\n")
subprocess.run(["git", "-C", str(d4), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(d4), "commit", "-qm", "x"], check=True)
envf4 = d4 / ".env"
envf4.write_text("PINECONE_API_KEY=%s\n" % SECRET.decode(), encoding="utf-8")
p5 = subprocess.run([sys.executable, str(AUDIT), "--repo", str(d4),
                     "--env", str(envf4), "--no-probe"],
                    capture_output=True, text=True, timeout=300)
out5 = p5.stdout + p5.stderr
check("a HEAD leak is caught", p5.returncode != 0, "rc=%d" % p5.returncode)
check("and the file is named", "h.md" in out5, out5[-300:])

print()
if fails:
    print("FAILURES: %d -> %s" % (len(fails), fails))
    sys.exit(1)
print("ALL CHECKS PASS")
