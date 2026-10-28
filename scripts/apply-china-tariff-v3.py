#!/usr/bin/env python3
"""
Apply CHINA TARIFF POSITION v3 to the live China coffee outreach copy.

Run:  python3 scripts/apply-china-tariff-v3.py            (apply)
      python3 scripts/apply-china-tariff-v3.py --check    (dry run, exit 1 if drift)

Every edit asserts EXACTLY ONE marker match before replacing. If a marker is
missing or ambiguous the script aborts without writing — so a partial or
mangled patch can never land in the outreach copy.

Corrections applied (source: research/2026-10-25.md):
  1. TARIFF FACT — zero-tariff effective 1 May 2026 (not "window opens July 20"),
     continental framework (not "SA-China bilateral agricultural protocol"),
     LDC origins incl. Rwanda have NO EXPIRY (non-LDC SA/KE/NG/EG expire 30 Apr 2028).
  2. DATES — email sequence re-dated to this week and tied to CIIE (11 days out).
  3. PAYMENT TERMS — confirmed irrevocable LC added to first-touch email.
  4. DOCUMENTATION — Certificate of Origin must cite the zero-tariff preference.
  5. CIIE — booth status escalated from "NOT YET APPLIED" to a flagged emergency.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---------------------------------------------------------------- tariff block
TARIFF_SUBJECT = (
    "Since **1 May 2026**, China has applied **zero tariff on 100% of tariff lines** to imports "
    "from the 53 African countries with diplomatic ties — including green and roasted coffee, "
    "which previously carried 8–15% duty.\n"
    "\n"
    "Because **Rwanda is an LDC (Least Developed Country) origin, that zero-tariff treatment has "
    "no expiry date.** This is not a promotional window that opens and closes — it is a permanent "
    "structural advantage, and it applies to our lots specifically. Non-LDC African origins "
    "(South Africa, Kenya, Nigeria, Egypt) only hold the duty-free position until "
    "**30 April 2028**. On a 60kg bag at our price band the 8–15% duty differential is "
    "**$32–$61 per bag** — enough to flip a comparison against a competing origin."
)

TARIFF_BOLD = (
    "**Why Rwanda works for China — and why our timing is better than a \"window\":**\n"
    + TARIFF_SUBJECT
)

TARIFF_PLAIN = TARIFF_SUBJECT

# ------------------------------------------------------------------- LC terms
LC_LINE = (
    "**Payment terms:** confirmed irrevocable Letter of Credit for initial transactions. "
    "We invoice on presentation of the full shipping document set — no open account on a "
    "first shipment."
)

# ------------------------------------------------------------- documentation
DOC_LINE = (
    "**Documentation:** Chinese-language phytosanitary certificate, health certificate, "
    "commercial invoice (HS code + FOB value), bill of lading, packing list — and a Certificate "
    "of Origin that **explicitly cites China's zero-tariff preference framework**, so the "
    "duty-free position survives customs."
)

ROASTED_LINE = (
    "**Roasting at origin available.** Green and roasted both enter China duty-free; roasted and "
    "packed at origin roughly doubles revenue per kilo on the same freight and the same "
    "counterparty. Tell us and we will quote it."
)

# --------------------------------------------------------------- tariff table
TARIFF_TABLE = """## TAB 3d: CHINA TARIFF POSITION — v3 (use this to win the comparison)

**Copy this block at the top of any China-facing buyer conversation.** It replaces the old
"window opens July 20" line, which was wrong on the date, wrong on the instrument, and wrong on
the origin that governs our lots.

| Fact | Correct position | What the old copy said | Why it mattered |
|---|---|---|---|
| Effective date | **1 May 2026** | "window opens July 20" | The window had been open for 4 months — the old line was already stale on the day it was sent |
| Instrument | **Continental framework** — 100% of tariff lines, all 53 African countries with diplomatic ties | "SA-China bilateral agricultural protocol" | There is no bilateral agricultural protocol. Pointing a Chinese buyer at one is a credibility hit |
| Our origin | **Rwanda is an LDC — zero tariff has NO expiry** | *(never mentioned)* | We were quoting our own weaker position. Our permanent advantage was our competitors' expiring one |
| Competing origins | South Africa / Kenya / Nigeria / Egypt lose the duty-free position **30 April 2028** | *(never mentioned)* | The differentiator is permanent for us and dated for them |
| Duty at stake | 8–15% on green + roasted coffee | *(never mentioned)* | At our band, **$32–$61 per 60kg bag** — enough to flip a lot comparison |
| Market pull | African coffee exports to China **+145.7% YoY (Jan–May 2026)**; China bought **$246M** of African coffee in 2025 (up from $157M in 2024); demand growing >30%/yr | *(never mentioned)* | Demand is not the problem. Being misinformed about the tariff was the problem |

> **One-line version for a buyer email or a LinkedIn message:**
> *"Since 1 May 2026 China has applied zero tariff on 100% of tariff lines to all 53 African
> countries with diplomatic ties — and because Rwanda is an LDC origin, that duty-free position
> has no expiry date, unlike South Africa's, which expires 30 April 2028."*

### 📦 Roasting at origin — the revenue line still missing from the sheet

| Route | Indicative FOB | Uplift | Duty treatment |
|---|---|---|---|
| Green, FOB Kigali | ~$3.80/kg baseline | — | Zero tariff (LDC, no expiry) |
| **Roasted + packaged at origin** | **~$8.50/kg** | **+124% (+$4.70/kg)** | **Zero tariff — same treatment** |

> ⚠️ **Not a quote.** The figures above are the market benchmark from `research/2026-10-25.md`.
> The roasted SKU is **not yet a confirmed Studex offering** — it is a development line pending
> Kigali partner confirmation of roasting capacity and cost. **Do not put a roasted price in a
> buyer email until that confirmation is in hand.** Raise it as a conversation ("green and roasted
> both enter duty-free — shall I quote roasted?"), then quote.
>
> **Why it matters:** processing the value in Africa keeps the value in Africa *and* raises the
> ticket on the same freight, the same counterparty and the same duty treatment. Same logic
> applies to the UAE re-export channel, where Dubai roasts and re-exports.

---

"""

EDITS = {
    "china-coffee-outreach.md": [
        (
            "## Studex Meat | Tumelo Ramaphosa | v2 — 24 October 2026 (live price band)",
            """## Studex Meat | Tumelo Ramaphosa | v3 — 25 October 2026 (tariff position corrected)

> 🔴 **v3 CORRECTS THE TARIFF FACT — READ BEFORE SENDING.**
>
> The old opening line said *"a rare market window opens July 20 — South African green coffee
> gains access to the Chinese market under the SA-China bilateral agricultural protocol."*
> **That sentence was wrong three times over:** the date (zero tariff began **1 May 2026**, not
> 20 July — the window had been open for four months); the instrument (there is **no** bilateral
> agricultural protocol — it is a **continental framework** covering 100% of tariff lines across
> all 53 African countries with diplomatic ties); and the origin that governs our lots
> (**Rwanda is an LDC, so our zero-tariff treatment has NO expiry** — unlike South Africa's,
> Kenya's, Nigeria's and Egypt's, which expires 30 April 2028).
>
> **We were quoting our own weaker position while our competitors' advantage was the dated one.**
> This has been corrected throughout this file. Full reasoning and sources:
> `research/2026-10-25.md`.
>
> Also in v3: email sequence **re-dated to this week** and tied to CIIE (11 days out); a
> **confirmed irrevocable LC** line added to the first-touch email; the **Certificate of Origin
> requirement** added; and a **roasted-at-origin** line added to EMAIL 1.

---""",
            "outreach-header-v3",
        ),
        (
            "## BUYER TARGET LIST — China Coffee Window (July 20 opens)",
            "## BUYER TARGET LIST — China Coffee (permanent zero-tariff, LDC origin)",
            "outreach-buyerlist-heading",
        ),
        (
            "### EMAIL 1 — Initial Outreach (Send July 20 or immediately)",
            "### EMAIL 1 — Initial Outreach (Send week of 26 Oct 2026 — ahead of CIIE)",
            "outreach-email1-heading",
        ),
        (
            "**We're writing to you because a rare market window opens July 20 — South African green "
            "coffee gains access to the Chinese market under the SA-China bilateral agricultural "
            "protocol. We're one of the first movers.**",
            TARIFF_BOLD,
            "outreach-email1-tariff",
        ),
        (
            "- Minimum order: 60kg bags\n\n**Why Rwanda, why now:**",
            "- Minimum order: 60kg bags\n\n"
            + ROASTED_LINE
            + "\n\n"
            + LC_LINE
            + "\n\n"
            + DOC_LINE
            + "\n\n**Why Rwanda, why now:**",
            "outreach-email1-terms",
        ),
        (
            "We're actively onboarding roasters ahead of the July 20 window. Sample stock is limited "
            "and allocated on a first-contact basis.",
            "We're actively onboarding roasters ahead of CIIE (5–10 November, Shanghai). Sample "
            "stock is limited and allocated on a first-contact basis.",
            "outreach-email2-window",
        ),
        (
            "July 20 a significant window opens for SA-origin coffee into China. We're early movers "
            "and looking to connect with roasters and importers who prioritise quality and "
            "certification.",
            "Since 1 May 2026 China has applied zero tariff on 100% of tariff lines to all 53 "
            "African countries with diplomatic ties — and because Rwanda is an LDC origin, that "
            "duty-free position has no expiry date, unlike South Africa's, which expires 30 April "
            "2028. We're looking to connect with roasters and importers who prioritise quality and "
            "traceability.",
            "outreach-linkedin-window",
        ),
        (
            "**Status:** Must apply by approximately September 30, 2026 (typically 60 days before "
            "event)",
            "**Status:** 🔴 **NOT YET APPLIED — EMERGENCY.** The ~30 September 2026 deadline has "
            "passed and the event opens in 11 days. Late entry may or may not be possible and must "
            "be confirmed with the organiser immediately.",
            "outreach-ciie-status",
        ),
        (
            "*v1 — Tumelo Ramaphosa | Studex Meat | July 2026*",
            "*v3 — Tumelo Ramaphosa | Studex Meat | 25 October 2026 (tariff position corrected)*",
            "outreach-footer",
        ),
    ],
    "china-coffee-sheet-copy-paste.md": [
        (
            "## Studex Meat | Tumelo Ramaphosa | v2 — 24 October 2026 (live price band rebuild)",
            """## Studex Meat | Tumelo Ramaphosa | v3 — 25 October 2026 (tariff position corrected)

> 🔴 **v3 CORRECTS THE TARIFF FACT — THE OLD OPENING LINE WAS WRONG ON DATE, INSTRUMENT AND
> ORIGIN.** Zero tariff on all tariff lines from the 53 African countries with diplomatic ties
> began **1 May 2026** (not "a window that opens July 20" — it had been open for four months); it
> is a **continental framework**, not an "SA-China bilateral agricultural protocol" (which does not
> exist); and because **Rwanda is an LDC origin our zero-tariff treatment has NO expiry**, while
> South Africa's, Kenya's, Nigeria's and Egypt's expires 30 April 2028. **We were quoting our own
> weaker position.** Full reasoning and sources: `research/2026-10-25.md`.
>
> Also in v3: **TAB 2 dates re-dated** to this week and tied to CIIE; **TAB 3d** added (tariff
> position + roasted-at-origin revenue line); **LC terms** added to Email Draft 1; **Certificate of
> Origin requirement** added; **TAB 4** CIIE status escalated.

---""",
            "sheet-header-v3",
        ),
        (
            "| 1 - Initial | July 20 (window opens) |",
            "| 1 - Initial | **26 Oct 2026** (week of, ahead of CIIE) |",
            "sheet-tab2-date-1",
        ),
        (
            "| 2 - Follow-up | July 25 |",
            "| 2 - Follow-up | **2 Nov 2026** (+7 days) |",
            "sheet-tab2-date-2",
        ),
        (
            "| 3 - Value Add | July 30 |",
            "| 3 - Value Add | **9 Nov 2026** (+7 days) |",
            "sheet-tab2-date-3",
        ),
        (
            "We're writing to you because a rare market window opens July 20 — South African green "
            "coffee gains access to the Chinese market under the SA-China bilateral agricultural "
            "protocol. We're one of the first movers.",
            TARIFF_PLAIN,
            "sheet-email1-tariff",
        ),
        (
            "- Minimum order: 60kg bags\n\n**Why Rwanda, why now:**",
            "- Minimum order: 60kg bags\n\n"
            + ROASTED_LINE
            + "\n\n"
            + LC_LINE
            + "\n\n"
            + DOC_LINE
            + "\n\n**Why Rwanda, why now:**",
            "sheet-email1-terms",
        ),
        (
            "We're actively onboarding roasters ahead of the July 20 window. Sample stock is limited "
            "and allocated on a first-contact basis.",
            "We're actively onboarding roasters ahead of CIIE (5–10 November, Shanghai). Sample "
            "stock is limited and allocated on a first-contact basis.",
            "sheet-email2-window",
        ),
        (
            "## TAB 4: CIIE NOV 2026",
            TARIFF_TABLE + "## TAB 4: CIIE NOV 2026",
            "sheet-tab3d-insert",
        ),
        (
            "| Application deadline | ~September 30, 2026 |",
            "| Application deadline | ~September 30, 2026 — **PASSED. Late entry must be confirmed "
            "with the organiser today.** |",
            "sheet-tab4-deadline",
        ),
        (
            "| Studex status | NOT YET APPLIED |",
            "| Studex status | 🔴 **NOT YET APPLIED — EMERGENCY, 11 days to the event** |",
            "sheet-tab4-status",
        ),
        (
            "## ⚠️ BEFORE YOU SEND — three things this file still gets wrong",
            "## ⚠️ BEFORE YOU SEND — four things this file still gets wrong",
            "sheet-warn-count",
        ),
        (
            "3. **The old price sentence** (\"FOB Kigali pricing from USD 4.80/kg\") — replaced in v2 "
            "with the live\n   band. See EMAIL 1 below.",
            """3. **The old price sentence** ("FOB Kigali pricing from USD 4.80/kg") — replaced in v2
with the live
   band. See EMAIL 1 below.
4. **The "window opens July 20 / SA-China bilateral agricultural protocol" line — REMOVED in v3.**
   It was factually wrong on the date (zero tariff began **1 May 2026**), wrong on the instrument
   (it is a **continental framework**, not a bilateral protocol), and wrong on our own position
   (**Rwanda is an LDC — no expiry**, while South Africa's expires 30 April 2028). The corrected
   tariff position is in **TAB 3d**. A Chinese buyer who reads the real policy will spot the old
   line immediately — and we hand that advantage to whichever competitor did the reading.""",
            "sheet-warn-item4",
        ),
        (
            "*v2 — Robusca VM | Tumelo Ramaphosa | Studex Meat | 24 October 2026*",
            "*v3 — Robusca VM | Tumelo Ramaphosa | Studex Meat | 25 October 2026 (tariff position "
            "corrected)*",
            "sheet-footer",
        ),
    ],
    "china-coffee-outreach-revised.md": [
        (
            "# 📧 China Coffee Outreach — REVISED (July 21, 2026)\n"
            "## Studex Meat | Based on Research Hour Intelligence",
            "# 📧 China Coffee Outreach — REVISED (July 21, 2026)\n"
            "## Studex Meat | Based on Research Hour Intelligence\n"
            "\n"
            "> ⚠️ **SUPERSEDED — 25 October 2026. Historical record only, do not send.**\n"
            "> This file stated *\"China market OPENED July 20, 2026\"*. The corrected position is\n"
            "> in `china-coffee-outreach.md` (v3): zero tariff on all tariff lines from the 53\n"
            "> African countries with diplomatic ties began **1 May 2026**; it is a **continental\n"
            "> framework**, not a bilateral protocol; and because **Rwanda is an LDC our zero-tariff\n"
            "> treatment has no expiry** (South Africa's expires 30 April 2028). The July framing is\n"
            "> retained below as the record of what was decided then.\n"
            "> **The false claims inside the email bodies have been corrected in place** so that no\n"
            "> one can lift them by copy-paste.",
            "revised-superseded-banner",
        ),
        (
            "4. **China market OPENED July 20, 2026** — yesterday. Timing is everything.",
            "4. **China zero-tariff OPENED 1 May 2026** — and because Rwanda is an LDC, it has no "
            "expiry. Timing is everything.",
            "revised-finding-4",
        ),
        (
            "and starting July 20, 2026, Rwandan green coffee has zero-tariff access to China under "
            "the new bilateral agricultural protocol.",
            "and since 1 May 2026, Rwandan green coffee — an LDC origin — has had zero-tariff "
            "access to China with no expiry date.",
            "revised-luckin-body",
        ),
        (
            "The new China bilateral framework that took effect yesterday (July 20) means those "
            "exports can now flow directly to Chinese roasters for the first time, zero-tariff.",
            "China's continental zero-tariff framework for African origins (effective 1 May 2026, "
            "no expiry for LDC origins such as Rwanda) means those exports flow directly to Chinese "
            "roasters, zero-tariff.",
            "revised-stat-body",
        ),
        (
            "- **Zero-tariff to China, effective July 20, 2026**",
            "- **Zero-tariff to China, effective 1 May 2026 — no expiry for LDC origins like Rwanda**",
            "revised-facts-bullet",
        ),
    ],
}


def apply_file(path, edits, check_only):
    """Apply edits idempotently.

    Rule per edit, evaluated in order:
      1. if the replacement text is already present -> SKIP (already applied).
         Checked FIRST, because some replacements legitimately contain their own
         marker (e.g. an insert that re-emits the heading it anchored on).
      2. else the marker must match EXACTLY once -> APPLY.
      3. otherwise -> hard FAIL. Nothing is written for that file.

    After all edits, every replacement must occur exactly once in the result --
    this is the duplication guard that catches a double-insert.
    """
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    original = text
    applied = []
    skipped = []
    for old, new, label in edits:
        if new in text:
            skipped.append(label)
            continue
        n_old = text.count(old)
        if n_old != 1:
            print(f"  FAIL[{label}]: marker count = {n_old} (expected exactly 1)")
            return False, applied
        text = text.replace(old, new)
        applied.append(label)

    # duplication guard
    for old, new, label in edits:
        n = text.count(new)
        if n != 1:
            print(f"  FAIL[{label}]: replacement occurs {n} times after apply (expected 1)")
            return False, applied

    if check_only:
        state = "DRIFT" if original != text else "CLEAN"
        print(f"  {state} (dry run): {path} — {len(applied)} pending, {len(skipped)} already applied")
    else:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"  WROTE: {path} — {len(applied)} applied, {len(skipped)} already applied")
        if applied:
            print(f"         edits: {', '.join(applied)}")
    return True, applied + skipped


def main():
    check_only = "--check" in sys.argv
    print(f"=== CHINA TARIFF POSITION v3 {'(CHECK ONLY)' if check_only else '(APPLY)'} ===")
    ok = True
    total = 0
    for path, edits in EDITS.items():
        if not os.path.exists(path):
            print(f"  FAIL: {path} not found")
            ok = False
            continue
        good, applied = apply_file(path, edits, check_only)
        total += len(applied)
        ok = ok and good
    print(f"=== {'ALL OK' if ok else 'FAILED'} — {total} edits across {len(EDITS)} files ===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
