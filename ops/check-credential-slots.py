#!/usr/bin/env python3
"""A credential slot must hold a CREDENTIAL.

On 2026-10-28 05:30 a redaction run wrote the literal text
`t = t.replace(secret, "***")` into the BLOTATO_API_KEY slots of .env and of
two tracked scripts. Every scanner then believed a credential was present,
because the NAME was present - the value was a line of code.

The API answered HTTP 401. The publish path kept working for a while only
because the gateway process had loaded the real key before the corruption.

Nothing checked the obvious: is this value actually a credential? A slot
holding a redaction artefact, a placeholder, an empty string, or a fragment
of source code is not a credential, and a guard that accepts one is not
guarding anything.

This check:
  * reads the credential slots of every .env it is pointed at,
  * classifies each value as CREDENTIAL / PLACEHOLDER / NOT-A-CREDENTIAL,
  * FAILS on any slot that is not a credential,
  * and (with --tracked) FAILS if a slot's value appears in tracked source.

It never prints a credential value: only the name, the length, and the
classification.
"""
import argparse
import pathlib
import re
import sys

# Names that should hold a secret. A slot whose name matches is inspected.
SECRET_NAME = re.compile(
    r"(API_KEY|_KEY$|_TOKEN|_SECRET|_PASSWORD|^KEY$|^TOKEN$|CREDENTIAL)", re.I)

# A plausible credential: long, and made of the characters real keys use.
CREDENTIAL_SHAPE = re.compile(r"^[A-Za-z0-9_\-\.\+/=~]{16,}$")

# Unambiguous redaction ARTEFACTS: the value IS a mask, not a credential.
#
# These are tested BEFORE the length check, and that order is the point.
# A mask is a mask whatever its length, and TOO-SHORT is a class the
# resolver ALLOWS - so a 12-asterisk masked credential used to be
# classified TOO-SHORT and handed to a caller as if it were a live key.
# The credential masker writes exactly that shape, so the tool that
# removes a leak was manufacturing one.
#
# Only the bare-artefact forms live here. The WORD markers (example,
# dummy, TODO...) stay in PLACEHOLDER, after the length test, because a
# short real credential containing one of those words must not be newly
# refused - a false positive in the direction that blocks working keys.
MASK = re.compile(r"(\*{3,}|x{6,}|<[^>]{2,}>)")

# Things that are definitely not credentials, however they are spelled.
PLACEHOLDER = re.compile(
    r"(REDACTED|PLACEHOLDER|CHANGEME|YOUR_|"
    r"example|EXAMPLE|dummy|DUMMY|not[_-]?set|TODO|\.\.\.|replace\(|"
    r"os\.environ|process\.env|\bimport\b|\bdef\b|\breturn\b)",
    # A bare "=" is NOT a placeholder marker: it is how a base64 credential
    # is PADDED. Marking it as a placeholder refused every padded key - a
    # false positive in the direction that blocks working credentials.
    # A source line is caught anyway: it contains spaces, quotes or
    # brackets, so it fails CREDENTIAL_SHAPE below.
    re.I)


def classify(value):
    """CREDENTIAL / PLACEHOLDER / NOT-A-CREDENTIAL. Never returns the value."""
    if value is None:
        return "EMPTY"
    v = value.strip()
    if not v:
        return "EMPTY"
    if MASK.search(v):
        return "PLACEHOLDER"
    if len(v) < 16:
        return "TOO-SHORT"
    if PLACEHOLDER.search(v):
        return "PLACEHOLDER"
    if not CREDENTIAL_SHAPE.match(v):
        return "NOT-A-CREDENTIAL"
    return "CREDENTIAL"


def read_env(path):
    """Return [(name, value)] for the slots of an env-style file."""
    out = []
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        out.append((k, v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("envfiles", nargs="*",
                    default=["/workspace/.env", "/root/.openclaw/.env"])
    ap.add_argument("--tracked", default=None,
                    help="a git repo whose tracked files must not contain a "
                         "credential value")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    problems = []
    warnings = []
    rows = []
    for envfile in a.envfiles:
        if not pathlib.Path(envfile).exists():
            continue
        for name, value in read_env(envfile):
            if not SECRET_NAME.search(name):
                continue
            kind = classify(value)
            rows.append((envfile, name, len(value), kind))
            if kind == "TOO-SHORT":
                # A length floor is a GUESS, not a rule. An 11-character SSH
                # password is a perfectly real credential - calling it BROKEN
                # trains people to ignore the checker, and the thing this
                # checker exists to catch is a PLACEHOLDER, not a short
                # password. It is reported, and it is not a failure.
                warnings.append((envfile, name, kind, len(value)))
            elif kind != "CREDENTIAL":
                problems.append((envfile, name, kind, len(value)))

    # A credential value must not appear in tracked source.
    tracked_hits = []
    if a.tracked:
        repo = pathlib.Path(a.tracked)
        import subprocess
        files = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                               capture_output=True, text=True).stdout.split("\0")
        for envfile, name, length, kind in rows:
            if kind != "CREDENTIAL":
                continue
            value = None
            for k, v in read_env(envfile):
                if k == name:
                    value = v
                    break
            if not value or len(value) < 16:
                continue
            needle = value.encode()
            for rel in files:
                if not rel:
                    continue
                p = repo / rel
                try:
                    if p.is_file() and p.stat().st_size < 20_000_000:
                        if needle in p.read_bytes():
                            tracked_hits.append((name, rel))
                except OSError:
                    pass

    if a.json:
        import json
        print(json.dumps({
            "slots": [{"env": e, "name": n, "length": l, "kind": k}
                      for e, n, l, k in rows],
            "problems": [{"env": e, "name": n, "kind": k, "length": l}
                         for e, n, k, l in problems],
            "tracked_hits": [{"name": n, "file": f} for n, f in tracked_hits],
        }, indent=2))
    else:
        print("  %-28s %-32s %-6s %s" % ("ENV", "SLOT", "LEN", "KIND"))
        for e, n, l, k in rows:
            print("  %-28s %-32s %-6d %s" % (e[-28:], n[:32], l, k))
        if warnings:
            print()
            print("  short-but-real credentials (reported, not failures):")
            for e, n, k, l in warnings:
                print("    %-30s %s (%d characters)" % (n, k, l))
        if tracked_hits:
            print()
            print("  credential VALUES in tracked source:")
            for n, f in tracked_hits:
                print("    %-30s %s" % (n, f))

    if problems or tracked_hits:
        print()
        print("VERDICT: BROKEN - %d credential slot(s) do not hold a credential, "
              "%d value(s) in tracked source" % (len(problems), len(tracked_hits)))
        for e, n, k, l in problems:
            print("  %s: %s holds a %s (length %d)" % (e, n, k, l))
        return 1
    print()
    print("VERDICT: CLEAN - every credential slot holds a credential "
          "(%d slot(s) checked, %d short-but-real)" % (len(rows), len(warnings)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
