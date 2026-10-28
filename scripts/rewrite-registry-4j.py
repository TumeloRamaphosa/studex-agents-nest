#!/usr/bin/env python3
"""Rewrite registry §4j in the format ops/build-manifest.py actually parses,
so the drift checker enforces real must/must_not assertions on the public desk."""
import sys

P = 'studex-meat/PRICE-SOURCE-REGISTRY.md'
s = open(P, encoding='utf-8').read()

old_pm = "| **Price reference (React)** — added 2026-10-24 | `studex-price-desk/dist/` | `jisom3k4i126.space.mcode.io` |"
new_pm = "| Price reference (React) | `studex-price-desk/dist/` | `jisom3k4i126.space.mcode.io` |"
if s.count(old_pm) == 1:
    s = s.replace(old_pm, new_pm)
    print("  OK page-map name")
else:
    print(f"  SKIP page-map name (count={s.count(old_pm)})")

start = s.index("## 4j. PRICE REFERENCE DESK")
end = s.index("## 5. OPEN ITEMS FOR OWNER CONFIRMATION")

new_section = """## 4j. PRICE REFERENCE DESK — live market & published prices (added 2026-10-24, Build Hour)
> Source: `studex-price-desk/` · Live URL: `jisom3k4i126.space.mcode.io` · Built from `research/2026-10-24-price-reality-check.md`.
>
> 🔒 **This page is public, so it publishes MARKET DATA and ALREADY-PUBLISHED prices only.** It does **not** publish our cost model, landed cost, margin floor, wholesale trade price, or recommended quote band. The internal build (`studex-price-desk/dist-internal/`) carries those and is **not deployed** — it needs auth and a decision. See `studex-meat/CAVIAR-TRADE-DESK-EXPOSURE-FINDING-2026-10-24.md`.
>
> 🔑 A permanent gate now exists: `studex-price-desk/scripts/audit-bundle.mjs` greps the public bundle for 29 internal identifiers and the old internal numbers (18.5, 23042, 32917, 34000, …) and **fails the build** if any is present. It also asserts the internal bundle still carries the cost model.

### Must appear on the price reference desk

| Published reference | Value | Must appear on |
|---|---|---|
| Best of Rwanda 2026 top lot, micro-lot Geisha (K-Organics, Huye) | `Best of Rwanda` | `jisom3k4i126` |
| SA Coffee Price Index Q3 2026 | `SA Coffee Price Index` | `jisom3k4i126` |
| ICE Arabica C live benchmark | `ICE Arabica` | `jisom3k4i126` |
| Published caviar SKU — Oscietra Imperial | `Oscietra` | `jisom3k4i126` |
| Published caviar SKU — Kaluga Prestige | `Kaluga` | `jisom3k4i126` |
| Published caviar SKU — Sevtruga Medium | `Sevtruga` | `jisom3k4i126` |
| CNY rate, for CIIE quoting | `USD/CNY` | `jisom3k4i126` |

### Must NOT appear on the price reference desk

| Forbidden internal string | Why | Must not appear on |
|---|---|---|
| `farmGateUsdPerKg` | farm-gate cost — hands a buyer our cost | `jisom3k4i126` |
| `landedZarPerKg` | landed cost | `jisom3k4i126` |
| `floorZarPerKg` | our minimum viable price — the buyer negotiates to exactly this | `jisom3k4i126` |
| `belowFloor` | margin verdict | `jisom3k4i126` |
| `marginPct` | our margin | `jisom3k4i126` |
| `SPECIALTY_DISCOUNT` | our quote band | `jisom3k4i126` |
| `fxImpact` | FX model | `jisom3k4i126` |
| `18.5` | the old hardcoded FX assumption — internal cost model | `jisom3k4i126` |
| `23042` | Oscietra landed cost at the old FX | `jisom3k4i126` |
| `32917` | Oscietra floor at the old FX | `jisom3k4i126` |
| `34000` | Oscietra wholesale trade price | `jisom3k4i126` |
| `22000` | Kaluga wholesale trade price | `jisom3k4i126` |
| `12500` | Sevtruga wholesale trade price | `jisom3k4i126` |
| `R29,535` | Oscietra floor at live FX | `jisom3k4i126` |
| `R20,674` | Oscietra landed cost at live FX | `jisom3k4i126` |
| `R34,000` | Oscietra wholesale trade price | `jisom3k4i126` |
| `farm gate` | farm-gate cost in prose | `jisom3k4i126` |
| `landed cost` | landed cost in prose | `jisom3k4i126` |
| `margin floor` | our minimum viable price in prose | `jisom3k4i126` |

> 🔒 The "must not" list is the durable half of this registration. If a future build puts any of
> these on the public page, the drift checker reports it as DRIFT — the same mechanism that caught
> the unsourced Rainforest Alliance claim on the China page.

### Open items this page is waiting on

- **Kigali partner:** is $4.80/kg still current, and does the A1 lot carry a premium over the ICE composite? Decides whether the sheet price is a genuine discount or a stale number.
- **Clearing agent:** HS classification (1604.31 vs 1604.14.10) and whether import VAT is claimable. Decides every caviar floor.

---

"""

s = s[:start] + new_section + s[end:]
open(P, 'w', encoding='utf-8').write(s)
print("  OK §4j rewritten in generator-parseable format")
