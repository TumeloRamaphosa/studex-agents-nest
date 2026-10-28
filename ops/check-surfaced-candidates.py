#!/usr/bin/env python3
"""Check the three credential-shaped candidates the shape scan surfaced.

Targets (from ops/measure-cred-shapes.py):
  .netrc:3                                       - opaque 70-char value
  studex-blotato-coffee-launch/BLOTATO-SETUP.md  - 'blotato' prefixed, 52 chars
  research/2026-08-10.md  /  research/2026-09-09.md - 'blt_'/'blotato' prefixed

For each, report only:
  - is the file TRACKED (would be published)?
  - does its value EQUAL a credential currently in .env? (is it live)
  - is its value a PREFIX of one? (a truncated reference, not a secret)

No credential value is ever printed. This is a single bounded pass over
three known files - not a scan.
"""
import pathlib
import re
import subprocess

# The canonical credential-name filter lives in ONE place so these tools
# cannot drift apart. See ops/cred_name_filter.py for why a copy-pasted
# regex in nine files was a real security bug.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_cred_name_filter", "/workspace/ops/cred_name_filter.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

WS = pathlib.Path("/workspace")
TARGETS = [
    (".netrc", 3),
    ("studex-blotato-coffee-launch/BLOTATO-SETUP.md", 32),
    ("research/2026-08-10.md", 62),
    ("research/2026-09-09.md", 60),
]
CAND_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:blt|blotato)[_-][A-Za-z0-9]{12,}={0,2}"
    r"|(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{60,}={0,2}"
)


def env_values():
    out = {}
    name_re = _mod.CRED_NAME_RE
    env = WS / ".env"
    if not env.exists():
        return out
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= 16 and name_re.match(k.strip()):
            out[k.strip()] = v
    return out


def tracked(path):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", path],
                       cwd=WS, capture_output=True, text=True)
    return r.returncode == 0


def main():
    env = env_values()
    for rel, line_no in TARGETS:
        p = WS / rel
        if not p.exists():
            print(f"{rel}:{line_no}  (file absent)")
            continue
        lines = p.read_text(errors="ignore").splitlines()
        if line_no > len(lines):
            print(f"{rel}:{line_no}  (line absent)")
            continue
        line = lines[line_no - 1]
        m = CAND_RE.search(line)
        val = m.group(0) if m else None
        is_tracked = tracked(rel)
        verdict = "no credential-shaped value on that line"
        if val:
            exact = [k for k, v in env.items() if v == val]
            prefix = [k for k, v in env.items()
                      if v != val and v.startswith(val) and len(val) >= 12]
            if exact:
                verdict = f"EQUALS a live .env credential ({', '.join(exact)})"
            elif prefix:
                verdict = (f"a PREFIX of a live .env credential "
                           f"({', '.join(prefix)}) - a truncated reference, not a secret")
            else:
                verdict = "does not match any .env credential"
        print(f"{rel}:{line_no}")
        print(f"   tracked by git : {is_tracked}"
              f"{'  <- WOULD BE PUBLISHED' if is_tracked else ''}")
        print(f"   value          : {verdict}")


if __name__ == "__main__":
    main()
