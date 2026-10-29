#!/usr/bin/env python3
"""Check that the pre-push guard is INSTALLED, EXECUTABLE, and MATCHES its source.

WHY THIS EXISTS
---------------
The guard has to be installed where GIT LOOKS FOR IT, and that is not
necessarily `.git/hooks/`.

🔑 **THE LESSON (2026-10-27): this checker originally validated the WRONG
FILE and reported CLEAN the whole time.** The repo has `core.hooksPath =
.githooks` set in `.git/config`, so git runs `.githooks/pre-push` and
**NEVER LOOKS AT `.git/hooks/`**. The guard was installed to `.git/hooks/`,
reported "installed and identical to its source", and had **never run once**
in its entire life. The repo also had a pre-existing `.githooks/pre-push`
doing the same job - so the protection looked doubly present and was
effectively absent from the path git actually uses.

So this checker must resolve the hooks directory the way git does:

    git config --get core.hooksPath   ->  if set, use it (relative to the
                                          repo root) - otherwise use
                                          .git/hooks

and then verify the guard at THAT path.

WHAT IT CHECKS
--------------
  1. The effective hooks dir is resolved from git's own configuration.
  2. A `pre-push` hook exists there.
  3. It is executable (a non-executable hook never runs).
  4. It is byte-identical to `ops/git-pre-push-guard.py` - so the policy
     being enforced is the policy in the repo.
  5. `core.hooksPath` is REPORTED, so the location is never a surprise.

🔑 **A checker that validates a path nothing reads is a checker that always
passes.** It reported CLEAN while the guard was inert. That is why the
resolution now comes from git itself rather than from a hard-coded path.
"""

import os
import pathlib
import stat
import subprocess
import sys

# The repo under inspection. Defaults to /workspace, but is overridable so
# the checker can be driven against a synthetic repo - which is the only
# way to prove it can actually FAIL. A checker that can only ever be run
# against the one healthy repo it was written for is a checker with no
# negative control.
REPO = pathlib.Path(os.environ.get("GUARD_CHECK_REPO", "/workspace"))
SOURCE = REPO / "ops" / "git-pre-push-guard.py"
SOURCE_PRE_COMMIT = REPO / "ops" / "git-pre-commit-guard.py"

# Both hooks git actually runs, and the source each must match byte-for-byte.
HOOKS = (
    ("pre-push", SOURCE),
    ("pre-commit", SOURCE_PRE_COMMIT),
)


def _git(*args):
    try:
        r = subprocess.run(["git"] + list(args), cwd=str(REPO),
                           capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout or "").strip()
    except Exception:
        return 1, ""


def effective_hooks_dir():
    """Resolve the hooks directory GIT ACTUALLY USES.

    `core.hooksPath` overrides `.git/hooks` entirely. A relative value is
    resolved against the repository root. This mirrors git's own rule.
    """
    rc, val = _git("config", "--get", "core.hooksPath")
    if rc == 0 and val:
        p = pathlib.Path(val)
        if not p.is_absolute():
            p = REPO / p
        return p, val
    return REPO / ".git" / "hooks", None


def main():
    findings = []

    for _hook_name, _source in HOOKS:
        if not _source.is_file():
            print("VERDICT: BROKEN - the %s guard source is missing: %s"
                  % (_hook_name, _source))
            return 2

    hooks_dir, configured = effective_hooks_dir()

    print("core.hooksPath      : %s" % (configured if configured
                                         else "(not set -> .git/hooks)"))
    print("effective hooks dir : %s" % hooks_dir)

    for hook_name, source in HOOKS:
        installed = hooks_dir / hook_name
        if not installed.is_file():
            findings.append("no %s hook at the effective hooks path: %s"
                            % (hook_name, installed))
            continue
        mode = installed.stat().st_mode
        if not (mode & stat.S_IXUSR):
            findings.append("the hook at %s is not executable" % installed)
        try:
            src = source.read_bytes()
            inst = installed.read_bytes()
        except Exception as e:  # noqa: BLE001
            findings.append("could not compare %s: %s" % (hook_name, type(e).__name__))
            src = inst = b""
        if src and inst and src != inst:
            findings.append(
                "the INSTALLED %s hook differs from %s - "
                "the policy being enforced is not the one in the repo"
                % (hook_name, source.relative_to(REPO)))

    # A hook in .git/hooks/ while core.hooksPath points elsewhere is the
    # exact failure this checker was written to catch: it LOOKS installed
    # and never runs.
    for hook_name, _source in HOOKS:
        legacy = REPO / ".git" / "hooks" / hook_name
        if configured and legacy.is_file() and legacy != hooks_dir / hook_name:
            print()
            print("NOTE: %s also exists but git does NOT read it - "
                  "core.hooksPath is set." % legacy)

    if findings:
        print()
        print("VERDICT: NOT INSTALLED - a commit/push guard is not protecting "
              "the repo")
        for f in findings:
            print("  - %s" % f)
        print()
        print("Fix:  cp ops/git-pre-push-guard.py %s && chmod +x %s"
              % (hooks_dir / "pre-push", hooks_dir / "pre-push"))
        print("      cp ops/git-pre-commit-guard.py %s && chmod +x %s"
              % (hooks_dir / "pre-commit", hooks_dir / "pre-commit"))
        return 1

    print()
    print("VERDICT: CLEAN - the commit and push guards are installed at the "
          "path git actually uses, executable, and identical to their sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
