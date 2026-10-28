#!/usr/bin/env python3
"""Measure candidate credential-shape rules against the tracked tree.

Goal: find rules that catch the Blotato exposures WITHOUT embedding the
secret itself in tracked source (the repo's own rule: never hardcode a
credential, not even inside the checker).
"""
import os
import re
import subprocess
import sys

CANDIDATES = {
    # brand variant: the key body behind a mutated brand prefix
    "brand_variant": re.compile(r"(?<![A-Za-z0-9])(?:blt|blotato)[_-][A-Za-z0-9]{12,}={0,2}"),
    # placeholder whose body was pasted over the prefix
    "mangled_ref": re.compile(
        r"\$\{(?![A-Z_]*\})([A-Z_]*(?:(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)[A-Z_]*|(?:[A-Z0-9]+_)*PAT(?:_[A-Z0-9]+)*))\}"
        r"[A-Za-z0-9+/]{16,}={0,2}"
    ),
    # opaque base64 body w/ mixed case + digit, no brand anchor
    "opaque_body": re.compile(
        r"(?<![A-Za-z0-9+/=])(?=[A-Za-z0-9+/]{32,}={0,2}(?![A-Za-z0-9+/=]))"
        r"(?=[A-Za-z0-9+/]*[A-Z])(?=[A-Za-z0-9+/]*[a-z])(?=[A-Za-z0-9+/]*[0-9])"
        r"[A-Za-z0-9+/]{32,}={0,2}"
    ),
}

SKIP = re.compile(r"^(\.git/|\.matrix-|node_modules/|Decepticon/|OpenJarvis/|gstack/|"
                   r"headroom/|OBLITERATUS/|Agent-Reach/|OpenClawHomeAssistant/|core/|"
                   r"odysseus/|\.archive/)")


def mask(s):
    """Show the SHAPE of a candidate, never the secret.

    This script's output goes to stdout, which the gateway captures into
    its session log. Printing a matched credential in full would leak it
    into that log - which is exactly how the live AgentMail keys ended up
    in /tmp/openclaw/openclaw-*.log in the first place. So a candidate is
    reported by its length and its character classes, and only a short
    prefix is shown (enough to identify which credential it is, not enough
    to use it).

    The repo's own rule: never print a credential, not even inside the
    tool that hunts for them.
    """
    if len(s) <= 8:
        return "<=8 chars>"
    classes = []
    if any(c.isupper() for c in s):
        classes.append("A")
    if any(c.islower() for c in s):
        classes.append("a")
    if any(c.isdigit() for c in s):
        classes.append("9")
    if any(c in "_-=+/." for c in s):
        classes.append("s")
    return f"len={len(s)} shape={''.join(classes)} prefix={s[:4]}..."


def tracked():
    out = subprocess.check_output(["git", "ls-files", "-z"]).decode()
    return [f for f in out.split("\0") if f]


def main():
    files = tracked()
    hits = {k: [] for k in CANDIDATES}
    scanned = 0
    for rel in files:
        if SKIP.match(rel):
            continue
        try:
            if os.path.getsize(rel) > 5_000_000:
                continue
            t = open(rel, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if not t.strip():
            continue
        scanned += 1
        for name, pat in CANDIDATES.items():
            for m in pat.finditer(t):
                ln = t.count("\n", 0, m.start()) + 1
                hits[name].append((rel, ln, m.group(0)[:70]))
    print(f"scanned {scanned} tracked files")
    print("(candidates are reported by SHAPE only - a matched credential is")
    print(" never printed, because stdout is captured into the gateway log)")
    print()
    for name, _ in CANDIDATES.items():
        h = hits[name]
        print(f"== {name}: {len(h)} hit(s)")
        for rel, ln, s in h[:60]:
            print(f"   {rel}:{ln}  {mask(s)}")
        print()


if __name__ == "__main__":
    main()
