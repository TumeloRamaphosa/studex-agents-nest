#!/usr/bin/env python3
"""A Rwandan LDC origin has NO China tariff expiry. No China-facing asset may
say otherwise.

🔴 THE DEFECT (found 2026-10-28 03:40 UTC, during a heartbeat)
-----------------------------------------------------------
China's zero-tariff framework for Africa has TWO parts, and the copy we
published used only one of them:

  * From 1 May 2026, China grants zero-tariff treatment to all 53 African
    countries with diplomatic relations (all but Eswatini).
  * That 1 May 2026 - 30 April 2028 window applies to the **20 African
    countries that are NOT least developed countries**.
  * The 33 African LDCs - Rwanda among them - have held **100% zero-tariff on
    all tariff lines since 1 Dec 2024**, and that treatment carries **no end
    date**.

Source: 国务院关税税则委员会 announcement, 28 Apr 2026 (gss.mof.gov.cn), and
english.www.gov.cn, 1 May 2026 ("China has already scrapped tariffs on 100
percent of tariff lines for 33 least developed countries (LDCs) in Africa
since Dec. 1, 2024").

🔑 **OUR LIVE CHINA PAGE SAID THE OPPOSITE OF OUR OWN BUYER SHEET.**
`china-coffee-export/index.html` published *"The 0% tariff window closes on
30 April 2028"* and *"a buyer who waits past 30 April 2028 is negotiating
under a different tariff regime"* - for a Rwandan LDC origin, whose window
does not close at all. Meanwhile `china-coffee-sheet-copy-paste.md` (the sheet
that actually goes to buyers) said the CORRECT thing: *"Rwanda is an LDC origin
our zero-tariff treatment has NO expiry, while South Africa's, Kenya's,
Nigeria's and Egypt's expires 30 April 2028."* TAB 3d of that sheet exists
precisely to win that comparison - and our website was arguing against it.

🔑 **AND THE DRIFT CHECKER SAID 18/18 CLEAN.** Every surface carried the same
wrong claim consistently, so parity was perfect. 🔑 *Parity is not truth.* A
parity checker proves the pages match their sources; it says nothing about
whether the source is right. This test is that missing check.

🔑 **AND THE ROOT CAUSE WAS A STANDING RULE**, in
`studex-trade-terms/trade-terms.json`:
    "The China 0% tariff is always written with its expiry date (30 April
     2028) attached."
with a `required` list that MANDATED the string "30 April 2028" on both China
pages, and a rationale that read *"a window without an end date is a claim we
cannot support."* The premise was right for a country inside a window and
inverted for an LDC - where there is no window, so there is no end date to
state, and inventing one is the claim we cannot support.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path("/workspace")
TT = ROOT / "studex-trade-terms" / "trade-terms.json"

# The wrong framings, in every shape we have ever written them.
BANNED = [
    "0% window runs to 30 April 2028",
    "Zero Tariff \u2014 to 30 Apr 2028",
    "tariff window closes on 30 April 2028",
    "0% for all 53 African countries, 1 May 2026 \u2013 30 April 2028",
]
# The correct claim, in the two forms the assets must carry.
REQUIRED = ["no expiry", "LDC"]

# Every China-facing source that ships to a buyer.
SURFACES = [
    "china-coffee-export/index.html",
    "china-coffee-export/dist/index.html",
    "studex-wildlife-coffee-vite/dist/index.html",
]

PASSED = 0
FAILED = 0


def check(name, cond, detail=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print("[PASS] " + name)
    else:
        FAILED += 1
        print("[FAIL] " + name + (("  -> " + detail) if detail else ""))


def banned_present(text):
    """Which banned framings are in this text?"""
    return [b for b in BANNED if b in text]


def required_missing(text):
    """Which required strings are missing from this text?"""
    return [r for r in REQUIRED if r not in text]


# --------------------------------------------------------------- the surfaces
for rel in SURFACES:
    p = ROOT / rel
    check("surface exists: " + rel, p.exists())
    if not p.exists():
        continue
    text = p.read_text(encoding="utf8")
    check("no banned expiry framing on " + rel,
          not banned_present(text), str(banned_present(text)))
    check("states the correct claim on " + rel,
          not required_missing(text), str(required_missing(text)))

# ------------------------------------------------- the trade-terms spec/rules
tt = json.loads(TT.read_text(encoding="utf8"))
rules = " ".join(tt.get("rules", []))
check("no rule mandates writing the expiry",
      "always written with its expiry date" not in rules)
check("a rule forbids putting the expiry on an LDC origin",
      "NEVER given an expiry" in rules and "LDC" in rules)

req_strings = {e.get("string") for e in tt.get("required", [])}
check("the required[] list no longer demands '30 April 2028'",
      "30 April 2028" not in req_strings)
forb_strings = {e.get("string") for e in tt.get("forbidden", [])}
check("the forbidden[] list bans the wrong framings",
      all(b in forb_strings for b in BANNED),
      "missing=%s" % [b for b in BANNED if b not in forb_strings])

china = tt["pages"]["china"]
china_row = json.dumps(china["sections"])
check("the china panel row states no expiry and LDC",
      "no expiry" in china_row and "LDC" in china_row)
check("the china callout is about the LDC, not a closing window",
      "no expiry" in china["callout"]["title"].lower()
      and "30 April 2028" in china["callout"]["body"])
b2b = json.dumps(tt["pages"]["b2b"]["sections"])
check("the b2b panel row states no expiry and LDC",
      "no expiry" in b2b and "LDC" in b2b)

# ------------------------------------------------------------- the registry
reg = (ROOT / "studex-meat" / "PRICE-SOURCE-REGISTRY.md").read_text(encoding="utf8")
check("the registry records that OUR expiry is none",
      "no expiry" in reg.lower() and "LDC" in reg)
check("the registry still names 30 Apr 2028 as THEIR expiry",
      "THEIRS" in reg and "30 April 2028" in reg)

# ------------------------------------------- the ENFORCED drift-manifest guard
man = json.loads((ROOT / "ops" / "drift-manifest.json").read_text(encoding="utf8"))
for pg in man["pages"]:
    if pg.get("name") == "Coffee China / CIIE":
        check("the drift manifest REQUIRES the corrected claim on the China page",
              "no expiry" in pg["must"] and "LDC" in pg["must"])
        check("the drift manifest BANS the wrong framing on the China page",
              any(b in pg["must_not"] for b in BANNED))
    if pg.get("name") == "Coffee B2B green":
        check("the drift manifest REQUIRES the corrected claim on the coffee B2B page",
              "no expiry" in pg["must"] and "LDC" in pg["must"])

# --------------------------------------------------------- NEGATIVE CONTROL
# The check must be able to FAIL. Feed it the copy we shipped until tonight
# and prove it is rejected - otherwise this test certifies nothing.
OLD_COPY = (
    '<p>Premium Rwanda A1 & A2 grade Arabica coffee. Tariff-free entry into '
    'China since 1 May 2026 \u2014 the 0% window runs to 30 April 2028.</p>'
    '<div class="tt-callout-title">The 0% tariff window closes on 30 April 2028</div>'
    '<tr><td><strong>0% for all 53 African countries, 1 May 2026 \u2013 30 April 2028.</strong></td></tr>'
)
check("NEGATIVE CONTROL: the old copy IS caught",
      bool(banned_present(OLD_COPY)) and bool(required_missing(OLD_COPY)),
      "banned=%s missing=%s" % (banned_present(OLD_COPY), required_missing(OLD_COPY)))
check("NEGATIVE CONTROL: the corrected copy is NOT caught",
      not banned_present(
          "Rwanda is an LDC origin - no expiry, and the 30 April 2028 window "
          "belongs to the 20 African non-LDC countries."))

print("\n%d passed, %d failed" % (PASSED, FAILED))
sys.exit(1 if FAILED else 0)
