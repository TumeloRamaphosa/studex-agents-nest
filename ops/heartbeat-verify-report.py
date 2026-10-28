#!/usr/bin/env python3
"""Consolidated heartbeat verification report.

Reads the artefacts already produced this cycle (test log, cron dump, git
state) and reports them in one place. Prints no credential VALUES - only
whether a value is present or absent.
"""
import json
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


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=WS).stdout


def real_secret_values():
    """Actual credential values from .env - used only for presence checks."""
    out = []
    env = WS / ".env"
    if not env.exists():
        return out
    name_re = _mod.CRED_NAME_RE
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= 16 and name_re.match(k.strip()):
            out.append(v)
    return out


print("=== TEST SUITE (this cycle) ===")
log = pathlib.Path("/tmp/hb7.log")
if log.exists():
    txt = log.read_text(errors="ignore")
    passes = len(re.findall(r"^PASS", txt, re.M))
    fails = re.findall(r"^FAIL\s+(\S+)", txt, re.M)
    print(f"  PASS count : {passes}")
    print(f"  FAIL count : {len(fails)}")
    for f in fails:
        print(f"    FAIL {f}")
    print(f"  last line  : {txt.strip().splitlines()[-1] if txt.strip() else 'n/a'}")
else:
    print("  (no log)")

print()
print("=== CRON FLEET ===")
cron = pathlib.Path("/tmp/cron2.txt")
if cron.exists():
    txt = cron.read_text(errors="ignore")
    ok = len(re.findall(r"\bok\b", txt))
    print(f"  jobs reporting ok : {ok}")
    print(f"  error jobs        : {len(re.findall(r'error', txt, re.I))}")
else:
    print("  (no dump)")

print()
print("=== GIT ===")
print("  " + sh("git log --oneline -1").strip())
ahead = sh("git rev-list --count origin/master..HEAD 2>/dev/null").strip()
print(f"  commits ahead of origin/master : {ahead or 'unknown'}")
print("  working tree:")
for line in sh("git status --short").splitlines():
    print(f"    {line}")

print()
print("=== UNTRACKED FILE HYGIENE (credential presence only) ===")
secrets = real_secret_values()
untracked = [l for l in sh("git status --short").splitlines() if l.startswith("??")]
for line in untracked:
    path = line[3:].strip()
    p = WS / path
    if p.is_dir():
        continue
    try:
        t = p.read_text(errors="ignore")
    except OSError:
        continue
    hits = sum(1 for s in secrets if s in t)
    verdict = "CONTAINS A REAL CREDENTIAL" if hits else "no real credential present"
    print(f"  {path}: {verdict}")

print()
print("=== ORPHAN CHECK (untracked ops scripts referenced by nothing) ===")
for line in untracked:
    path = line[3:].strip()
    if not path.endswith(".py"):
        continue
    name = pathlib.Path(path).name
    refs = sh(f"grep -rl '{name}' --include='*.py' --include='*.sh' --include='*.md' . "
              f"2>/dev/null | grep -v '^./memory' | grep -v '{path}'")
    refs = [r for r in refs.splitlines() if r.strip()]
    print(f"  {path}: {'referenced by ' + ', '.join(refs) if refs else 'ORPHAN (referenced by nothing)'}")
