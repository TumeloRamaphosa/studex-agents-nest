#!/usr/bin/env python3
"""Measure how many TRACKED files would trip a proposed rule.

Rule under test: a variable whose name is EXACTLY a credential word
(KEY/SECRET/SEC/TOKEN/PASSWORD/CREDENTIAL) assigned a 16+ char opaque value.

Why this rule and not the existing OPAQUE_ASSIGNED: that pattern requires
the credential word to be preceded by at least one other character
([A-Z_][A-Z_0-9]*(?:KEY|...)), so a variable literally named `KEY` or `SEC`
never matches. That is exactly how the GoDaddy key/secret slipped through
both checkers and reached the public remote.
"""
import os
import re
import subprocess
import sys

EXACT = re.compile(
    r"^\s*(?:export\s+)?(?:KEY|SECRET|SEC|TOKEN|PASSWORD|CREDENTIAL)"
    r"\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{16,})[\"']?\s*$"
)

DUMMY = re.compile(
    r"(xxx+|YOUR_|_YOUR_|REDACTED|placeholder|dummy|fake|test[-_]?key|example)",
    re.I,
)


def main() -> int:
    files = [f for f in subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0") if f]
    hits = []
    for f in files:
        if f.startswith((".matrix-", ".git/")):
            continue
        try:
            if os.path.getsize(f) > 5_000_000:
                continue
            t = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for i, line in enumerate(t.splitlines(), 1):
            m = EXACT.match(line)
            if m and not DUMMY.search(m.group(1)):
                hits.append((f, i, m.group(1)))
    print(f"{len(hits)} candidate hit(s) across {len(files)} tracked file(s)")
    for f, i, v in hits:
        print(f"  {f}:{i}  -> {v[:14]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
