#!/usr/bin/env python3
"""
Guard: a long-term memory file must not SILENTLY LOSE a committed section.

THE PROBLEM THIS GUARDS
-----------------------
On 2026-10-23 23:19 UTC a concurrent session rewrote /workspace/MEMORY.md.
The rewrite took the file from 23 `##`-level sections to 9 and ended
mid-sentence ("- Separate Biltong sequence still"). Measured against the
committed version, the sections it dropped included every live P0:

    CIIE badge (unpaid, deadline passed)   3 -> 0
    Blotato roster + Meta-token blocker     4 -> 0
    Zatsepilov lead (unread 8 weeks)        1 -> 0
    GitHub PAT blocker                      16 -> 1
    Saudi RFQ (P0)                          3 -> 1

Nothing was technically wrong with the file. It parsed. It was committed, and
a future session would have loaded a memory that no longer contained the
open items it was supposed to act on.

WHY THE OBVIOUS CHECK IS NOT USED HERE
--------------------------------------
The natural rule - "the last line must end in terminal punctuation" - was
measured against 408 prose .md files in this repo and produced **58 false
positives** (memory/2026-07-20.md ends "- HEARTBEAT_OK"; campaign-brief.md
ends ", LinkedIn copy, ad creatives on request"). A rule that fires on correct
files teaches people to ignore it, which is worse than having no rule. So the
check is scoped to MEMORY.md and keyed on STRUCTURE, not punctuation.

THE RULE
--------
Compare the STAGED MEMORY.md against HEAD's MEMORY.md. Every `##`-level
section present in HEAD must still be present in the staged file, unless it
is listed in `ops/memory-shrink-allowlist.txt` (one section per line, `#`
comments allowed).

Structure, not prose: rewording, reordering, adding and removing BULLET LINES
inside a section are all fine. Only the disappearance of a whole section is a
failure. That is exactly the failure that happened.

WHY AN ALLOWLIST
-----------------
A deliberate trim should be possible - but it must be DELIBERATE. The
allowlist is where you write "yes, I meant to drop this one". An intentional
trim becomes a one-line edit; an accidental one stays blocked.

Usage:
    python3 ops/memory-shrink-guard.py            # check the worktree file
    python3 ops/memory-shrink-guard.py --staged   # check the staged file
Exit 0 = ok, 1 = a committed section vanished without an allowlist entry.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = "MEMORY.md"
ALLOWLIST = REPO / "ops" / "memory-shrink-allowlist.txt"


def section_headings(text):
    """`##`-level headings, normalised for comparison.

    `##` and `###` are both treated as sections: a `##` promoted to `###` is
    still present, and a `##` demoted to `###` is still present. Only a
    section that has NO heading at all, at either level, counts as lost.
    """
    out = set()
    for line in text.splitlines():
        m = re.match(r"^#{2,3}\s+(.*\S)\s*$", line)
        if m:
            out.add(re.sub(r"\s+", " ", m.group(1)).strip().lower())
    return out


def git_show(ref_path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref_path, TARGET)],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.stdout if r.returncode == 0 else None


def read_worktree():
    p = REPO / TARGET
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else None


def read_staged():
    r = subprocess.run(["git", "show", ":%s" % TARGET], capture_output=True,
                       text=True, cwd=str(REPO))
    return r.stdout if r.returncode == 0 else None


def load_allowlist():
    if not ALLOWLIST.exists():
        return set()
    out = set()
    for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(re.sub(r"\s+", " ", line).strip().lower())
    return out


def main():
    staged = "--staged" in sys.argv
    head = git_show("HEAD")
    if head is None:
        print("no committed %s to compare against - nothing to guard yet"
              % TARGET)
        return 0
    new = read_staged() if staged else read_worktree()
    if new is None:
        print("no %s to check" % TARGET)
        return 0

    old_secs = section_headings(head)
    new_secs = section_headings(new)
    allowed = load_allowlist()
    lost = sorted(s for s in (old_secs - new_secs) if s not in allowed)

    if not lost:
        print("memory shrink guard   OK   %d section(s) in HEAD, all present"
              % len(old_secs))
        return 0

    print("🚫 MEMORY.md LOST %d committed section(s)" % len(lost))
    print()
    for s in lost:
        print("  - " + s)
    print()
    print("These sections existed in the committed %s and are gone." % TARGET)
    print("A long-term memory file that silently drops its open P0s is a")
    print("SHORTER memory, not a tidier one - a future session cannot act on")
    print("an item it can no longer see.")
    print()
    print("If the drop is INTENTIONAL, record it in")
    print("  %s" % ALLOWLIST.relative_to(REPO))
    print("(one section title per line). Otherwise restore the section.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
