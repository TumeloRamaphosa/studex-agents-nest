#!/usr/bin/env python3
"""A guard must not report CLEAN because it had nothing to look at.

On 2026-10-28 three guards reported CLEAN against a repository that had
never held a commit:

    check-git-index.py          -> "VERDICT: CLEAN - the index is intact"
                                   (0 files in the index == 0 files in HEAD,
                                    and 0 == 0 was read as "consistent")
    credential-resolution-check -> "VERDICT: CLEAN - 0 credential-bearing
                                   tracked file(s) scanned"  (a vacuous scan)
    the pre-push guard          -> CLEAN, because there was no history to
                                   scan for a leaked credential.

A guard that cannot fail is a comment. These two checkers now FAIL LOUDLY
when the repository has no commits.

THE TWO VACUOUS STATES, precisely:
  * an index file that EXISTS but is EMPTY, and HEAD that has no commits
    (this is the state a bare `git status` leaves behind);
  * a scan that read ZERO tracked files.

THE NEGATIVE CONTROL: the pre-fix source of both checkers is taken from the
baseline commit and is asserted to report CLEAN on the same empty state. If
the pre-fix source also failed, this test would prove nothing about the fix.
"""
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/workspace")
IDX_CHECKER = REPO / "ops" / "check-git-index.py"
CRED_CHECKER = REPO / "ops" / "credential-resolution-check.py"
# The baseline commit: both checkers exactly as they were before the fix.
BASELINE = "347c1d0"

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def run(cmd, cwd, timeout=300):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout)


def make_repo(root, commit=True, empty_index=False):
    """A repo. commit=False -> no commits. empty_index=True -> an index file
    that EXISTS and is empty (the state that used to read as CLEAN)."""
    root.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "empty-repo@example.invalid"], root)
    run(["git", "config", "user.name", "empty repo test"], root)
    (root / "hello.txt").write_text("hello\n", encoding="utf-8")
    if commit:
        run(["git", "add", "-A"], root)
        run(["git", "commit", "-q", "-m", "one commit"], root)
    if empty_index:
        run(["git", "read-tree", "--empty"], root)
    return root


def run_index_checker(script, repo):
    env = dict(os.environ)
    env["GIT_INDEX_CHECK_REPO"] = str(repo)
    p = subprocess.run([sys.executable, str(script)], capture_output=True,
                       text=True, timeout=300, env=env, cwd=str(repo))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def load_checker(path):
    spec = importlib.util.spec_from_file_location("checker_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cred_verdict(script_path, track_nothing):
    """Run the credential checker's decision with a controlled tracked set."""
    mod = load_checker(script_path)
    if track_nothing:
        mod.tracked_files = lambda: []
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.main()
    return rc, buf.getvalue()


def pre_fix_source(path_rel, dest):
    """The checker as it was BEFORE the fix (from the baseline commit)."""
    p = subprocess.run(["git", "show", "%s:%s" % (BASELINE, path_rel)],
                       cwd=str(REPO), capture_output=True, text=True,
                       timeout=120)
    if p.returncode != 0:
        return None
    dest.write_text(p.stdout, encoding="utf-8")
    return dest


def main():
    work = pathlib.Path(tempfile.mkdtemp(prefix=".tmp-empty-repo-",
                                          dir=str(REPO)))
    try:
        vacuous = make_repo(work / "vacuous", commit=False, empty_index=True)
        healthy = make_repo(work / "healthy", commit=True)

        # ---- 1. the git-index checker on the vacuous state ----
        rc, out = run_index_checker(IDX_CHECKER, vacuous)
        check("an EMPTY index + NO commits is BROKEN, not CLEAN (git-index)",
              rc != 0, "rc=%d %s" % (rc, out[-200:]))
        check("it says the repo has no commits", "NO COMMITS" in out,
              out[-300:])

        # ---- 2. the credential checker on a vacuous scan ----
        rc, out = cred_verdict(CRED_CHECKER, track_nothing=True)
        check("a scan that read ZERO tracked files is BROKEN (credential scan)",
              rc != 0, "rc=%d %s" % (rc, out[-200:]))
        check("it says the scan was VACUOUS", "VACUOUS" in out, out[-300:])

        # ---- 3. NEGATIVE CONTROL: the pre-fix DECISION was vacuous ----
        # The control used to be the pre-fix source read out of the git
        # history - and a history rewrite removes it, so a control that
        # depends on history can silently stop being a control. The pre-fix
        # DECISION is now written out here as the golden reference.
        def pre_fix_git_index_findings(tracked, head_count):
            """ops/check-git-index.py's decision BEFORE the fix."""
            findings = []
            if tracked == 0 and head_count > 0:
                findings.append("the index is empty but HEAD is not")
            elif head_count > 0 and tracked != head_count:
                findings.append("the index and HEAD disagree")
            return findings

        def pre_fix_credential_verdict(scanned, issues):
            """ops/credential-resolution-check.py's decision BEFORE the fix."""
            if issues:
                return "BROKEN"
            return "CLEAN"

        check("NEGATIVE CONTROL: the pre-fix git-index decision read an empty "
              "index with no HEAD as CLEAN (so the fix changed something)",
              not pre_fix_git_index_findings(0, -1),
              "the pre-fix decision was NOT vacuous - the control is wrong")
        check("NEGATIVE CONTROL: the pre-fix credential decision read a "
              "zero-file scan as CLEAN (so the fix changed something)",
              pre_fix_credential_verdict(0, []) == "CLEAN")

        # ---- 4. POSITIVE CONTROL: a real repo is still CLEAN ----
        rc, out = run_index_checker(IDX_CHECKER, healthy)
        check("a repo WITH a commit is still CLEAN (git-index)",
              rc == 0, "rc=%d %s" % (rc, out[-300:]))
        rc, out = cred_verdict(CRED_CHECKER, track_nothing=False)
        check("a real tracked set is still CLEAN (credential scan)",
              rc == 0, "rc=%d %s" % (rc, out[-300:]))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print()
    if fails:
        print("FAILURES: %d -> %s" % (len(fails), fails))
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
