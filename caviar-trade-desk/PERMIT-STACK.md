# Studex — SA Caviar Import Permit Stack

> **INTERNAL.** Built 2026-10-29 23:00 SAST (Build Hour) from
> `research/2026-10-29.md` Topic 2. This document exists because the public
> caviar page said *"we handle it"* and *"full import compliance"* while the
> stack below **does not exist yet**.
>
> 🔑 **Status as at 2026-10-29: NONE of the six permits below is applied for,
> held, or confirmed.** Every one is a planned step with a named issuer. The
> public page has been rewritten tonight to say exactly that, in those words.

---

## 1. The stack, in order

| # | Step | Who issues it | What it is | Status |
|---|---|---|---|---|
| 1 | **DFFE marine aquaculture import/export permit** | **Department of Forestry, Fisheries and the Environment** — the designated **CITES Management Authority**, with permits issued through **Marine and Coastal Management** | Import/export permit required for marine aquaculture product | 🔴 Not applied for |
| 2 | **ITAC frozen-fish notification** | International Trade Administration Commission | Notification for frozen fish products | 🔴 Not lodged |
| 3 | **DAFF importer registration + veterinary import permit** | Department of Agriculture, Forestry and Fisheries | Register as an importer of animal products; veterinary import permit for the consignment | 🔴 Not registered. Permit takes **5–10 working days** once approved, and must be applied for **≥4 weeks ahead** |
| 4 | **SARS importer code** | South African Revenue Service | Importer code to clear customs | 🔴 Not issued |
| 5 | **NRCS registration** | National Regulator for Compulsory Specifications | Registered food-business operator | 🔴 Not registered |
| 6 | **CITES export permit + registered exporter code** | CITES authority in the **exporting** country (via our supplier) | Export permit for the species, plus a registered exporter code | 🔴 Not held — **no supplier identified** |

### 1.1 The labelling rule that is easy to miss

**Every tin must carry a non-reusable label bearing the species code.** Not a
sticker on the outer carton — a non-reusable label on the tin itself. This is a
CITES requirement, it is per-tin, and it is not something we can add at our
warehouse before dispatch. It has to be built into the supplier's packing line,
which means it is a **supplier-selection criterion**, not a logistics step.

---

## 2. The money line — HS 1604.31

**HS 1604.31 — prepared or preserved caviar and caviar substitutes:
30% import duty + 15% VAT** (SARS 2026 schedule, via JLog).

**The classification hinge, unresolved:** **0305.20** is live / chilled / frozen.
**1604.31** is the prepared or preserved (**tinned**) line — and 1604.31 is what
retail caviar actually lands on. We must not quote a price until a broker
confirms which line our tins are classified under.

| | 0305.20 (live/chilled/frozen) | 1604.31 (prepared/preserved) |
|---|---|---|
| Retail tin of caviar | — | ✅ **this is us** |
| Duty | 0% | **30%** |
| VAT | 15% | 15% |
| Status | not our line | 🔴 **unconfirmed by broker** |

**30% is the highest duty rate on any line Studex imports.** It is the number
that moves the R12,500 / R22,000 / R34,000 trade prices.

> ⚠️ **Provenance of this number — state it honestly.** The 30% was **found** in
> a tariff-lookup service (JLog) on 2026-10-29. It was **not** read from the
> SARS Schedule 1 PDF, and it is **not broker-confirmed**. It is an **input to
> be verified**, not a settled figure.

> 🔴 **And the model has not been re-run with it.** `caviar-landed-cost.xlsx`
> was **not opened** during the 2026-10-29 research hour (the exec loop guard
> cut the read). The 30% duty line is therefore **found, not modelled**, and
> the landed-cost model has **not** been re-run against it. This is the single
> largest open number in the caviar work.

---

## 3. Why the 30% changes the trade price

The internal trade desk (`caviar-trade-desk/src/model.ts`, floor = landed ÷
(1 − target margin)) already shows two of our three SKUs **below their own
modelled floor** on the *old* assumptions:

| SKU | Published trade | Modelled floor | Shortfall |
|---|---:|---:|---:|
| Oscietra Imperial | R34,000/kg | R37,661/kg | −R3,661 (**−9.7%**) |
| Kaluga Prestige | R22,000/kg | R26,720/kg | −R4,720 (**−17.7%**) |
| Sevtruga Medium | R12,500/kg | R15,778/kg | −R3,278 (**−20.8%**) |

Those floors were computed **without** the 30% duty. Re-running the model with
it will push the floors **up**, which widens every one of those shortfalls.

**Therefore: no trade price is quoted, published or promised until the model is
re-run with (a) HS 1604.31 at 30% + 15% VAT, (b) current FX, and (c) farmed
supply as the base case.** The public page was stripped of prices tonight for
exactly this reason.

---

## 4. The origin question — and why "Russian" is not on the page any more

| Supply | Size | Note |
|---|---|---|
| **Russian farmed sturgeon caviar** | 45 t (Jan–Jul 2026, +5% y/y) · 48 t (Jan–Aug 2026) · 89 t (full-year 2025) | A **48-tonne pool**, not a supply line |
| **China** | USD 118.2 m = **42.1%** of global black-caviar trade · est. **260 t** farmed production | Chinese scale has **lowered global wholesale prices** |

Russia→China seafood export revenue is **+54%** in the first nine months of 2026
— Russian caviar is being sold into China, not waiting for us. The US passed the
**Sanctioning Russia and Iran Act of 2026** (Senate, 8 Aug 2026) and Russia lost
PNTR (US effective tariff on Russian goods 7.3%, Aug 2026). **South Africa does
not sanction Russia** — but our export customers in the EU and US will read a
Russian supply chain as a question, and a Global South buyer will read it as an
exoticism rather than a quality claim.

**Position:** farmed (Chinese) caviar fixes the cost base; **wild,
CITES-traceable caviar fixes the price.** A farmed core range at an honest
landed cost plus a small, scarce, traceable premium tier is a better business
than a catalogue of aspirational names.

> 🔑 **"Russian" was removed from the public page tonight** because **no
> supplier has been identified and priced.** Origin is now stated as
> *confirmed per consignment*. The species grades (Oscietra, Kaluga, Sevtruga)
> are global product grades and remain — they are not origin claims. Overclaiming
> origin on a CITES-listed product is the fastest way to lose the hospitality
> buyer who knows what Oscietra actually tastes like.

---

## 5. Three open gaps

| # | Gap | Why it matters | Owner |
|---|---|---|---|
| 1 | **Broker confirmation of the HS line and the duty rate** | 30% vs 0% decides whether the Sevtruga trade price is R12,500 or R18,000 | One email to a SA food-fish clearing agent — draft at `studex-meat/regulatory-emails/A-clearing-agent.md`. ⚠️ *Any figure built on the old FX assumption of 18.5 must be recomputed — the live rate is 16.578, and the old assumption made every landed cost R1,922/kg too high per $1,000 of cost.* |
| 2 | **Re-run `caviar-landed-cost.xlsx`** with HS 1604.31 @ 30% + 15% VAT, current FX, farmed-China base case | Nothing about caviar pricing can be decided before this | Robusca |
| 3 | **Supplier origin verification** | Determines whether we may say "Russian" at all, and sets the base case | Robusca |

**Also open, and not a gap but a fact:** Africa's caviar trade figures
(imports 18 t / $935k led by South Africa; exports 17 t / $4.6m) are an
indexbox aggregation of a broad caviar-and-sturgeon category and **do not
reconcile with premium caviar pricing**. **Do not quote them as price
benchmarks.** The directional fact — that South Africa is Africa's **importing**
node — is the usable part. The unit economics are not.

---

## 6. What this means for the business, and why it is still worth doing

South Africa is the one country in Africa that already imports caviar, and
**we are not the ones importing it.** That cuts both ways:

- ✅ **Strong:** our proposition is legitimately **import-and-distribute**. We
  know the corridor, and our permit stack starts from the DFFE/DAFF axis we
  already work on for frozen fish — a newcomer's does not.
- ⚠️ **Weak:** the story "we will import caviar into the country that already
  imports more of it than anyone else in Africa" is not a story about making
  caviar in Africa. It is a distribution proposition. It should be *sold* as
  one.
- 🔴 **And our 2027 proposition was being sold as a sale, not a pipeline.** The
  public page advertised retail and trade prices for a product whose permit
  stack does not exist — through a page anyone could screenshot.

**Caviar is a hospitality product.** Fine dining and luxury hotels are the two
demand drivers named in every caviar market report. **We already have a
hospitality coffee page and a named prospect list.** So: **sell caviar to the
same accounts in 2027 — with coffee in 2026.**

---

## 7. Compliance language — what may and may not be published

| 🔴 May not publish (unconditional claim) | ✅ May publish (permit-conditioned) |
|---|---|
| "cites-certified" / "cites compliant" | "CITES documentation where applicable" |
| "itac compliant" | "subject to import permit" |
| "full import compliance" | "on issuance of" / "before dispatch" |
| "all permits in place" | "lead time" / "where required" |
| "import permit is in hand" | "documentation where applicable" |
| "we handle the paperwork" | |
| "fully compliant" | |

🔑 **Two more that are banned by the house rules even though the automated guard
does not catch them:**

- 🔴 **"Import permit stack in hand."** This was live on the SA hospitality page
  until tonight. The stack is **not** in hand — nothing has been applied for.
  The automated guard missed it because its pattern is `import permit (is)? in
  hand` and this string inserts *stack* in between. **Semantically it is the
  most dangerous sentence on the page and the tool scored it clean.** Fixed
  tonight by hand.
- 🔴 **"Landed cost provided on request"** on the caviar page — landed cost is
  an internal figure (`PRICE-SOURCE-REGISTRY.md` §5). Offer a **quotation**,
  never the landed cost.

The automated guard is `ops/price-ladder-guard.py`. **It is necessary and not
sufficient** — tonight proved that.
