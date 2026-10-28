#!/usr/bin/env python3
"""One consolidated check: did the scanner leak a LIVE credential into the log,
and is the known-published Blotato literal still in tracked source?

Questions answered (all in one bounded pass, no repeated scanning):

  1. Which files does git actually track? (TOOLS.md, BLOTATO-SETUP.md, ...)
  2. Does any TRACKED file carry a value that matches a live .env credential?
  3. Does any TRACKED file carry the known-published Blotato literal?
  4. Which distinct candidate values did the scanner print into the gateway
     log, and does any of them equal a live .env credential?

No credential value is ever printed. Only file paths, counts, and verdicts.
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
LOGS = [pathlib.Path("/tmp/openclaw/openclaw-2026-10-23.log"),
        pathlib.Path("/tmp/openclaw/openclaw-2026-10-24.log")]

# The scanner's output line inside the log is JSON-escaped:
#   hit(s)\n   <rel>:<line>  '<value>'
# so the newline is a literal backslash-n in the raw bytes.
LOG_CAND = re.compile(rb"hit\(s\)\\n\s+(\S+?):(\d+)\s+'([^']{12,})'")


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


def git_tracked(path):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", path],
                       cwd=WS, capture_output=True, text=True)
    return r.returncode == 0


def main():
    env = env_values()
    live_values = set(env.values())

    print("=== 1-3. TRACKED files carrying a live credential ===")
    files = subprocess.run(["git", "ls-files"], cwd=WS,
                           capture_output=True, text=True).stdout.splitlines()
    print(f"  tracked files: {len(files)}")
    carriers = []
    for rel in files:
        p = WS / rel
        try:
            if p.stat().st_size > 5_000_000:
                continue
            t = p.read_text(errors="ignore")
        except OSError:
            continue
        for name, val in env.items():
            if val in t:
                carriers.append((rel, name))
    if carriers:
        for rel, name in carriers:
            print(f"  !! {rel} contains the live {name}")
    else:
        print("  no tracked file contains a live .env credential value")

    print()
    print("=== TOOLS.md / the Blotato key: tracked? ===")
    for rel in ("TOOLS.md",
                "studex-blotato-coffee-launch/BLOTATO-SETUP.md"):
        p = WS / rel
        if not p.exists():
            print(f"  {rel}: absent")
            continue
        t = p.read_text(errors="ignore")
        # The Blotato literal shape, whatever its exact value.
        blt = re.findall(r"blt_[A-Za-z0-9+/]{20,}={0,2}", t)
        tracked = git_tracked(rel)
        print(f"  {rel}")
        print(f"     tracked by git : {tracked}")
        print(f"     blotato-shaped literals in the file : {len(blt)}")
        if blt:
            hits = [v for v in blt if v in live_values]
            print(f"     of those, equal to a live .env credential : {len(hits)}")
            if hits:
                print(f"     !! LIVE BLOTATO KEY IN {'A TRACKED FILE' if tracked else 'an untracked file'}")

    print()
    print("=== 4. values the scanner printed into the gateway log ===")
    printed = {}
    for log in LOGS:
        if not log.exists():
            continue
        data = log.read_bytes()
        for m in LOG_CAND.finditer(data):
            val = m.group(3)
            printed[val] = printed.get(val, 0) + 1
    print(f"  distinct candidates printed : {len(printed)}")
    print(f"  total printed occurrences   : {sum(printed.values())}")
    live_hits = {v: n for v, n in printed.items() if v in live_values}
    prefix_hits = {v: n for v, n in printed.items()
                   if v not in live_values
                   and any(lv.startswith(v) and len(v) >= 12 for lv in live_values)}
    print(f"  equal to a live .env credential : {len(live_hits)}")
    print(f"  a PREFIX of a live credential    : {len(prefix_hits)}")
    print(f"  not matching any live credential : {len(printed) - len(live_hits) - len(prefix_hits)}")
    if live_hits:
        print("  !! LIVE CREDENTIAL PRINTED INTO THE GATEWAY LOG")


if __name__ == "__main__":
    main()
