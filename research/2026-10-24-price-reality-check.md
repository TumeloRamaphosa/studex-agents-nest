# Price Reality Check — 2026-10-24

**Owner:** Tumelo · **Built:** Build Hour, 24 Oct 2026 23:00 SAST
**Live desk:** https://jisom3k4i126.space.mcode.io
**Code:** `/workspace/studex-price-desk/`

---

## 1. Why this exists

Tonight's research brief said one thing three times: **the FX assumption of 18.5 is wrong, and it is
wrong in three models.** It also said the coffee price band needs to be rebuilt against the live ICE C
benchmark, and that the two things must be *"one place a price changes."*

This is that place. The desk fetches live FX and live ICE Arabica, and derives the coffee FOB band
and the caviar floors from them. The hardcoded 18.5 is gone from every model it touches.

---

## 2. Live values at build time (2026-10-24 21:16 UTC)

| Input | Value | Source | Cross-check |
|---|---|---|---|
| USD/ZAR | **16.578102** | exchangerate-api.com | frankfurter.dev (ECB) = 16.5976 → agree within 0.12% |
| USD/CNY | **6.684864** | exchangerate-api.com | frankfurter.dev = 6.6702 |
| ICE Arabica C | **$3.06/lb = $6.7461/kg** green-equivalent | ICE Futures via Yahoo chart API (KC=F, Coffee Dec 26) | matches the research brief's $3.06/lb exactly |
| ICE C 1-month change | **+11.66%** | same | brief said +11.66% — exact match |
| ICE C 52-week range | $2.427 – $4.2395 /lb | same | — |

🔑 **The live feed independently reproduced the brief's headline figures to the cent.** That is the
strongest evidence available that the brief's numbers were read off a real source and not invented.

**Effect of the FX correction:** 18.5 → 16.578 = the rand is **10.39% weaker against the dollar** than
our models assumed. **Every $1,000/kg landed cost is R1,922 cheaper than modelled.**

---

## 3. The coffee FOB band (the China sheet)

| Line | USD/kg | Basis |
|---|---|---|
| ICE C benchmark (green-equivalent) | **$6.75** | live |
| Our published sheet price (FOB Kigali) | **$4.80** | china-coffee-sheet-copy-paste.md — **UNVERIFIED** |
| Position vs benchmark | **−28.85%** | we quote 29% under the exchange composite |
| Recommended band — floor | **$6.07** | benchmark − 10% specialty differential |
| Recommended band — ask | **$6.75** | at market |

🔑 **Our sheet price sits BELOW the recommended band.** A premium A1 lot normally trades *above* the
exchange composite. Quoting 29% under it is either a genuine deep-specialty discount (our margin) or
a stale number from a softer 2025 market. **One message to the Kigali partner decides which** — and
that message is the highest-value thing to send tomorrow.

**Band logic:** the band is deliberately conservative (floor = benchmark − 10%, ask = at market).
Rationale: a specialty lot with a strong story should not be anchored below the exchange composite.
If the Kigali partner confirms a genuine structural discount, the floor can be revisited downward
with evidence. Until then, never quote below $6.07.

**Best of Rwanda 2026 (won 21 Oct 2026):** top lot Geisha (K-Organics, Huye) **$452/kg** — roughly
66× the average international price. **This is a micro-lot and a CEILING PROOF, never a market
comparable and never "our price."** The 2026 sample set sells at $250 per 100g.

### SA Coffee Price Index — Q3 2026 (retail, ZAR/kg)

Blends R640 · SA retail median R760 · Rwanda origin R968 · Ethiopia R1,084 · Kenya R1,236.

---

## 4. The caviar floors — the "pricing defect" was partly our own stale FX

**Do NOT reprice the caviar line on the strength of the 23 Oct "selling below cost" finding.** That
verdict was produced by a model with the stale 18.5 FX *and* recoverable import VAT treated as cost.

| SKU | Landed @ live FX | Landed @ 18.5 | Floor @30% | Trade price | Margin | Verdict |
|---|---|---|---|---|---|---|
| Oscietra Imperial | R20,674 | R23,042 | R29,535 | R34,000 | **39.2%** | ✅ clears floor |
| Kaluga Prestige | R14,706 | R16,382 | R21,009 | R22,000 | **33.2%** | ✅ clears floor |
| Sevtruga Medium | R8,738 | R9,722 | R12,483 | R12,500 | **30.1%** | ✅ clears floor (R17 of headroom) |

🔑 **At live FX all three SKUs clear the 30% floor.** Oscietra — the SKU the old model said was
R3,661 short — has R4,465 of headroom. That was a modelling error, not a pricing error.

⚠️ **Two caveats that keep this from being a green light:**

1. **Sevtruga Medium clears by R17 per kg.** That is noise, not margin. If the broker's duty answer
   moves at all, Sevtruga goes red. Treat it as at-floor, not above-floor.
2. **If import VAT is NOT recoverable** (i.e. we are not VAT-registered on import, or the broker
   charges it and it cannot be claimed), Kaluga and Sevtruga both fall below floor. This single
   input decides the answer and only the broker can confirm it.

**Still unverified and it still decides everything:** the **20% duty rate**. The sourcing memo says
HS 1604.14.10 = 25% or 200c/kg — a *different* HS line from the 1604.31/1604.32 modelled. Both
floors move with the broker's answer.

---

## 5. 🔒 What was published, and what was NOT

The desk is deployed on a **public URL**, so the public build was built to be safe.

**Published (public build):** ICE Arabica C, USD/ZAR, USD/CNY, SA Coffee Price Index, Best of
Rwanda 2026 result, and our **published D2C retail prices**.

**NOT published (internal build only, `dist-internal/`):** farm-gate cost, duty/VAT assumptions,
landed cost, margin floors, wholesale trade prices, our recommended coffee quote band.

**Why this matters:** `studex-meat/CAVIAR-TRADE-DESK-EXPOSURE-FINDING-2026-10-24.md` records that the
caviar trade desk published our farm gate, duty assumptions, landed cost and minimum viable price to
anyone who opened the URL. **We did not rebuild that mistake.** The cost model lives in a separate
module (`src/costModel.ts`) that the public entry point never imports, and it builds to a separate
output directory so it cannot be published by accident.

**A permanent gate now exists:** `npm run build` runs `scripts/audit-bundle.mjs`, which greps the
public bundle for 29 internal markers (identifiers *and* the old numbers — 18.5, 23042, 32917, 34000…)
and **fails the build** if any is present. It also asserts the internal bundle still carries the cost
model, so a refactor cannot silently strip the internal tool.

---

## 6. Verification

`scripts/verify.ts` — **33 checks, 0 failed.**

The important part is *what* it pins. The caviar desk's harness asserted our prices were too low and
pinned the wrong model, making a defect look verified. This harness instead:

- reproduces the **authoritative workbook values at FX 18.5** (landed cost and floor for all three
  SKUs) — proving the engine is a faithful re-implementation and that **only FX changed**;
- asserts **properties** of the model — margin measured *on price*, VAT excluded when recoverable,
  duty on CIF, floor = landed / (1 − 30%), and that the margin verdict and the floor verdict can
  never disagree;
- pins the workbook numbers as the only pinned values, keyed on SKU **id** not name.

---

## 7. What to test

| # | Test | Expected |
|---|---|---|
| 1 | Open the live URL | ICE C $3.06/lb, USD/ZAR ~16.58, SA index R760/kg |
| 2 | Click **↻ Refresh FX** | rate updates; if the network blocks it, a clear error shows and the build snapshot stays |
| 3 | `npm run verify` in `studex-price-desk/` | 33 passed, 0 failed |
| 4 | `npm run audit` | public clean (29 markers), internal carries the model |
| 5 | `grep -r "farmGate\|34000" dist/assets/*.js` | **no matches** |
| 6 | `npm run build:internal` | builds to `dist-internal/` with the cost model |

---

## 8. Recommended next moves

1. **Send the Kigali partner one message** asking whether $4.80/kg is still their price and whether
   the A1 lot carries a premium over the exchange composite. This unlocks the coffee band.
2. **Ask the clearing agent the two questions that decide the caviar line:** the HS classification
   (1604.31 vs 1604.14.10) and whether import VAT is claimable for us. Their answer moves every floor.
3. **Decide the caviar trade desk exposure** — it is still live and still public with the old bundle.
   The corrected engine is built and verified; it needs a decision (unpublish / strip / auth).
4. **Register the new desk** in `studex-meat/PRICE-SOURCE-REGISTRY.md` so the drift checker can see
   it — a live surface no checker covers is the failure mode this repo keeps re-learning.

---

*AI-generated analysis for internal decision-making. No price changed on a live page. No email sent.
The public build publishes market data and already-published prices only.*
