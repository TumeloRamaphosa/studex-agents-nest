#!/usr/bin/env python3
"""Regression test for ops/check-public-exposure.py.

THE RULE THIS ENFORCES
-----------------------
A credential checker that only scans the working tree is blind to the thing
that actually leaks: a PUBLIC remote. This workspace proved it - the tracked
working tree was CLEAN over 4166 files while the pushed branches still served
live, authenticating keys to any stranger who cloned them.

So the check must scan the PUSHED REFS, including their history.

THE RULE ABOUT THE TEST
-----------------------
"A green tick that asserted nothing is worse than no checker." This test must
therefore prove the check FAILS when a credential is genuinely reachable from
a pushed ref - not merely that it passes on a clean repo.

The fixture is built in a THROWAWAY git repo under a temp dir. The test must
never write into the live repo, and must never touch the live refs.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "check-public-exposure.py")
FAILS: list[str] = []
PASSES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSES.append(name)
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def run(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def make_repo(tmp: str, branch: str = "main") -> str:
    """A throwaway repo with one pushed-tracking ref, so the checker can scan it."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo, exist_ok=True)
    run(["git", "init", "-q", "-b", branch], cwd=repo)
    run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Test"], cwd=repo)
    with open(os.path.join(repo, "clean.md"), "w") as f:
        f.write("# nothing to see here\n")
    run(["git", "add", "clean.md"], cwd=repo)
    run(["git", "commit", "-qm", "clean"], cwd=repo)
    return repo


def commit_file(repo: str, path: str, content: str, message: str) -> None:
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    run(["git", "add", path], cwd=repo)
    run(["git", "commit", "-qm", message], cwd=repo)


def main() -> int:
    print("test: check-public-exposure.py")
    check("checker file exists", os.path.isfile(CHECKER), CHECKER)

    with tempfile.TemporaryDirectory(prefix="pubexp-test-") as tmp:
        # ---------------------------------------------------------
        # 1. NEGATIVE CONTROL: a credential reachable from a pushed
        #    ref MUST be reported. If this passes silently, the check
        #    is decorative.
        # ---------------------------------------------------------
        repo = make_repo(tmp, "main")
        # A syntactically valid AgentMail-shaped token. It is a FAKE (no real
        # account), and the test asserts on DETECTION, not on liveness, so the
        # value never needs to authenticate.
        #
        # It is ASSEMBLED AT RUNTIME rather than written as a literal. That
        # way no credential-shaped string exists in tracked source at all, so
        # neither the pre-commit guard nor the checker's own placeholder
        # filter has to make an exception for this file. The assembled value
        # lands in the throwaway repo's blob, which is what the checker reads.
        fake = "am_us_" + "0123456789" + "abcdefghijklmnopqrstuvwxyz0123"
        commit_file(repo, "TOOLS.md",
                    f"# creds\nBearer {fake}\n", "publish a credential")
        run(["git", "update-ref", "refs/remotes/origin/main",
             run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()], cwd=repo)

        res = run([sys.executable, CHECKER, "--refs", "origin/main", "--no-probe"],
                  cwd=repo)
        out = res.stdout + res.stderr
        check("NEGATIVE CONTROL: a credential in a pushed ref is DETECTED",
              fake[-4:] in out, f"output did not contain the token suffix. got:\n{out[:800]}")
        check("NEGATIVE CONTROL: the checker exits non-zero on a reachable credential",
              res.returncode == 1, f"exit={res.returncode} out={out[:400]}")
        check("NEGATIVE CONTROL: the result is never reported as CLEAN",
              "RESULT: CLEAN" not in out, out[:400])

        # ---------------------------------------------------------
        # 2. POSITIVE CONTROL: a repo with nothing published must
        #    come back CLEAN, exit 0.
        # ---------------------------------------------------------
        repo2 = make_repo(os.path.join(tmp, "clean"), "main")
        run(["git", "update-ref", "refs/remotes/origin/main",
             run(["git", "rev-parse", "HEAD"], cwd=repo2).stdout.strip()], cwd=repo2)
        res2 = run([sys.executable, CHECKER, "--refs", "origin/main", "--no-probe"],
                   cwd=repo2)
        out2 = res2.stdout + res2.stderr
        check("POSITIVE CONTROL: a clean pushed ref reports CLEAN",
              "RESULT: CLEAN" in out2, out2[:400])
        check("POSITIVE CONTROL: a clean pushed ref exits 0",
              res2.returncode == 0, f"exit={res2.returncode}")

        # ---------------------------------------------------------
        # 3. HISTORY IS SCANNED, NOT JUST THE TIP. A credential that
        #    was REMOVED in the newest commit is still in the history
        #    of the pushed ref - and still clonable by a stranger.
        # ---------------------------------------------------------
        repo3 = make_repo(os.path.join(tmp, "hist"), "main")
        fake2 = "am_us_" + "abcdefghijklmnopqrstuvwxyz" + "0123456789AB"
        commit_file(repo3, "TOOLS.md", f"Bearer {fake2}\n", "publish")
        commit_file(repo3, "TOOLS.md", "# redacted\n", "remove it again")
        run(["git", "update-ref", "refs/remotes/origin/main",
             run(["git", "rev-parse", "HEAD"], cwd=repo3).stdout.strip()], cwd=repo3)
        res3 = run([sys.executable, CHECKER, "--refs", "origin/main", "--no-probe"],
                   cwd=repo3)
        out3 = res3.stdout + res3.stderr
        check("HISTORY: a credential removed in the tip but present in the pushed "
              "history is still detected",
              fake2[-4:] in out3, out3[:800])

        # ---------------------------------------------------------
        # 4. THE TEST MUST NOT POLLUTE THE LIVE REPO.
        # ---------------------------------------------------------
        live = run(["git", "status", "--porcelain"], cwd="/workspace")
        check("the live repo is untouched by the test fixtures",
              "pubexp-test" not in live.stdout and "TOOLS.md" not in live.stdout,
              live.stdout[:300])

    print()
    print(f"{len(PASSES)} passed, {len(FAILS)} failed")
    for f in FAILS:
        print(f"  FAILED: {f}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
