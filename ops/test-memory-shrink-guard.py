#!/usr/bin/env python3
"""
Regression test for ops/memory-shrink-guard.py.

A checker that accepts no negative control is unusable, so every rule here is
proven by injecting the violation it is supposed to catch and asserting the
guard FAILS - and by asserting it PASSES on a benign change.

The test runs entirely in a SANDBOX (a throwaway git repo under a temp dir).
It never writes to the live tree, and never touches the real MEMORY.md.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / "ops" / "memory-shrink-guard.py"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %s %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  <- " + detail) if (detail and not cond) else ""))


def run_guard(root, staged=False):
    # Run the SANDBOX COPY of the guard, not the live one. The guard resolves
    # its repo root from its own __file__, so executing the live copy would
    # silently check the live tree and every assertion would be about the
    # wrong files entirely.
    cmd = [sys.executable, str(root / "ops" / "memory-shrink-guard.py")]
    if staged:
        cmd.append("--staged")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    return r.returncode, r.stdout + r.stderr


def make_sandbox(tmp, initial):
    root = Path(tmp) / "repo"
    (root / "ops").mkdir(parents=True)
    # copy the guard + allowlist into the sandbox
    shutil.copy(GUARD, root / "ops" / "memory-shrink-guard.py")
    (root / "ops" / "memory-shrink-allowlist.txt").write_text(
        "# sections deliberately dropped\n", encoding="utf-8")
    (root / "MEMORY.md").write_text(initial, encoding="utf-8")
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, capture_output=True, cwd=str(root))
    subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(root))
    subprocess.run(["git", "commit", "-qm", "base"], capture_output=True,
                   cwd=str(root))
    return root


BASE = """# MEMORY.md

## Primary Mission
- Ship things.

## Open lead — Zatsepilov
- Unread 8 weeks.

## GitHub Sync
- PAT rejected.

## Email Warmup
- Sent 5/5.
"""


def main():
    tmp = tempfile.mkdtemp(prefix="memguard-")
    try:
        # ---------- 1. baseline: unchanged file passes ----------
        root = make_sandbox(tmp, BASE)
        rc, out = run_guard(root)
        check("unchanged MEMORY.md passes", rc == 0, out)

        # ---------- 2. NEGATIVE CONTROL: drop a section -> must FAIL ----------
        dropped = BASE.replace(
            "## Open lead — Zatsepilov\n- Unread 8 weeks.\n\n", "")
        (root / "MEMORY.md").write_text(dropped, encoding="utf-8")
        rc, out = run_guard(root)
        check("NEGATIVE: dropping a section FAILS the guard", rc == 1, out)
        check("NEGATIVE: the lost section is named in the output",
              "zatsepilov" in out.lower(), out)

        # ---------- 3. benign: reword a bullet, same sections -> passes ----------
        reworded = BASE.replace("- Ship things.", "- Ship real things, daily.")
        (root / "MEMORY.md").write_text(reworded, encoding="utf-8")
        rc, out = run_guard(root)
        check("reworded bullet inside a section still passes", rc == 0, out)

        # ---------- 4. benign: ADD a section -> passes ----------
        added = BASE + "\n## New Section\n- Added later.\n"
        (root / "MEMORY.md").write_text(added, encoding="utf-8")
        rc, out = run_guard(root)
        check("adding a section passes", rc == 0, out)

        # ---------- 5. benign: reorder sections -> passes ----------
        reordered = """# MEMORY.md

## Email Warmup
- Sent 5/5.

## GitHub Sync
- PAT rejected.

## Primary Mission
- Ship things.

## Open lead — Zatsepilov
- Unread 8 weeks.
"""
        (root / "MEMORY.md").write_text(reordered, encoding="utf-8")
        rc, out = run_guard(root)
        check("reordering sections passes", rc == 0, out)

        # ---------- 6. benign: demote ## to ### -> still present ----------
        demoted = BASE.replace("## GitHub Sync", "### GitHub Sync")
        (root / "MEMORY.md").write_text(demoted, encoding="utf-8")
        rc, out = run_guard(root)
        check("demoting ## to ### is not a loss", rc == 0, out)

        # ---------- 7. the allowlist makes a deliberate drop legal ----------
        (root / "MEMORY.md").write_text(dropped, encoding="utf-8")
        (root / "ops" / "memory-shrink-allowlist.txt").write_text(
            "Open lead — Zatsepilov\n", encoding="utf-8")
        rc, out = run_guard(root)
        check("allowlisted section drop passes", rc == 0, out)

        # ---------- 8. the allowlist does NOT blanket-allow ----------
        (root / "MEMORY.md").write_text(
            BASE.replace("## GitHub Sync\n- PAT rejected.\n\n", ""),
            encoding="utf-8")
        rc, out = run_guard(root)
        check("allowlist does not permit an UNlisted drop", rc == 1, out)

        # ---------- 9. the real 2026-10-23 case is caught ----------
        (root / "ops" / "memory-shrink-allowlist.txt").write_text(
            "# sections deliberately dropped\n", encoding="utf-8")
        (root / "MEMORY.md").write_text(BASE, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(root))
        subprocess.run(["git", "commit", "-qm", "full"], capture_output=True,
                       cwd=str(root))
        truncated = """# MEMORY.md

## Primary Mission
- Ship things.

## Email Warmup
- Sent 5/5.
- Separate Biltong sequence still
"""
        (root / "MEMORY.md").write_text(truncated, encoding="utf-8")
        rc, out = run_guard(root)
        check("the real truncation is caught", rc == 1, out)
        check("the real truncation names the lost sections",
              "zatsepilov" in out.lower() and "github" in out.lower(), out)

        # ---------- 10. DAILY NOTES are covered too (the 2026-10-28 case) ----
        # The "Research Hour" job overwrote memory/2026-10-28.md - the whole
        # day's accumulated log - with its own 28-line note. MEMORY.md was
        # untouched, so a MEMORY.md-only guard would have said OK.
        (root / "MEMORY.md").write_text(BASE, encoding="utf-8")
        (root / "memory").mkdir(exist_ok=True)
        daily = """# 2026-10-28 - daily notes

## 00:15-01:30 UTC - heartbeat
- pass done

## 09:00 SAST - Morning Nudge
- storefront healthy

## 13:00 - price audit
- ladder inverted
"""
        (root / "memory" / "2026-10-28.md").write_text(daily, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(root))
        subprocess.run(["git", "commit", "-qm", "daily"], capture_output=True,
                       cwd=str(root))

        # a NEW standalone note file must NOT trip the guard
        (root / "memory" / "2026-10-28-research-hour.md").write_text(
            "# Research brief\n\n## Lead finding\n- caviar in 2 of 3 tiers\n",
            encoding="utf-8")
        rc, out = run_guard(root)
        check("a NEW daily note file passes", rc == 0, out)

        # APPENDING to the day's log must pass
        (root / "memory" / "2026-10-28.md").write_text(
            daily + "\n## 20:00 - Research Hour\n- note appended\n",
            encoding="utf-8")
        rc, out = run_guard(root)
        check("APPENDING to the day's log passes", rc == 0, out)

        # OVERWRITING the day's log with a short note must FAIL
        (root / "memory" / "2026-10-28.md").write_text(
            "# 2026-10-28 - Research Hour\n\n## Lead finding\n- caviar\n",
            encoding="utf-8")
        rc, out = run_guard(root)
        check("NEGATIVE: overwriting the day's log FAILS the guard", rc == 1, out)
        check("NEGATIVE: the clobbered daily file is named in the output",
              "2026-10-28.md" in out, out)
        check("NEGATIVE: the lost daily sections are named",
              "heartbeat" in out.lower() and "morning nudge" in out.lower(), out)

        # DELETING the day's log must FAIL too
        (root / "memory" / "2026-10-28.md").unlink()
        rc, out = run_guard(root)
        check("NEGATIVE: deleting the day's log FAILS the guard", rc == 1, out)

        # a per-file allowlist entry makes a deliberate daily trim legal
        (root / "memory" / "2026-10-28.md").write_text(
            daily + "\n## 20:00 - Research Hour\n- note appended\n",
            encoding="utf-8")
        (root / "ops" / "memory-shrink-allowlist.txt").write_text(
            "memory/2026-10-28.md :: 13:00 - price audit\n", encoding="utf-8")
        (root / "memory" / "2026-10-28.md").write_text(
            "# 2026-10-28 - daily notes\n\n## 00:15-01:30 UTC - heartbeat\n"
            "- pass done\n\n## 09:00 SAST - Morning Nudge\n- storefront healthy\n",
            encoding="utf-8")
        rc, out = run_guard(root)
        check("per-file allowlist entry permits a deliberate daily trim",
              rc == 0, out)

        # a per-file allowlist entry must NOT blanket-allow MEMORY.md
        (root / "ops" / "memory-shrink-allowlist.txt").write_text(
            "memory/2026-10-28.md :: 13:00 - price audit\n", encoding="utf-8")
        (root / "MEMORY.md").write_text(
            BASE.replace("## GitHub Sync\n- PAT rejected.\n\n", ""),
            encoding="utf-8")
        rc, out = run_guard(root)
        check("per-file allowlist does NOT permit a MEMORY.md drop", rc == 1, out)

        # restore a clean tree for the remaining cases
        (root / "MEMORY.md").write_text(BASE, encoding="utf-8")
        (root / "ops" / "memory-shrink-allowlist.txt").write_text(
            "# sections deliberately dropped\n", encoding="utf-8")
        (root / "memory" / "2026-10-28.md").write_text(daily, encoding="utf-8")
        (root / "memory" / "2026-10-28-research-hour.md").unlink(
            missing_ok=True)
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(root))
        subprocess.run(["git", "commit", "-qm", "restore"], capture_output=True,
                       cwd=str(root))

        # ---------- 11. --staged mode reads the INDEX, not the worktree ----------
        # Setup: the INDEX holds the intact file, the WORKTREE is truncated
        # (a half-finished edit that was never staged). What would actually be
        # committed is the index version - so the staged check must PASS while
        # the worktree check must FAIL. The two must not agree.
        (root / "MEMORY.md").write_text(BASE, encoding="utf-8")
        subprocess.run(["git", "add", "MEMORY.md"], capture_output=True,
                       cwd=str(root))
        (root / "MEMORY.md").write_text(truncated, encoding="utf-8")
        rc, out = run_guard(root, staged=True)
        check("--staged passes when the INDEX is intact", rc == 0, out)
        rc, out = run_guard(root)
        check("worktree check FAILS when the worktree is truncated", rc == 1,
              out)

        # and with a truncated INDEX the staged check must fail too
        subprocess.run(["git", "add", "MEMORY.md"], capture_output=True,
                       cwd=str(root))
        rc, out = run_guard(root, staged=True)
        check("--staged fails on a truncated index", rc == 1, out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("%d passed, %d failed" % (len(PASS), len(FAIL)))
    if FAIL:
        print("FAILED: " + "; ".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
