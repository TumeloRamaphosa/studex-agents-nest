#!/usr/bin/env python3
"""Correct the CIIE breach count everywhere it is recorded.

THE SINGLE SOURCE OF TRUTH (verified 2026-10-23 00:30 UTC against AgentMail with the
ciie-nurture key, and independently recounted by scripts/ciii-breach-recount.py):

    29 emails to 12 recipients, of which 26 carried a CIIE claim.
    3 of those 26 went out with an uninterpolated ${lead.company} literal in the subject.

THE TWO PRIOR FIGURES WERE BOTH WRONG:
    "21 emails to 9 buyers"  — counted ciie-nurture/prospects.json only; it MISSED 3 recipients
                                (li.wei@luckincoffee.cn, c.jie@timhortonschina.com,
                                sarah@eurotrading.co.za) who live only in ciie-nurture/data/state.json.
    "26 emails to 12 recipients" — right recipient count, but each state.json lead was counted as
                                1 email when each actually received 2 (a 24 Sep "Welcome" catalogue
                                email plus a 2 Oct custom quote).

WHY THE 9-vs-12 ERROR MATTERED: the correction note was scoped to "the 9 CIIE buyers". Taking
that at face value would have left 3 real buyers with an uncorrected false promise in their inbox.
Every one of the 12 needs the note.

This script rewrites the stale phrasing in place across the vault, MEMORY.md and the daily notes.
It is idempotent: running it twice changes nothing the second time.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (relative path, old substring, new substring)
REPLACEMENTS = [
    (
        "studex-obsidian-vault/daily/2026-10-22.md",
        "Correction note to the 9 CIIE buyers",
        "Correction note to ALL 12 CIIE buyers",
    ),
    (
        "studex-obsidian-vault/daily/2026-10-22-MORNING.md",
        "Correction note to the 9 CIIE buyers",
        "Correction note to ALL 12 CIIE buyers",
    ),
    (
        "memory/2026-10-22-standup-1700.md",
        "Correction note to the 9 CIIE buyers",
        "Correction note to ALL 12 CIIE buyers",
    ),
    (
        "memory/2026-10-22-evening-wrap.md",
        "Correction note to the 9 CIIE buyers",
        "Correction note to ALL 12 CIIE buyers",
    ),
    (
        "memory/2026-10-21-evening-wrap.md",
        "sent **21 emails to 9 real buyers** promising a CIIE meeting",
        "sent **29 emails to 12 real buyers** promising a CIIE meeting",
    ),
]

# The exact standalone phrases that carry the old counts.
PHRASES = [
    (
        "**Correction note to the 9 CIIE buyers** — 21 emails already promised a meeting we can't evidence.",
        "**Correction note to ALL 12 CIIE buyers** — 29 emails (26 carrying a CIIE claim) already promised a meeting we can't evidence. **All 12 need it** — the old '9 buyers' scope would have left 3 uncorrected.",
    ),
    (
        "**Correction note to the 9 CIIE buyers** — 21 emails promised a meeting we can't evidence. Send before CIIE.",
        "**Correction note to ALL 12 CIIE buyers** — 29 emails (26 with a CIIE claim) promised a meeting we can't evidence. Send before CIIE.",
    ),
    (
        "**Correction note to the 9 CIIE buyers** — 21 emails already promised a meeting we cannot evidence. **Recommendation: send before CIIE, not after.**",
        "**Correction note to ALL 12 CIIE buyers** — 29 emails (26 carrying a CIIE claim) already promised a meeting we cannot evidence. **All 12 need it.** **Recommendation: send before CIIE, not after.**",
    ),
    (
        "pipeline ledger for the 21 CIIE buyers",
        "pipeline ledger for the 12 CIIE buyers",
    ),
    (
        "pipeline ledger for 21 CIIE buyers",
        "pipeline ledger for 12 CIIE buyers",
    ),
    (
        "Attach to all 21 CIIE buyer meetings",
        "Attach to all 12 CIIE buyer meetings",
    ),
    (
        "correction note to the 9 CIIE buyers who got the false \"let's meet at CIIE\" opener (**26 emails sent**)",
        "correction note to ALL 12 CIIE buyers who got the false \"let's meet at CIIE\" opener (**29 emails sent, 26 with a CIIE claim**)",
    ),
    (
        "correction note to the 9 CIIE buyers who got the false \"let's meet at CIIE\" opener (21 emails sent)",
        "correction note to ALL 12 CIIE buyers who got the false \"let's meet at CIIE\" opener (29 emails sent, 26 with a CIIE claim)",
    ),
    (
        "**Send the correction note to the 9 CIIE buyers**",
        "**Send the correction note to ALL 12 CIIE buyers**",
    ),
    (
        "**Correction note to ALL 12 CIIE buyers** \u2014 21 emails already promised a meeting we cannot evidence. **Recommendation: send before CIIE, not after.**",
        "**Correction note to ALL 12 CIIE buyers** \u2014 29 emails (26 carrying a CIIE claim) already promised a meeting we cannot evidence. **All 12 need it.** **Recommendation: send before CIIE, not after.**",
    ),
    (
        "**Correction note to ALL 12 CIIE buyers** \u2014 21 emails already promised a meeting we can't evidence. Send before CIIE.",
        "**Correction note to ALL 12 CIIE buyers** \u2014 29 emails (26 carrying a CIIE claim) already promised a meeting we can't evidence. Send before CIIE.",
    ),
    (
        "**Correction note to ALL 12 CIIE buyers** \u2014 21 emails promised a meeting we can't evidence. Send before CIIE.",
        "**Correction note to ALL 12 CIIE buyers** \u2014 29 emails (26 with a CIIE claim) promised a meeting we can't evidence. Send before CIIE.",
    ),
]


def main():
    changed = 0
    files = 0
    for rel, old, new in REPLACEMENTS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        s = open(path, encoding="utf-8").read()
        if old in s:
            s = s.replace(old, new)
            open(path, "w", encoding="utf-8").write(s)
            changed += 1
            print(f"  {rel}: {old[:52]!r} -> replaced")

    # Now the free-standing phrases, across a wider set of files.
    targets = []
    for base in ("studex-obsidian-vault", "memory", "research"):
        d = os.path.join(ROOT, base)
        for dirpath, _dirs, files_ in os.walk(d):
            for f in files_:
                if f.endswith(".md"):
                    targets.append(os.path.join(dirpath, f))
    md = os.path.join(ROOT, "MEMORY.md")
    if os.path.exists(md):
        targets.append(md)

    for path in targets:
        try:
            s = open(path, encoding="utf-8").read()
        except Exception:
            continue
        orig = s
        for old, new in PHRASES:
            s = s.replace(old, new)
        if s != orig:
            open(path, "w", encoding="utf-8").write(s)
            changed += 1
            files += 1
            print(f"  {os.path.relpath(path, ROOT)}: phrase corrections applied")

    print(f"\n{changed} file(s) updated across {files} phrase-bearing file(s)")

    # Verify no stale figure survives in the operational files.
    print("\n=== residual scan ===")
    stale = 0
    for path in targets:
        try:
            s = open(path, encoding="utf-8").read()
        except Exception:
            continue
        for pat in (r"9 CIIE buyers", r"21 emails", r"21 CIIE"):
            for m in re.finditer(pat, s):
                line = s[: m.start()].count("\n") + 1
                ctx = s[max(0, m.start() - 70) : m.start() + 70].replace("\n", " ")
                # README files in outbound-corrections intentionally quote the old figures.
                if "outbound-corrections" in path:
                    continue
                stale += 1
                print(f"  STALE {os.path.relpath(path, ROOT)}:{line}  ...{ctx}...")
    if not stale:
        print("  clean — no stale '9 buyers' / '21 emails' figures remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
