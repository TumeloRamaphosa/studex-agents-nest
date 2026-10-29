#!/usr/bin/env python3
"""Fix the stale figures in the CIIE correction draft + README, and add the
missing drift rule that would have caught it.

THE GAP THIS CLOSES:
The recipients JSON was corrected to 29 emails / 12 recipients by a concurrent
session, but the DRAFT BODY and the README still said 26 - and the drift
checker passed the whole time. The checker validated the JSON's internal
structure but never compared the JSON against the human-facing note. So the
authoritative number and the number a human would read (and a human might
approve, and then send) silently disagreed.

Three fixes:
  1. The draft note's table and prose -> 29 emails, and per-recipient counts
     corrected (the 3 named leads each received 2, not 1), and the send window
     widened to 24 Sep (the 24 Sep "Welcome" emails).
  2. The README -> 29, and the second engine's real shape (6 emails / 3
     recipients, not 3/3).
  3. A new drift rule: every email count that appears in a correction note must
     agree with the recipients JSON, and the note must not claim a count that
     the JSON does not support.

Idempotent. Run: python3 ops/fix-correction-figures.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, "outbound-corrections", "ciie-correction-note.md")
README = os.path.join(ROOT, "outbound-corrections", "README.md")
RJSON = os.path.join(ROOT, "outbound-corrections", "ciie-correction-recipients.json")

changed = []


def sub1(text, old, new, label):
    if old in text:
        return text.replace(old, new), True
    print(f"    (skip - not found) {label}")
    return text, False


# ------------------------------------------------------------------ 1. the note
data = json.load(open(RJSON, encoding="utf8"))
total = data["totalEmails"]
nrec = data["totalRecipients"]

t = open(NOTE, encoding="utf8").read()
orig = t

t, _ = sub1(t,
    "**Why it exists:** between **25 Sep and 3 Oct 2026** we sent **26 emails to 12 external buyers** containing",
    f"**Why it exists:** between **24 Sep and 3 Oct 2026** we sent **{total} emails to {nrec} external buyers** containing",
    "why-it-exists line")

t, _ = sub1(t,
    "## 📋 WHO — 12 external recipients, 26 emails (authoritative, verified against AgentMail)",
    f"## 📋 WHO — {nrec} external recipients, {total} emails (authoritative, verified against AgentMail)",
    "WHO heading")

# per-recipient counts: the 3 named leads each received 2, not 1
for r in data["recipients"]:
    if r["email"] in ("li.wei@luckincoffee.cn", "c.jie@timhortonschina.com", "sarah@eurotrading.co.za"):
        label = {"li.wei@luckincoffee.cn": "Luckin Coffee (named lead)",
                 "c.jie@timhortonschina.com": "Tim Hortons China (named lead)",
                 "sarah@eurotrading.co.za": "Euro Trading SA"}[r["email"]]
        old = f"| `{r['email']}` | {label} | 1 | 2 Oct |"
        new = f"| `{r['email']}` | {label} | {r['emails']} | 24 Sep, 2 Oct |"
        t, ok = sub1(t, old, new, f"row {r['email']}")
        if ok:
            changed.append(f"note row {r['email']}")

t, _ = sub1(t,
    "- **26 emails**, not 21 — the 9 `prospects.json` contacts received 23, and the 3 named leads in\n"
    "  `data/state.json` received 3 more from a **second** engine (`dist/cli.js`) that we had forgotten was live.",
    f"- **{total} emails**, not 21 — the 9 `prospects.json` contacts received 23, and the 3 named leads in\n"
    "  `data/state.json` received **6 more** from a **second** engine (`dist/cli.js`) that we had forgotten was\n"
    "  live. Each of those 3 received **2** emails — a 24 Sep *\"Welcome — Catalogue & Introduction\"* (which\n"
    "  carried no CIIE claim) and a 2 Oct custom quote. So **26 of the "
    f"{total} emails carried a CIIE claim**, and all {nrec} recipients received at least one of those.",
    "correction-to-record bullet")

t, _ = sub1(t,
    "- [x] **Recipient list verified against AgentMail**, not from memory — 12 addresses, 26 emails",
    f"- [x] **Recipient list verified against AgentMail**, not from memory — {nrec} addresses, {total} emails",
    "pre-send checklist")

# send-from line: the false email came from the CIIE agent inbox, not sales@
t, _ = sub1(t,
    "**Send from:** `sales@studex-group.com` (the inbox they were contacted from).",
    "**Send from:** `project-2571-studex-agent-2077@agentmail.to` — **the inbox the false emails actually came "
    "from**, so the correction lands in the same thread they remember. ⚠️ `sales@studex-group.com` exists and "
    "works, but it is a *different* AgentMail account; an apology from an address they were never contacted "
    "from reads like phishing and undermines the correction. The CIIE inbox needs the **ciie-nurture key** "
    "(`**************…`); the main key 404s it.",
    "send-from line")

if t != orig:
    open(NOTE, "w", encoding="utf8").write(t)
    changed.append("note prose")
    print("  note updated")
else:
    print("  note unchanged")

# ------------------------------------------------------------------ 2. README
r = open(README, encoding="utf8").read()
orig = r
r, _ = sub1(r,
    "- **26 emails**, not 21 — 23 to the 9 `ciie-nurture/prospects.json` contacts, plus **3 more from a",
    f"- **{total} emails**, not 21 — 23 to the 9 `ciie-nurture/prospects.json` contacts, plus **6 more from a",
    "README count")
r, _ = sub1(r,
    "and both CIIE crons (`36bc4f61`, `766d1f8a`) are **disabled**. The 26 emails were sent 25 Sep – 3 Oct",
    f"and both CIIE crons (`36bc4f61`, `766d1f8a`) are **disabled**. The {total} emails were sent 24 Sep – 3 Oct",
    "README window")
if r != orig:
    open(README, "w", encoding="utf8").write(r)
    changed.append("README")
    print("  README updated")
else:
    print("  README unchanged")

# ------------------------------------------------------------------ 3. the new rule
DP = os.path.join(ROOT, "ops", "drift-check.py")
src = open(DP, encoding="utf8").read()

anchor = '''    # 5. recipient coverage: every address that received the bad copy must be listed
    rpath = os.path.join(ROOT, CORRECTION_RECIPIENTS)'''

new_rule = '''    # 4b. THE NOTE MUST AGREE WITH THE AUTHORITATIVE JSON.
    # This rule exists because it did NOT: the JSON said 29 and the draft body
    # still said 26, and the checker passed. A number that lives in two places
    # will drift unless something compares them.
    rpath0 = os.path.join(ROOT, CORRECTION_RECIPIENTS)
    if os.path.exists(rpath0):
        d0 = json.load(open(rpath0, encoding="utf8"))
        auth_total = d0.get("totalEmails")
        auth_recs = d0.get("totalRecipients")
        for name in notes:
            rel = f"{CORRECTION_DIR}/{name}"
            raw = open(os.path.join(cdir, name), encoding="utf8", errors="ignore").read()
            # every "<n> emails" / "<n> emails to <m> recipients" claim in the note
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
                                f"list says {rr.get('emails')}")

    # 5. recipient coverage: every address that received the bad copy must be listed
    rpath = os.path.join(ROOT, CORRECTION_RECIPIENTS)'''

if "THE NOTE MUST AGREE WITH THE AUTHORITATIVE JSON" not in src:
    assert anchor in src, "rule-5 anchor not found"
    src = src.replace(anchor, new_rule, 1)
    open(DP, "w", encoding="utf8").write(src)
    changed.append("drift-check rule 4b")
    print("  drift-check.py: added rule 4b (note must agree with the JSON)")
else:
    print("  drift-check.py: rule 4b already present")

print("\nchanged:", ", ".join(changed) if changed else "nothing")
