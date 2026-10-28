# 🔴 The Caviar Trade Desk is an internal tool on a PUBLIC URL — it publishes our unit economics

**Found:** 2026-10-24 13:41 UTC (heartbeat window) · **Status:** source fixed, **NOT deployed**
**URL:** `https://awyjxfplygag.space.mcode.io` — HTTP 200 to an unauthenticated request from outside.
**Own footer:** *"Internal tool — Studex Group. Not a customer-facing price list. Do not publish trade prices from this screen without sign-off from Tumelo."*

## 1. What it publishes
The page renders, to anyone who opens the URL:

| Shown | Value |
|---|---|
| Farm gate (per SKU) | $1,000 / $700 / $400 per kg |
| Airfreight · Brokerage · CITES | $10 · $5 · $15 per kg |
| Import duty · VAT · FX | 20% · 15% · **18.5 ZAR/USD** — all editable in the browser |
| Landed cost | **R23,042 / R16,382 / R9,722 per kg** |
| **Margin floor @30%** | **R32,917 / R23,403 / R13,889 per kg** |
| Our published trade price | R34,000 / R22,000 / R12,500 per kg, shown **in red** |
| A red banner | *"Pricing defect live — 2 of 3 SKUs are quoted below their modelled floor."* |
| A CSV button | *"Export corrected price sheet (CSV)"* — exports the whole sheet |

🔑 **We publish landed cost and our minimum viable price; competitors publish retail.** Any buyer can
read our farm-gate price, our duty and FX assumptions, our landed cost and our floor — and then
negotiate us to exactly our own floor. 🔑 Worse, it says **our published prices are a bug**, while the
canonical caviar page quotes those same prices as the price. Two live Studex pages contradict each
other, and a buyer reading both learns our margin structure.

## 2. Why no checker ever saw it
- 🔑 **It is not in `PRICE-SOURCE-REGISTRY.md`** (0 hits). The drift manifest is generated from the
  registry, so the page is simply not in the set the checker walks — **17 pages checked, this one
  invisible.** The repo's own rule: *"Check the repo before concluding a surface doesn't exist."*
  It existed, live, the whole time.
- It is a **Vite SPA** (`/assets/index-CkBix7lK.js`), so the HTML shell carries ~150 visible chars.
  Even a URL-list check would have seen almost nothing.

## 3. The model itself was wrong in four ways
| Defect | Effect |
|---|---|
| **Import VAT added to landed cost** | Import VAT is **recoverable** input VAT for a VAT-registered importer — it is claimed back, not a cost. This inflated every floor by ~15%. |
| **Duty charged on farm gate only** | Duty is ad valorem on the **CIF** value (goods + freight to the border). |
| **"Current margin" was a markup on cost** | The floor formula is margin **on price**, so the page could show a green *"Current margin 34.3%"* directly above a red *"BELOW FLOOR"*. |
| **SKU named "Sevtruga Classic"** | Canonical name is **"Sevtruga Medium"**. |

Also: the **trade × 1.5 "recommended retail"** was presented as a price. It is not one — it is a
reference. And it put Oscietra at R56,600/kg, **62% above** the indexed SA premium band ceiling of
R35,000/kg, for a price we have never published.

## 4. The corrected model — and it CHANGES THE VERDICT ON THE HALO SKU
| SKU | Landed ZAR/kg | Floor @30% | Our trade price | Gross margin | Verdict |
|---|---|---|---|---|---|
| Oscietra Imperial | R23,042 | R32,917 | R34,000 | **32.2%** | ✅ **clears the floor** — the old model said it was R3,661 short |
| Kaluga Prestige | R16,382 | R23,403 | R22,000 | 25.5% | 🔴 R1,403 below |
| Sevtruga Medium | R9,722 | R13,889 | R12,500 | 22.2% | 🔴 R1,389 below |

🔑 **The "PRICING BUG" verdict was itself wrong for Oscietra** — a modelling error, not a pricing
error. Do not reprice the halo SKU on the strength of the old model.

**Still unverified, and it still decides everything:** the **20% duty rate** (the sourcing memo says
HS 1604.14.10 = 25% or 200c/kg, a *different* HS line from the 1604.31/1604.32 modelled) and the
**unhedged 18.5 FX**. Both floors move with the broker's answer. The VAT treatment is the one input
that is now a settled matter of accounting rather than assumption.

## 5. 🔑 The harness was asserting the bug
`caviar-trade-desk/scripts/verify.ts` reported **18/18 checks pass** and the workbook cited that as
proof the page and the sheet agree. It did agree — with the wrong model:
- it expected **every** SKU to be below floor, i.e. it **asserted our prices were too low**;
- its "margin arithmetic" check compared against `price / landed - 1`, i.e. it **asserted the markup
  definition of margin**;
- it keyed its expectations on the SKU **name**, so renaming a SKU **crashed** it.

🔑 **A harness that pins wrong numbers is worse than no harness — it makes the defect look verified.**
Rewritten: every check is now a *property* of the model (VAT excluded when recoverable, duty on CIF,
margin on price, flag agrees with recommended-vs-current, published retail matches the registry), the
workbook values are the only pinned numbers, and expectations key on SKU id. **45 checks, 0 failed.**

## 6. What was changed (committed, NOT deployed)
- `caviar-trade-desk/src/model.ts` — VAT recoverable flag; duty on CIF; margin on price; canonical
  SKU name; published retail carried alongside the modelled reference.
- `caviar-trade-desk/src/App.tsx` — separate rows for duty / VAT / CITES; **published** D2C retail
  shown as the price and the ×1.5 model shown as a reference only; corrected "how this engine
  behaves" copy; the banner now says duty and FX are unverified.
- `caviar-landed-cost.xlsx` — corrected formulas + a static authoritative sheet
  **"Corrected Model 2026-10-24"**; backup at `caviar-landed-cost.pre-model-fix-2026-10-24.xlsx`.
- `caviar-trade-desk/scripts/verify.ts` — rewritten, 45 property checks.
- `scripts/fix-caviar-price-sheet.py` — 🔑 **now refuses to run.** It rebuilt the sheet from the
  pre-correction model; running it would have silently reverted the fix.

## 7. The decision that is Tumelo's
**The page must not stay public in this form.** Options:

| Option | What it means | My view |
|---|---|---|
| **A — unpublish** | Take the URL down; rebuild the engine as an authenticated internal tool. | ✅ **Recommended.** The engine is a *tool*, not a page. It should be behind auth. |
| **B — strip to public-safe** | Same URL, but it shows only the published prices and a "request a quote" form. No cost model, no floor, no "defect" banner. | Acceptable if you want the URL to keep working. |
| **C — leave it** | Keep publishing our landed cost and floor. | ❌ Do not. |

Whatever we choose, the **drift checker must be able to see it** — a live customer-facing surface
that no checker covers is the failure mode this repo keeps re-learning.

## 8. Coverage limits of this finding
- **Not verified:** whether any of our *customer-facing* pages link to this URL.
  `studex-meat-subscription/subscription-sku.md` links to it, but that is a repo document, not a
  verified public link. This needs one live-page link check.
- **Not verified:** who has already seen it. The URL has been live since at least 2026-10-23.
- 🔑 **Deployment is not authorised**, so the live URL still runs the **old** bundle. The fix is ready
  and built (`dist/assets/index-EztMj-WO.js`), but nothing is published until you say so.

---
*This document is AI-generated analysis for internal decision-making. No price changed. No email sent.
No page deployed.*
