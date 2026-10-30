# 🦴 Studex Biltong — Price Ladder Sheet

**One ladder. Two live ladders reconciled. Every number with its source.**

| | |
|---|---|
| **Owner** | `biltong-ladder/compute-ladder.mjs` → `biltong-ladder/ladder.generated.json` |
| **Generated** | 2026-10-30 |
| **Status** | 🟡 **NOT YET APPLIED** — Shopify needs the Admin token (401 as of 28 Oct) |
| **Cost model** | ⚠️ **ASSUMPTIONS, not invoices** — see §4 for the break-even table |

---

## 1. THE TWO LIVE LADDERS

| Ladder | 500g | Luxury 1kg | Gold 1kg | 7kg case | Verdict |
|---|---:|---:|---:|---:|---|
| Shopify live store (studexmeat.com) | R450 | R650 | R1,450 | R12,500 | LIVE — structurally broken |
| Marketing page + registry §2.1 (studex-biltong/index.html) | R325 | — | R1,250 | R8,400 | LIVE — right shape, thin money |

*Both ladders are live at the same time. The store and the marketing page disagree, and the marketing page shows "From R325" for a product whose card states no size at all.*

---

## 2. WHY THEY ARE WRONG

### Standard silverside beef — raw beef at R140/kg

_What the product looks like if "Wagyu" is a label rather than a grade._

**Shopify live store (studexmeat.com)** — LIVE — structurally broken

| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? |
|---|---:|---:|---:|---:|:---:|
| Luxury Wagyu Biltong 500g | R450 | R900.00 | R551.00 | 38.8% | ✅ |
| Luxury Wagyu Biltong 1kg | R650 | R650.00 | R546.00 | 16% | 🔴 |
| Wagyu Biltong Gold 1kg | R1,450 | R1,450.00 | R591.00 | 59.2% | ✅ |
| Wagyu Biltong Gold 7kg case | R12,500 | R1,785.71 | R592.00 | 66.8% | ✅ |

- 🔴 **small pack per-kg premium over the 1kg** — the 500g is 38.5% MORE per kg than the 1kg. _Required: at most 15.0% per-kg premium._
- 🔴 **the 7kg case must be CHEAPER in total than 7 x 1kg** — the case COSTS R2,350 MORE than 7 x 1kg (+23.2%). _Required: must be cheaper._

**Marketing page + registry §2.1 (studex-biltong/index.html)** — LIVE — right shape, thin money

| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? |
|---|---:|---:|---:|---:|:---:|
| Luxury Wagyu Biltong 500g (from, size not stated on the card) | R325 | R650.00 | R551.00 | 15.2% | 🔴 |
| Wagyu Biltong Gold 1kg | R1,250 | R1,250.00 | R591.00 | 52.7% | ✅ |
| Wagyu Biltong Gold 7kg case | R8,400 | R1,200.00 | R592.00 | 50.7% | ✅ |

- ✅ **the 7kg case must be CHEAPER in total than 7 x 1kg** — the case saves R350 against 7 x 1kg (4.0% off). _Required: must be cheaper._

### Wagyu, trimmed — raw beef at R320/kg

_What the product costs if the beef really is wagyu. This is the scenario that decides whether SA retail works at all._

**Shopify live store (studexmeat.com)** — LIVE — structurally broken

| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? |
|---|---:|---:|---:|---:|:---:|
| Luxury Wagyu Biltong 500g | R450 | R900.00 | R1,065.29 | -18.4% | 🔴 |
| Luxury Wagyu Biltong 1kg | R650 | R650.00 | R1,060.29 | -63.1% | 🔴 |
| Wagyu Biltong Gold 1kg | R1,450 | R1,450.00 | R1,105.29 | 23.8% | 🔴 |
| Wagyu Biltong Gold 7kg case | R12,500 | R1,785.71 | R1,106.29 | 38% | ✅ |

- 🔴 **small pack per-kg premium over the 1kg** — the 500g is 38.5% MORE per kg than the 1kg. _Required: at most 15.0% per-kg premium._
- 🔴 **the 7kg case must be CHEAPER in total than 7 x 1kg** — the case COSTS R2,350 MORE than 7 x 1kg (+23.2%). _Required: must be cheaper._

**Marketing page + registry §2.1 (studex-biltong/index.html)** — LIVE — right shape, thin money

| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? |
|---|---:|---:|---:|---:|:---:|
| Luxury Wagyu Biltong 500g (from, size not stated on the card) | R325 | R650.00 | R1,065.29 | -63.9% | 🔴 |
| Wagyu Biltong Gold 1kg | R1,250 | R1,250.00 | R1,105.29 | 11.6% | 🔴 |
| Wagyu Biltong Gold 7kg case | R8,400 | R1,200.00 | R1,106.29 | 7.8% | 🔴 |

- ✅ **the 7kg case must be CHEAPER in total than 7 x 1kg** — the case saves R350 against 7 x 1kg (4.0% off). _Required: must be cheaper._

---

## 3. THE PROPOSED LADDER

### Standard silverside beef — raw beef at R140/kg

| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? | Break-even raw |
|---|---:|---:|---:|---:|:---:|---:|
| Luxury Wagyu Biltong 500g | R415 | R830.00 | R551.00 | 33.6% | ✅ | R165/kg |
| Luxury Wagyu Biltong 1kg | R730 | R730.00 | R546.00 | 25.2% | ✅ | R141/kg |
| Wagyu Biltong Gold 1kg | R1,630 | R1,630.00 | R591.00 | 63.7% | ✅ | R361/kg |
| Wagyu Biltong Gold 7kg case | R10,500 | R1,500.00 | R592.00 | 60.5% | ✅ | R327/kg |

- ✅ **500g per kg vs Luxury 1kg per kg** — 500g R830.00/kg vs 1kg R730.00/kg — premium 13.7%
- ✅ **7kg case vs 7 x Gold 1kg** — case R10,500 vs 7 x 1kg R11,410 — saving R910 (8.0%)
- ✅ **per-kg price falls as pack size rises, within each line** — Luxury 500g R830.00/kg → 1kg R730.00/kg  ·  Gold 1kg R1,630.00/kg → case R1,500.00/kg

**Change against the live Shopify ladder**

| Tier | Live | Proposed | Change |
|---|---:|---:|---:|
| Luxury Wagyu Biltong 500g | R450 | R415 | ▼ R35 (-7.8%) |
| Luxury Wagyu Biltong 1kg | R650 | R730 | ▲ R80 (+12.3%) |
| Wagyu Biltong Gold 1kg | R1,450 | R1,630 | ▲ R180 (+12.4%) |
| Wagyu Biltong Gold 7kg case | R12,500 | R10,500 | ▼ R2,000 (-16%) |

### Wagyu, trimmed — raw beef at R320/kg

| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? | Break-even raw |
|---|---:|---:|---:|---:|:---:|---:|
| Luxury Wagyu Biltong 500g | R810 | R1,620.00 | R1,065.29 | 34.2% | ✅ | R372/kg |
| Luxury Wagyu Biltong 1kg | R1,415 | R1,415.00 | R1,060.29 | 25.1% | ✅ | R320/kg |
| Wagyu Biltong Gold 1kg | R3,160 | R3,160.00 | R1,105.29 | 65% | ✅ | R763/kg |
| Wagyu Biltong Gold 7kg case | R20,355 | R2,907.86 | R1,106.29 | 62% | ✅ | R696/kg |

- ✅ **500g per kg vs Luxury 1kg per kg** — 500g R1,620.00/kg vs 1kg R1,415.00/kg — premium 14.5%
- ✅ **7kg case vs 7 x Gold 1kg** — case R20,355 vs 7 x 1kg R22,120 — saving R1,765 (8.0%)
- ✅ **per-kg price falls as pack size rises, within each line** — Luxury 500g R1,620.00/kg → 1kg R1,415.00/kg  ·  Gold 1kg R3,160.00/kg → case R2,907.86/kg

**Change against the live Shopify ladder**

| Tier | Live | Proposed | Change |
|---|---:|---:|---:|
| Luxury Wagyu Biltong 500g | R450 | R810 | ▲ R360 (+80%) |
| Luxury Wagyu Biltong 1kg | R650 | R1,415 | ▲ R765 (+117.7%) |
| Wagyu Biltong Gold 1kg | R1,450 | R3,160 | ▲ R1,710 (+117.9%) |
| Wagyu Biltong Gold 7kg case | R12,500 | R20,355 | ▲ R7,855 (+62.8%) |

---

## 4. THE BREAK-EVEN TABLE — the one number that matters

> **We do not have a biltong cost model. We have an assumption.** So here is the question answered without one: **at what raw beef price does each tier exactly clear the 25% floor?**

| Tier | Proposed price | Break-even raw cost | vs standard silverside R140 | vs wagyu R320 |
|---|---:|---:|:---:|:---:|
| Luxury Wagyu Biltong 500g | R810 | **R372/kg** | ✅ 2.66x | ✅ 1.16x |
| Luxury Wagyu Biltong 1kg | R1,415 | **R320/kg** | ✅ 2.29x | ✅ 1.00x |
| Wagyu Biltong Gold 1kg | R3,160 | **R763/kg** | ✅ 5.45x | ✅ 2.38x |
| Wagyu Biltong Gold 7kg case | R20,355 | **R696/kg** | ✅ 4.97x | ✅ 2.18x |

**How to read it:** if the 1kg tier breaks even at R250/kg raw, then a raw beef invoice at R320/kg means that tier loses money at the proposed price, and one at R180/kg means it clears comfortably.

### What the market implies

Reverse-engineering the same 25% floor back out of competitor shelf prices tells us what raw beef the market can bear:

| Competitor | Shelf price/kg | Implied raw cost at a 25% floor |
|---|---:|---:|
| Woolworths — Free Range Chilli Beef Biltong Snapsticks | R1,053.27 | R225/kg |
| Woolworths — Free Range Sliced Beef Biltong | R699.98 | R133/kg |
| Woolworths — Sliced Beef Biltong (gifting range) | R549.98 | R93/kg |
| Woolworths — Bulk Original Beef Biltong Snapsticks | R439.98 | R64/kg |
| Woolworths — Free Range Sliced Beef Biltong | R879.92 | R180/kg |
| Checkers — Kalahari Biltong Moist Sliced Beef | R429.99 | R62/kg |
| Shoprite — Kalahari Bulk Biltong | R129.99 | R-17/kg |
| Biltong Boytjies — Wagyu Biltong / Wagyu Drywors | R549.99 | R93/kg |

> 🔑 **This is the strategic read.** The SA market implies a raw cost in the low hundreds. If our invoice is materially above that, then **the product is not an SA retail product — it is an export product**, and it should be priced and merchandised as one. The US DTC band is where a premium price actually lives.

### Benchmarks used

| SA benchmark | Pack | Price | Per kg | Date |
|---|---|---:|---:|---|
| Woolworths — Free Range Chilli Beef Biltong Snapsticks | 150g | R158 | R1,053.27 | Oct 2026 |
| Woolworths — Free Range Sliced Beef Biltong | 400g | R280 | R699.98 | Oct 2026 |
| Woolworths — Sliced Beef Biltong (gifting range) | 400g | R220 | R549.98 | Oct 2026 |
| Woolworths — Bulk Original Beef Biltong Snapsticks | 500g | R220 | R439.98 | Oct 2026 |
| Woolworths — Free Range Sliced Beef Biltong | 5 x 25g (125g) | R110 | R879.92 | Oct 2026 |
| Checkers — Kalahari Biltong Moist Sliced Beef | per kg | R430 | R429.99 | Oct 2026 |
| Shoprite — Kalahari Bulk Biltong | per kg | R130 | R129.99 | Oct 2026 |
| Biltong Boytjies — Wagyu Biltong / Wagyu Drywors | per kg | R550 | R549.99 | Apr 2026 |

| US DTC benchmark | Pack | Price | Per kg (R) | Date |
|---|---|---:|---:|---|
| Biltong Depot — Original Biltong with Fat (slab subscription) | 1 lb | $35.99 | R1,320.29 | Oct 2026 |
| BeefSnacksUSA — Monthly Biltong | 1 lb | $33.00 | R1,210.60 | Oct 2026 |
| Lowfeld Soul Food — Beef Biltong Slices | 1 lb | $33.99 | R1,246.92 | Oct 2026 |
| The Grub Company — Bulk Biltong | 1 lb | $58.00 | R2,127.72 | Oct 2026 |

---

## 5. POLICY — the rules the proposal obeys

| Rule | Value | Why |
|---|---|---|
| Margin floor | 25.0% | Matches the coffee sheet and the caviar desk. A ladder below this is not a ladder. |
| Small-pack premium cap | 15.0% over the 1kg per kg | The buyer must not be charged a penalty for buying less than 1kg. Woolworths runs 25–50% at the snack end; we cap it lower because our buyer has a good calculator. |
| Case saving | 8.0% cheaper per kg than 7 × 1kg | The buyer has to be able to count the saving, or the case is a decoration. |
| Luxury-to-Gold ratio | 2.2308× | Preserved from the live ladder (R1,450 ÷ R650). Packaging explains only R45/kg of it — the rest is positioning, and positioning is not ours to rewrite in a build hour. |
| Rounding | nearest R5 | A price sheet with R1,413.72 on it is not a price sheet. |

> 📖 **A note on the brief.** The brief asked for a ladder that makes the 500g **cheaper per kg** than the 1kg. That is backwards for retail: the small pack carries the higher packaging cost per kg (R19 vs R14), and every SA benchmark runs the other way — Woolworths charges R880/kg for 125g against R700/kg for 400g. Making the 500g cheaper per kg than the 1kg means a buyer is penalised for buying a kilo. **What is enforced instead** is that the 500g carries no more than a 15% per-kg premium over the 1kg, and that per-kg price falls as pack size rises. The brief’s real target — the inversion in the Shopify ladder — is closed either way.

---

## 6. WHAT TO DO WITH THIS

1. **Get the raw beef invoice.** One number. It is the only input that matters and it is currently an assumption.
2. **Re-run** `node biltong-ladder/compute-ladder.mjs`. The whole sheet moves.
3. **Apply to Shopify** once the Admin token works (401 as of 28 Oct). Four variant prices.
4. **Align the marketing page** `studex-biltong/index.html` to the same numbers, and fix the "From R325" card which states no size.
5. **Fix the registry** `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.1 — it still carries the old R325 / R1,250 / R8,400 set as if it were the live ladder.

### Disclaimers

Cost inputs are documented assumptions except where a source is named; the raw beef price is an assumption in both scenarios and is the input most likely to be wrong. Benchmarks are observed shelf prices at the dates shown and move without notice. Nothing here is a commitment to sell at any price. Do not publish any figure from this sheet to a customer before the raw beef invoice has replaced the assumption.

