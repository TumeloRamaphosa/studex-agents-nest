#!/usr/bin/env python3
"""Final context: product descriptions from the retail owner page, and a
registry-violation scan of the OTHER Facebook posters."""
import re, os

src = open("/workspace/studex-biltong/index.html").read()
print("=== context: product blocks ===")
for kw in ("Fire &amp; Feast Box", "Luxury Wagyu Biltong", "Wagyu Biltong Gold — 1kg",
           "Oscietra Imperial", "Kaluga Prestige"):
    i = src.find(kw)
    if i == -1:
        print(f"  [{kw}] NOT FOUND")
        continue
    seg = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", src[i:i + 700])).strip()
    print(f"  [{kw}]\n     {seg[:320]}")

print()
print("=== other facebook posters: registry-violation scan ===")
FORBIDDEN = [
    ("R320", "not a registry price (Classic Beef Biltong)"),
    ("R1,850", "not a registry price (MS5+ ribeye)"),
    ("R2,400", "retired/never-registered caviar price"),
    ("R280", "FORBIDDEN string in registry 4g"),
    ("R480", "not a registry price (game biltong)"),
    ("R3,200", "not a registry price (Experience Box)"),
    ("Oscietra Golden", "retired caviar name"),
    ("Sevruga", "retired caviar name"),
    ("Kaluga Hybrid", "wrong caviar tier"),
    ("MS5+", "unregistered Wagyu grade claim"),
    ("Wildebeest", "unsourced game species claim"),
    ("Kudu", "unsourced game species claim"),
    ("Springbok", "unsourced game species claim"),
    ("per 250g", "wrong caviar unit"),
    ("250g", "wrong caviar unit"),
    ("Rainforest Alliance", "unsourced certification"),
    ("PROWTC", "prospect brand, not ours"),
    ("booth", "unverified CIIE booth claim"),
    ("Halaal", "halal scope claim"),
    ("certified", "unsourced certification claim"),
    ("Organic", "unsourced certification claim"),
    ("Experience Box", "not a registry product"),
    ("Game Biltong", "not a registry product"),
]
files = ["scripts/meta-check.py", "scripts/morning-check.py",
         "workflows/blotato-content-pipeline.js"]
for f in files:
    p = os.path.join("/workspace", f)
    if not os.path.exists(p):
        print(f"  {f}: MISSING")
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    hits = []
    for tok, why in FORBIDDEN:
        for m in re.finditer(re.escape(tok), t, re.I):
            ln = t[:m.start()].count("\n") + 1
            hits.append((ln, tok, why))
    print(f"  {f}: {len(hits)} hit(s)")
    for ln, tok, why in sorted(hits)[:12]:
        print(f"     line {ln}: {tok!r} — {why}")
    # does it actually post?
    if "graph.facebook.com" in t:
        for m in re.finditer(r".{0,90}graph\.facebook\.com.{0,90}", t):
            print("     POSTS:", re.sub(r"\s+", " ", m.group(0))[:170])
