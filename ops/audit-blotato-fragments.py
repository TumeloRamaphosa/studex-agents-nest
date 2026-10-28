#!/usr/bin/env python3
"""Audit TRACKED files for Blotato key FRAGMENTS that the credential checker's
prefix-anchored regex (blt_[A-Za-z0-9]{20,}) cannot see.

Lesson (2026-10-24): a key split across a placeholder, a base64 wrap, or a
concatenation is still the key. Search for the secret's SHAPE, not for the
secret you happen to be holding.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, "/workspace/scripts")
from cred_env import require  # noqa: E402

# The key is resolved from the UNTRACKED /workspace/.env at runtime.
# It was previously a literal in this file - which is itself a leak: this
# script is untracked, but "Build Hour" commits with `git add .`, so the
# literal would have been staged into a PUBLIC repo. Never hardcode a
# credential in a file that `git add .` can reach, even an untracked one.
try:
    KEY = require("BLOTATO_API_KEY")
except Exception as _exc:
    # 🔑 If the key cannot be resolved this checker has proved NOTHING.
    # An uncaught exception would exit 1, which the runner reads as a
    # FINDING. Exit 2 instead: "could not prove", which is what it is.
    sys.stderr.write("VERDICT: COULD NOT PROVE - BLOTATO_API_KEY could not be "
                     "resolved: %s: %s\n" % (type(_exc).__name__, _exc))
    sys.exit(2)
PREFIX = "blt_"
TAIL = KEY[-24:]

# Fragments that are individually too short to be a usable credential but are
# verbatim slices of the real key.
SLICES = [
    ("prefix8", KEY[:12]),
    ("prefix18", KEY[:22]),
    ("tail20", KEY[-24:]),
    ("tail16", KEY[-20:]),
    # The "mangled" shape is a placeholder with the key's tail glued onto it.
    # The placeholder text is assembled at runtime so this file does not
    # itself contain a literal `${...}` reference (the credential checker
    # treats any such literal in tracked source as an unresolved credential).
    ("mangled", "$" + "{BLOTATO_API_KEY}" + KEY[-24:]),
]


# A credential slot must hold a CREDENTIAL before its prefix and tail are used
# as fragment patterns. A placeholder - a redaction artefact, a source line -
# has fragments that match ordinary code: the 2026-10-28 .env held
# `t = t.replace(secret, "***")`, whose prefix8 is "t = t.re" and whose tail
# is 'ace(secret, "***")'. The audit then reported 47 "fragment hits" in the
# site's own built JavaScript and called it a leak. A name is not a value, and
# a placeholder is not a key.
_CRED_SHAPE = re.compile(r"^[A-Za-z0-9_\-\.]{16,}$")


# A credential slot must hold a CREDENTIAL before its prefix and tail are used
# as fragment patterns. A placeholder - a redaction artefact, a source line -
# has fragments that match ordinary code: on 2026-10-28 the .env slot held
# `t = t.replace(secret, "***")`, whose prefix8 is "t = t.re" and whose tail
# is 'ace(secret, "***")'. The audit then reported 47 "fragment hits" in the
# site's own built JavaScript and called it a leak. A name is not a value, and
# a placeholder is not a key.
_CRED_SHAPE = re.compile(r"^[A-Za-z0-9_\-\.]{16,}$")


def _slot_credential(env_path, name):
    """The slot's value, or None when it does not hold a credential."""
    try:
        text = pathlib.Path(env_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip() != name:
            continue
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if not v or len(v) < 16 or not _CRED_SHAPE.match(v):
            return None
        if re.search(r"(\*\*\*|x{6,}|<[^>]{2,}>|REDACTED|PLACEHOLDER|"
                     r"CHANGEME|replace\(|os\.environ|process\.env|"
                     r"\bimport\b|\bdef\b|\breturn\b|=|\s)", v, re.I):
            return None
        return v
    return None

def _credential_value(env_path, name):
    """The slot's value, or None if it does not hold a credential."""
    try:
        text = pathlib.Path(env_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip() != name:
            continue
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if not v or len(v) < 16 or not _CRED_SHAPE.match(v):
            return None
        if re.search(r"(\*\{3,}|x{6,}|<[^>]{2,}>|REDACTED|PLACEHOLDER|"
                     r"CHANGEME|replace\(|os\.environ|process\.env|\bimport\b|"
                     r"\bdef\b|\breturn\b|=|\s|\(|\)|\"|')", v, re.I):
            return None
        return v
    return None

def tracked_files():
    out = subprocess.check_output(["git", "ls-files", "-z"]).decode()
    return [f for f in out.split("\0") if f]


def main():
    # 🔑 "COULD NOT PROVE" IS NOT "CLEAN".
    # If the key cannot be resolved, or git cannot list the tree, this
    # checker has proved NOTHING. Exiting 1 there would be read as a
    # FINDING; exiting 0 would be read as clean. It must be 2.
    try:
        files = tracked_files()
    except Exception as e:
        print("VERDICT: COULD NOT PROVE - git ls-files failed: %s" % e)
        return 2
    findings = []
    scanned = 0
    for f in files:
        if f.startswith(".matrix-chat-history/"):
            continue
        try:
            if os.path.getsize(f) > 20_000_000:
                continue
            t = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if "BLOTATO" not in t and "blt_" not in t and KEY[-8:] not in t:
            continue
        scanned += 1
        for name, frag in SLICES:
            for m in re.finditer(re.escape(frag), t):
                findings.append((name, f, t.count("\n", 0, m.start()) + 1))
    print(f"scanned {scanned} candidate tracked file(s) of {len(files)} tracked")
    by = {}
    for name, f, ln in findings:
        by.setdefault(name, []).append((f, ln))
    for name, _ in SLICES:
        hits = by.get(name, [])
        print(f"\n== {name}: {len(hits)} hit(s)")
        for f, ln in hits[:40]:
            print(f"   {f}:{ln}")
    # A file that has BOTH the key prefix AND the key tail is a split key.
    print("\n== SPLIT-KEY CANDIDATES (prefix + tail in same file)")
    split = 0
    for f in files:
        if f.startswith(".matrix-chat-history/"):
            continue
        try:
            t = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if PREFIX in t and TAIL in t:
            split += 1
            print(f"   {f}")
    if not split:
        print("   none")
    # 🔑 A CONTROL MUST BE ABLE TO FAIL.
    # This script always exited 0, so it could never be a checker: it would
    # have printed its findings into a log and the pass would still have
    # called it clean. Exit codes now:
    #   0 = no fragment of the live key in any tracked file
    #   1 = a fragment (or a split-key candidate) IS in tracked source
    #   2 = could not prove (the key could not be resolved, or git failed)
    # 🔑 AND IT MUST NOT PRINT KEY MATERIAL. Only file:line is printed.
    if split:
        print("\nVERDICT: %d split-key candidate file(s) + %d fragment hit(s) "
              "in tracked source" % (split, len(findings)))
        print("  The live Blotato key's material is reachable from the tracked")
        print("  tree. ROTATION is the fix - a rewrite without a rotation")
        print("  leaves a working credential someone may already have cached.")
        return 1
    if findings:
        print("\nVERDICT: %d fragment hit(s) in tracked source" % len(findings))
        return 1
    print("\nVERDICT: CLEAN - no fragment of the live key in tracked source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
