# ☕ Studex Green Coffee — FOB BAND CARD

**One page. One band. Every number with its source and its status.**

| | |
|---|---|
| **Owner** | `coffee-fob-band/compute-band-card.mjs` → `coffee-fob-band/band.generated.json` |
| **Generated** | 2026-10-30 |
| **Band authority** | `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.6 |
| **Model self-test** | ✅ PASS — reproduces the published price sheet exactly |
| **Status of the band** | ⚠️ **PARTIALLY VERIFIED** — the published set is internally consistent; the internal cost band is not |

---

## 1. THE BAND

### 1.1 Published — what buyers see

| Lot | Screen | Lot size | FOB USD/MT | FOB USD/kg | Status |
|---|---|---|---:|---:|---|
| Rwanda A1, 17+ screen, wet polished, 20 MT | 17+ | 20 MT | $4,200–$4,800 | $4.20–$4.80 | ✅ FOUND |
| Rwanda A2, 15–16 screen, 40 MT | 15–16 | 40 MT | $3,600–$4,000 | $3.60–$4.00 | ✅ FOUND |
| Custom blend, MOQ 5 MT | custom | 5 MT | $3,800 | $3.80 | ✅ FOUND |
| origin portfolio table (multi-origin) | — | per container | $3,400–$5,200 | $3.40–$5.20 | ✅ FOUND |

### 1.2 Internal — what our cost model floors on

| Band | FOB USD/kg | Status | Source |
|---|---:|---|---|
| the band the wholesale sheet floors on | $6.07–$6.75 | 🔴 **UNVERIFIED** | studex-price-sheet/dist/index.html ("Live desk — re-verify before quoting"); consumed by sa-b2b-coffee/compute-price-sheet.mjs |

> ⚠️ **The internal band is above the UAE import ceiling.** IndexBox (Sep 2026) puts UAE green coffee imports at **$2.50–6.50/kg**. Our internal high of $6.75/kg is *above* that ceiling. If the internal band is the true one, we are priced out of the Gulf by construction — before a single buyer says no.

### 1.3 The reconciliation

The brief flagged **three live green FOB bands**. On inspection, **two of the three reconcile**, and only one number is actually orphaned:

1. **$3,400–5,200/MT** — the origin portfolio table (Uganda low, SA Bourbon high). This is a **different scope**, not a competing price for the same product. Rwanda A1 at $4,200–4,800 **sits inside it**. ✅ consistent
2. **$4,200–4,800/MT (A1) and $3,600–4,000/MT (A2)** — the registry-owned Rwanda rows, correctly quoted in the PROWTC offer. ✅ consistent
3. **$6.07–6.75/kg** — the internal cost band. **Not traceable to any published table.** Flagged UNVERIFIED in our own assumptions register. 🔴 orphaned

> 💡 **This is the good news, and it is also the risk.** The published set is coherent. So the exposure is not *"we are contradicting ourselves publicly"* — it is *"our internal floor is probably too high, and we have been pricing to it."*

---

## 2. WHAT THE AMBIGUITY COSTS

Landed green cost `= (FOB $/kg + freight $/kg) × FX + port clearing` · cost per kg roasted `= landed ÷ 0.85 + R38 roasting + packaging`

| Scenario | FOB $/kg | Landed green R/kg | Cost/kg roasted | Natural 30 kg+ margin |
|---|---:|---:|---:|---:|
| A1 band LOW — $4.20/kg | $4.20 | R72.85 | R129.71 | **46%** ✅ |
| A1 band HIGH — $4.80/kg | $4.80 | R82.84 | R141.46 | **41.1%** ✅ |
| Internal band LOW — $6.07/kg | $6.07 | R103.97 | R166.32 | **30.7%** ✅ |
| Internal band HIGH — $6.75/kg | $6.75 | R115.28 | R179.63 | **25.2%** ✅ |

### 🔴 The headline

> At the **published** A1 band-high ($4.80/kg) our landed green is **R82.84/kg**. At the **internal** band-high ($6.75/kg) it is **R115.28/kg**.
>
> **That is R32.44/kg of landed green we may be over-paying for — R1,144.94 per 30 kg roasted bag, and R648,800.00 per 20 MT container.**
>
> On the published tier prices, Natural at 30 kg+ earns **41.1%** margin at the published band but only **25.2%** at the internal band — a **15.9-point** difference.
>
> **We are pricing the published sheet on the pessimistic number.** If the published band is right, the 30 kg+ tier could carry **R188.61/kg** and still clear the 25% floor — we are leaving margin on the table on every bag we sell. If the internal band is right, we are nearly at the floor and the sheet is correct.

> 🔑 Either way **the current published prices are safe** — they clear the floor under the *worst* case. What is at risk is **opportunity**, not solvency. Which is the better problem.

---

## 3. THE ONE CALL THAT CLOSES THIS

Send this to the supplier today. Five questions, one email, one phone call:

1. FOB Kigali (and FOB Djibouti if that is the contract) — USD per kg, for A1 and for A2, current crop.
2. Is the $6.07-6.75/kg band we have on file (a) green FOB, (b) something else entirely (landed, roasted, CIF), or (c) a stale figure?
3. Confirm the lot structure: A1 20 MT, A2 40 MT, custom blend 5 MT, samples 5-10 kg.
4. Screen size, moisture %, water activity, process, and the cupping score you will stand behind for each lot.
5. Who signs the phytosanitary certificate and the certificate of origin, and at what cost?

**Until question 2 is answered, the band card above is the answer — and the internal band stays flagged.**

---

## 4. CONTACT — use these, not the dead ones

| Field | Value |
|---|---|
| Support email | `info@studexmeat.com` |
| Order line | +27 83 593 2577 |
| Store phone | +27 84 421 6035 |
| Store WhatsApp | +27 94 988 8737 |
| Trading entity | Studex Meat (Pty) Ltd |
| Locations | Cape Town, South Africa & Kigali, Rwanda |

### 🔴 Dead contacts — must not appear on any buyer-facing document

| Dead value | Where it is | Note |
|---|---|---|
| `t.ramaphosa@studexwildlife.com` | studex-os/proposals/rwanda-offer-PROWTC-2026-07.json | Dead. The PROWTC buyer cannot reply to the offer that names them. |
| `tumelo@studexmeat.com` | ciie-buyer-brief/src/App.tsx (before tonight) | Not an asserted contact anywhere in the registry. |
| `coffee@studexmeat.com` | ciie-buyer-brief/src/App.tsx (before tonight) | Not an asserted contact anywhere in the registry. |
| `ceo@agent.studexmeat.com` | superseded China lead page | No DNS. Already retired from the registry. |

---

## 5. FILES THAT STILL CARRY A GREEN FOB NUMBER

| File | Carries | Status | Action |
|---|---|---|---|
| `studex-meat/PRICE-SOURCE-REGISTRY.md` | $3,400-5,200/MT origin table + $4,200-4,800 A1 + $3,600-4,000 A2 + $3,800 custom blend + $28-45/kg samples | SOURCE OF TRUTH — this file owns the published band. Do not edit the numbers; edit the status fields here if the supplier re-bases. | Keep. Add the re-verified band + date once the supplier answers. |
| `studex-os/proposals/rwanda-offer-PROWTC-2026-07.json` | t.ramaphosa@studexwildlife.com — DEAD, the buyer cannot reply | 🔴 ACTION REQUIRED — re-issue with a live reply address and the re-based band | Replace contact.email with info@studexmeat.com; keep the price strings, which already match registry §2.6. |
| `sa-b2b-coffee/compute-price-sheet.mjs` | $6.75/kg (band high) — UNVERIFIED | 🔴 COST FLOOR IS 32%+ HIGHER THAN THE PUBLISHED BAND | Re-base to the supplier-confirmed band, then re-run. The published tier prices only move if a tier falls below the floor. |
| `sa-b2b-coffee/price-sheet.generated.json` | $6.07 and $6.75 sensitivity poles | 🔴 GENERATED — do not hand-edit; re-run the generator | Regenerate after the band is re-based. |
| `sa-b2b-coffee/WHOLESALE-PRICE-SHEET.md` | "re-verify before quoting" + the live-page contradiction note | 🟡 ALREADY HANDLED — the live page stopped publishing green FOB numbers on 29 Oct (now "quoted on request") | Update assumption #10 to say the contradiction is closed. |
| `sa-hospitality-coffee/index.html` | NO published green price — "FOB pricing is quoted on request against the current season's band" | ✅ ALREADY CORRECT — no number to fix | None. Leave alone. |
| `ciie-buyer-brief/src/App.tsx` | MANGLED price strings (USD 4.20-4.20-4.80/kg; USD 4.80-3.60-4.00/kg) and unsourced tiers ($4.60/kg, from $4.30/kg) | 🔴 FIXED 2026-10-30 — realigned to this band card | Already corrected by tonight's build. Re-verify after deploy. |
| `studex-wildlife-coffee-vite/dist/index.html` | The published origin portfolio table | 🟡 OWNER of the published band — changes only via the registry | Re-check when the band is re-based. |

---

## 6. OPEN ITEMS

| Item | Status | Detail | Owner |
|---|---|---|---|
| China registration gate for a Rwandan green-coffee exporter | NOT VERIFIED | From 20 Jul 2026 China runs a single continent-wide approval regime for qualified coffee beans from all 53 African countries. That is NOT the same as the overseas-establishment registration/certification a specific Rwandan exporter must hold to clear customs. Do not assume one implies the other. | Tumelo / freight forwarder |
| Tariff date wording | FOUND — and two dates are being conflated | Zero tariff for all 53 African countries from 1 May 2026 (that is the TARIFF). 20 Jul 2026 is the unified PHYTOsanitary approval regime (that is not a tariff date). A Rwandan LDC origin has no expiry; the 30 Apr 2028 window belongs to the 20 non-LDC African countries. | copy — corrected 2026-10-30 |
| Green coffee to SA: duty rate | ASSUMPTION 0% | Not broker-confirmed. The whole SA landed-cost floor rests on it. | broker |
| Ocean freight + insurance | ASSUMPTION $0.07/kg | Needs a forwarder quote. | forwarder |

---

### Disclaimers

Prices are the published Studex band as at the generation date, sourced to `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.6. The internal cost band is **UNVERIFIED** and is used only for internal margin floors — never quote it. FX, freight, duty, port, roast and packaging figures are documented assumptions, not quotes. Nothing here is a commitment to buy, sell or ship. No trade price should be issued to a buyer until the band is re-based and this card is regenerated.

