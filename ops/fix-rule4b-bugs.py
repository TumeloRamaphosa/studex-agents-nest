#!/usr/bin/env python3
"""Fix the two bugs in drift-check rule 4b.

BUG 1: the rule flagged the quoted HISTORICAL figure "21 emails to 9 buyers"
(the wrong number we are correcting). A correction note legitimately quotes the
old number in order to withdraw it, so a number inside quotes, or immediately
preceded by "said"/"claimed"/"wrote", is a historical reference - not a claim
about how many emails were sent.

BUG 2: the per-row check took the FIRST numeric cell in the row, which is the
row NUMBER ("| 2 | email | company | 3 | dates |"), not the email count. It
must take the cell AFTER the email's cell.

Also: a row's date list can contain a number ("24 Sep, 2 Oct") - only the cell
immediately following the email cell is the count.

Idempotent. Run: python3 ops/fix-rule4b-bugs.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "ops", "drift-check.py")

src = open(DP, encoding="utf8").read()
orig = src

old = '''            # every "<n> emails" / "<n> emails to <m> recipients" claim in the note
            for m in re.finditer(r"\\b(\\d+)\\s+emails?\\b", raw, re.I):
                n = int(m.group(1))
                if n in (1, 2, 3):
                    continue  # per-recipient counts are checked below
                if auth_total and n != auth_total:
                    issues.append(
                        f"{rel} - says '{n} emails' but the authoritative recipient list says "
                        f"{auth_total}; the note a human approves must match the file")
            for m in re.finditer(r"\\b(\\d+)\\s+external recipients\\b|\\b(\\d+)\\s+recipients\\b", raw, re.I):
                n = int(m.group(1) or m.group(2))
                if auth_recs and n != auth_recs:
                    issues.append(
                        f"{rel} - says '{n} recipients' but the authoritative recipient list says "
                        f"{auth_recs}")
            # per-recipient email counts in the note's table must match the JSON
            for rr in d0.get("recipients", []):
                em = rr.get("email")
                for line in raw.splitlines():
                    if em and em in line and "|" in line:
                        cells = [c.strip() for c in line.split("|")]
                        nums = [c for c in cells if c.isdigit()]
                        if nums and int(nums[0]) != rr.get("emails"):
                            issues.append(
                                f"{rel} - row for {em} says {nums[0]} email(s) but the authoritative "
                                f"list says {rr.get('emails')}")'''

new = '''            # A number that is QUOTED as the old/wrong figure is a historical
            # reference we are withdrawing - not a claim about what was sent.
            historical = re.compile(
                r"(said|claims?|claimed|wrote|previously|previously said|old\\s+|wrong\\s+"
                r"figure|\\"[^\\"]*\\"|\\'[^\\']*\\')", re.I)

            def is_historical(text, pos):
                window = text[max(0, pos - 120):pos + 40]
                return bool(historical.search(window))

            # every "<n> emails" claim in the note must match the authoritative total
            for m in re.finditer(r"\\b(\\d+)\\s+emails?\\b", raw, re.I):
                n = int(m.group(1))
                if n in (1, 2, 3):
                    continue  # per-recipient counts are checked below
                if auth_total and n != auth_total:
                    if is_historical(raw, m.start()):
                        continue
                    issues.append(
                        f"{rel} - says '{n} emails' but the authoritative recipient list says "
                        f"{auth_total}; the note a human approves must match the file")
            for m in re.finditer(r"\\b(\\d+)\\s+external recipients\\b|\\b(\\d+)\\s+recipients\\b", raw, re.I):
                n = int(m.group(1) or m.group(2))
                if auth_recs and n != auth_recs:
                    if is_historical(raw, m.start()):
                        continue
                    issues.append(
                        f"{rel} - says '{n} recipients' but the authoritative recipient list says "
                        f"{auth_recs}")
            # per-recipient email counts in the note's table must match the JSON.
            # The count is the cell IMMEDIATELY AFTER the email cell - the first
            # numeric cell is the row number, and the date cells also contain numbers.
            for rr in d0.get("recipients", []):
                em = rr.get("email")
                for line in raw.splitlines():
                    if not (em and em in line and "|" in line):
                        continue
                    cells = [c.strip() for c in line.split("|")]
                    idx = next((i for i, c in enumerate(cells) if em in c), None)
                    if idx is None or idx + 1 >= len(cells):
                        continue
                    cnt = cells[idx + 1]
                    if cnt.isdigit() and int(cnt) != rr.get("emails"):
                        issues.append(
                            f"{rel} - row for {em} says {cnt} email(s) but the authoritative "
                            f"list says {rr.get('emails')}")'''

assert old in src, "rule 4b body not found"
src = src.replace(old, new, 1)
assert src != orig
open(DP, "w", encoding="utf8").write(src)
print("fixed rule 4b: historical figures excluded, count cell located by column")
