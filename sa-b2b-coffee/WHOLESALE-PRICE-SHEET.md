# Studex — SA B2B Coffee Wholesale Price Sheet (INTERNAL)

> **INTERNAL — NOT FOR PUBLICATION.** Landed cost, margin floor, FX, duty and
> farm-gate figures in this document must never appear on a public page.
> See `studex-meat/PRICE-SOURCE-REGISTRY.md` §5 ("Never publish landed cost,
> farm-gate cost, duty/VAT/FX assumptions or a margin-floor on a [public page]").
> The **public** sheet is the tier table + service lines in
> `sa-hospitality-coffee/index.html`. This file explains why those numbers are
> safe.
>
> **Built:** 2026-10-29 23:00 SAST (Build Hour) · **Author:** Robusca (CEO)
> **Basis:** `research/2026-10-29.md` — *"Publish a tiered B2B wholesale price
> sheet"* (recommended action 1)
> **Generator:** `sa-b2b-coffee/compute-price-sheet.mjs` →
> `sa-b2b-coffee/price-sheet.generated.json` — **the published table and this
> document are emitted from the same file so they cannot drift.**

---

## 1. The blocker this clears

The research brief put it plainly:

> *"A procurement manager cannot approve a supplier who has not published a
> tiered wholesale sheet. This is the single biggest blocker on this channel and
> it is fixable tonight without a single API key."*

And it was true. The live SA hospitality page carried four per-kg prices, a
single flat "Trade MOQ 50 kg", and a WhatsApp button. There was no tiering, no
lead time, no delivery threshold, no sample pack, and — critically — **no
priced line for the one thing that is actually our differentiator: barista
training.**

We also had 25 named prospects (`sa-b2b-coffee-prospects.md`, 9 Aug) and a
sequenced email set (`sa-b2b-coffee-outreach/email-sequence.md`) that pointed at
an offer that did not exist. The outreach was asking for a meeting to discuss a
price sheet we had not written. That is tonight's fix.

---

## 2. Public price table — roasted, ex VAT

Roasted to order, packed in South Africa. **Per kilogram.**

| Origin | 1 kg | 5 kg | 20 kg | 30 kg + |
|---|---:|---:|---:|---:|
| **Washed** — clean, bright, classic body | R400 | R385 | R370 | R350 |
| **Honey** — sweet, rounded, gentle fruit | R350 | R335 | R320 | R310 |
| **Aerobic** — winey depth, high clarity | R380 | R365 | R350 | R335 |
| **Natural** — fruity, full, syrupy | R270 | R260 | R250 | R240 |

VAT-inclusive (15%): multiply by 1.15. Ex-VAT and VAT-inclusive figures are
both on the published table — a procurement manager cannot approve a
VAT-inclusive quote without being told the VAT-inclusive number.

**Discount ladder:** 1 kg = list · 5 kg = −4% · 20 kg = −8% · 30 kg+ = −12%.
**The ladder is deliberately shallow.** See §5 for why there is not more room.

### 2.1 Service lines — priced separately, and they are the wedge

| Line | Price (ex VAT) | Price (VAT incl.) | Unit |
|---|---:|---:|---|
| Sample pack — 5 × 250 g cupping set | R495 | R569 | per pack |
| Barista training — foundations workshop | R7,500 | R8,625 | per on-site day, up to 8 staff |
| Barista training — monthly retainer | R3,500 | R4,025 | per month, quarterly minimum |
| In-room single-serve sachet | R3.95 | R4.54 | per 2 g sachet, 1,000+ units |

- **Sample pack** is fully credited against a first order of 20 kg or more.
- **In-room sachet** is R4.20 each at 500–999 units; case of 1,000 is R3,950;
  R1,500 one-off print setup. Custom-printed with the hotel's brand.
- **Retainer** is one on-site half-day per month, up to 6 staff, 3-month minimum
  (R10,500). Travel outside Gauteng quoted at cost.

### 2.2 Commercial terms

| | |
|---|---|
| Roasted minimum | 5 kg first order; 20 kg+ for scheduled monthly supply |
| Green minimum | 20 MT per 20 ft container (A1 20 MT / A2 40 MT) |
| Roasting | Roasted to order, dispatched within 2 business days of order |
| Delivery | Free over R850 in Gauteng, over R1,500 nationally. Below: R95 (Gauteng) / R135 (national) |
| Delivery time | 48 h Gauteng, KZN, Cape Town · 72 h nationally |
| Payment | 30-day terms on account after the first order; card or EFT for the first order |
| Green stock | Green lots land Durban on a 3–4 week cycle from FOB; stock dates quoted per order |

> ⚠️ **MOQ contradiction fixed.** The live page said "Trade MOQ 50 kg" next to
> *roasted* prices, while its green section says 20 MT. 50 kg was never a real
> order size for either segment. Roasted hospitality MOQ is now **5 kg** (the
> tier table's own opening rung), green trade MOQ is **20 MT**. A café that
> wants 5 kg must not read "50 kg" and conclude we cannot serve them.

---

## 3. Cost model — the floor

🔑 **A floor is only a floor at worst-case cost.** So the model uses the **top**
of the green FOB band, the **higher** of two live FX rates, and adds duty,
freight, roasting and packaging explicitly.

| Input | Value | Source | Confidence |
|---|---:|---|---|
| FX USD/ZAR | 16.64 | frankfurter.dev (ECB ref) 29 Oct 2026; cross-check exchangerate-api 16.6339 (agree 0.04%). Higher of the two used. | ✅ verified |
| Green FOB, Kigali | **$6.75/kg** | Our published band $6.07–6.75/kg (`studex-price-sheet/dist/index.html`, flagged "re-verify before quoting"). **Top** of band used. | 🔴 UNVERIFIED |
| Ocean freight + insurance | $0.07/kg | **ASSUMPTION** — $70/tonne origin → Durban. Needs a forwarder quote. | 🔴 assumption |
| Import duty on green | 0% | **ASSUMPTION** — not broker-confirmed. If wrong, the floor moves. | 🔴 assumption |
| Port, clearing, inland | R1.80/kg | **ASSUMPTION** | 🔴 assumption |
| Roast yield | 0.85 kg roasted / kg green | **ASSUMPTION** — 15% weight loss, filter roast | 🔴 assumption |
| Roasting cost | R38/kg roasted | **ASSUMPTION** — energy, labour, depreciation, roast loss | 🔴 assumption |
| Packaging | R11 (1 kg) · R8 (5 kg) · R6 (20/30 kg) per kg | **ASSUMPTION** — valve bag + label | 🔴 assumption |
| Target gross margin | 25% | **POLICY** — see §5 | policy |

**Derivation**

```
green landed /kg      = (FOB + freight) × (1 + duty) × FX + port/clearing
                      = (6.75 + 0.07) × 1.00 × 16.64 + 1.80
                      = R115.28
green per kg roasted  = 115.28 ÷ 0.85 = R135.63
landed / kg roasted   = 135.63 + roasting + packaging
```

| Tier | Landed / kg | Floor @ 25% margin |
|---|---:|---:|
| 1 kg | R184.63 | R246.17 |
| 5 kg | R181.63 | R242.17 |
| 20 kg | R179.63 | R239.51 |
| 30 kg+ | R179.63 | R239.51 |

**Margin actually achieved at each published price**

| Origin | 1 kg | 5 kg | 20 kg | 30 kg+ |
|---|---:|---:|---:|---:|
| Washed | 53.8% | 52.8% | 51.5% | 48.7% |
| Aerobic | 51.4% | 50.2% | 48.7% | 46.4% |
| Honey | 47.2% | 45.8% | 43.9% | 42.1% |
| **Natural** | 31.6% | 30.1% | 28.1% | **25.2%** |

Every published cell clears the 25% floor. **No cell required the discount to be
capped** — the ladder and the floor happen to agree exactly at the tightest
point (Natural, 30 kg+, R240 vs a R239.51 floor). That is luck, not design, and
§5 says why it will not survive a green price rise.

---

## 4. Sensitivity — what breaks the floor

| Scenario | Green landed / kg | Worst cell | Margin | Verdict |
|---|---:|---|---:|---|
| Band low — green $6.07/kg | R103.97 | Natural 30 kg+ | 30.7% | ✅ comfortable |
| **Band high — green $6.75/kg (published floor)** | R115.28 | Natural 30 kg+ | **25.2%** | ✅ clears, barely |
| **Stress — green $7.50/kg (+11% on band high)** | R127.76 | Natural 5 kg | **24.5%** | 🔴 **below the floor** |

**This is the single most important number in the sheet.** A green price rise of
about 11% takes the Natural 5 kg tier under the 25% floor. Natural is our
tightest line and it is also the one that gets quoted hardest. Two options, both
Tumelo's call:

1. **Re-verify the green band** (the price sheet already says "re-verify before
   quoting"). If the true band is $6.07–6.30, there is no problem at all.
2. **Re-price Natural** if the band is confirmed at $6.75+. R270/kg at 1 kg is
   the published entry price; it is the number most likely to be compared
   against another roaster's shelf.

---

## 5. Why the ladder is shallow, and why the target is 25% not 30%

The caviar trade desk runs a 30% margin floor. Coffee cannot.

At the top of the green band, Natural at 1 kg (R270) clears a 25% floor by
R23.83/kg. At 30% the same cell would need R257.10 — and the 30 kg+ tier would
need R256.61, which is **above** the R270 list price before any discount at all.
A 30% floor on coffee therefore forbids the entire volume ladder, because
Natural simply does not have the margin to discount into.

So: **25% target, shallow ladder, and the margin table published internally so
Tumelo can see exactly where the thin line is.** The ladder is not timid — it is
as deep as the cost model allows, and the floor check is automated in the
generator so it can never be quietly widened past the model.

---

## 6. Assumptions register — what is NOT confirmed

Nothing below is confirmed. Each one is priced into the sheet as if it were
true, and each one is a way for the floor to be wrong.

| # | Assumption | If it is wrong | Owner |
|---|---|---|---|
| 1 | Green FOB band $6.07–6.75/kg | Whole cost base moves. Top of band used, so downside is covered — but if the true cost is *above* the band, the floor is below landed cost. | Robusca — re-verify before quoting (already flagged on the price sheet) |
| 2 | Import duty on green coffee = 0% | Floor drops below landed cost | Clearing agent (email drafted in `studex-meat/regulatory-emails/`) |
| 3 | FX 16.64 | ±1% FX = ±R1.15/kg landed | Trader — live rate, published date |
| 4 | Ocean freight $0.07/kg | Floor moves | Forwarder quote needed |
| 5 | Roast yield 0.85 | ±0.03 yield = ±R5/kg landed | Roastery |
| 6 | Roasting cost R38/kg | ±R10/kg = ±R11.76/kg landed | Roastery quote needed |
| 7 | Packaging R6–R11/kg | Minor (±R5/kg at worst) | Supplier |
| 8 | Trainer day rate R2,500 | Training lines under-priced | Tumelo — confirm trainer cost |
| 9 | Sachet packaging R1.20/unit | Sachet line under-priced | Supplier quote needed |
| 10 | **Green FOB on the live page ($3,400–5,200/MT) contradicts our current band ($6.07–6.75/kg)** | A buyer prices off the OLD table while we cost the NEW one. **This is a live commercial exposure on the page.** | Tumelo — decide which band is true, then reconcile the green table |

### 6.1 On assumption #10 — read this one twice

`sa-hospitality-coffee/index.html` publishes green coffee at **USD 3,400–5,200/MT**
($3.40–5.20/kg). Our current band on the price sheet is **$6.07–6.75/kg**. The
two cannot both be true. The price-sheet band was re-based on 24 Oct; the
hospitality page's green table was not updated when it was.

This is a *source/deploy divergence with money attached* — the third one this
month, and the first one where a buyer could price a contract off our stale
number. Tonight's sheet costs on the **higher** band, so we are not selling
below landed cost. But the published green table is still the older, lower band
and it is still live. **Tumelo must decide which band is real.** I did not
silently rewrite the published green prices tonight, because publishing a band I
cannot source is exactly the failure mode this house has been fighting all
month.

---

## 7. Why "training" is priced first, not coffee

The sector brief (Hostex, 2026) names the four things SA hospitality says is
hurting it: import-dependent supply vulnerable to price and supply swings;
rising operating costs and load shedding; **training and retaining skilled
baristas is a major issue**; and guests now expect single-origin, dialed
espresso and alt-brew.

Three of those four we can answer with a bean. The fourth is the one nobody
else sells:

- Canteen and CoffeeDesk sell **the machine and the consumable**. They do not
  sell the farm, the origin, the story, or **the trained barista**.
- Our own prospects file said it on 9 Aug: *"none of these OCS players offer
  barista training or cold brew. Adding training converts bean supply into a
  retainer contract."*
- It costs us **a trainer, not inventory**. No Shopify token, no stock, no
  permit — the whole retainer line can be sold from tonight's page.

So the sheet is not "coffee at a discount". It is **coffee + training + a
brand-visible in-room sachet**, and the retainer is the line that turns a
transaction into a monthly account. The pricing ladder on coffee is what gets
us into the door; the training line is what keeps us there.

And it is the cross-sell door: a hotel that takes our training also takes our
in-room sachets, and — the same buyer — our biltong hampers, which are already
built and already cheaper than our own corporate-gifting page.

---

## 8. What to test

| # | Test | Expected |
|---|---|---|
| 1 | Open the published sheet. Tier table shows 4 origins × 4 tiers, ex VAT **and** VAT-inclusive | matches §2 exactly |
| 2 | Compare published prices against `sa-b2b-coffee/price-sheet.generated.json` | identical |
| 3 | Submit the quote-request form with all fields blank | browser blocks it (required fields) |
| 4 | Submit the form filled | opens a WhatsApp message **and** a pre-filled mailto — both containing the business name, volume tier and coffees selected |
| 5 | Change the volume tier and re-submit | the message text changes with it |
| 6 | Look for caviar prices on the page | **none** |
| 7 | Look for the phrase "permit stack in hand" | **absent** (it was a false claim — the stack does not exist) |
| 8 | Look for "Russian" in the caviar card | **absent** (we cannot evidence the origin) |
| 9 | Check the MOQ | roasted **5 kg**, green **20 MT** — not "50 kg" |
| 10 | Re-run `node sa-b2b-coffee/compute-price-sheet.mjs` | same numbers, same JSON |

---

## 9. Owner actions this build does NOT close

1. **Re-verify the green FOB band** and reconcile the live green table
   (assumption #1 + #10). *Before CIIE, 5 days.*
2. **Broker-confirm the green-coffee import duty** (assumption #2).
3. **Confirm the trainer day rate** before the first training quote goes out
   (assumption #8).
4. **Send the 10-name outreach** — `sa-b2b-coffee-outreach/email-sequence.md`
   now has something real to point at. Ask for **a 1 kg sample and a cupping**,
   not a contract.
5. **Price the in-room sachet with a real print quote** before pitching it to
   a hotel (assumption #9).
6. **Decide the OCS posture**: Dish Café and Coffee Devices SA are named
   partners *and* competitors. Approach as a **white-label bean supplier to
   their machine clients**, not as a competing brand.
