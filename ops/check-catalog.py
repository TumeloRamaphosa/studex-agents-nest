#!/usr/bin/env python3
"""Confirm Perplexity works with a valid max_tokens, and audit the content
agent's product catalog against the registry (it publishes to Facebook)."""
import json, subprocess, os, re, sys

# 🔑 The response travels on STDOUT, not through a file. A fixed -o path
# that a failed curl leaves untouched made a failed probe print a STALE body
# from a previous run - see ops/http_probe.py for the proof and the fix.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http_probe import probe_json, format_line

env = {}
for line in open("/workspace/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

PPLX = env.get("PERPLEXITY_API_KEY", "")

print("=== perplexity with valid max_tokens ===")
_res = probe_json("perplexity", "https://api.perplexity.ai/chat/completions",
                  ["Authorization: Bearer " + PPLX],
                  '{"model":"sonar","messages":[{"role":"user","content":"Reply with the single word: ok"}],"max_tokens":16}')
print(format_line(_res, width=12))

print("=== content agent product catalog vs registry ===")
cat = json.load(open("/workspace/studex-content-automation/products/catalog.json"))
reg = open("/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md").read()

# 🔑 COMPARE ON THE NUMERIC PRICE, NOT ON THE PRICE STRING.
# The old check was `price in reg` - a literal substring test of the whole
# price string. That is format-dependent and produced BOTH kinds of wrong:
#   * FALSE NEGATIVES - "R4,200 per 100g" and "R400/kg" are registry prices
#     written with a unit suffix, so the substring did not match even
#     though the price IS owned. Two of the six products were wrongly
#     reported as unregistered.
#   * It could not see a product whose price is simply ABSENT from the
#     registry, because the absence is exactly what a substring test
#     cannot distinguish from a formatting difference.
# The numeric amount is the authoritative, format-independent unit: the
# registry writes R1,450 and R1450.20 the same way it writes "R1,450 per
# 100g" - the amount is what must be owned.
_rx = re.compile(r"R\s?([0-9][0-9,]*)")
reg_prices = set()
for m in _rx.finditer(reg):
    try:
        reg_prices.add(int(m.group(1).replace(",", "")))
    except ValueError:
        pass
print("  registry numeric prices: %d distinct (e.g. %s)"
      % (len(reg_prices), ", ".join("R%d" % p for p in sorted(reg_prices)[:10])))

items = cat if isinstance(cat, list) else cat.get("products", cat)
unowned = 0
for it in (items if isinstance(items, list) else items.values()):
    name = it.get("name", "?")
    price = str(it.get("price", ""))
    raw = it.get("price_raw")
    allowed = [p for p in (it.get("allowed_prices") or []) if p is not None]
    # The headline price is the one the caption quotes.
    checks = [("price_raw", raw)] if raw is not None else []
    checks += [("allowed", a) for a in allowed if a != raw]
    missing = [(kind, v) for kind, v in checks if int(v) not in reg_prices]
    ok = not missing
    if not ok:
        unowned += 1
    print("  %-34s %-14s in-registry=%s%s"
          % (name[:34], price[:14], "yes" if ok else "NO",
             "" if ok else "  unowned: " + ", ".join(
                 "%s=%s" % (k, v) for k, v in missing)))
print()
print("  products with an UNREGISTERED price: %d" % unowned)
print("VERDICT: %s" % ("UNOWNED PRICE" if unowned else "CLEAN"))
