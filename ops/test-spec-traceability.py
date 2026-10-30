#!/usr/bin/env python3
"""Test ops/check-spec-traceability.py.

THE DEFECT UNDER TEST (2026-10-30): the content catalog's tagline said "Marbling
grade 5 Wagyu" for the Wagyu Ribeye while the owning source
(`studex-products-catalog.csv`) says "marble scores 8+ to 11+". The caption machine
copied it faithfully and published it (Threads 8633885, IG 8634450).

🔑 WHY THE NEGATIVE CONTROLS ARE THE POINT
A traceability checker can fail in three ways, and only one of them is the defect:
  1. it does not catch the unsourced claim  -> the defect survives
  2. it catches claims that ARE sourced   -> it eats real captions, the feed goes
     silent, and a missing post is a revenue loss
  3. it matches the wrong product         -> a claim about the auction lot's
     "Marble Score 7/8" is waved through for the ribeye
Case 3 is the subtle one: the owning source legitimately contains "5" ("All 5-7
marble score", Wagyu Black Box) and "7" ("Marble Score 7/8", auction lot), so a
corpus-wide check would pass "grade 5" for a product that says 8+ to 11+.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "ops" / "check-spec-traceability.py"
LIVE_CATALOG = REPO / "studex-content-automation" / "products" / "catalog.json"
FAILS = []


def check(label, cond, detail=""):
    if cond:
        print("PASS  %s" % label)
    else:
        print("FAIL  %s %s" % (label, detail))
        FAILS.append(label)


def run(catalog, extra=()):
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "catalog.json"
        p.write_text(json.dumps(catalog), encoding="utf8")
        r = subprocess.run(
            [sys.executable, str(CHECKER), "--catalog", str(p)] + list(extra),
            capture_output=True, text=True, cwd=str(REPO))
        return r.returncode, (r.stdout or "") + (r.stderr or "")


def cat(products):
    return {"products": products}


RIBEYE = {"id": "wagyu-ribeye", "name": "Wagyu Ribeye Steak",
          "available": True,
          "tagline": "Marbling grade 5 Wagyu",
          "description": "Our Wagyu ribeye - the deepest marbling in the range. "
                         "Available as a 500g steak at R950 and a 1kg at R1,950."}
RIBEYE_FIXED = dict(RIBEYE, tagline="Marble scores 8+ to 11+")
CAVIAR = {"id": "caviar-oscietra", "name": "Oscietra Imperial Caviar",
          "available": False, "tagline": "The aristocrat of the sea",
          "description": "Oscietra Imperial caviar - the richest tier we carry."}

print("=== A. THE REAL DEFECT - AN UNSOURCED GRADE CLAIM ===")
rc, out = run(cat([RIBEYE]))
check("an unsourced 'marbling grade 5' is a finding", rc == 1, "rc=%d out=%s" % (rc, out[-400:]))
check("the finding names the claim", "marbling grade 5" in out.lower(), out[-400:])
check("the finding names the unsupported number", "5 not supported" in out, out[-400:])
check("the finding names the owning source's truth", "8" in out, out[-400:])

print("\n=== B. NEGATIVE CONTROL - THE CHECK IS NOT VACUOUS ===")
check("section A proved a red result exists (rc==1)", rc == 1, "rc=%d" % rc)
rc_clean, out_clean = run(cat([RIBEYE_FIXED]))
check("the SAME checker passes the sourced claim", rc_clean == 0,
      "rc=%d out=%s" % (rc_clean, out_clean[-400:]))
check("so the difference is the claim, not the checker", rc == 1 and rc_clean == 0,
      "rc=%d vs %d" % (rc, rc_clean))

print("\n=== C. NO FALSE POSITIVE ON SIZE AND PRICE TEXT ===")
check("a description with 500g / R950 / 1kg / R1,950 is clean", rc_clean == 0,
      "rc=%d out=%s" % (rc_clean, out_clean[-400:]))
plain = dict(RIBEYE_FIXED, tagline="Premium Wagyu Ribeye Steak",
             description="Rich, buttery, melt-in-your-mouth. Available as a 500g "
                         "steak at R950 and a 1kg at R1,950.")
rc_plain, out_plain = run(cat([plain]))
check("a product with no quality claim at all is clean", rc_plain == 0,
      "rc=%d out=%s" % (rc_plain, out_plain[-400:]))

print("\n=== D. THE CHECK IS PER-PRODUCT, NOT CORPUS-WIDE ===")
wrong_score = dict(RIBEYE_FIXED, tagline="Marble score 7/8")
rc_wrong, out_wrong = run(cat([wrong_score]))
check("the ribeye cannot claim the auction lot's score 7", rc_wrong == 1,
      "rc=%d out=%s" % (rc_wrong, out_wrong[-400:]))
check("the finding says which number is unsupported", "not supported" in out_wrong,
      out_wrong[-400:])

print("\n=== E. UNAVAILABLE PRODUCTS ARE SKIPPED (caviar has no owning row) ===")
rc_cav, out_cav = run(cat([CAVIAR]))
check("an unavailable product with no owning row is not a finding", rc_cav == 0,
      "rc=%d out=%s" % (rc_cav, out_cav[-400:]))
check("the checker says it skipped it", "skipped" in out_cav, out_cav[-400:])

print("\n=== F. A PUBLISHABLE PRODUCT WITH NO OWNING ROW IS A FINDING ===")
orphan = {"id": "invented-product", "name": "Zebra Salted Caramel Truffle",
          "available": True, "tagline": "Grade 5 indulgence",
          "description": "The good stuff."}
rc_orph, out_orph = run(cat([orphan]))
check("a publishable product with no owning row is a finding", rc_orph == 1,
      "rc=%d out=%s" % (rc_orph, out_orph[-400:]))
check("the finding says its claims cannot be traced", "cannot be traced" in out_orph,
      out_orph[-400:])

print("\n=== G. THE LIVE CATALOG MUST PASS (the fix is in place) ===")
r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True,
                   cwd=str(REPO))
live_out = (r.stdout or "") + (r.stderr or "")
check("the live content catalog has no unsourced quality claim", r.returncode == 0,
      "rc=%d out=%s" % (r.returncode, live_out[-500:]))
live = json.loads(LIVE_CATALOG.read_text(encoding="utf8"))
rib = [p for p in live["products"] if p["id"] == "wagyu-ribeye"]
check("the ribeye tagline no longer says 'grade 5'",
      rib and "grade 5" not in (rib[0].get("tagline") or "").lower(),
      str(rib[0].get("tagline")) if rib else "-")
check("the ribeye tagline carries the sourced scores",
      rib and "8" in (rib[0].get("tagline") or "") and "11" in (rib[0].get("tagline") or ""),
      str(rib[0].get("tagline")) if rib else "-")
check("the owning source really says 8+ to 11+",
      "marble scores 8+ to 11+" in (REPO / "studex-products-catalog.csv").read_text(encoding="utf8"),
      "owning source text changed")

print("\n=== H. THE OWNING SOURCE IS THE ONE WE THINK IT IS ===")
own = (REPO / "studex-products-catalog.csv").read_text(encoding="utf8")
check("the owning source contains 'marble scores 8+ to 11+'",
      "marble scores 8+ to 11+" in own)
check("the owning source also contains other grades (5-7, 7/8) - which is why a "
      "corpus-wide check would be wrong",
      "5-7 marble score" in own and "7/8" in own)

print("")
if FAILS:
    print("%d CHECK(S) FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("ALL CHECKS PASS")
