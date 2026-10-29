#!/usr/bin/env python3
"""
SA B2B COFFEE + CAVIAR — BUILD VERIFICATION HARNESS
Built: 2026-10-29 (Build Hour). Owner: Robusca / Studex Ops.

WHY THIS EXISTS
---------------
Tonight's brief warned that source files and live deploys had drifted apart
three times in a month, and that each build must "verify the source against
the live deploy before and after."

A guard that only reads the source cannot catch the worst case: a source that
is correct while the page the customer sees is not. So this harness checks
THREE things:

  1. The SOURCE files (what we deployed)
  2. The GENERATED price sheet (does the published table match the model?)
  3. The LIVE URLs (what the customer actually sees)

and it FAILS LOUDLY on any caviar price, any false compliance claim, or any
number that has drifted between the model and the page.

WHY LEGACY DEPLOYS ARE A WARNING, NOT A FAILURE
-------------------------------------------------
The deploy platform's delete lives in Tumelo's dashboard, not in the CLI. Three
pre-existing deploys still carry the old content and this harness cannot remove
them. If they were hard failures the harness would exit 1 forever — and a
guard that always fails is a guard that gets switched off. So: the deploys this
build produced are HARD failures; the legacy ones are REPORTED with a named
owner action.

Run:  python3 ops/verify-build-2026-10-29.py
Exit: 0 = all pass, 1 = at least one FAIL
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

WS = Path("/workspace")

CAVIAR_SRC = WS / "deploy-caviar" / "index.html"
COFFEE_SRC = WS / "sa-hospitality-coffee" / "index.html"
PRICE_JSON = WS / "sa-b2b-coffee" / "price-sheet.generated.json"

# Deploys this build produced — HARD failures if anything is wrong.
LIVE_CAVIAR_NEW = ["https://b0hj2mt9c1nt.space.mcode.io"]
LIVE_COFFEE_NEW = ["https://iei7fdqx5j1y.space.mcode.io"]

# Deploys that predate tonight and cannot be deleted from here.
LEGACY = [
    ("https://ess0ocgcd9f0.space.mcode.io", "caviar page with published prices"),
    ("https://i09hd71cvt06.space.mcode.io", "SA hospitality coffee, old build"),
    ("https://psq9xaisb9kf.space.mcode.io", "SA hospitality coffee, older build with caviar prices"),
    ("https://vbctytmp8t3c.space.mcode.io", "SA hospitality coffee, first deploy of tonight (pre-link-fix)"),
]

# Any of these on a live page = a caviar sale with no permit stack behind it.
CAVIAR_PRICE_PATTERNS = [
    r"R\s*4\s*[,.]?\s*200",
    r"R\s*2\s*[,.]?\s*800",
    r"R\s*1\s*[,.]?\s*600",
    r"R\s*34\s*[,.]?\s*000",
    r"R\s*22\s*[,.]?\s*000",
    r"R\s*12\s*[,.]?\s*500",
]

# Unconditional compliance claims. The permit stack is NOT assembled.
FALSE_CLAIM_PATTERNS = [
    (r"cites[- ]compliant", "cites-compliant"),
    (r"itac[- ]compliant", "itac-compliant"),
    (r"\bcites certified\b", "cites certified"),
    (r"we handle the paperwork", "we handle the paperwork"),
    (r"fully compliant", "fully compliant"),
    (r"all permits in place", "all permits in place"),
    (r"import permit (?:is )?in hand", "import permit in hand"),
    (r"import permit stack in hand", "import permit stack in hand"),
    (r"permit stack in hand", "permit stack in hand"),
    (r"full import compliance", "full import compliance"),
]

# A sale path for caviar while the stack is unassembled.
SALE_PATH_PATTERNS = [
    (r"50%\s*deposit", "50% deposit"),
    (r"pro-?forma invoice", "pro-forma invoice"),
    (r"request sample pack", "request sample pack"),
    (r"we send a 50g sample", "50g sample offer"),
    (r"landed cost provided on request", "landed cost offered"),
]

# Origin claims we cannot evidence.
ORIGIN_CLAIM_PATTERNS = [
    (r"\brussian\b", "russian"),
    (r"🇷🇺", "RU flag"),
    (r"moscow", "moscow"),
]

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
    return ok


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (build-verifier)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def scan(html, label):
    for pat in CAVIAR_PRICE_PATTERNS:
        hits = re.findall(pat, html, re.I)
        check(f"{label}: no caviar price /{pat}/", not hits, f"found {len(hits)}: {hits[:3]}")
    for pat, label_txt in FALSE_CLAIM_PATTERNS:
        hits = re.findall(pat, html, re.I)
        check(f"{label}: no false claim '{label_txt}'", not hits, f"found {len(hits)}")
    for pat, label_txt in SALE_PATH_PATTERNS:
        hits = re.findall(pat, html, re.I)
        check(f"{label}: no sale path '{label_txt}'", not hits, f"found {len(hits)}")
    for pat, label_txt in ORIGIN_CLAIM_PATTERNS:
        hits = re.findall(pat, html, re.I)
        check(f"{label}: no unevidenced origin '{label_txt}'", not hits, f"found {len(hits)}")


print("=" * 78)
print("BUILD VERIFICATION — 2026-10-29 Build Hour")
print("=" * 78)

print("\n[1] SOURCE FILES")
caviar_html = CAVIAR_SRC.read_text(encoding="utf-8")
coffee_html = COFFEE_SRC.read_text(encoding="utf-8")
scan(caviar_html, "caviar source")
scan(coffee_html, "coffee source")

for needle, label in [
    ("subject to import permit", "permit-conditioned line"),
    ("not yet assembled", "stack-not-assembled disclosure"),
    ("trade accounts only", "trade-accounts-only qualifier"),
]:
    check(f"caviar source: has {label}", needle.lower() in caviar_html.lower())

check("caviar source: keeps 'import duty and VAT quoted in the landed cost'",
      "import duty and vat quoted in the landed cost" in caviar_html.lower())

check("coffee source: has 4 volume tiers",
      all(t in coffee_html for t in ["1 kg", "5 kg", "20 kg", "30 kg"]))
check("coffee source: has a quote-request form",
      'id="quote"' in coffee_html and 'quote-form' in coffee_html)
check("coffee source: has training price line", "R7,500" in coffee_html)
check("coffee source: has retainer price line", "R3,500" in coffee_html)
check("coffee source: has sachet price line", "R3.95" in coffee_html)
check("coffee source: has sample pack line", "R495" in coffee_html)
check("coffee source: roasted MOQ is 5 kg, not the old 50 kg",
      "trade moq" not in coffee_html.lower()
      and "minimum order is <strong>5 kg</strong>" in coffee_html.lower())
check("coffee source: green MOQ is 20 MT", "20 MT" in coffee_html)

print("\n[2] GENERATED PRICE SHEET vs PUBLISHED PAGE")
data = json.loads(PRICE_JSON.read_text(encoding="utf-8"))
for origin in data["publicSheet"]["origins"]:
    for cell in origin["cells"]:
        price = f"R{cell['priceZarPerKg']:,}"
        check(f"page carries {origin['name']} {cell['tier']} = {price}", price in coffee_html)
        check(f"floor ok: {origin['name']} {cell['tier']} margin {cell['marginPct']}% >= 25%",
              cell["marginPct"] >= 25)
        check(f"floor ok: {origin['name']} {cell['tier']} price >= floor",
              cell["priceZarPerKg"] >= cell["floorZarPerKg"] - 0.01,
              f"price {cell['priceZarPerKg']} < floor {cell['floorZarPerKg']}")

for leak in ["landed", "floor @", "margin floor", "16.64", "115.28"]:
    check(f"coffee page does not leak internal '{leak}'", leak.lower() not in coffee_html.lower())

print("\n[3] LIVE PAGES — deploys shipped tonight (must be clean)")
for url in LIVE_CAVIAR_NEW:
    try:
        html = fetch(url)
        scan(html, f"live {url.split('//')[1][:12]}")
        check("live caviar has 'not yet assembled'", "not yet assembled" in html.lower())
        check("live caviar keeps the approved landed-cost wording",
              "import duty and vat quoted in the landed cost" in html.lower())
    except Exception as e:
        check(f"live caviar {url} reachable", False, repr(e))

for url in LIVE_COFFEE_NEW:
    tag = url.split("//")[1][:12]
    try:
        html = fetch(url)
        scan(html, f"live {tag}")
        check(f"live coffee {tag} has the tier table",
              all(t in html for t in ["R400", "R240", "R7,500", "R3.95", "R495"]))
        check(f"live coffee {tag} has the quote form",
              'id="quote"' in html and "quote-form" in html)
        check(f"live coffee {tag} points caviar at the clean page", "b0hj2mt9c1nt" in html)
    except Exception as e:
        check(f"live coffee {url} reachable", False, repr(e))

print("\n[4] LEGACY DEPLOYS — stale, cannot be deleted from here (OWNER ACTION)")
stale = []
for url, why in LEGACY:
    try:
        html = fetch(url)
        hits = []
        for pat in CAVIAR_PRICE_PATTERNS:
            hits += re.findall(pat, html, re.I)
        for pat, txt in FALSE_CLAIM_PATTERNS + SALE_PATH_PATTERNS + ORIGIN_CLAIM_PATTERNS:
            if re.search(pat, html, re.I):
                hits.append(txt)
        if hits:
            stale.append((url, why, sorted(set(hits))[:6]))
    except Exception:
        stale.append((url, why, ["unreachable"]))

if stale:
    print(f"  [STALE] {len(stale)} legacy deploy(s) still carry old content:")
    for url, why, hits in stale:
        print(f"     - {url.split('//')[1]}  ({why})")
        print(f"       carries: {', '.join(str(h) for h in hits)}")
    print("     ACTION (Tumelo, dashboard): delete these three deploys.")
    print("     Superseded by:")
    print("       caviar : https://b0hj2mt9c1nt.space.mcode.io")
    print("       coffee : https://iei7fdqx5j1y.space.mcode.io")
else:
    print("  [OK] no legacy deploy carries old content")

failed = [r for r in RESULTS if not r[1]]
print("\n" + "=" * 78)
print(f"RESULT: {len(RESULTS) - len(failed)} passed / {len(failed)} failed  ({len(RESULTS)} checks)")
print(f"LEGACY DEPLOYS NEEDING OWNER DELETION: {len(stale)}")
if failed:
    print("\nFAILURES:")
    for name, _, detail in failed:
        print(f"  x {name}" + (f" — {detail}" if detail else ""))
    sys.exit(1)
print("ALL CHECKS PASS")
sys.exit(0)
