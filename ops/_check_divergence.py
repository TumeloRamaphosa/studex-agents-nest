#!/usr/bin/env python3
"""Read-only: is .env gitignored, and what are the 106 remote-only commits?"""
import subprocess


def run(cmd, timeout=180):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       timeout=timeout, cwd='/workspace')
    return p.returncode, ((p.stdout or '') + (p.stderr or '')).strip()


print("== is /workspace/.env ignored by git? ==")
rc, out = run('git check-ignore -v .env')
print("   rc:", rc, "|", out or "NOT IGNORED")
rc, out = run('git ls-files --error-unmatch .env 2>&1')
print("   tracked by git:", "YES - DANGER" if rc == 0 else "no")
rc, out = run('git log --oneline -3 -- .env')
print("   history mentions of .env:", out.replace("\n", " | ") or "none")

print()
print("== the 106 commits on origin/master that are NOT in local HEAD ==")
rc, out = run('git log --oneline --no-decorate HEAD..origin/master')
lines = out.splitlines()
print("   count:", len(lines))
for line in lines[:12]:
    print("    ", line)
if len(lines) > 12:
    print(f"     ... and {len(lines) - 12} more")

print()
print("== who authored them (are they another machine's work?) ==")
rc, out = run('git log --format=%an HEAD..origin/master | sort | uniq -c | sort -rn')
for line in out.splitlines()[:8]:
    print("    ", line)

print()
print("== do the two tips differ in TREE (i.e. is content actually different)? ==")
rc, out = run('git diff --stat HEAD origin/master | tail -3')
print("   ", out.replace("\n", " | "))
rc, out = run('git merge-base HEAD origin/master')
mb = out.strip()
print("   merge-base:", mb[:12] if mb else "NONE (unrelated histories)")
rc, out = run(f'git log --oneline -1 {mb}')
print("   merge-base commit:", out)

print()
print("== disk space (a rewrite needs room) ==")
rc, out = run('df -h /tmp /workspace | tail -3')
print("   ", out.replace("\n", " | "))
rc, out = run('du -sh /workspace/.git 2>/dev/null')
print("   .git size:", out.strip())
