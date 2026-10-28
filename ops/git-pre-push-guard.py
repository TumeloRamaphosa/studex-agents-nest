#!/usr/bin/env python3
"""pre-push hook: refuse to push a commit that carries a LIVE credential.

WHY THIS EXISTS
---------------
On 2026-10-27 a live, push-capable GitHub PAT was recovered and installed
into the git credential store. Before that, `git push` could not authenticate,
so the local history was SAFE BY ACCIDENT - it could not leave the machine.

Installing a working credential removed that accident. The public remote
`origin/master` already publishes copies of two live credentials (Blotato,
GoDaddy). The local `HEAD` carries more copies of the same values, and a
fast-forward push would publish the ADDITIONAL ones - turning a known
exposure into a larger one.

KEY A GUARD THAT ONLY EXISTS IN PROSE IS NOT A GUARD. The pre-push hook is
the last point where the exposure can still be stopped, and it runs inside
git, not inside an agent that might not be invoked.

WHAT IT DOES
------------
For every commit about to be pushed, it reads the tree BLOBS (not the
working tree) and looks for the literal value of any credential in
/workspace/.env that still classifies as LIVE.

  * LIVE credential found in a pushed blob  -> BLOCK the push (exit 1)
  * DEAD credential found                   -> allowed (it authenticates
                                               to nothing; it is noise)
  * UNKNOWN credential found               -> BLOCKED, because UNKNOWN is
                                               not safe and a false block
                                               is recoverable while a
                                               published live key is not.

KEY BLOCKING IS THE SAFE DEFAULT. The owner can always push with
`--no-verify` once a credential is rotated; a key published to a public repo
cannot be un-published.

The values are read from /workspace/.env IN-PROCESS. They are never placed
in argv, never printed, and never written to a log.

CONFIGURATION (for testability)
-------------------------------
  GUARD_REPO      the git repository to inspect   (default: /workspace)
  GUARD_ENV_FILE  the file holding credentials     (default: /workspace/.env)

Both exist so this hook can be driven against a SCRATCH repo. The first
version of its test ran against the real repo and damaged it - see
ops/test-git-pre-push-guard.py for that story.
"""

import os
import time
import subprocess
import sys
import importlib.util as _ilu
import pathlib

TOOLS = pathlib.Path("/workspace")
REPO = pathlib.Path(os.environ.get("GUARD_REPO", str(TOOLS)))
ENV_FILE = pathlib.Path(os.environ.get("GUARD_ENV_FILE", str(TOOLS / ".env")))
REDACTOR = TOOLS / "ops" / "redact-live-secrets-in-place.py"

_spec = _ilu.spec_from_file_location("_redactor", str(REDACTOR))
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def log(msg):
    sys.stderr.write("pre-push-guard: %s\n" % msg)


# Total wall-clock budget for the liveness probes, in seconds. Overridable
# so the test can prove the cap bites.
PROBE_DEADLINE_S = float(os.environ.get("GUARD_PROBE_DEADLINE_S", "8"))


def live_credentials():
    """Return {name: (value, state)} for credentials that are not provably dead.

    Names only are ever reported. The value is used for matching and is
    never printed.

    The two blocking states are kept apart on purpose:
      * LIVE    - the provider CONFIRMED it still authenticates.
      * UNKNOWN - the provider could not be probed, so liveness is unknown.

    Both block, because UNKNOWN is not safe. But they are reported
    separately, because they call for different urgency: a LIVE credential
    in a public repo is an active breach, while an UNKNOWN one is a
    credential nobody has been able to prove is dead.
    """
    # 🔑 Pass ENV_FILE through explicitly. Without the argument,
    # load_env() fell back to /workspace/.env and the documented
    # GUARD_ENV_FILE knob silently did NOTHING - a documented control that
    # was not wired up. A knob that does not work is worse than no knob,
    # because it is trusted.
    env = _mod.load_env(ENV_FILE)
    out = {}
    # 🔑 A pre-push hook must not hang. classify() asks each provider in turn
    # and a single request can take 15s, so an unbounded run over ~30
    # credentials can take MINUTES - long enough for a push to look hung, and
    # long enough to push a test past its timeout (this test failed in the
    # suite while passing on its own, purely because of load).
    # The budget is therefore capped: once the deadline passes the remaining
    # credentials are classified UNKNOWN. UNKNOWN still BLOCKS - only the
    # urgency differs - so a slow network makes the guard stricter, never
    # laxer. That is the safe direction to fail in.
    deadline = time.monotonic() + PROBE_DEADLINE_S
    for name, value in env.items():
        if time.monotonic() > deadline:
            out[name] = (value, "UNKNOWN")
            continue
        state, _detail = _mod.classify(value, env=env, name=name)
        if state in ("LIVE", "UNKNOWN"):
            out[name] = (value, state)
    return out, env


def blobs_in_push(local_sha, remote_sha):
    """Blob contents reachable from local_sha but not from remote_sha.

    These are the NEW objects the push would publish. Objects already on the
    remote are excluded: re-publishing an object that is already published
    adds no new exposure, and blocking on it would make the guard
    unusable.
    """
    # Commits that would be pushed.
    try:
        revs = subprocess.run(
            ["git", "rev-list", local_sha, "--not", "--remotes=origin"],
            cwd=str(REPO), capture_output=True, text=True, timeout=120)
    except Exception as e:  # noqa: BLE001
        log("could not enumerate commits (%s) - ALLOWING" % type(e).__name__)
        return None
    commits = [c for c in revs.stdout.split() if c]
    if not commits:
        return []
    # Blobs reachable from those commits.
    try:
        objs = subprocess.run(
            ["git", "rev-list", "--objects", "--no-walk=unsorted"] + commits,
            cwd=str(REPO), capture_output=True, text=True, timeout=180)
    except Exception as e:  # noqa: BLE001
        log("could not enumerate objects (%s) - ALLOWING" % type(e).__name__)
        return None
    blob_ids = []
    for line in objs.stdout.splitlines():
        parts = line.split(" ", 1)
        oid = parts[0]
        kind = parts[1] if len(parts) > 1 else ""
        # "git rev-list --objects" prints "<oid> <path>" for blobs and
        # "<oid>" for commits/trees. Blobs are the ones with a path.
        if kind:
            blob_ids.append(oid)
    return blob_ids


def blob_content(oid):
    try:
        cat = subprocess.run(
            ["git", "cat-file", "blob", oid],
            cwd=str(REPO), capture_output=True, timeout=60)
        if cat.returncode == 0:
            return cat.stdout
    except Exception:  # noqa: BLE001
        return b""
    return b""


def main():
    # stdin: <local ref> <local sha> <remote ref> <remote sha>
    lines = [l.strip() for l in sys.stdin.readlines() if l.strip()]
    if not lines:
        return 0
    _lr, local_sha, _rr, remote_sha = lines[0].split()[:4]

    # A delete, or an up-to-date push: nothing new to publish.
    if set(local_sha) == {"0"}:
        return 0
    if local_sha == remote_sha:
        return 0

    creds, _env = live_credentials()
    if not creds:
        return 0

    blob_ids = blobs_in_push(local_sha, remote_sha)
    if blob_ids is None:
        log("could not compute the object set - ALLOWING (not provable)")
        return 0

    hits = {}
    states = {n: s for n, (_v, s) in creds.items()}
    for oid in blob_ids:
        content = blob_content(oid)
        if not content:
            continue
        for name, (value, _state) in creds.items():
            vb = value.encode("utf-8", "replace")
            if vb and vb in content:
                hits[name] = hits.get(name, 0) + 1

    if not hits:
        return 0

    live = sorted(n for n in hits if states.get(n) == "LIVE")
    unknown = sorted(n for n in hits if states.get(n) != "LIVE")
    log("PUSH BLOCKED - this push would publish credential material to a")
    log("PUBLIC repository.")
    if live:
        log("")
        log("  CONFIRMED STILL AUTHENTICATING (active breach):")
        for name in live:
            log("    %-28s %d pushed blob(s)" % (name, hits[name]))
    if unknown:
        log("")
        log("  LIVENESS UNPROVEN (blocked anyway - not provably safe):")
        for name in unknown:
            log("    %-28s %d pushed blob(s)" % (name, hits[name]))
    log("")
    log("Rotating the credential is what actually fixes this. Rewriting")
    log("history does not un-publish a value that already worked, and a")
    log("value already published stays in every clone made since.")
    log("")
    log("To bypass deliberately: git push --no-verify")
    return 1


if __name__ == "__main__":
    sys.exit(main())
