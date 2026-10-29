#!/usr/bin/env python3
"""Which refs carry live credential material - using `git grep -F -f`.

`git grep` over a ref's tree with a fixed-string pattern file is the fast
way to ask this question: it does the matching in one process, in C.

The decisive question is NOT "how many blobs are contaminated". It is
WHICH REFS reach them:

  * a blob reachable from the LOCAL master is what the next push would
    publish - that is what the pre-push guard exists to stop, and it is
    fixable here;
  * a blob reachable only from origin/* is ALREADY published. It is the
    standing escalation, and rewriting it locally does not un-publish it.
"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

REPO = "/workspace"


def git(*args, **kw):
    p = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True,
                       timeout=kw.get("timeout", 600))
    return p.stdout, p.returncode


spec = importlib.util.spec_from_file_location("ccs", REPO + "/ops/check-credential-slots.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
pairs = [(n, v) for n, v in m.read_env(REPO + "/.env")
         if m.classify(v) == "CREDENTIAL" and len(v) >= 16]
print("live credentials checked: %d" % len(pairs))

slices = set()
for _n, v in pairs:
    for i in range(len(v) - 11):
        slices.add(v[i:i + 12])
print("distinct 12-char slices: %d" % len(slices))

tmp = pathlib.Path(tempfile.mkdtemp(prefix="slices-"))
pat = tmp / "slices.txt"
pat.write_text("\n".join(sorted(slices)) + "\n", encoding="utf-8")

refs = [l.strip() for l in git("for-each-ref", "--format=%(refname)")[0].splitlines() if l.strip()]
print()
print("%-38s %8s %9s" % ("REF", "COMMITS", "SLICE-HIT"))
print("-" * 58)
results = {}
for ref in refs:
    out, rc = git("grep", "-F", "-f", str(pat), "-l", ref)
    files = [l for l in out.splitlines() if l.strip()]
    commits = git("rev-list", "--count", ref)[0].strip()
    print("%-38s %8s %9d" % (ref, commits, len(files)))
    results[ref] = files

print()
print("=== LITERALS: the full credential value, per ref ===")
for ref in refs:
    lits = []
    for _n, v in pairs:
        out, _rc = git("grep", "-F", "-l", v, ref)
        if out.strip():
            lits.append((_n, len(out.splitlines())))
    print("  %-38s %s" % (ref, lits if lits else "CLEAN - no literal"))

print()
print("=== the local branch, file by file ===")
for ref in ("refs/heads/master",):
    files = results.get(ref, [])
    print("  %s: %d file(s) hold a 12+ slice" % (ref, len(files)))
    for f in files[:30]:
        print("   ", f)
print()
print("DONE")
