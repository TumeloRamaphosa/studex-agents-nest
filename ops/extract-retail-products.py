#!/usr/bin/env python3
"""Extract the retail product list (name + price) from the OWNER source page
studex-biltong/index.html, and check what the registry says about game biltong."""
import re

src = open("/workspace/studex-biltong/index.html").read()

print("=== product cards: name + R-price, in document order ===")
# find any element that looks like a product name followed by an R price
pat = re.compile(r"(?:data-name|title=\")([^\"<>]{4,60})[^\n]{0,400}?R\s?([0-9][0-9,\.]{0,9})")
seen = set()
for m in pat.finditer(src):
    n, p = m.group(1).strip(), m.group(2)
    if (n, p) in seen:
        continue
    seen.add((n, p))
    print(f"  {n:44} R{p}")

print()
print("=== every R-price literal on the page (deduped, in order) ===")
prices = []
for m in re.finditer(r"R\s?([0-9][0-9,\.]{0,9})", src):
    v = m.group(1)
    if v not in prices:
        prices.append(v)
print(" ", prices)

print()
print("=== product-ish headings ===")
for m in re.finditer(r"<(?:h[1-4]|div class=\"[^\"]*name[^\"]*\")[^>]*>([^<]{4,70})<", src):
    t = m.group(1).strip()
    if t and not t.startswith("&") and len(t) > 3:
        print("  ", t)

print()
print("=== registry: game biltong / coffee retail product names ===")
reg = open("/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md").read()
for kw in ("game", "Game", "Premium Beef", "Classic", "Experience Box", "Fire & Feast"):
    for ln in reg.splitlines():
        if kw in ln:
            print(f"  [{kw}] {ln.strip()[:130]}")
            break
