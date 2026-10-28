#!/usr/bin/env python3
"""Test the pre-push guard checker - and the guard itself.

This covers the failure that shipped a CLEAN verdict over an INERT guard:

    core.hooksPath = .githooks  ->  git runs .githooks/pre-push
                                 ->  a hook in .git/hooks/ NEVER RUNS

The old checker hard-coded `.git/hooks/pre-push`, so it reported CLEAN
while the guard it was "confirming" was never executed by git. A checker
that validates a path nothing reads always passes.

So the tests here drive the checker against a REPO WITH A DIFFERENT
hooksPath, and assert it finds the effective path - not a hard-coded one.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/workspace")
CHECKER = REPO / "ops" / "check-pre-push-guard.py"
SOURCE = REPO / "ops" / "git-pre-push-guard.py"

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def run_checker(cwd, repo=None):
    env = dict(os.environ)
    if repo is not None:
        env["GUARD_CHECK_REPO"] = str(repo)
    p = subprocess.run([sys.executable, str(CHECKER)], cwd=str(cwd),
                       capture_output=True, text=True, timeout=300, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def make_repo(root, hooks_path=None):
    """A tiny git repo with the checker + source copied in."""
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=str(root), capture_output=True,
                   timeout=120)
    (root / "ops").mkdir(exist_ok=True)
    shutil.copy2(CHECKER, root / "ops" / "check-pre-push-guard.py")
    shutil.copy2(SOURCE, root / "ops" / "git-pre-push-guard.py")
    if hooks_path:
        subprocess.run(["git", "config", "core.hooksPath", hooks_path],
                       cwd=str(root), capture_output=True, timeout=60)
    return root


def main():
    base = pathlib.Path(tempfile.mkdtemp(prefix="prepush-check-test-"))

    # --- 1. the REAL repo: the effective path must be reported ---
    rc, out = run_checker(REPO)
    check("the real repo resolves a hooks path via git config",
          "effective hooks dir" in out, out[:300])
    check("the real repo's guard is CLEAN", rc == 0, out[-300:])
    if "core.hooksPath" in out:
        _, hooks = _hooks_path_of(REPO)
        check("the reported hooks dir is the one git uses",
              hooks in out, "git says %r, checker said %r" % (hooks, out))

    # --- 2. a repo whose core.hooksPath points elsewhere ---
    r2 = make_repo(base / "r2", hooks_path=".githooks")
    (r2 / ".githooks").mkdir(exist_ok=True)
    (r2 / ".githooks" / "pre-push").write_bytes(SOURCE.read_bytes())
    os.chmod(r2 / ".githooks" / "pre-push", 0o755)
    # A decoy in .git/hooks/ - the exact trap that shipped the bug.
    (r2 / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
    (r2 / ".git" / "hooks" / "pre-push").write_bytes(SOURCE.read_bytes())
    os.chmod(r2 / ".git" / "hooks" / "pre-push", 0o755)

    rc2, out2 = run_checker(r2, repo=r2)
    check("a repo with core.hooksPath is judged by THAT path",
          ".githooks" in out2, out2[:400])
    check("the decoy in .git/hooks/ does not make it PASS alone",
          rc2 == 0, "rc=%d" % rc2)

    # --- 3. NEGATIVE CONTROL: remove the hook git actually reads ---
    os.unlink(r2 / ".githooks" / "pre-push")
    rc3, out3 = run_checker(r2, repo=r2)
    check("NEGATIVE: removing the EFFECTIVE hook is caught (rc=1)",
          rc3 == 1, "rc=%d" % rc3)
    check("NEGATIVE: the verdict says NOT INSTALLED",
          "NOT INSTALLED" in out3, out3[-300:])

    # --- 4. NEGATIVE CONTROL: a stale hook at the effective path ---
    r4 = make_repo(base / "r4", hooks_path=".githooks")
    (r4 / ".githooks").mkdir(exist_ok=True)
    (r4 / ".githooks" / "pre-push").write_bytes(b"#!/bin/sh\n# an OLD policy\n")
    os.chmod(r4 / ".githooks" / "pre-push", 0o755)
    rc4, out4 = run_checker(r4, repo=r4)
    check("NEGATIVE: a STALE hook at the effective path is caught (rc=1)",
          rc4 == 1, "rc=%d" % rc4)
    check("NEGATIVE: the verdict names the source divergence",
          "differs" in out4, out4[-300:])

    # --- 5. NEGATIVE CONTROL: a non-executable hook ---
    r5 = make_repo(base / "r5", hooks_path=".githooks")
    (r5 / ".githooks").mkdir(exist_ok=True)
    (r5 / ".githooks" / "pre-push").write_bytes(SOURCE.read_bytes())
    os.chmod(r5 / ".githooks" / "pre-push", 0o644)   # not executable
    rc5, out5 = run_checker(r5, repo=r5)
    check("NEGATIVE: a NON-EXECUTABLE hook is caught (rc=1)",
          rc5 == 1, "rc=%d" % rc5)

    # --- 6. the guard's own test suite must PASS ---
    if SOURCE.is_file():
        proc = subprocess.run([sys.executable, str(REPO / "ops" /
                                                    "test-git-pre-push-guard.py")],
                               cwd=str(REPO), capture_output=True, text=True,
                               timeout=900)
        # This used to assert `proc.returncode != 0` under the name "the
        # guard itself still blocks a live credential": it ran the guard's
        # own test file and REQUIRED IT TO FAIL. It was green because that
        # test was genuinely broken - a test asserting that another test is
        # broken, green while asserting the opposite of its name.
        check("the guard's own test suite passes",
              proc.returncode == 0, (proc.stdout or "")[-400:])

    shutil.rmtree(base, ignore_errors=True)

    print()
    if fails:
        print("FAILURES: %d -> %s" % (len(fails), fails))
        return 1
    print("ALL CHECKS PASS")
    return 0


def _hooks_path_of(repo):
    r = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                       cwd=str(repo), capture_output=True, text=True, timeout=60)
    v = (r.stdout or "").strip()
    return r.returncode, (v if v else ".git/hooks")


if __name__ == "__main__":
    sys.exit(main())
