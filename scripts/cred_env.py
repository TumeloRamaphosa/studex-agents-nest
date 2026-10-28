#!/usr/bin/env python3
"""Resolve credentials from the untracked /workspace/.env at RUNTIME.

WHY THIS EXISTS
---------------
On 2026-10-23 a credential scrub replaced live credential literals with the
text `${VAR_NAME}` across ~80 tracked files. That is a SHELL interpolation
idiom. In Python it is just a string:

    KEY = '${AGENTMAIL_API_KEY}'   ->  KEY == "${AGENTMAIL_API_KEY}"

Python does not expand `${}`. Worse, inside an f-string it raises
**NameError at import time** - the script dies before it does anything, and
the error names the credential, not the bug.

The failure this creates is the repo's own documented trap: a placeholder used
as a credential returns 401/403, and the caller prints "0 messages" / "0 posts"
- byte-identical to "nothing there". A false all-clear is worse than a loud
failure, because it is trusted.

THE RULE
--------
A credential reference in tracked source must resolve to a real value in the
language it is written in:

    Python    os.environ / this module (never a literal, never `${VAR}`)
    JS/TS     process.env.X, loaded from /workspace/.env
    shell     a sourced env file, or explicit substitution

Secrets live in the UNTRACKED /workspace/.env. Tracked source names the
variable; it never contains the value. The remote is PUBLIC.

Usage:
    import sys
    sys.path.insert(0, "/workspace/scripts")
    from cred_env import require
    KEY = require("AGENTMAIL_API_KEY")   # raises loudly if missing
"""
import os
import pathlib
import re
import sys

# The single untracked env file for this workspace. It is gitignored
# (.gitignore: ".env"), so its contents never reach the public remote.
# The env file to read. Overridable so a test - or a war-room
# deployment on a different host - can point at its own file.
ENV_FILE = pathlib.Path(
    os.environ.get("STUDEX_ENV_FILE") or "/workspace/.env"
)


def load_env():
    """Return the merged environment: process env first, then /workspace/.env."""
    env = dict(os.environ)
    try:
        raw = ENV_FILE.read_text(errors="replace")
    except OSError:
        return env
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        # A value that is still a `${VAR}` reference has NOT been resolved.
        # Treat it as absent so the caller fails loudly instead of sending
        # the placeholder text to a provider.
        if v.startswith("${") and v.endswith("}"):
            continue
        env.setdefault(k.strip(), v)
    return env


# A value that is NOT a credential, however it is spelled.
#
# 2026-10-28: the .env slot for BLOTATO_API_KEY held the literal text
# `t = t.replace(secret, "***")` - a redaction SOURCE LINE, written into the
# credential slot by a botched masking run. require() returned it happily,
# and the fragments audit then searched every tracked file for the "prefix8"
# of it - which is "t = t.re" - and reported 13 "fragment hits" in ordinary
# JavaScript, and called it a leak. A resolver that returns a non-credential
# launders a mistake into a fact.
#
# The test is deliberately narrow: a real credential never contains
# whitespace, a quote, a bracket or a brace. Words like "def" or "return" are
# NOT used as signals, because a hex key can legitimately contain them.
_NOT_A_CREDENTIAL = re.compile(r"""(\s|["'`()\[\]{}<>]|os\.environ|process\.env)""")

def _classify_credential(value):
    """CREDENTIAL / PLACEHOLDER / NOT-A-CREDENTIAL / EMPTY / TOO-SHORT.

    ONE definition, shared with ops/check-credential-slots.py, so the two
    cannot drift apart and disagree about the same slot.

    2026-10-28: the .env slot for BLOTATO_API_KEY held a redaction ARTEFACT
    - 48 characters of placeholder text, not a key. require() returned it
    happily, and the fragments audit then searched every tracked file for
    the "prefix8" of that text and reported 13 "fragment hits" in ordinary
    JavaScript, calling it a leak. A resolver that returns a non-credential
    launders a mistake into a fact.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_studex_credential_slots", "/workspace/ops/check-credential-slots.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.classify(value)


def get(name, default=None):
    """Return the value of `name`, or None if it is not configured."""
    v = load_env().get(name)
    if v is None or v == "":
        return default
    return v


def require(name):
    """Return the value of `name` or exit loudly.

    Failing loudly is the point. A missing credential must never become a
    placeholder that a provider 401s on, because that reads as "empty".
    """
    v = get(name)
    if v is None:
        sys.stderr.write(
            f"FATAL: {name} is not configured. Add it to {ENV_FILE} "
            f"(untracked). Refusing to run with a placeholder credential.\n"
        )
        raise SystemExit(2)
    # Only the classes that CANNOT be a credential are refused.
    # TOO-SHORT is allowed: an 11-character SSH password is a real
    # credential, and refusing it would break a working path. A truncated
    # key fails loudly at the provider, which is honest.
    kind = _classify_credential(v)
    if kind in ("EMPTY", "PLACEHOLDER", "NOT-A-CREDENTIAL"):
        sys.stderr.write(
            f"FATAL: {name} does not hold a CREDENTIAL (it is {kind}). "
            f"Refusing to hand a placeholder to a caller as if it were a "
            f"key - that is how a broken credential reads as 'empty'.\n"
        )
        raise SystemExit(2)
    return v


if __name__ == "__main__":
    # Print the NAMES that resolve, never the values.
    for k in sorted(load_env()):
        print(k)
