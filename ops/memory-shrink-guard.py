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

THE SAME FAILURE, ONE FILE OVER (2026-10-28)
--------------------------------------------
The 2026-10-23 incident was not the last one. On 2026-10-28 the "Research
Hour" cron job (5d4d7ab7) wrote its own note to `memory/2026-10-28.md` -
the file that holds THAT DAY's accumulated notes - with a whole-file
overwrite. It replaced 789 lines / 21 sections with 28 lines / 5 sections.
The next scheduled writer ("Build Hour", 23:00 SAST) runs `git add . && git
commit && git push`, so the loss was about to be published to a PUBLIC
remote.

Nothing was wrong with the agent's intent - it wrote a legitimate note to a
path that is ALSO the day's log. Two writers, one path, no append semantics.

WHY THE OBVIOUS CHECK IS NOT USED HERE
---------------------------------------
The natural rule - "the last line must end in terminal punctuation" - was
measured against 408 prose .md files in this repo and produced **58 false
positives** (memory/2026-07-20.md ends "- HEARTBEAT_OK"; campaign-brief.md
ends ", LinkedIn copy, ad creatives on request"). A rule that fires on correct
files teaches people to ignore it, which is worse than having no rule. So the
check is scoped to memory files and keyed on STRUCTURE, not punctuation.

THE RULE
--------
Compare each memory file against its committed version. Every `##`-level
section present in the committed file must still be present, unless it is
listed in `ops/memory-shrink-allowlist.txt`.

Structure, not prose: rewording, reordering, adding and removing BULLET LINES
inside a section are all fine. Only the disappearance of a whole section is a
failure. That is exactly the failure that happened.

WHICH FILES ARE COVERED
-----------------------
    MEMORY.md              - the curated long-term memory
    memory/*.md            - the daily notes (one file per day)

The daily notes are covered because they are the SAME failure class: they
accumulate through the day, several writers append to them, and one writer
that saves a whole file instead of appending destroys every other writer's
contribution. A guard that only watched MEMORY.md would have watched the
smaller half of the problem.

WHY AN ALLOWLIST
----------------
A deliberate trim should be possible - but it must be DELIBERATE. The
allowlist is where you write "yes, I meant to drop this one". An intentional
trim becomes a one-line edit; an accidental one stays blocked.

Allowlist formats (one entry per line, `#` comments allowed):
    Open lead - Zatsepilov                 applies to MEMORY.md
    memory/2026-10-28.md :: Some Heading   applies to that file only

Usage:
    python3 ops/memory-shrink-guard.py            # check the worktree files
    python3 ops/memory-shrink-guard.py --staged   # check the staged files
Exit 0 = ok, 1 = a committed section vanished without an allowlist entry.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = "MEMORY.md"
MEMORY_DIR = "memory"
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


def git_show(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.stdout if r.returncode == 0 else None


def read_worktree(path):
    p = REPO / path
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else None


def read_staged(path):
    r = subprocess.run(["git", "show", ":%s" % path],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.stdout if r.returncode == 0 else None


def load_allowlist():
    """Return {path_or_None: {section, ...}}.

    A bare section title applies to MEMORY.md only. A
    "<path> :: <section>" entry applies to that one file.
    """
    out = {}
    if not ALLOWLIST.exists():
        return out
    for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "::" in line:
            path, _, sec = line.partition("::")
            path = path.strip()
            sec = re.sub(r"\s+", " ", sec).strip().lower()
            out.setdefault(path, set()).add(sec)
        else:
            sec = re.sub(r"\s+", " ", line).strip().lower()
            out.setdefault(TARGET, set()).add(sec)
    return out


def daily_memory_paths():
    """Committed daily-notes files, newest last. Only files git knows about."""
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "--",
                        MEMORY_DIR + "/"],
                       capture_output=True, text=True, cwd=str(REPO))
    if r.returncode != 0:
        return []
    return sorted(p for p in r.stdout.split("\n")
                  if p.strip().endswith(".md") and p.strip())


def staged_paths():
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRD"],
        capture_output=True, text=True, cwd=str(REPO))
    if r.returncode != 0:
        return []
    return [p for p in r.stdout.split("\n") if p.strip()]


def check_file(path, head_text, new_text, allow, problems):
    """Compare one file's sections against its committed version."""
    old_secs = section_headings(head_text)
    new_secs = section_headings(new_text)
    allowed = allow.get(path, set()) | (allow.get(TARGET, set())
                                        if path == TARGET else set())
    lost = sorted(s for s in (old_secs - new_secs) if s not in allowed)
    if lost:
        problems.append((path, len(old_secs), lost))
    return len(old_secs), len(lost)


def main():
    staged = "--staged" in sys.argv
    allow = load_allowlist()

    # Which files to compare. In staged mode we only care about files that are
    # actually in the index - otherwise every unrelated daily note would be
    # re-checked on every commit.
    if staged:
        candidates = [p for p in staged_paths()
                      if p == TARGET
                      or (p.startswith(MEMORY_DIR + "/") and p.endswith(".md"))]
        candidates = sorted(set(candidates))
    else:
        candidates = sorted(set([TARGET] + daily_memory_paths()))

    problems = []
    checked = 0
    total_sections = 0
    for path in candidates:
        head_text = git_show("HEAD", path)
        if head_text is None:
            # Not committed yet - a NEW file has nothing to lose.
            continue
        new_text = read_staged(path) if staged else read_worktree(path)
        if new_text is None:
            # The file is gone from the worktree entirely. Everything it held
            # is gone with it, so every section counts as lost.
            lost = sorted(section_headings(head_text))
            if lost:
                problems.append((path, len(lost), lost))
            checked += 1
            continue
        n, nlost = check_file(path, head_text, new_text, allow, problems)
        checked += 1
        total_sections += n

    if not problems:
        print("memory shrink guard   OK   %d file(s) checked, %d section(s) in HEAD, all present"
              % (checked, total_sections))
        return 0

    print("🚫 MEMORY FILE(S) LOST COMMITTED SECTION(S)")
    print()
    for path, nsections, lost in problems:
        print("  %s  (%d section(s) in HEAD, %d lost)" % (path, nsections, len(lost)))
        for s in lost:
            print("    - " + s)
        print()
    print("These sections existed in the committed file and are gone.")
    print("A memory file that silently drops its open P0s is a SHORTER memory,")
    print("not a tidier one - a future session cannot act on an item it can no")
    print("longer see. Daily notes are APPEND-ONLY: add a section, do not")
    print("rewrite the file. If you are saving a standalone note, write it to")
    print("its OWN file (e.g. memory/YYYY-MM-DD-topic.md), not to the day's log.")
    print()
    print("If the drop is INTENTIONAL, record it in")
    print("  %s" % ALLOWLIST.relative_to(REPO))
    print("as either '<section title>' (MEMORY.md) or")
    print("'<path> :: <section title>' (one specific file).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
