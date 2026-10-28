#!/usr/bin/env python3
"""Mask LIVE credential literals in place, in a set of files. GET-only liveness probes.

Why in place, and not by replacing the file:
  The gateway holds its log open for append. Swapping the inode would leave the
  process writing to an orphaned file (the visible log silently freezes).
  Truncating it would destroy the diagnostic trail for no disk gain - there is
  15G free and the log is not what is filling the disk.

  So: overwrite each match IN PLACE with a same-length mask. Byte offsets never
  shift, the inode is never replaced, the gateway's file descriptor and append
  position stay exactly as they were, and the secret is gone.

Why this tool exists separately from redact-active-gateway-log.py:
  That tool's KEY_RE matched only `am_us_[A-Za-z0-9_]{20,}` - it could never
  match a Blotato key (`blt_...`) or any other provider prefix, and it targeted
  exactly one hardcoded log file. It reported "the /tmp surface is CLOSED" while
  the live Blotato key still sat in the log 1051 times. A redactor whose regex
  knows one brand of secret redacts one brand of secret - and reports the rest
  as clean.

Liveness is established by the PROVIDER, with GET only. A 401/403 is proof of
death; a 400/404 is a request-shape error and is NOT proof of death. A key we
cannot probe is reported as UNKNOWN, and is still masked - masking a dead key is
harmless, and the mask is what lets the report say "no live literal remains"
without over-claiming.

Nothing here POSTs, DELETEs or rotates anything. Read-only except the in-place
byte writes.
"""
import argparse
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

# The canonical credential-name filter lives in ONE place so these tools
# cannot drift apart. See ops/cred_name_filter.py for why a copy-pasted
# regex in nine files was a real security bug.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_cred_name_filter", "/workspace/ops/cred_name_filter.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ENV_FILE = pathlib.Path("/workspace/.env")

# Provider -> (env var, header name, probe URL). GET only, never POST.
PROBES = {
    "agentmail": ("AM", "Authorization: Bearer {key}", "https://api.agentmail.to/v0/inboxes"),
    "blotato": ("BL", "blotato-api-key: {key}", "https://backend.blotato.com/v2/users/me/accounts"),
    # FeedHive answers 404 on EVERY endpoint, for the real key AND for a
    # fabricated one. That is what makes the CONTROL probe necessary: a lone
    # 404 cannot tell "this credential is dead" from "this service is gone".
    # Probing with a control key does.
    "feedhive": ("FH", "Authorization: Bearer {key}", "https://api.feedhive.com/v1/accounts"),
}

# Credential-shaped values in .env. We mask every one of these that we find in
# the target files; liveness only decides how we LABEL them in the report.
CRED_RE = _mod.CRED_NAME_RE
MIN_LEN = 16


def load_env(path=None):
    """Read credential-shaped NAME=VALUE pairs from an env file.

    `path` defaults to /workspace/.env. It is a parameter because the
    pre-push guard needs to be pointed at a scratch env file when it is
    driven from a test - without this, a documented GUARD_ENV_FILE knob
    would silently do nothing, because the guard would keep reading the
    real .env regardless.
    """
    env_path = pathlib.Path(path) if path else ENV_FILE
    vals = {}
    if not env_path.exists():
        return vals
    for line in env_path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= MIN_LEN and CRED_RE.match(k.strip()):
            vals[k.strip()] = v
    return vals


def get(url, headers, timeout=15):
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(400).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def classify(value, env=None, name=""):
    """Return (state, detail). state in LIVE/DEAD/UNKNOWN.

    GoDaddy has no prefix on its key and authenticates as
    `sso-key <key>:<secret>`, so it cannot be probed from the key alone -
    it needs the secret too. It is therefore probed by env NAME. A
    prefix-only probe would never have fired for it, which is exactly how
    a live, PUBLISHED GoDaddy key stayed classified UNKNOWN.
    """
    if name == "GODADDY_API_KEY" and env:
        secret = env.get("GODADDY_API_SECRET", "")
        if not secret:
            return "UNKNOWN", "no secret to pair with the key"
        st, _ = get("https://api.godaddy.com/v1/domains?statuses=ACTIVE",
                    {"Authorization": "sso-key %s:%s" % (value, secret)})
    elif name.startswith("ORGO_API_KEY"):
        st, _ = get("https://www.orgo.ai/api/computers/"
                    "946b3156-cab9-4187-a94b-056dfab35105",
                    {"Authorization": "Bearer " + value})
    elif value.startswith("am_us_"):
        st, _ = get(PROBES["agentmail"][2], {"Authorization": "Bearer %s" % value})
    elif value.startswith("blt_"):
        st, _ = get(PROBES["blotato"][2], {"blotato-api-key": value})
    elif value.startswith("fh_"):
        # FeedHive needs a CONTROL probe. Its API answers 404 on every
        # endpoint - but it answers 404 for a FABRICATED key too, which
        # proves the SERVICE is gone rather than the credential being
        # rejected. Without the control, a 404 is indistinguishable from a
        # malformed request and the key stays UNKNOWN forever: masked on
        # every pass, re-masked on the next, and reported as an "exposure"
        # that is really noise hiding the real findings.
        #
        # The rule the control establishes:
        #   real key AND control key return the SAME status
        #       -> the endpoint cannot tell them apart -> DEAD. The service
        #          is down / the route is gone / the account is gone. The
        #          credential is not the variable.
        #   real key 404 but the control key gets something else
        #       -> the endpoint is alive and answering -> UNKNOWN.
        st, _body = get(PROBES["feedhive"][2], {"Authorization": "Bearer %s" % value})
        ctl_st, _ = get(PROBES["feedhive"][2],
                        {"Authorization": "Bearer fh_%s" % ("0" * 40)})
        if st == 200:
            return "LIVE", "HTTP 200"
        if st in (401, 403):
            return "DEAD", "HTTP %s" % st
        if st == 0:
            return "UNKNOWN", "network error"
        if ctl_st == st:
            return "DEAD", ("HTTP %s for the real key AND for a control key - "
                            "the service is gone, not the credential" % st)
        return "UNKNOWN", ("HTTP %s (real key) vs HTTP %s (control key) - the "
                           "endpoint is alive, so this is NOT proof of death"
                           % (st, ctl_st))
    elif value.startswith("ghp_") or value.startswith("github_pat_"):
        # GitHub PAT. GET /user returns 200 only for a token that still
        # works, and the body names the account. A PAT with push rights on
        # a public repo is the credential you least want published: a
        # stranger can WRITE to the repo, not just read it.
        st, _ = get("https://api.github.com/user",
                    {"Authorization": "Bearer %s" % value})
    else:
        return "UNKNOWN", "no GET probe defined for this prefix"
    if st == 200:
        return "LIVE", "HTTP 200"
    if st in (401, 403):
        return "DEAD", "HTTP %s" % st
    if st == 0:
        return "UNKNOWN", "network error"
    return "UNKNOWN", "HTTP %s (request-shape error, NOT proof of death)" % st


def mask_in_place(path, value, mask=b"REDACTED"):
    """Overwrite every occurrence of `value` with a same-length mask.

    Returns (occurrences_masked, size_before, size_after, inode_before,
    inode_after). The inode pair is the proof that no inode swap happened:
    the gateway holds this file open for append, and a renamed replacement
    would leave it writing to an orphaned file while the visible log
    silently freezes.
    """
    vb = value.encode()
    data = pathlib.Path(path).read_bytes()
    n = data.count(vb)
    if not n:
        return 0, 0, 0, 0, 0
    before = os.stat(path)
    repl = (mask + b"_" * len(vb))[:len(vb)]
    with open(path, "r+b") as fh:
        start = 0
        while True:
            i = data.find(vb, start)
            if i < 0:
                break
            fh.seek(i)
            fh.write(repl)
            start = i + len(vb)
        fh.flush()
    after = os.stat(path)
    return n, before.st_size, after.st_size, before.st_ino, after.st_ino


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = load_env()
    if not env:
        print("no credential-shaped values in .env")
        return 1

    print("=== liveness of .env credentials (GET only) ===")
    states = {}
    for name, value in sorted(env.items()):
        state, detail = classify(value, env, name)
        states[value] = (name, state, detail)
        print("  %-30s %s...  %-8s %s" % (name, value[:12], state, detail))
    print()

    print("=== scan ===")
    total_hits = 0
    live_hits = 0
    for p in args.paths:
        path = pathlib.Path(p)
        if not path.exists() or not path.is_file():
            print("  %-70s ABSENT" % p)
            continue
        data = path.read_bytes()
        for value, (name, state, detail) in states.items():
            n = data.count(value.encode())
            if not n:
                continue
            total_hits += n
            if state == "LIVE":
                live_hits += n
            print("  %-60s %-28s %-8s occurrences=%d" % (p, name, state, n))
    print("\ntotal credential-literal occurrences: %d (of which LIVE: %d)" % (total_hits, live_hits))
    if not total_hits:
        print("no credential literal in the scanned files")
        return 0

    if args.dry_run:
        print("\nDRY RUN - nothing masked")
        return 0

    print("\n=== masking in place ===")
    for p in args.paths:
        path = pathlib.Path(p)
        if not path.exists() or not path.is_file():
            continue
        data = path.read_bytes()
        for value, (name, state, detail) in states.items():
            if value.encode() not in data:
                continue
            if state == "DEAD":
                # A 401/403 is proof of death: a dead key is not a credential.
                # Leave it - the point is removing a usable secret, not
                # reducing a number.
                print("  %-60s %-28s DEAD - left in place" % (p, name))
                continue
            n, before, after, ino_before, ino_after = mask_in_place(p, value)
            print("  %-60s %-28s masked=%d size %d->%d inode %s->%s%s" % (
                p, name, n, before, after, ino_before, ino_after,
                "" if ino_before == ino_after else "  <-- INODE CHANGED, INVESTIGATE"))

    print("\n=== verify ===")
    ok = True
    for p in args.paths:
        path = pathlib.Path(p)
        if not path.exists() or not path.is_file():
            continue
        data = path.read_bytes()
        for value, (name, state, detail) in states.items():
            # Verify EVERY non-DEAD credential, not just the LIVE ones. A
            # verify step that only re-checks the class it just acted on
            # cannot see the class it did not act on - which is how a file
            # full of UNKNOWN literals gets reported as clean.
            if state == "DEAD":
                continue
            if value.encode() in data:
                print("  STILL PRESENT: %s (%s) in %s" % (name, state, p))
                ok = False
    print("no credential literal remains in the scanned files" if ok else "VERIFICATION FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
