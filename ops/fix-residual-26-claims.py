#!/usr/bin/env python3
"""Fix the remaining stale '26 emails' live claims in MEMORY.md and memory/2026-10-22.md.

My pass-6 entry (2026-10-22 23:58 UTC) asserted 26 emails. The verified figure
is 29. The recipients JSON's 'priorClaim' note is a deliberate record of the
prior wrong figure and is left alone.

Idempotent. Run: python3 ops/fix-residual-26-claims.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (file, old, new) - exact strings
EDITS = [
    # ---- memory/2026-10-22.md : my own pass-6 entry
    ("memory/2026-10-22.md",
     "- `outbound-corrections/ciie-correction-recipients.json` — the authoritative **12 recipients / 26 emails**",
     "- `outbound-corrections/ciie-correction-recipients.json` — the authoritative **12 recipients / 29 emails** "
     "(corrected 23 Oct 00:30 UTC — see below)"),
    ("memory/2026-10-22.md",
     "### ⚠️ CORRECTION 1 — it was **26 emails to 12 buyers**, not 21 to 9",
     "### ⚠️ CORRECTION 1 — it was **29 emails to 12 buyers**, not 21 to 9 "
     "*(the 29 figure was itself corrected on 23 Oct 00:30 UTC — see `memory/2026-10-23.md`)*"),
    ("memory/2026-10-22.md",
     "both CIIE crons (`36bc4f61`, `766d1f8a`) are **disabled**. The 26 emails ran 25 Sep – 3 Oct and stopped.",
     "both CIIE crons (`36bc4f61`, `766d1f8a`) are **disabled**. The 29 emails ran 24 Sep – 3 Oct and stopped."),
    # ---- MEMORY.md
    ("MEMORY.md",
     "**26 emails to 9 real coffee/import buyers were sent on 25 Sep / 29 Sep / 3 Oct with copy that was false and unregistered**",
     "**29 emails to 12 real coffee/import buyers were sent on 24 Sep / 25 Sep / 29 Sep / 2 Oct / 3 Oct with copy that was false and unregistered**"),
    ("MEMORY.md",
     "`ciie-nurture/send-sequence.js` — not `dist/cli.js` — sent the 26 emails. It had **its own hardcoded copy** of the email text and **no kill switch**",
     "`ciie-nurture/send-sequence.js` sent 23 of the 29 emails, and `dist/cli.js` sent the other **6** to 3 named leads "
     "in `data/state.json` (a second, forgotten engine). Both had **their own hardcoded copy** of the email text and **no kill switch**"),
]

changed = []
for rel, old, new in EDITS:
    p = ROOT / rel
    if not p.exists():
        print(f"  (missing) {rel}")
        continue
    t = p.read_text(encoding="utf8")
    if old in t:
        p.write_text(t.replace(old, new, 1), encoding="utf8")
        changed.append(f"{rel}: {old[:52]}...")
    else:
        print(f"  (not found in {rel}) {old[:70]}")

# ---- residual scan with a stricter historical test
print("\n=== residual scan ===")
HIST = re.compile(r"'(?:21|26) emails to \d+ (?:buyers|recipients)'", re.I)
live = 0
for f in ["MEMORY.md", "memory/2026-10-22.md", "memory/2026-10-23.md",
          "outbound-corrections/ciie-correction-note.md", "outbound-corrections/README.md"]:
    p = ROOT / f
    if not p.exists():
        continue
    for i, l in enumerate(p.read_text(encoding="utf8").splitlines(), 1):
        if re.search(r"\b26 emails\b", l):
            if HIST.search(l) or "priorClaim" in l or "counted each" in l:
                print(f"  [historical-ok] {f}:{i}: {l.strip()[:120]}")
            else:
                print(f"  [*** STALE LIVE CLAIM ***] {f}:{i}: {l.strip()[:160]}")
                live += 1

print(f"\nchanged {len(changed)} edit(s); {live} stale live claim(s) remain")
for c in changed:
    print("  -", c)
