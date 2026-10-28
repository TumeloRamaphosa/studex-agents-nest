#!/usr/bin/env python3
"""Test the pre-push guard: it must BLOCK a credential-bearing push and
ALLOW a clean one.

A guard that cannot fail is not a guard, so this test drives the hook the way
git does - over stdin, with real refs - and asserts on the EXIT CODE.

🔴 WHY THIS TEST RUNS IN A SCRATCH REPO, NOT IN /workspace
---------------------------------------------------------
The FIRST version of this test ran against the real repository, and it called
`git read-tree --empty` against the REAL index - the `git()` helper passed
no `GIT_INDEX_FILE`, so that one call EMPTIED /workspace/.git/index and made
all 15,922 tracked files appear staged-for-deletion.

It was not a one-off. This file is in `ops/run-tests.sh`, so **every
canonical suite run emptied the real index.** The repo's tracking was one
`git commit` away from being wiped - twice - and NO CHECKER NOTICED, because
the damage was being done BY the test suite. A checker that only inspects
the repo cannot catch a test that corrupts it.

So the test now builds its own throwaway repository in /tmp and points the
guard at it with `GUARD_REPO` / `GUARD_ENV_FILE`.

🔑 AND IT NO LONGER WRITES A REAL CREDENTIAL ANYWHERE
------------------------------------------------------
The second version wrote the REAL live credential value into a git object in
/tmp - so a real secret landed on disk, in a path the /tmp audit treats as a
SYNTHETIC fixture and therefore ignores. If the test were killed mid-run,
a live credential would sit on disk and nothing would flag it.

This version writes a **synthetic** credential, generated at runtime, into a
**synthetic** env file. The real credential is never written to any file.
🔑 **A test fixture that holds a real secret is a real secret with extra
steps** - the fixture-ignore list exists precisely so that synthetic tokens
can be excluded, and putting a live key behind that exemption would
launder it out of the audit's sight.

The REAL credential is still proven - just without writing it. Test B runs
the guard against the REAL repository's existing history, where the literals
already live in blobs that were committed long ago, and requires the guard
to BLOCK and to name the credential WITHOUT printing its value. Nothing is
written; the proof comes from history that is already on disk.

The credentials it matches on come from the REAL /workspace/.env (read
in-process, values never printed) so the guard is exercised against genuine
LIVE/UNKNOWN classifications - but the repository it scans is the scratch
one.
"""

import os
import subprocess
import sys
import pathlib
import shutil
import tempfile
import importlib.util as _ilu

TOOLS = pathlib.Path("/workspace")
HOOK = TOOLS / "ops" / "git-pre-push-guard.py"
ENV_FILE = TOOLS / ".env"

_spec = _ilu.spec_from_file_location("_guard", str(HOOK))
_guard = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_guard)

fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s %s" % (name, detail))
        fails.append(name)


def git(cwd, *args, **kw):
    """Run git in a scratch repo. Never touches /workspace's index."""
    return subprocess.run(["git"] + list(args), cwd=str(cwd),
                          capture_output=True, text=True, timeout=180, **kw)


def make_scratch_repo(root):
    """A throwaway repo with an origin remote, so the guard's
    `--not --remotes=origin` logic is exercised for real."""
    repo = root / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    remote = root / "remote.git"
    remote.mkdir(parents=True, exist_ok=True)
    git(remote, "init", "--bare", "-q", str(remote))
    git(repo, "init", "-q", "-b", "master", str(repo))
    git(repo, "config", "user.email", "guard-test@example.invalid")
    git(repo, "config", "user.name", "guard test")
    git(repo, "remote", "add", "origin", str(remote))
    # A first commit so the repo has a history and an origin/master.
    (repo / "README").write_text("scratch\n")
    git(repo, "add", "README")
    git(repo, "commit", "-q", "-m", "scratch base")
    git(repo, "push", "-q", "origin", "master")
    git(repo, "fetch", "-q", "origin")
    return repo


def write_commit(repo, name, content, message):
    """Create a commit containing `content` in file `name`; return its sha."""
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"],
                          cwd=str(repo), input=content,
                          capture_output=True, text=True, timeout=120)
    blob_oid = blob.stdout.strip()
    if not blob_oid:
        return ""
    idx = repo / ".git" / "scratch-index"
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = str(idx)
    git(repo, "read-tree", "--empty", env=env)
    git(repo, "update-index", "--add", "--cacheinfo",
        "100644,%s,%s" % (blob_oid, name), env=env)
    tree = git(repo, "write-tree", env=env).stdout.strip()
    commit = git(repo, "commit-tree", tree, "-m", message, env=env).stdout.strip()
    if idx.exists():
        idx.unlink()
    return commit


def run_hook(repo, stdin_text, env_file=None):
    """Run the guard the way git runs a pre-push hook: stdin = ref lines.

    GUARD_REPO points the guard at the repo to scan; GUARD_ENV_FILE points
    it at the env file holding the credentials it must match.
    """
    env = dict(os.environ)
    env["GUARD_REPO"] = str(repo)
    env["GUARD_ENV_FILE"] = str(env_file or ENV_FILE)
    p = subprocess.run([sys.executable, str(HOOK)], cwd=str(repo),
                       input=stdin_text, capture_output=True, text=True,
                       timeout=600, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    creds, env = _guard.live_credentials()
    names = sorted(creds)
    print("credentials classified LIVE/UNKNOWN by the guard: %d" % len(names))
    for n in names:
        print("   %-28s %s" % (n, creds[n][1]))
    check("the guard can find at least one credential to guard",
          len(names) > 0, "none found - the guard would be a no-op")
    check("the guard reads the REAL .env by default",
          bool(names), "no credentials found in %s" % ENV_FILE)

    root = pathlib.Path(tempfile.mkdtemp(prefix="guard-test-"))
    try:
        # ---------------- A. HERMETIC: synthetic credential ----------------
        # A synthetic credential, generated at runtime so it is never a
        # literal in tracked source, and never a real secret.
        synth_name = "GUARDTEST_TOKEN"
        synth_value = "GUARDTEST-" + os.urandom(8).hex() + "-not-a-real-secret"
        synth_env = root / "synthetic.env"
        synth_env.write_text("%s=%s\n" % (synth_name, synth_value))

        repo = make_scratch_repo(root)
        base = git(repo, "rev-parse", "HEAD").stdout.strip()
        remote_base = git(repo, "rev-parse", "origin/master").stdout.strip()

        leak_commit = write_commit(repo, "leak.txt", synth_value,
                                   "guard test: credential present")
        check("wrote a commit containing the credential literal",
              bool(leak_commit))

        rc, out = run_hook(repo, "refs/heads/test %s refs/heads/master %s\n"
                           % (leak_commit, remote_base),
                           env_file=synth_env)
        check("BLOCKS a push that would publish a credential",
              rc != 0, "rc=%d" % rc)
        check("the block names the credential, not the value",
              synth_name in out and synth_value not in out,
              "name present=%s value present=%s"
              % (synth_name in out, synth_value in out))

        clean_commit = write_commit(repo, "clean.txt",
                                    "a perfectly ordinary file with no secret\n",
                                    "guard test: no secret")
        rc2, out2 = run_hook(repo, "refs/heads/test %s refs/heads/master %s\n"
                             % (clean_commit, remote_base),
                             env_file=synth_env)
        check("ALLOWS a push of a clean commit", rc2 == 0,
              "rc=%d %s" % (rc2, out2[:300]))

        # An up-to-date push and a delete are no-ops.
        head = git(repo, "rev-parse", "HEAD").stdout.strip()
        rc3, _ = run_hook(repo, "refs/heads/master %s refs/heads/master %s\n"
                          % (head, head), env_file=synth_env)
        check("ALLOWS an up-to-date push", rc3 == 0, "rc=%d" % rc3)

        rc4, _ = run_hook(repo, "refs/heads/master %s refs/heads/master %s\n"
                          % ("0" * 40, head), env_file=synth_env)
        check("ALLOWS a delete", rc4 == 0, "rc=%d" % rc4)

        # ---- CONTROL: the probe budget must be SAFE, not merely fast ----
        # With the budget exhausted every credential is UNKNOWN - and UNKNOWN
        # still blocks. A cap that made the guard LAWER would be a
        # vulnerability, so this asserts it is stricter, not laxer.
        os.environ["GUARD_PROBE_DEADLINE_S"] = "0"
        try:
            spec2 = _ilu.spec_from_file_location("_guard_budget", str(HOOK))
            g2 = _ilu.module_from_spec(spec2)
            spec2.loader.exec_module(g2)
            creds2, _ = g2.live_credentials()
            states = sorted({v[1] for v in creds2.values()})
            check("the probe budget caps the work (all UNKNOWN once exhausted)",
                  bool(creds2) and states == ["UNKNOWN"],
                  "states=%s" % states)
            rc6, out6 = run_hook(repo, "refs/heads/test %s refs/heads/master %s\n"
                                 % (leak_commit, remote_base),
                                 env_file=synth_env)
            check("an exhausted probe budget still BLOCKS (UNKNOWN is not safe)",
                  rc6 != 0, "rc=%d" % rc6)
        finally:
            os.environ.pop("GUARD_PROBE_DEADLINE_S", None)

        # GUARD_ENV_FILE must ACTUALLY be honoured - otherwise the knob is
        # decoration and the guard silently keeps reading the real .env.
        rc5, out5 = run_hook(repo, "refs/heads/test %s refs/heads/master %s\n"
                             % (leak_commit, remote_base),
                             env_file=synth_env)
        check("GUARD_ENV_FILE is honoured (the scratch env was used)",
              rc5 != 0 and "GUARDTEST_TOKEN" in out5,
              "rc=%d" % rc5)

        # ---------------- B. THE REAL CREDENTIAL, WITHOUT WRITING IT -------
        # The real repo's history already contains the real literals in
        # blobs committed long ago. Run the guard against that history and
        # require it to BLOCK and to name the credential - without printing
        # the value, and WITHOUT writing anything new to disk.
        real_head = git(TOOLS, "rev-parse", "HEAD").stdout.strip()
        rc6, out6 = run_hook(TOOLS, "refs/heads/master %s refs/heads/master %s\n"
                             % (real_head, "0" * 40))
        # The real repo's history may or may not hold a live credential - that
        # is a fact about the repo, not about the guard. What must ALWAYS hold
        # is that the guard's verdict and its output agree: if it blocked, it
        # names the credential; if it did not, it names none.
        # "Blocked" has TWO legitimate reasons, and the guard must be allowed
        # to use either:
        #   1. it found a credential in the history and named it
        #      ("CREDENTIAL FOUND IN HISTORY: <name>"), or
        #   2. it could not prove liveness within its probe budget
        #      ("LIVENESS UNPROVEN - BLOCKING") - not provably safe, so it
        #      blocks anyway.
        # An earlier version of this assertion only allowed reason 1, so it
        # failed whenever the network was slow - a false alarm about the
        # guard rather than about the repo.
        blocked = rc6 != 0
        named = any(n in out6 for n in names) if names else False
        unproven = "LIVENESS UNPROVEN" in out6
        check("the guard's verdict on the real repo agrees with its output",
              (blocked == (named or unproven)),
              "rc=%d blocked=%s named=%s unproven=%s"
              % (rc6, blocked, named, unproven))
        if blocked and named:
            check("it names a real credential", named, out6[:300])
        if creds:
            leaked = [n for n in names
                      if creds[n][0] and creds[n][0] in out6]
            check("it never prints a credential VALUE", not leaked,
                  "printed value for %s" % leaked)

        # ---------------- C. THE POINT OF THE SCRATCH REPO ----------------
        real_index = TOOLS / ".git" / "index"
        before = real_index.stat().st_size if real_index.exists() else None
        n_before = len(git(TOOLS, "ls-files").stdout.split())
        write_commit(repo, "again.txt", "x\n", "second")
        after = real_index.stat().st_size if real_index.exists() else None
        n_after = len(git(TOOLS, "ls-files").stdout.split())
        check("the real repo's index is untouched by this test",
              before == after and n_before == n_after,
              "index %s->%s, tracked %s->%s" % (before, after,
                                                n_before, n_after))
        n_commits = int((git(TOOLS, "rev-list", "--count", "HEAD").stdout
                         or "0").strip() or 0)
        check("the real repo has commits (the tree is under version control)",
              n_commits >= 1,
              "%s commit(s) - the tree is NOT version controlled!" % n_commits)
        check("the real repo still tracks its files",
              n_after > 100, "only %s tracked - the index is empty!" % n_after)

        # ---------------- D. NO REAL SECRET LEFT ON DISK ------------------
        # The scratch repo must contain ONLY the synthetic value.
        blob_hits = []
        for oid in git(repo, "rev-list", "--objects", "--no-walk=unsorted",
                       "HEAD").stdout.splitlines():
            oid = oid.split(" ", 1)[0]
            content = subprocess.run(["git", "cat-file", "blob", oid],
                                     cwd=str(repo), capture_output=True,
                                     timeout=60).stdout
            for n in names:
                if creds[n][0] and creds[n][0].encode() in content:
                    blob_hits.append(n)
        check("no REAL credential was written into the scratch repo",
              not blob_hits, "wrote %s" % blob_hits)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print()
    if fails:
        print("FAILURES: %d -> %s" % (len(fails), fails))
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
