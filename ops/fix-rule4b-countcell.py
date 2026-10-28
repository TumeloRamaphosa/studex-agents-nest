#!/usr/bin/env python3
"""Fix rule 4b's per-recipient count lookup.

BUG: the check took the cell IMMEDIATELY AFTER the email cell, but the table
has a Company column in between:

    | 2 | `procurement.cn@timhortons.com` | Tim Hortons China | 3 | 25 Sep, 29 Sep, 3 Oct |
      ^row#   ^email                        ^company            ^count

so cells[idx+1] was the company name, not a digit, and the check silently
passed a wrong per-recipient count. That is exactly the failure mode this rule
exists to prevent - a check that cannot fail is worse than no check.

FIX: take the FIRST cell after the email cell that is purely a digit. The date
cell ("25 Sep, 29 Sep, 3 Oct") is not purely digits, so it is not picked up.

Idempotent. Run: python3 ops/fix-rule4b-countcell.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "ops", "drift-check.py")

src = open(DP, encoding="utf8").read()
orig = src

old = '''                    cells = [c.strip() for c in line.split("|")]
                    idx = next((i for i, c in enumerate(cells) if em in c), None)
                    if idx is None or idx + 1 >= len(cells):
                        continue
                    cnt = cells[idx + 1]
                    if cnt.isdigit() and int(cnt) != rr.get("emails"):
                        issues.append(
                            f"{rel} - row for {em} says {cnt} email(s) but the authoritative "
                            f"list says {rr.get('emails')}")'''

new = '''                    cells = [c.strip() for c in line.split("|")]
                    idx = next((i for i, c in enumerate(cells) if em in c), None)
                    if idx is None:
                        continue
                    # The count is the FIRST purely-numeric cell after the email
                    # cell. The table has a Company column in between, and the
                    # date cell ("25 Sep, 29 Sep, 3 Oct") is not purely numeric,
                    # so this picks the count and nothing else.
                    cnt = next((c for c in cells[idx + 1:] if c.isdigit()), None)
                    if cnt is not None and int(cnt) != rr.get("emails"):
                        issues.append(
                            f"{rel} - row for {em} says {cnt} email(s) but the authoritative "
                            f"list says {rr.get('emails')}")'''

assert old in src, "count-cell lookup not found"
src = src.replace(old, new, 1)
assert src != orig
open(DP, "w", encoding="utf8").write(src)
print("fixed rule 4b count lookup: first purely-numeric cell after the email cell")
