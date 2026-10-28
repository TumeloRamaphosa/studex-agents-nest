#!/usr/bin/env python3
"""Verify push auth + scope the remote exposure. READ-ONLY (dry-run push only)."""
import os
import subprocess

os.environ['GIT_TERMINAL_PROMPT'] = '0'
os.environ['GCM_INTERACTIVE'] = 'never'


def run(cmd, timeout=300):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       timeout=timeout, cwd='/workspace')
    return p.returncode, ((p.stdout or '') + (p.stderr or '')).strip()


print("== 1. push auth (DRY RUN - nothing is pushed) ==")
rc, out = run('git push --dry-run origin HEAD:refs/heads/_auth_probe_20261027')
print("   rc:", rc)
for line in out.splitlines()[:10]:
    print("   ", line)

print()
print("== 2. is the local history a FAST-FORWARD over origin/master? ==")
rc, out = run('git merge-base --is-ancestor origin/master HEAD')
print("   origin/master is an ancestor of HEAD (fast-forward possible):", rc == 0)
rc, out = run('git rev-list --count origin/master..HEAD')
print("   commits ahead of origin/master:", out.strip())
rc, out = run('git rev-list --count HEAD..origin/master')
print("   commits on origin/master NOT in local HEAD:", out.strip())

print()
print("== 3. which credentials are exposed on the PUBLIC remote right now? ==")
rc, out = run('timeout 900 python3 ops/check-public-exposure.py', timeout=950)
print("   rc:", rc)
for line in out.splitlines()[-40:]:
    print("   ", line)
