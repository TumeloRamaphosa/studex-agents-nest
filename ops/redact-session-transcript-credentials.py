#!/usr/bin/env python3
"""Redact live credential literals from OpenClaw session transcripts.

WHY THIS EXISTS (2026-10-27)
----------------------------
The FEEDHIVE_API_KEY leak looked like a log problem and was not:

  * The key was in ~250 places across /root/.openclaw/agents/main/sessions/*.jsonl
    (plus their .reset/.bak siblings).
  * The gateway copies session content into the gateway log on every read, so
    a credential in a transcript re-enters the log WHENEVER that session is
    read. Masking the log was undone twice in one session for exactly this
    reason.
  * The transcript therefore has to be masked, not just the copy.

WHAT IT DOES
------------
Replaces every occurrence of every EXPOSED credential value from `.env` with
an equal-length mask, IN PLACE, preserving each file's byte length and
inode. Equal length matters: the transcripts are JSONL and the gateway
tracks file positions; changing a file's length would shift every offset
after the edit. An equal-length mask changes the bytes but not the geometry.

LIVENESS REUSES THE EXISTING CLASSIFIER
----------------------------------------
`ops/redact-live-secrets-in-place.py` already encodes the house rule: a key
the provider rejects (401/403) is DEAD and is NOT an exposure, so masking it
is pointless churn. This tool imports that classifier rather than inventing a
second one - two classifiers would drift, and the more aggressive one would
win by accident. A credential whose liveness cannot be probed is UNKNOWN and
IS masked: an unproven key is treated as a key.

The values are read from `.env` in-process. They are never placed in argv,
never printed, and never written anywhere. The report names the credential
and the count - never the value.

EXIT CODES
----------
  0 = done (whether or not anything was found)
  2 = could not read .env
"""

import importlib.util
import os
import re
import sys

# The canonical credential-name filter lives in ONE place so these tools
# cannot drift apart. See ops/cred_name_filter.py for why a copy-pasted
# regex in nine files was a real security bug.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_cred_name_filter", "/workspace/ops/cred_name_filter.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ROOT = "/workspace"
ENV_PATH = os.path.join(ROOT, ".env")
SESSIONS_DIR = "/root/.openclaw/agents"

_NAME_RE = _mod.CRED_NAME_RE

_spec = importlib.util.spec_from_file_location(
    "redact_live_secrets", os.path.join(ROOT, "ops", "redact-live-secrets-in-place.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def load_env(path=ENV_PATH):
    env = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError as e:
        return {}, str(e)
    return env, None


def transcript_files(root=SESSIONS_DIR):
    out = []
    if not os.path.isdir(root):
        return out
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if ".jsonl" not in fn:
                continue
            p = os.path.join(dirpath, fn)
            try:
                if os.path.isfile(p) and os.path.getsize(p) < 200 * 1024 * 1024:
                    out.append(p)
            except OSError:
                continue
    return out


def main():
    dry = "--dry-run" in sys.argv
    env, err = load_env()
    if err:
        print("could not read %s (%s)" % (ENV_PATH, err))
        return 2

    # Classify each credential with the EXISTING classifier. DEAD keys are
    # left in place; LIVE and UNKNOWN are masked.
    states = {}
    for name, value in sorted(env.items()):
        # Use the SAME selection rule as the scanner
        # (`ops/check-scanner-log-exposure.py::env_values`): a credential-named
        # variable of at least 16 characters. A first version of this tool used
        # a 20-character floor and MISSED ORGO_PASSWORD (16 chars) - which the
        # scanner then correctly reported as exposed. Two tools must agree on
        # what counts as a credential, or the redactor will quietly leave
        # behind exactly what the scanner is complaining about.
        if len(value) < 16 or not _NAME_RE.match(name):
            continue
        state, detail = _mod.classify(value, env, name)
        states[value] = (name, state, detail)

    maskable = [(v, s) for v, s in states.items() if s[1] != "DEAD"]
    if not maskable:
        print("no exposed credential values to mask")
        return 0

    files = transcript_files()
    touched = 0
    total = 0
    per_cred = {}

    for path in files:
        try:
            data = open(path, "rb").read()
        except OSError:
            continue
        if not data:
            continue
        buf = bytearray(data)
        changed = False
        for value, (name, state, _detail) in maskable:
            needle = value.encode()
            n = buf.count(needle)
            if not n:
                continue
            buf = bytearray(buf.replace(needle, b"X" * len(needle)))
            changed = True
            total += n
            per_cred[name] = per_cred.get(name, 0) + n
        if not changed:
            continue
        touched += 1
        if dry:
            continue
        out = bytes(buf)
        assert len(out) == len(data), "length must be preserved"
        with open(path, "r+b") as fh:
            fh.seek(0)
            fh.write(out)
        st = os.stat(path)
        print("redacted %s (size %d, inode %d preserved)"
              % (os.path.basename(path), st.st_size, st.st_ino))

    print("")
    print("transcripts scanned : %d" % len(files))
    print("transcripts changed : %d%s" % (touched, " (DRY-RUN)" if dry else ""))
    print("occurrences masked  : %d" % total)
    for name, n in sorted(per_cred.items(), key=lambda x: -x[1]):
        print("   %-28s %d" % (name, n))
    print("(values never printed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
