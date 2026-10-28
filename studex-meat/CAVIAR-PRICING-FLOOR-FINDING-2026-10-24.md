# Caviar pricing floor — LIVE FINDING (2026-10-24)

**Status:** 🔴 two live customer-facing pages are publishing wholesale prices that are below our
own modelled margin floor, on all three SKUs. **No price has been changed.** This is a decision
input for Tumelo, not a fix.

## The finding

The caviar cost model was recomputed on **2026-10-23** (`research/2026-10-23.md`, TOPIC 1). It
produced a minimum viable trade price for each SKU. **Those numbers never reached the
publication source of truth**, so the pages still publish the old prices.

`studex-meat/PRICE-SOURCE-REGISTRY.md` §2.3 — the file that owns every published price —
records **"Last verified: 2026-10-21 21:40 UTC"**. The cost model was rebuilt **two days later**.
The registry is the drift alarm; it was never given the new numbers, so it could not alarm.

### Live verification, 2026-10-24 — both pages, current prices

| SKU | Landed ZAR/kg | **Published trade** | Markup on cost | **30% floor** | **Shortfall** |
|---|---|---|---|---|---|
| Oscietra Imperial | R26,363 | **R34,000/kg** | +29.0% | **R37,661/kg** | **−R3,661 (−9.7%)** |
| Kaluga Prestige | R18,704 | **R22,000/kg** | +17.6% | **R26,720/kg** | **−R4,720 (−17.7%)** |
| Sevtruga Medium | R11,045 | **R12,500/kg** | +13.2% | **R15,778/kg** | **−R3,278 (−20.8%)** |

*"Margin" here is markup on landed cost; floor = landed ÷ 0.70.*

**Where it is published right now:**
- `ess0ocgcd9f0.space.mcode.io` — caviar trade page: *"Trade (per kg) R34,000 / R22,000 / R12,500"*
- `nudsduvyrc12.space.mcode.io` — retail store: *"trade R34,000/kg · R22,000/kg · R12,500/kg"*

🔑 **Every trade quote a buyer takes off either page today is priced below our floor.** A 13%
markup cannot fund a CITES-bound 4–8 week supply chain plus cold-chain failure risk — the
research memo says so in one line: *"This is a pricing bug, not a market problem."*

## The two options (Tumelo's call)

**Option A — raise trade price to the floor.** `R34,000 → R37,661` · `R22,000 → R26,720` ·
`R12,500 → R15,778`. Closes the gap outright. Costs us competitiveness against Aquatir and the
local R2,000–3,000/100g Kaluga/Sevtruga band — Aquatir is farmed, local, and has no CITES clock.

**Option B — keep the price, accept the margin.** The volume case is the **5kg private-label
tier** (memo decision #4), and the way to protect margin at the table is the **R650–900 service
entry tier** (memo decision #3, *not yet built*, *not approved for publication*).

**My recommendation: Option A on Sevtruga and Kaluga, Option B on Oscietra.** Oscietra is the
halo and the trade buyers who want it are choosing provenance, not price. The two mid tiers are
where a buyer can switch to Aquatir in one message — that is where the floor bites. And per
memo decision #1, the premium tier should be **a clearly-labelled optional SKU, not the spine** —
which is exactly the shape of Option B for Oscietra.

**Whichever is chosen, the floor belongs in the registry** — as a visible reference row, exactly
as `research/2026-10-23.md` asked: *"add the IndexBox SA band as a visible reference row so the
R42,000/kg Oscietra retail price is a deliberate choice on the page, not an accident."* It was
never done.

## Three smaller things in the same file

1. **🟡 Naming inconsistency.** The cost model calls the third SKU **"Sevtruga Classic"**; both
   live pages call it **"Sevtruga Medium"**. The published name is the correct one (the retired
   names are "Sevruga Premium" and "Siberian Reserve"). The **cost sheet is the outlier** — fix
   the sheet, not the pages.
2. **🟡 Retail sits at/above the market band.** IndexBox SA premium retail is R8,000–35,000/kg.
   Oscietra at R42,000/kg is **above the top of it**; Kaluga at R28,000/kg is at the top. That
   is a defensible premium-brand position *only if it is a deliberate choice with the band shown
   next to it* — which is what the floor row would do.
3. **🟠 "Sevtruga Classic" is also the reason the R2,000–2,500/100g entry SKU was never built.**
   The memo wants a ~R2,000–2,500/100g entry SKU to pull the brand in. Today the cheapest thing
   on offer is R1,600/100g (Sevtruga, retail) and R12,500/kg (trade) — the entry point is not a
   product, it is an absence.

## What is already correct on the live pages (do not "fix" these)

- ✅ **No duty percentage is published** — *"Prices in ZAR, exclude import duty and delivery"* ·
  *"import duty and VAT quoted in the landed cost"*. Correct: the broker's HS classification
  answer is still outstanding and **must not be published** until it is in writing.
- ✅ **Lead time is separated correctly**: *"7–14 days' commercial handling from order
  confirmation, counted from the date the DAFF veterinary import permit is issued. For a first
  shipment the permit must be applied for at least 4 weeks ahead and takes 5–10 working days to
  issue once approved — allow roughly two months end to end."*
- ✅ **Origin is explicit** — *"Russia · Caspian Sea"*, *"Moscow → SA cold-chain"*, and an
  **Origin: Russia** column in the trade table. Decision #1's "not silence" is satisfied.
- ✅ Units are per 100g; the retired `per 250g` and `500g per tin` claims are gone.

## 6. 🔴🔴 THE FLOOR ITSELF IS BUILT ON TWO UNVERIFIED ASSUMPTIONS — **my earlier recommendation was premature**

I read `caviar-landed-cost.xlsx` → `Assumptions` in full this morning. The floor is derived from
six inputs, and two of them are assumptions nobody has verified:

| Assumption | Value in the sheet | Source status |
|---|---|---|
| Farm gate (Oscietra) | $1,000/kg | modelled from supplier quotes |
| Airfreight Moscow → SA | $10/kg | quoted |
| **Import duty rate** | **20%** | 🟡 **"ASSUMED — UNVERIFIED for 2026. Confirm with broker"** (the sheet's own words) |
| **VAT rate** | **15%** | 🟡 **treated as a cost — see below** |
| Brokerage + cold chain | $5/kg | quoted |
| CITES + permit fees | $15/kg | standing assumption |
| Last-mile refrigerated | R250/kg | quoted |
| USD/ZAR | 18.5 | 🔴 **a fixed rate, not a hedge** |

🔑 **Two of these move the floor more than anything the registry could publish.**

**A — Import VAT is normally recoverable, so it probably should not be in a price floor.** A
VAT-registered SA importer claims import VAT back and charges output VAT on the sale. Putting
15% VAT into landed cost treats recoverable tax as a cost. If import VAT comes out of the model:

> Oscietra landed = $1,230 × 18.5 + R250 = **R23,005** → floor **R32,900** (published R34,000)
> **→ the published trade price is ABOVE the floor. Oscietra is fine.**

**B — If ITAC Rebate 460.19 applies to us as a reseller, the duty line changes.** If duty went to
zero on Oscietra: landed = **R22,663** → floor **R32,400** → also **above** the published
R34,000. Kaluga's floor drops R26,800 → **R23,100** (published R22,000); Sevtruga's
R15,800 → **R13,700** (published R12,500). Still below, but the gap narrows from 21% to 15%.

**And the two files disagree on the HS line.** The sourcing memo §4 says **HS 1604.14.10 = 25% or
200c/kg**; the cost sheet models **20% on HS 1604.31/1604.32** — which is the line the research
brief asked the broker to confirm. Two different codes, two different duties, neither sourced.

### 🔑 The revised conclusion — do NOT reprice on this floor
My earlier recommendation in this file was *"raise trade to the floor"* (Option A). **I am
withdrawing it as premature.** The floor is a derived number resting on an unconfirmed duty rate,
a probably-recoverable VAT, and an unhedged FX rate. Repricing three live published prices
against it would be **correcting one error with another.**

**The right first move is the clearing-agent email** — not a price change. It answers the HS
line, the 2026 duty rate, the ITAC import-permit question, **and whether Rebate 460.19 applies to
us as a reseller**. One email, and it can move the floor on all three SKUs. It has been sitting in
`outbound-drafts/` unsent.

**Revised recommendation order:**
1. **Send the clearing-agent email.** (needs a named recipient + your approval)
2. **Correct the landed-cost model** — remove recoverable import VAT, replace the assumed duty
   rate with the broker's answer, and move FX off a hardcoded 18.5.
3. **Recompute the floor** with the corrected model.
4. **Only then** decide Option A vs Option B, and only then touch the registry.

**Option B (accept the margin) stays the safer default in the meantime** — and the pages are
currently quoting *below* floor, so every day this sits unresolved is a day we could be quoting
under cost. If you want a stop-gap before the broker answers, the cheapest safe move is to publish
the **floor as a visible reference row** on the caviar page — *"Trade (per kg) R34,000 — our
modelled minimum viable is R37,661"* — which tells buyers where the price is without changing it.

## 7. 🔴 The cost sheet's own "Recommended retail" formula would price the halo SKU outside the market

`Trade Pricing` column I computes *"Recommended retail (ZAR/kg)"* as
`CEILING(recommended_trade × 1.5, 100)`. Run on the current floors:

| SKU | Current retail | Sheet's recommended retail | vs current | Indexed SA premium band |
|---|---|---|---|---|
| Oscietra Imperial | R42,000/kg (R4,200/100g) | **R56,600/kg (R5,660/100g)** | **+35%** | R8,000–35,000/kg → **62% above the band ceiling** |
| Kaluga Prestige | R28,000/kg (R2,800/100g) | **R40,200/kg (R4,020/100g)** | **+44%** | R8,000–35,000/kg → **above band top** |
| Sevtruga Medium | R16,000/kg (R1,600/100g) | **R23,700/kg (R2,370/100g)** | +48% | R2,000–6,000/100g → **inside** |

🔑 **Two of three land above the top of the indexed SA premium band**, in a market where the
competitor (Aquatir) is farmed, local and cheaper. The formula is arithmetically fine and
**commercially wrong**: it treats "recommended trade" as a base for a retail price, which is not
what a 1.5× markup means in a market that already caps at R3,500/100g.

Nothing is published from this sheet, so nothing is broken. **It is a trap for whoever applies it
later** — the obvious move is "the sheet says so", and the sheet does say so. The strategy the
memo actually wants is the opposite: keep Oscietra a **halo** and bring the brand in with an
**entry SKU at ~R2,000–2,500/100g** (memo §6 decision #3, R650–900 service tier — *pending
approval*). A formula that lifts the *bottom* of the range is the opposite of an entry tier.

🟡 **And the sheet still says "Sevtruga Classic"** while both live pages say "Sevtruga Medium" —
confirming the cost sheet is the outlier on naming. Fix the sheet, not the pages.

## Still open on this file

- ✅ **CORRECTED 2026-10-24 09:05 UTC — the cost sheet WAS rebuilt.** An earlier version of this
  file said the sheet had not been rebuilt. **That was false.** `caviar-landed-cost.xlsx` has three
  sheets — `Assumptions`, `Landed Cost`, **`Trade Pricing`** — and `Trade Pricing` carries
  *"Min viable trade price (ZAR/kg)"* (= landed ÷ 0.70), *"Shortfall vs floor (ZAR/kg)"*, a
  `STATUS` column that prints **"BELOW FLOOR — FIX BEFORE…"** when trade < floor, the
  **IndexBox SA premium band R8,000–35,000/kg**, the **local R2,000–6,000/100g** band, and the
  ITAC Rebate / CITES / Aquatir reference rows. `scripts/fix-caviar-price-sheet.py` did that;
  `caviar-landed-cost.pre-floor-fix-2026-10-23.xlsx` is the pre-fix snapshot.

  🔑 **So the gap is NOT the cost sheet. The gap is the registry.** The sheet knows the floors;
  the registry — which feeds the pages — was never given them. **The rebuild landed; the
  publication never happened.** That is the whole finding.
- **The clearing-agent email** (duty rate, ITAC permit, Rebate 460.19) was drafted to
  `outbound-drafts/` and is **still unsent**. It closes three open questions in one email.
- **ITAC Rebate 460.19** — a 20% duty relief worth ~R3,000–4,000/kg on Oscietra — has never been
  pulled. If it applies to us as a reseller, it moves the floor materially.

## 🔑 The root cause, in one line
**A source was updated but its publisher was not.** The cost model moved on 2026-10-23; the
registry that feeds the pages was last verified 2026-10-21; the drift alarm therefore had nothing
new to alarm on. This is the same bug class as the rest of tonight's findings — and the same one
the registry itself was created to prevent. 🔑 **A drift alarm that is not fed the new facts is a
green light, not a safety net.**
