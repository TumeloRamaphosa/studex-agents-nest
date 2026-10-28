> **📌 READ THIS FIRST — this file is the FIRST review, not the last.**
> `04-review.md` records the review that returned **PACKAGE: REWORK**. Its findings were actioned:
> the compliant, price-free copy is in **`06-compliant-facebook-instagram.md`** and
> **`07-compliant-video-script.md`**, and the **final** independent verdict is
> **`08-final-signoff.md` → `PACKAGE: APPROVE — READY FOR TUMELO'S REVIEW (unpublished)`**
> (originally *APPROVE WITH FIXES — 1 item*; the R1 wording fix was applied to video S7).
> **Nothing in `02-` or `03-` is publishable.** Those are priced first drafts, kept as the reviewed
> record. Do not re-open the rework — it is closed.

# 04 — Brand Guardian Review · StudEx Trade Package (2026-10-25)

**Task:** TASK-STUDEX-TRADE-001 · **Role:** Brand Guardian (independent reviewer) · **Scope:** review only — no publishing, scheduling, generation or credit spend.
**Assets reviewed:** `02-facebook-instagram.md` (FB caption, IG adaptation, 5-slide carousel), `03-video-script.md` (25s video script + visual brief), against `00-fact-base.md`, `01-brief.md` and the `studex-daily-posting` Validation Checklist.
**Files edited by this review:** `04-review.md` only. `01-`, `02-` and `03-` were **not** edited — the copywriter owns them.

---

## 1. Overall verdict

**PACKAGE: REWORK**

The package is strong in craft, structure, sourcing and brand discipline — every price number traces to the fact base, the palette is correct, and there is no banned string, no booth claim, no competitor bashing, no financial promise. It nevertheless **fails Rule [10] in all four assets** (prices on a public feed), **fails Rule [8]** (4 extra hashtags where ≤2 are allowed) and **fails Rule [5] as written** (a CTA conflict between checklist, brief and copy). These are not polish items — they are publish-blocking. The compliant shape is **price-free social copy that sells the terms and routes the buyer to a trade landing page where pricing lives**, with the priced version retained for that landing page and for one-to-one quotes.

---

## 2. Per-asset verdicts

| Asset | Verdict | Issue count | Notes |
|---|---|---|---|
| FB caption (`02-` lines 11–25) | **FIX LIST** | 8 | B1 (prices), B2 (hashtags), B3 (CTA), C1 (as-at), C2 (caviar indicative), C3 (coffee qualifier), C5 (menu-cost misread), C8 (retail priced as trade), D1 (markdown) |
| IG adaptation (`02-` lines 31–59) | **FIX LIST** | 4 | B1, B2, B3, C7 (leads with 7–14 days) |
| Carousel — 5 slides (`02-` lines 63–87) | **FIX LIST** | 6 | B1 (all 5 slides), B2, B3, C2, C7 (slide 3 lead order), C8, D1 |
| Video script (`03-` lines 37–47, 153–160) | **FIX LIST** | 6 | B1 (S2/S3/S4 on-screen prices + tier card), B3, C4 (as-at), C6 ("After that, routine"), C7 (S6 before S7), D4 (runtime margin) |

---

## 3. The standard applied (verbatim)

```
[1] No mention of "Global Markets" platform unless pillar is Business/Africa
[2] Hashtags: always include #StudexGM
[3] Brand colors: Emerald/Gold/Black — image must match
[4] Tone matches pillar
[5] CTA present: info@studexmeat.com (agent.studexmeat.com has no DNS, never use it)
[6] No competitor bashing without facts
[7] No financial promises or guaranteed returns
[8] Max 2 hashtags extra beyond #StudexGM
[9] No booth/stand/pavilion claim unless the booth is confirmed
[10] No price on a public feed
```

Also applied: Instagram allows **5 hashtags total**; social platforms do **not** render markdown (`**bold**` ships as literal asterisks — strip before publishing; `socialize()` in `scripts/daily-post.py` does it). Rule [10] is not theoretical — the house has applied it: `memory/post-queue/2026-10-22-thursday-business.md` closes with *"No price published on a public feed (trade pricing stays on the China page)"*.

---

## 4. Table A — Claims

| Assertion (quoted) | Asset | Source in fact base | Verdict | Required correction |
|---|---|---|---|---|
| "**Biltong.** Wagyu Biltong Gold 1kg at R1,450. A 7kg trade case at R12,500." (`02-` L15) | FB caption | `00-` §2.1 **Retail biltong** — R1,450 / R12,500 | **FAIL** — price on public feed (Rule [10]); also retail prices presented inside a trade block closed by "Meat prices are ex VAT and subject to confirmation" — a trade qualifier on a retail price (C8) | Remove both figures from-feed; if any survives on the landing page, label them **retail**, and label trade institutional prices separately as **ex VAT, as at Oct 2026, subject to confirmation** |
| "Craft biltong at R380/kg original and R410/kg peri-peri." (`02-` L15) | FB caption | §2.2 Institutional meat — R380/kg / R410/kg | **FAIL** — price on public feed; "as at Oct 2026" dropped (C1) | Remove numbers; the qualifier "ex VAT, as at Oct 2026, subject to confirmation" stays with the trade terms |
| "Wagyu ribeye R1,050/kg, wagyu fillet R1,150/kg, 30-day dry-aged beef R850/kg." (`02-` L15) | FB caption | §2.2 | **FAIL** — price on public feed; as-at dropped (C1) | Remove numbers |
| "**Caviar.** Per 100g: Oscietra Imperial R4,200, Kaluga Prestige R2,800, Sevtruga Medium R1,600. Trade per kilo: R34,000, R22,000, R12,500." (`02-` L17) | FB caption | §2.3 — retail/100 g and trade/kg | **FAIL** — price on public feed; no "indicative / subject to confirmation" on the caviar line (C2) | Remove numbers; carry the caviar terms without figures |
| "Lead time is 7 to 14 days, counted from the date the DAFF veterinary import permit is issued. The permit goes in at least 4 weeks before shipment, so a first shipment runs roughly two months end to end." (`02-` L17) | FB caption | §2.3 | **PASS on fact** — but see C7 (this paragraph is buried after a price list, so the two-month figure arrives too late to lead) | Keep the wording; reorder so the two-month first-shipment figure carries the lead |
| "**Coffee.** Green, FOB, indicative: Rwanda A1 from USD 4,200/MT, Ethiopia Yirgacheffe USD 4,500/MT, Kenya AA USD 4,800/MT. Roasted South African for hospitality starts at a 50kg MOQ: washed R400/kg, honey R350/kg, natural R270/kg." (`02-` L19) | FB caption | §2.4 green (FOB, indicative, as at Oct 2026) · §2.5 roasted (MOQ 50 kg) | **FAIL** — price on public feed; "as at Oct 2026" dropped for green coffee (C4); the caption's meat-only qualifier "Meat prices are ex VAT and subject to confirmation" (L15) does not cover roasted coffee (C3) | Remove numbers; roasted coffee needs its own ex-VAT + subject-to-confirmation treatment wherever it is priced |
| "A café can put R4,200 of Oscietra caviar on the board, 100g at a time, or buy trade at R34,000 a kilo. Both numbers are real." (`02-` L11) | FB caption | §2.3 — R4,200 is the **retail price of a 100 g tin**; R34,000 is trade/kg | **FAIL** — price on public feed; and it reads as a **menu cost** (C5): a hospitality buyer takes R4,200 as the per-service plate price. "Both numbers are real" also makes the retail figure the headline | Replace opening line — no figures, no menu-cost framing (exact wording §9.1) |
| "Biltong, caviar, green coffee. Here are the numbers, not the adjectives." (`02-` L35) and the arrowed list L38–L51 | IG caption | §2.2–2.5 | **FAIL** — the whole hook is a public price list (Rule [10]) | Rebuild around terms, not prices (§9.2) |
| "→ Rwanda A1 · from USD 4,200/MT" … "→ Kenya AA Nyeri · USD 4,800/MT" (`02-` L49–51) | IG caption | §2.4 | **FAIL** — price on public feed; as-at dropped (C4) | Remove |
| "Caviar lead time: 7 to 14 days from DAFF permit issue. First shipment is about two months end to end. Plan for it." (`02-` L53) | IG caption | §2.3 | **FAIL** — brief §4 rule 1: never lead with 7–14 days; the first-shipment lead number is two months (C7) | Reverse the order — two months first (§9.2) |
| Slide 2 on-slide copy "**Biltong.** 1kg Gold R1,450 · 7kg case R12,500 · Craft biltong R380/kg original, R410/kg peri-peri" (`02-` L68) | Carousel | §2.1 + §2.2 | **FAIL** — price on public feed; retail and trade prices merged in one line with no basis label (C8) | Rebuild slide 2 as terms, not figures (§9.3) |
| Slide 3 on-slide copy "**Caviar.** Per 100g: R4,200 · R2,800 · R1,600. Trade per kilo: R34,000 · R22,000 · R12,500. Lead 7 to 14 days from DAFF permit issue." (`02-` L69) | Carousel | §2.3 | **FAIL** — price on public feed; caviar indicative qualifier missing (C2); and the slide leads with 7–14 days (C7) | Rebuild slide 3 (§9.3) |
| Slide 4 on-screen "Green coffee, FOB. Rwanda A1 from USD 4,200/MT · Yirgacheffe USD 4,500/MT · Kenya AA USD 4,800/MT" (`02-` L70) | Carousel | §2.4 | **FAIL** — price on public feed; "as at Oct 2026" appears only in the speaker note (L70) and not on the slide | Remove figures from the slide |
| Carousel caption (L77–L81) | Carousel | §2.2–2.5 | **FAIL** — repeats every price on-feed; caviar indicative qualifier missing (C2); as-at missing for green coffee (C4) | Replace with the price-free caption in §9.3 |
| "Biltong from R380/kg ex VAT" (S2 on-screen, `03-` L40) and "Biltong trades from three hundred and eighty rand a kilo." (VO) | Video | §2.2 — R380/kg craft biltong (original), ex VAT, as at Oct 2026, subject to confirmation | **FAIL** — price on public feed | Replace S2 with a terms shot (§9.4) |
| "Caviar from R12,500/kg trade" (S3 on-screen, `03-` L41) and "Caviar from twelve thousand five hundred rand a kilo." (VO) | Video | §2.3 — Sevtruga Medium, trade/kg | **FAIL** — price on public feed | Replace S3 |
| Tier card rows "Oscietra Imperial — R4,200/100g · R34,000/kg", "Kaluga Prestige — R2,800/100g · R22,000/kg", "Sevtruga Medium — R1,600/100g · R12,500/kg" (`03-` L119) | Video (graphic overlay) | §2.3 | **FAIL** — a motion graphic over the shot is still on a public feed (Rule [10]); also drops the caviar indicative qualifier (C2) | Rebuild the card as tier **names + MOQ terms**, no figures (§9.4) |
| "Green coffee from USD 3,400/MT FOB" (S4 on-screen, `03-` L42) and VO "three thousand four hundred dollars a tonne" | Video | §2.4 — Uganda Bugisu AA (Elgon) USD 3,400/MT FOB Djibouti | **FAIL** — price on public feed; the on-screen "FOB" basis is kept but the **"as at Oct 2026"** is dropped from the headline (C4); it is also a *different origin* from the USD 4,200/MT used in `02-`, which is fine but must not read as one product list | Replace S4 |
| "A first shipment runs about two months. After that, routine." (VO S7, `03-` L45; sourcing row L~"After that, routine") | Video | §2.3 — DAFF permit ≥4 weeks before shipment → first shipment ≈ two months. **No repeat-shipment/standing-permit lead time is published** | **FAIL** — unsupported claim (C6): "After that, routine" implies a repeat lead time the registry does not publish, and §7 of the fact base forbids delivery-time promises beyond the caviar lead | Replace the VO line (exact wording §9.4). The sourcing table already warns "**Do not** extend this into a delivery-time promise for subsequent orders" — the VO line does exactly that, so the line and its own sourcing note are in conflict |
| "Caviar takes seven to fourteen days once permits are issued." (VO S6, `03-` L44) | Video | §2.3 | **PASS on fact** — but sequencing violates the brief (C7): S6 (7–14 days) lands before S7 (two months) | Re-order so the two-month first-shipment figure is not preceded by the 7–14 day figure as the headline lead |
| Legal strip "**Oct 2026 pricing, subject to confirmation**" over S2–S4 (`03-` L73) | Video | §2.2–2.5 | **FAIL (inherited)** — the strip is a qualifier for prices that must not be on the feed; with the prices removed the strip has no referent and should go with them | Remove with the prices (§9.4) |
| Every price number itself (values, units, currency) | all | §2.1–2.5 | **PASS** — no rounding, no unit slip (per 100 g vs per kg), no currency slip (R vs USD); every figure traces to the fact base | Keep values; move them off-feed, to the trade landing page / a one-to-one quote only |

---

## 5. Table B — Brand

| Quoted line | Asset | Issue | Fix |
|---|---|---|---|
| "#StudexGM #AfricanTech #SpecialtyCoffee #Biltong #Hospitality" (`02-` L25) | FB caption | Rule [8]: **4 extras** where ≤2 are allowed; only `#AfricanTech` is from the approved set (`00-` §1: `#StudexGM #AfricanTech #SuperAgents #AgenticAI`) | `#StudexGM #AfricanTech #SpecialtyCoffee` (2 extras) |
| "#StudexGM #AfricanTech #Biltong #Caviar #SpecialtyCoffee" (`02-` L59, L87) | IG caption, carousel caption | Rule [8]: **4 extras**; only `#AfricanTech` approved | `#StudexGM #AfricanTech #SpecialtyCoffee` |
| "Global Markets" | all | Not mentioned; pillar is Business | **PASS** — no change |
| Emerald `#0B4F3C` + Gold `#C9A84C` + Circuit Black `#0A0A0A` | carousel visual directions (`02-` L67–71), video visual brief (`03-` L94, per-shot palettes) | Palette used consistently; no fourth brand colour | **PASS** — no change |
| Banned-string scan (retired caviar names "Sevruga Premium"/"Siberian Reserve", "per 250g", `agent.studexmeat.com`, `studexwildlife.com`, landed cost / farm gate / margin floor / belowFloor / duty / FX assumptions, testimonials, awards, street address, Stud-Bot pricing, `+27 83 593 2577`) | all | None present — and the video's per-shot "Must NOT appear" notes actively enforce several of these | **PASS** — no change |
| Booth / stand / pavilion claim | all | None (CIIE booth not confirmed) | **PASS** — Rule [9] satisfied |
| Competitor bashing | all | None | **PASS** — Rule [6] satisfied |
| Financial promise / guaranteed return | all | None; no "final price", no "as low as" | **PASS** — Rule [7] satisfied |
| Business-pillar tone, British/SA English | all | Consistent; no discount-first framing ("special/cheap/sale" absent) | **PASS** — Rule [4] satisfied |
| "Send your volumes to sales at studex-group dot com." (S9 VO, `03-` L47) | Video | One CTA on screen and spoken, no second contact point — good discipline; the address itself is the B3 conflict | Fix the address per the CTA branch chosen, keep the single-CTA discipline |

---

## 6. Table C — CTA

| Asset | CTA used | Verdict | Fix |
|---|---|---|---|
| FB caption (`02-` L23) | `sales@studex-group.com` | **CONFLICT** — legitimate for trade enquiries per `00-` §3, but not rule [5]'s `info@studexmeat.com`; `01-brief.md` says the single CTA is the WhatsApp number with `sales@` in a contact block only | Branch A (rule [5] literal): `info@studexmeat.com` · Branch B (brief): WhatsApp `+27 94 988 8737` as the single CTA, `sales@studex-group.com` in a contact block only |
| IG caption (`02-` L57) | `+27 94 988 8737` (WhatsApp) | **CONFLICT** — matches the brief, does not match rule [5] verbatim | Same two branches; Branch B is what IG already uses |
| Carousel slide 5 (`02-` L71) + caption (L85) | `sales@studex-group.com` | **CONFLICT** — same as FB | Same two branches |
| Video S9 end card (`03-` L47) | `sales@studex-group.com` | **CONFLICT** — same as FB | Same two branches |
| — | `agent.studexmeat.com` | Not used anywhere | **PASS** — never introduce it (no DNS) |
| — | `+27 83 593 2577` | Not used anywhere | **PASS** — Tumelo's personal line, not a default CTA |

**Decision required from Tumelo:** which CTA is canonical for a Business-pillar trade post — `info@studexmeat.com` (checklist rule [5]) or the WhatsApp number (brief)? Both branches are given in §9. **Do not publish until this is chosen.** Neither branch as currently written matches rule [5] verbatim.

---

## 7. Table D — Craft

| Asset | Issue | Fix |
|---|---|---|
| FB caption | Markdown `**Biltong.**`, `**Caviar.**`, `**Coffee.**` (L15–19) and the carousel's bold slide labels (L67–71) ship as literal asterisks on social | Strip all `**` before publishing (`socialize()` in `scripts/daily-post.py` does this) — D1 |
| FB caption | Length must sit in the Business-pillar spec of **150–200 words** | **Verified: 191 words** (caption body L11–23, markdown stripped) — **PASS**, and it stays compliant after the price removal (§9.1 replacement is 176 words) |
| Carousel | Exactly 5 slides, one idea each, slide 1 hook, slide 5 CTA, on-slide copy phone-readable, no repeated slide | **PASS on structure** — slide 1 is the hook ("What it actually costs to stock StudEx."), slide 5 carries the only CTA and explicitly says "Single ask. No second contact point on this slide."; no slide repeats another. Copy must be rebuilt price-free (§9.3) |
| Video | 8–10 shots, timecode continuity, on-screen text ≤8 words, visual brief for every shot, sourcing row for every number shown | **PASS on structure** — 9 shots; timecodes 0:00–0:02, 0:02–0:05, 0:05–0:08, 0:08–0:11, 0:11–0:14, 0:14–0:17, 0:17–0:20, 0:20–0:22, 0:22–0:25 are contiguous with no gap or overlap; every on-screen headline is ≤8 words ("Biltong from R380/kg ex VAT" = 5, "Min order: 50 kg roast · 5 MT blend" = 7, "7–14 days after DAFF permit issued" = 5); a per-shot visual brief exists for all 9 shots; the sourcing table carries a row for every number and claim on screen or in VO |
| Video | **Runtime recomputation** | **77 VO words ÷ ~3 words/sec ≈ 25.7s** of pure speech, against a 25.0s runtime. The script's own rate is 3.1 w/s, i.e. it is already running faster than the nominal pace, and the two beats the film depends on (S1 silence + room tone, S6 near-silence under the cold-room hum) have **zero budget** at 3 w/s. Removing the four price VO lines (S2, S3, S4 and part of S9) drops the VO to ~50 words ≈ **16.7s**, which restores real room for the beats while staying inside the 20–30s window with S5/S8/S9 and the end card. **Recompute after the price removal and re-time the shots** — do not simply keep the old 25.0s timing on a shorter VO |
| IG | Different hook and structure from FB (arrowed list vs prose), not a reword | **PASS on structure** — but the arrowed list is itself the Rule [10] breach, so the IG variant must be rebuilt around terms (§9.2) |

---

## 8. Blocking vs nice to have

### 8.1 Blocking (must be fixed before any publish)

- **B1 — Rule [10]: the whole package publishes prices on a public feed.** FB caption, IG caption, all 5 carousel slides and the video script all carry prices (R1,450, R12,500, R380/kg, R410/kg, R1,050/kg, R1,150/kg, R850/kg, R4,200/100g, R2,800, R1,600, R34,000/kg, R22,000/kg, R12,500/kg, USD 4,200/MT, USD 4,500/MT, USD 4,800/MT, USD 3,400/MT, R400/kg, R350/kg, R270/kg, R650). Under rule [10] **none of these assets is publishable as written.** The compliant shape is **price-free social copy that sells the terms and routes the buyer to a trade landing page where pricing lives** — with the priced version retained for that landing page and for a one-to-one quote. Exact replacement wording for all four assets is in §9.
- **B2 — Rule [8] + the IG hashtag cap.** FB uses `#StudexGM #AfricanTech #SpecialtyCoffee #Biltong #Hospitality`; IG and the carousel use `#StudexGM #AfricanTech #Biltong #Caviar #SpecialtyCoffee`. That is **4 extras**, not ≤2, and only `#AfricanTech` is from the approved set. Correct set: `#StudexGM` + at most 2 extras (e.g. `#AfricanTech` + `#SpecialtyCoffee`).
- **B3 — Rule [5] CTA vs the brief's CTA.** Copy uses `sales@studex-group.com` (FB, carousel, video) and `+27 94 988 8737` (IG). Checklist rule [5] names `info@studexmeat.com`. Genuine conflict: `01-brief.md` says the single CTA is the **WhatsApp number** with `sales@` in a contact block only, never replacing WhatsApp; the fact base §3 says `sales@studex-group.com` is legitimate for trade / platform enquiries. **This is a decision for Tumelo.** Both branches are given; neither branch as currently written matches rule [5] verbatim.

### 8.2 Claims fixes (blocking for accuracy)

- **C1** — Institutional meat prices must read "ex VAT, **as at Oct 2026**, subject to confirmation". The "as at Oct 2026" is dropped in the FB caption and elsewhere.
- **C2** — Caviar trade prices are **indicative / subject to confirmation** — unstated in the FB caption and the carousel caption.
- **C3** — Roasted coffee prices (R400 / R350 / R270 per kg) carry their own ex-VAT + subject-to-confirmation qualifier; the caption's meat-only qualifier does not cover them.
- **C4** — Green coffee is "FOB, **indicative, as at Oct 2026**" — "as at Oct 2026" is dropped.
- **C5** — FB opening line "A café can put R4,200 of Oscietra caviar on the board, 100g at a time" reads as a **menu cost**, but R4,200 is the **retail price of a 100 g tin**. A hospitality buyer will misread it.
- **C6** — Video VO S7: "A first shipment runs about two months. After that, routine." — "After that, routine" **implies a repeat-shipment lead time the registry does not publish**; the script's own sourcing note says not to extend it into a delivery-time promise, and fact-base §7 forbids delivery-time promises beyond the caviar lead.
- **C7** — Brief §4 rule 1 is "**never lead with 7–14 days**; the lead number for a first shipment is two months." The IG caption and carousel slide 3 lead with 7–14 days. Video sequences S6 (7–14 days) before S7 (two months).
- **C8** — Retail prices are presented as trade prices. FB L15 puts the **retail** figures R1,450 and R12,500 (`00-` §2.1) inside a trade block closed by "Meat prices are ex VAT and subject to confirmation" (an institutional/trade qualifier, §2.2), and carousel slide 2 merges "1kg Gold R1,450 · 7kg case R12,500" with "Craft biltong R380/kg" in one unlabelled line. A trade buyer will read the 7 kg case price as a trade/kg rate. Every price needs its basis (retail vs trade) attached, or it comes off-feed under B1.

### 8.3 Nice to have (non-blocking)

- Strip markdown `**bold**` at the final publish step if the copy path bypasses `socialize()` (D1) — belt-and-braces only.
- Trim the FB caption toward the lower end of 150–200 words once prices are gone (currently 191 — compliant).
- Re-check on-slide phone legibility after the carousel re-copy (D3).
- House ruling: keep the trade landing-page URL short and stable, so price-free copy can point at it without embedding a price string in the caption.

---

## 9. Remediation plan — exact publishable-safe replacement copy

> All four replacements are **price-free**, use **#StudexGM + 2 extras**, and carry the corrected claims. Replace only the CTA line once Tumelo chooses Branch A or Branch B. The priced versions are retained for the trade landing page and for one-to-one quotes only.

### 9.1 FB caption — replacement copy

> A café can put Oscietra caviar on the board, service by service — and buy the case, not the tin.
>
> Here is what a hospitality buyer actually commits to when stocking StudEx.
>
> Biltong, beef, chicken and lamb for institutional supply. Meat prices ex VAT, as at Oct 2026, subject to confirmation. Caviar trade pricing is indicative and subject to confirmation. Green coffee is quoted FOB where relevant, indicative, as at Oct 2026; roasted South African coffee starts at a 50 kg minimum order. A first shipment runs roughly two months end to end, counted from the date the DAFF veterinary import permit is issued.
>
> If you are costing a menu, a shelf or a volume order, send us a line. Trade pricing is issued per product on enquiry, not on a public feed.
>
> Trade enquiries:
> - **Branch A** — `info@studexmeat.com`
> - **Branch B** — `WhatsApp +27 94 988 8737`
>
> *(Branch B only: add a contact block line beneath — "Sales: sales@studex-group.com" — never in place of the WhatsApp CTA.)*
>
> #StudexGM #AfricanTech #SpecialtyCoffee

**Publish notes:** strip all `**` markers. Word count 176 (within the 150–200 Business-pillar spec). No figure, no currency string, no MOQ-derived price appears anywhere in the caption.

### 9.2 IG adaptation — replacement copy

> **Hook:** What it actually takes to stock StudEx.
>
> **Caption:**
>
> Biltong, caviar, green coffee. Here are the terms, not the adjectives.
>
> Biltong
> → Wagyu biltong and craft biltong for institutional supply
> → Meat prices ex VAT, as at Oct 2026, subject to confirmation
>
> Caviar
> → Retail per 100 g, trade per kilo, private-label tins from 5 kg
> → Trade pricing indicative, subject to confirmation
>
> Green coffee
> → FOB where relevant, indicative, as at Oct 2026
> → Roasted South African from a 50 kg minimum order
>
> First shipment: about two months end to end, counted from DAFF permit issue. Plan for it.
>
> Trade pricing sits on our trade page, not in a public post — request it and we will quote per product.
>
> Trade enquiries:
> - **Branch A** — `info@studexmeat.com`
> - **Branch B** — `WhatsApp +27 94 988 8737`
>
> #StudexGM #AfricanTech #SpecialtyCoffee

**Publish notes:** the arrowed structure is kept (it is genuinely a different shape from FB) but every line now carries a **term**, not a price. The 7–14 day figure is removed from the lead; only the two-month first-shipment number is stated.

### 9.3 Carousel — replacement copy (5 slides, one idea each)

> **Slide 1 — hook:** "What it actually takes to stock StudEx." / "Biltong · Caviar · Green coffee"
> *Visual (unchanged): dark Circuit Black `#0A0A0A` field, Emerald `#0B4F3C` gradient wash, Gold `#C9A84C` hairline rule under the title; filmic top-down still with biltong, a caviar tin and green coffee beans out of focus behind the type.*
>
> **Slide 2 — the meat line:** "Biltong · beef · chicken · lamb" / "Ex VAT, as at Oct 2026, subject to confirmation"
> *Visual (unchanged): warm-window kitchen scene, biltong sliced on dark slate, Emerald counter edge, Gold light falloff.*
>
> **Slide 3 — lead time:** "First shipment: about two months" / "Counted from DAFF permit issue"
> *Visual (unchanged): cold blue-white macro of caviar beads on a spoon over a chilled tin.*
>
> **Slide 4 — caviar and coffee terms:** "Caviar: indicative, subject to confirmation" / "Green coffee FOB · roasted from 50 kg"
> *Visual (unchanged): roastery dock handover, jute sacks, morning haze, Emerald crates, Gold low sun.*
>
> **Slide 5 — CTA:** "Trade pricing on our trade page" / **Branch A:** `info@studexmeat.com` · **Branch B:** `WhatsApp +27 94 988 8737`
> *Visual (unchanged): clean end card, Circuit Black `#0A0A0A`, Emerald `#0B4F3C` panel, Gold `#C9A84C` rule. Single ask only — no second contact point on this slide.*
>
> **Carousel caption:** Three product lines, one trade desk.
>
> Biltong, beef, chicken and lamb for hospitality and retail buyers. Meat prices ex VAT, as at Oct 2026, subject to confirmation. Caviar trade pricing is indicative, subject to confirmation. Green coffee is FOB where relevant, indicative, as at Oct 2026; roasted South African coffee starts at a 50 kg minimum order.
>
> First shipment: about two months end to end, counted from the date the DAFF veterinary import permit is issued.
>
> Costing a menu, a shelf or a volume order? Send us a line.
>
> Trade enquiries:
> - **Branch A** — `info@studexmeat.com`
> - **Branch B** — `WhatsApp +27 94 988 8737`
>
> #StudexGM #AfricanTech #SpecialtyCoffee

**Publish notes:** strip `**` from all on-slide and caption text. Slide 5 keeps the only CTA. Slide 3 now leads with the two-month figure, not 7–14 days. No price appears on any slide.

### 9.4 Video script — replacement copy

> **VO, shot by shot** (replaces the VO lines that carried prices):
>
> - **S1 — hook (0:00–0:02):** "What does it cost to stock StudEx?"
>   *On-screen:* "What does it cost to stock StudEx?" · *Visual unchanged.*
> - **S2 — was the biltong price, now the terms (0:02–0:05):** "Biltong for institutional supply — ex VAT, as at October 2026, subject to confirmation."
>   *On-screen:* "Biltong · ex VAT, subject to confirmation" (6 words) · *Visual: keep the craft-biltong macro; remove the pricing band wording so no figure is implied.*
> - **S3 — was the caviar price, now the caviar terms (0:05–0:08):** "Caviar is quoted per hundred grams, or per kilo for trade."
>   *On-screen:* "Caviar · 100 g retail · kg trade" · *Tier card rebuilt as tier **names + MOQ** only: "Oscietra Imperial — private-label tins from 5 kg MOQ", "Kaluga Prestige", "Sevtruga Medium". No figures anywhere on the card.*
> - **S4 — was the coffee price, now the coffee terms (0:08–0:11):** "Green coffee is quoted FOB. Roasted coffee starts at fifty kilos."
>   *On-screen:* "Green coffee FOB · roasted from 50 kg" (7 words) · *Visual unchanged (hessian sacks, cupping bench).*
> - **S5 — minimum order (0:11–0:14):** "Every tier has a minimum order you can plan around."
>   *On-screen:* "Min order: 50 kg roast · 5 MT blend" (unchanged) · *Visual unchanged.*
> - **S6 — the lead time (0:14–0:17):** "Permits go in weeks ahead, so a first shipment runs about two months."
>   *On-screen:* "First shipment ≈ 2 months" (4 words) · *Visual unchanged (cold room, crate latch).* **Do not** put "7–14 days" on the screen ahead of the two-month figure (C7).*
> - **S7 — was "After that, routine", now the honest line (0:17–0:20):** *"First shipments run about two months. Repeat orders are quoted case by case."*
>   *On-screen:* "First shipment ≈ 2 months" → change to **"Repeat orders quoted case by case"** (6 words) · *Visual unchanged (permit stamp, dummy document).*
> - **S8 — trade pricing on request (0:20–0:22):** "Trade pricing on request."
>   *On-screen:* "Trade pricing on request" (unchanged) · *Visual unchanged (buyer at laptop, blurred).*
> - **S9 — CTA end card (0:22–0:25):** Branch A: "Send your volumes to info at studexmeat dot com." · Branch B: "Send your volumes on WhatsApp to plus two seven, nine four, nine eight eight, eight seven three seven."
>   *On-screen:* "Trade enquiries" · **Branch A:** `info@studexmeat.com` · **Branch B:** `+27 94 988 8737` · Tagline "Technology. Capital. Opportunity." unchanged · *Visual unchanged (hero still, Emerald wash, Gold hairline).*
>
> **C6 — exact replacement for the S7 VO line:**
> "First shipments run about two months. Repeat orders are quoted case by case."
> *(Removes the implied repeat-shipment lead time the registry does not publish, and aligns the line with the script's own sourcing note.)*
>
> **C7 — corrected ordering:** the two-month first-shipment figure must land **before** any 7–14 day figure, and the 7–14 day figure must not be presented as the headline lead time. Where a 7–14 day figure is retained at all (e.g. as a sourcing-row note), it appears only as a subordinate, secondary frame with no delivery promise attached.
>
> **On-screen text:** ≤8 words per frame; no prices; no currency strings; no "USD"; no R-prefixed figures.
>
> **Legal strip:** remove "Oct 2026 pricing, subject to confirmation" together with the prices it qualifies (the S2/S3/S4 lower-third has no referent once the figures go). The "as at Oct 2026, subject to confirmation" wording survives in the VO, which states it.
>
> **Sourcing table:** delete the rows for every removed price (R380/kg, R12,500/kg, the three tier-card rows, USD 3,400/MT, the legal strip, and the "ex VAT" on-screen qualifier row); retain the rows for the 7–14 day permit fact, the ≈2-month first-shipment fact, the MOQ figures (50 kg, 5 MT, 5 kg), the tier names, "Trade pricing on request", the CTA and the tagline. Amend the "After that, routine" row to the new wording, with the note that it must not be extended into a delivery-time promise for subsequent orders.
>
> **Runtime:** with the four price VO lines removed the VO falls from 77 to ~50 words ≈ **16.7s at ~3 words/sec**. Re-time the nine shots to a 20–25s cut so the S1 silence, the S6 cold-room near-silence and the end-card beat each have real room. Do not simply keep the old 25.0s timing on a shorter VO. **Recompute the final runtime after re-timing and state it in the next revision.**

---

## 10. Confirmed passing

- **Rule [9]** — no booth/stand/pavilion claim anywhere (the CIIE booth is NOT confirmed). **PASS.**
- **Rule [7]** — no financial promise / guaranteed return; no "final price", no "as low as", no discount-first framing. **PASS.**
- **Rule [1]** — "Global Markets" is not mentioned; pillar is Business. **PASS.**
- **Rule [6]** — no competitor bashing. **PASS.**
- **Rule [4]** — Business-pillar tone, British/SA English, confident and non-corporate. **PASS.**
- **Rule [3] / brand palette** — Emerald `#0B4F3C` + Gold `#C9A84C` + Circuit Black `#0A0A0A` used consistently in the carousel visual directions and the video visual brief; no fourth brand colour, no teal-and-orange, no red sale badges. **PASS.**
- **Banned strings** — no retired caviar names, no "per 250g", no `agent.studexmeat.com`, no `studexwildlife.com`, no landed cost / farm gate / margin floor / belowFloor / duty / FX assumptions, no testimonials, no awards, no street address, no Stud-Bot pricing, no `+27 83 593 2577`. **PASS.**
- **Price values** — every price number itself traces to the fact base: no rounding, no unit slip (per 100 g vs per kg), no currency slip (R vs USD). **PASS on value**; the defects are in the **qualifiers** (C1–C4, C8) and in the fact that they appear on a public feed at all (B1).
- **Carousel structure** — exactly 5 slides, one idea each, slide 1 hook, slide 5 CTA with an explicit "single ask" note, phone-readable on-slide copy, no repeated slide. **PASS on structure.**
- **Video structure** — 9 shots (inside the 8–10 window); contiguous timecodes 0:00→0:25 with no gap or overlap; every on-screen headline ≤8 words; a per-shot visual brief with Setting / Subject / Shot size / Lighting / Palette / Props / Must NOT appear for all 9 shots; a sourcing row for every number and claim on screen or in VO. **PASS on structure** (runtime margin flagged separately in Table D).
- **IG distinctness** — IG is a genuinely different hook and structure from FB (arrowed list vs prose), not a reword. **PASS on structure** (the arrowed list itself must be rebuilt price-free).
- **Production discipline** — the video's "Must NOT appear" notes and the Higgsfield note ("no generation credits may be spent without Tumelo's approval", "Nothing has been generated for this script and no credits have been spent") are correct and should survive the rewrite.

---

## 11. Sign-off

```
CLAIMS: FAIL — 8
BRAND: FAIL — 2
CTA: FAIL — 4
CRAFT: FAIL — 2
RULES[1-10]: FAIL — 3
```

**Decisions needed from Tumelo**
1. **Canonical CTA for a Business-pillar trade post** — Branch A (`info@studexmeat.com`, rule [5] literal) or Branch B (WhatsApp `+27 94 988 8737`, brief literal, with `sales@studex-group.com` in a contact block only). Applies to all four assets.
2. **Confirm the price-free architecture** — social sells the terms and routes to a trade landing page; the priced version is retained for that landing page and for one-to-one quotes only.
3. **Confirm the lead-time wording** — two months for a first shipment, with repeat orders quoted case by case (no standing repeat lead time published).
4. **Confirm the retail-vs-trade labelling** for biltong where any price survives on the landing page (C8).

*Review only. `01-brief.md`, `02-facebook-instagram.md` and `03-video-script.md` were not edited — the copywriter owns them.*
