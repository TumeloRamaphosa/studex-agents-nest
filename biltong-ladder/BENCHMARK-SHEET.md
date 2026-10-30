# 📊 Studex Biltong — Benchmark Sheet

**The input sheet.** Hand-maintained. The ladder is computed from this by
`compute-ladder.mjs` → `LADDER.md`.

| | |
|---|---|
| **Owner** | `biltong-ladder/compute-ladder.mjs` |
| **Last reviewed** | 2026-10-30 (Build Hour) |
| **Next review** | when any raw beef invoice lands — that is the trigger |
| **Rule** | every row carries a source and a date. A benchmark without both is not a benchmark. |

---

## 1. HOW TO USE THIS SHEET

Two questions, two jobs:

1. **Can we price this product in South Africa?** → compare our per-kg price against §3 (SA).
2. **Can we price this product for export?** → compare against §4 (US DTC).

The cost model is in `inputs.mjs`. The benchmarks here do **not** feed the
cost model — they tell you where the price can land, and whether the cost
model is even in the right universe.

> 🔑 **If the SA benchmarks imply a raw beef cost far below our invoice, the product is not an SA retail product.** That is not a failure of the product; it is a signal that it belongs in the export band, or in a different format. Act on the signal.

---

## 2. THE TWO LIVE LADDERS (what we are comparing against)

| Ladder | 500g | Luxury 1kg | Gold 1kg | 7kg case | Source |
|---|---:|---:|---:|---:|---|
| **Shopify live store** | R450 | R650 | R1,450 | R12,500 | products.json variants, verified 28 Oct 2026; re-confirmed 30 Oct on studexmeat.com/products/wagyu-biltong (sale R650.00, regular R812.50) |
| **Marketing page + registry §2.1** | R325 "From" | — | R1,250 | R8,400 | studex-biltong/index.html product grid, re-read 30 Oct; matches studex-meat/PRICE-SOURCE-REGISTRY.md §2.1 |

**Known defects, both live right now:**

- Shopify: the 500g costs **R250 more per kg** than the 1kg (R900 vs R650).
- Shopify: the 7kg case costs **R2,350 more** than 7 × 1kg (+23.2% per kg). You pay more for bulk.
- Marketing: the Luxury card says **"From R325" and states no size at all** — an unquotable price.

---

## 3. SOUTH AFRICA — 8 benchmarks

| # | Benchmark | Pack | Price | Per kg | Date | Source | What it tells us |
|---|---|---|---:|---:|---|---|---|
| 1 | **Woolworths — Free Range Chilli Beef Biltong Snapsticks** | 150g | R157.99 | **R1,053.27** | Oct 2026 | woolworths.co.za; the per-kg figure was calculated by Newsday, Jul 2026 | 🔑 **The ceiling of the SA market.** Nothing in SA retail sells biltong above this. It is chilli-and-snack positioning, not a grade. |
| 2 | Woolworths — Free Range Sliced Beef Biltong | 400g | R279.99 | R699.98 | Oct 2026 | woolworths.co.za | The mainstream SA tier. A premium brand must beat this to justify itself. |
| 3 | Woolworths — Sliced Beef Biltong (gifting range) | 400g | R219.99 | R549.98 | Oct 2026 | woolworths.co.za gifting range | Same pack size, different cut/range. Shows how much the range, not the weight, moves the price. |
| 4 | Woolworths — Bulk Original Beef Biltong Snapsticks | 500g | R219.99 | R439.98 | Oct 2026 | woolworths.co.za product A-6009195240318 | The value end. Below this, no SA buyer is interested. |
| 5 | Woolworths — Free Range Sliced Beef Biltong | 5 × 25g (125g) | R109.99 | R879.92 | Oct 2026 | woolworths.co.za | **Small-pack premium benchmark: +26% per kg against the 400g.** Our policy caps the 500g premium at 15%, tighter than Woolworths, because our buyer is comparing spec sheets. |
| 6 | Checkers — Kalahari Biltong Moist Sliced Beef | per kg | R429.99 | R429.99 | Oct 2026 | checkers.co.za product 10155402KG | Mass-retail comparator. |
| 7 | Shoprite — Kalahari Bulk Biltong | per kg | R129.99 | R129.99 | Oct 2026 | shoprite.co.za | **The floor of the SA market.** If our price cannot beat this on merit, there is no SA case at all. |
| 8 | **Biltong Boytjies — Wagyu Biltong / Wagyu Drywors** | per kg | R549.99 | R549.99 | Apr 2026 | biltongboytjies.co.za blog, Apr 2026 — "Most Biltong Shops will sell fresh Wagyu biltong or Wagyu drywors for R499.99-R599.99 Per KG" | 🔑 **The single most important row on this sheet.** It is the only SA benchmark that uses the word *Wagyu*, which is our word. This is the price we are actually compared against, and it is **less than half** the Woolworths chilli-snack per kg. |

### The two raw-beef anchors hiding in the SA data

| Anchor | Value | Source | Use |
|---|---|---|---|
| Retail bulk silverside | **R130–150/kg** | r/southafrica, Jul 2026 — "Retail bulk silverside is currently R130-150/kg" | The standard-beef cost assumption (we take the R140 midpoint) |
| Implied cost at R599/kg retail | **~R200/kg** | r/southafrica, Jul 2026 — "at R599/kg that is based on a raw beef price of around R200/kg" | Independent cross-check: if the market's best wagyu-sold product implies ~R200/kg raw, our R320 wagyu assumption is 60% above the market's implied input cost |

---

## 4. UNITED STATES — 4 direct-to-consumer benchmarks

| # | Benchmark | Pack | Price | Per kg | Date | Source |
|---|---|---|---:|---:|---|---|
| 9 | Biltong Depot — Original Biltong with Fat (slab subscription) | 1 lb | $35.99 | R1,316 | Oct 2026 | biltongdepot.com |
| 10 | BeefSnacksUSA — Monthly Biltong | 1 lb | $33.00 | R1,208 | Oct 2026 | beefsnacksusa.com — subscribe and save 10% |
| 11 | Lowfeld Soul Food — Beef Biltong Slices | 1 lb | $33.99 | R1,245 | Oct 2026 | lowfeld-soul-food.com |
| 12 | The Grub Company — Bulk Biltong | 1 lb | $58.00 | R2,124 | Oct 2026 | thegrubcompany.com blog, Jul 2026 |

*Per kg converted at USD/ZAR 16.64 (frankfurter.dev, ECB reference, 29 Oct 2026) and 1 lb = 0.4536 kg.*

**Export band: R1,208 – R2,124/kg.** This is where a premium price actually lives. The gap between the SA ceiling (R1,053/kg) and the US DTC floor (R1,208/kg) is only **15%** — which is why "just export it" is not automatically the answer, and why the export channel has to be chosen deliberately rather than assumed.

---

## 5. HOW TO UPDATE THIS SHEET

1. Change the price in `inputs.mjs` → `SA_BENCHMARKS` / `US_BENCHMARKS`.
2. `node biltong-ladder/compute-ladder.mjs`
3. Read the new `LADDER.md`.
4. If the **raw beef cost** in `COST_INPUTS.rawBeefRarPerKg` changed, update that too — it is the input that moves everything.

**Never hand-edit `LADDER.md` or `ladder.generated.json`.** They are generated. A hand-edited generated file is a file that lies to the next person who trusts it.

---

## 6. OPEN ITEMS

| Item | Status | Owner |
|---|---|---|
| Raw beef invoice — actual cost per kg, trimmed, delivered | 🔴 **THE blocking input. Nothing in this sheet is final without it.** | Tumelo |
| Is the "Wagyu" grade claim on the SKU supported by a certificate, or is it a range name? | 🟡 Unverified — and it drives the R1,450 vs R650 brand architecture | Tumelo |
| Waste/yield — actual kg finished per kg raw, measured not assumed | 🟡 ASSUMPTION at 0.35 | Production |
| Packaging quotes — 70g pouch, 1kg valve bag, 100-pack bulk liner | 🟡 ASSUMPTION at R4.20 / R14 / R60 per kg | Production |
| Does the 7kg case ship as 100 × 70g or as bulk liners? | 🟡 Changes the case cost per kg by R32 | Production |
| Frozen vs ambient dispatch cost per kg | 🟡 ASSUMPTION at R22 | Logistics |
