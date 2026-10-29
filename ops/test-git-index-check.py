#!/usr/bin/env python3
"""Test the git-index checker.

WHY THIS EXISTS
---------------
`ops/check-git-index.py` was written after the index was emptied twice in
one afternoon, with no checker noticing. The whole point of it is to catch a
class of damage that CONTENT checks cannot see - the working tree was
perfectly intact, so every other checker stayed green while the repo's
tracking was one commit away from being wiped.

🔑 **A checker written to catch a nasty failure must itself be shown to be
ABLE to catch it.** Otherwise it is decoration. So this test damages a
SCRATCH repo in exactly the way the live repo was damaged, and requires the
checker to notice.

The checker reads GIT_INDEX, so it is driven against a scratch repo via
GIT_INDEX_CHECK_REPO.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/workspace")
CHECKER = REPO / "ops" / "check-git-index.py"

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def run_checker(repo):
    env = dict(os.environ)
    env["GIT_INDEX_CHECK_REPO"] = str(repo)
    p = subprocess.run([sys.executable, str(CHECKER)], cwd=str(repo),
                       capture_output=True, text=True, timeout=300, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def make_repo(root):
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=str(root), capture_output=True,
                   timeout=120)
    subprocess.run(["git", "config", "user.email", "idx@example.invalid"],
                   cwd=str(root), capture_output=True, timeout=60)
    subprocess.run(["git", "config", "user.name", "idx test"],
                   cwd=str(root), capture_output=True, timeout=60)
    for i in range(12):
        (root / ("f%02d.txt" % i)).write_text("content %d\n" % i)
    subprocess.run(["git", "add", "-A"], cwd=str(root), capture_output=True,
                   timeout=120)
    subprocess.run(["git", "commit", "-q", "-m", "files"], cwd=str(root),
                   capture_output=True, timeout=120)
    return root


def main():
    base = pathlib.Path(tempfile.mkdtemp(prefix="git-index-check-test-"))
    try:
        # --- 1. a healthy repo is CLEAN ---
        r1 = make_repo(base / "r1")
        rc1, out1 = run_checker(r1)
        check("a healthy repo is CLEAN (rc=0)", rc1 == 0, out1[-400:])
        check("the checker compares the index against HEAD",
              "tracked by HEAD" in out1, out1[:300])

        # --- 2. NEGATIVE CONTROL: the index is emptied ---
        # Exactly what ops/test-git-pre-push-guard.py did to the live repo.
        r2 = make_repo(base / "r2")
        subprocess.run(["git", "read-tree", "--empty"], cwd=str(r2),
                       capture_output=True, timeout=120)
        rc2, out2 = run_checker(r2)
        check("NEGATIVE: an EMPTIED index is caught (rc=1)", rc2 == 1,
              "rc=%d %s" % (rc2, out2[-400:]))
        check("NEGATIVE: the verdict says BROKEN", "BROKEN" in out2,
              out2[-400:])
        check("NEGATIVE: the repair is given", "reset --mixed" in out2,
              out2[-400:])
        check("NEGATIVE: it names the mass-deletion risk",
              "staged for deletion" in out2 or "index is EMPTY" in out2,
              out2[-400:])

        # --- 3. NEGATIVE CONTROL: the index is missing entirely ---
        r3 = make_repo(base / "r3")
        idx = r3 / ".git" / "index"
        if idx.exists():
            idx.unlink()
        rc3, out3 = run_checker(r3)
        check("NEGATIVE: a MISSING index is caught (rc=1)", rc3 == 1,
              "rc=%d %s" % (rc3, out3[-400:]))

        # --- 4. NEGATIVE CONTROL: index disagrees with HEAD ---
        r4 = make_repo(base / "r4")
        subprocess.run(["git", "rm", "-q", "--cached", "f00.txt"],
                       cwd=str(r4), capture_output=True, timeout=120)
        rc4, out4 = run_checker(r4)
        check("NEGATIVE: an index that DISAGREES with HEAD is caught",
              rc4 == 1, "rc=%d %s" % (rc4, out4[-400:]))

        # --- 5. NEGATIVE CONTROL: a GITLINK in the index ---
        # A gitlink (mode 160000) is a path that is ANOTHER repository. It
        # is not a file, so every CONTENT-based checker reads a clone and
        # finds an empty directory there, with no error anywhere. This is
        # the damage a leftover scratch dir with its own .git would cause
        # the moment `git add .` ran - and the index would still be
        # perfectly consistent with HEAD, so the OTHER checks in this
        # checker would all stay green.
        r5 = make_repo(base / "r5")
        nested = r5 / "nested-repo"
        nested.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=str(nested),
                       capture_output=True, timeout=120)
        subprocess.run(["git", "config", "user.email", "l@example.invalid"],
                       cwd=str(nested), capture_output=True, timeout=60)
        subprocess.run(["git", "config", "user.name", "link test"],
                       cwd=str(nested), capture_output=True, timeout=60)
        (nested / "x.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(nested),
                       capture_output=True, timeout=120)
        subprocess.run(["git", "commit", "-q", "-m", "nested"], cwd=str(nested),
                       capture_output=True, timeout=120)
        # This is the exact command that stages an embedded repo as a
        # gitlink - the same warning git prints in the live repo.
        subprocess.run(["git", "add", "-f", "nested-repo"], cwd=str(r5),
                       capture_output=True, timeout=120)
        rc5, out5 = run_checker(r5)
        check("NEGATIVE: a GITLINK in the index is caught (rc=1)", rc5 == 1,
              "rc=%d %s" % (rc5, out5[-400:]))
        check("NEGATIVE: the verdict names the gitlink",
              "GITLINK" in out5, out5[-400:])

        # --- 6. POSITIVE CONTROL: the gitlink check does not fire on a
        #            healthy repo (a guard that always fires is noise) ---
        r6 = make_repo(base / "r6")
        rc6, out6 = run_checker(r6)
        check("POSITIVE: a healthy repo with no gitlinks is still CLEAN",
              rc6 == 0, "rc=%d %s" % (rc6, out6[-400:]))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    if fails:
        print("FAILURES: %d -> %s" % (len(fails), fails))
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
