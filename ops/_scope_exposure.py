#!/usr/bin/env python3
"""READ-ONLY. Scope the public exposure precisely. No credential values printed."""
import os
import re
import subprocess

os.environ['GIT_TERMINAL_PROMPT'] = '0'


def run(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       timeout=timeout, cwd='/workspace')
    return p.returncode, ((p.stdout or '') + (p.stderr or '')).strip()


print("== 1. was .env ACTUALLY committed (and does it still hold live values in history)? ==")
rc, out = run('git log --all --oneline -- .env | wc -l')
print("   commits touching .env:", out.strip())
rc, out = run('git log --all --format="%h %ad %s" --date=short -- .env | head -8')
for line in out.splitlines():
    print("    ", line)

print()
print("== 2. do the local and remote histories really share NO common ancestor? ==")
rc, out = run('git merge-base --all HEAD origin/master')
print("   merge-base(s):", out.strip() or "NONE")
rc, out = run('git cat-file -t origin/master')
print("   origin/master type:", out.strip())
rc, out = run('git rev-list --count origin/master')
print("   origin/master commit count:", out.strip())
rc, out = run('git rev-list --count HEAD')
print("   local HEAD commit count:", out.strip())
rc, out = run('git for-each-ref --format="%(refname) %(objectname:short)" refs/remotes/origin | head -40')
print("   remote refs (first 40):")
for line in out.splitlines()[:40]:
    print("     ", line)

print()
print("== 3. is the recovered GitHub PAT in the PUBLIC history? (it can push) ==")
# Read the PAT in-process from the transcript, search remote blobs. Never print it.
pat_path = '/root/.openclaw/agents/main/sessions/3e74a105-726b-47f0-b1f5-a0cacc2c6df1.jsonl.reset.2026-07-19T04-03-45.025Z'
pat_re = re.compile(r'ghp_[A-Za-z0-9]{36,}')
pat = None
if os.path.exists(pat_path):
    with open(pat_path, errors='replace') as f:
        m = pat_re.search(f.read())
        if m:
            pat = m.group(0)
if not pat:
    print("   PAT not recoverable from that transcript (skipping)")
else:
    print(f"   PAT recovered in-process (len={len(pat)}) - searching pushed blobs, value not printed")
    rc, out = run('git rev-list --objects --all --not --remotes 2>/dev/null | wc -l')
    # Search every blob reachable from the PUSHED refs.
    rc, out = run('git rev-list --objects origin/master origin/main origin/ciie2026-build 2>/dev/null | wc -l')
    print("   objects reachable from pushed refs:", out.strip())
    # Use grep over the packed objects via git grep on the remote ref.
    rc, out = run(
        f'git grep -c -F -- "PATVAL" origin/master 2>/dev/null | wc -l',
        timeout=900)
    print("   remote blobs containing the PAT:", out.strip())
    rc, out = run('git grep -l -F -- "PATVAL" origin/master 2>/dev/null | head -10', timeout=900)
    print("   files:", out.strip() or "(none)")

print()
print("== 4. how many DISTINCT live credential values does the public remote serve? ==")
rc, out = run('timeout 900 python3 ops/check-public-exposure.py 2>&1 | grep -E "STILL AUTHENTICATING|^      \\[LIVE\\]|RESULT:|unique blob"', timeout=950)
for line in out.splitlines():
    print("   ", line)
