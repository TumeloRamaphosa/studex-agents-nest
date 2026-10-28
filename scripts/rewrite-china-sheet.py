#!/usr/bin/env python3
"""Rewrite the China FOB band in china-coffee-sheet-copy-paste.md (v2, live band)."""
import sys

P = 'china-coffee-sheet-copy-paste.md'
s = open(P, encoding='utf-8').read()
edits = []


def sub(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        print(f"FAIL[{label}]: marker count = {n}")
        sys.exit(1)
    s = s.replace(old, new)
    edits.append(label)


sub(
"""# 📊 China Coffee Strategy — COPY-PASTE FOR GOOGLE SHEETS
## Studex Meat | Tumelo Ramaphosa | July 7, 2026""",
"""# 📊 China Coffee Strategy — COPY-PASTE FOR GOOGLE SHEETS
## Studex Meat | Tumelo Ramaphosa | v2 — 24 October 2026 (live price band rebuild)

> 🔴 **v2 CHANGES THE PRICE BASIS.** The FOB prices below were re-anchored to the **live ICE
> Arabica C benchmark** ($3.06/lb = $6.75/kg green-equivalent, 24 Oct 2026). The July sheet quoted
> **USD 4.80/kg** — a single legacy number, ~29% under the exchange composite, with no stated basis.
> That number is now carried as a **legacy column only** and must not be quoted until the Kigali
> partner confirms it is a live 2026 contract price.
>
> **Live quote band (FOB Kigali): USD 6.07 – 6.75/kg**, anchored to ICE C less a specialty
> differential. Source of truth: `research/2026-10-24-price-reality-check.md` and the live desk
> at **https://jisom3k4i126.space.mcode.io**. Re-verify before every customer-facing use — market
> data is a point-in-time observation, not a Studex published price.
>
> ⚠️ **Before you send anything from TAB 2:** the subject lines and bullets below still contain
> **"PROWTC Certified"** and **"Rainforest Alliance certified"**. Per `PRICE-SOURCE-REGISTRY.md` §4f,
> **no source document exists for any Studex coffee certification** — the Rainforest Alliance claim
> was removed from the coffee pages on 2026-10-21 as unsourced, and "PROWTC" is a *prospect's* brand,
> not ours. **Fix both before sending.** See the note at the foot of this file.""",
'header')

sub(
"""## TAB 3: COFFEE PRODUCTS

| Grade | Process | Cup Profile | Certifications | Min Order | FOB Price/kg | Pack Size |
|-------|---------|------------|---------------|-----------|-------------|-----------|
| Rwanda A1 | Washed | Jasmine, stone fruit, clean finish | Rainforest Alliance, PROWTC | 60kg | USD 4.80 | 60kg bags |
| Rwanda A2 | Natural | Blueberry, dark chocolate, full body | Rainforest Alliance, PROWTC | 60kg | USD 5.20 | 60kg bags |
| Rwanda A1 | Natural | Floral, honey, balanced | Rainforest Alliance, PROWTC | 60kg | USD 5.50 | 60kg bags |
| Rwanda A2 | Washed | Citrus, caramel, medium body | Rainforest Alliance, PROWTC | 60kg | USD 4.60 | 60kg bags |""",
"""## TAB 3: COFFEE PRODUCTS

| Grade | Process | Cup Profile | Certifications | Min Order | FOB Price/kg | **Quote band USD/kg (live)** | Pack Size |
|-------|---------|------------|---------------|-----------|-------------|-------------|-----------|
| Rwanda A1 | Washed | Jasmine, stone fruit, clean finish | ⚠️ see note below | 60kg | ~~USD 4.80~~ *(legacy)* | **6.07 – 6.75** | 60kg bags |
| Rwanda A2 | Natural | Blueberry, dark chocolate, full body | ⚠️ see note below | 60kg | ~~USD 5.20~~ *(legacy)* | **6.37 – 6.75** | 60kg bags |
| Rwanda A1 | Natural | Floral, honey, balanced | ⚠️ see note below | 60kg | ~~USD 5.50~~ *(legacy)* | **6.60 – 6.75** | 60kg bags |
| Rwanda A2 | Washed | Citrus, caramel, medium body | ⚠️ see note below | 60kg | ~~USD 4.60~~ *(legacy)* | **5.92 – 6.60** | 60kg bags |

> **How the band was built.** ICE Arabica C = **$3.06/lb = $6.75/kg** green-equivalent (live, 24 Oct
> 2026). The band floor is the benchmark less a **10% specialty differential** ($6.07/kg); the ask is
> at market ($6.75/kg). Each grade keeps the **relative structure of the July sheet** (A2 washed
> cheapest → A1 natural dearest) rescaled onto that band, so no grade is quoted below the floor.
> A premium A1 lot normally trades *above* the exchange composite — the July sheet quoted 29% *below*
> it, which is either a genuine deep discount or a stale 2025 number. **One message to the Kigali
> partner decides which.**
>
> ⚠️ **Certifications column.** "Rainforest Alliance" and "PROWTC" are placeholders here, NOT claims we
> can make — see the note at the foot of this file. Leave the column blank until a certificate
> document exists.

---

## TAB 3b: LIVE MARKET BENCHMARK — copy this block whenever a price needs checking

| Reference | Value | As of | Source |
|---|---|---|---|
| ICE Arabica C | **$3.06/lb** | 23 Oct 2026 | ICE Futures (KC=F) |
| ICE C green-equivalent | **$6.75/kg** | 23 Oct 2026 | $3.06 x 2.20462 |
| ICE C 1-month change | **+11.66%** | 23 Oct 2026 | ICE Futures |
| ICE C 52-week range | $2.43 - $4.24 /lb | 23 Oct 2026 | ICE Futures |
| USD/ZAR | **16.578** | 24 Oct 2026 | exchangerate-api.com (ECB ref: 16.598) |
| USD/CNY | **6.685** | 24 Oct 2026 | exchangerate-api.com |
| SA Coffee Price Index — SA retail median | **R760/kg** | Q3 2026 | SA Coffee Price Index |
| SA Coffee Price Index — Rwanda origin avg | **R968/kg** | Q3 2026 | SA Coffee Price Index |
| SA Coffee Price Index — Ethiopia / Kenya | **R1,084 / R1,236** | Q3 2026 | SA Coffee Price Index |
| SA Coffee Price Index — blends | **R640/kg** | Q3 2026 | SA Coffee Price Index |

> 🔗 **Live desk:** https://jisom3k4i126.space.mcode.io — refreshes FX live in the browser and carries
> the price band. Use it instead of this static block whenever you can.

---

## TAB 3c: BEST OF RWANDA 2026 — the quality ceiling (halo, not a price)

| Fact | Value |
|---|---|
| Auction | Best of Rwanda 2026 online auction, **won 21 October 2026** |
| Top lot | **Geisha, K-Organics, Huye — US$452/kg** (approx RWF 670,000) |
| What that means | roughly **66x the average international market price** |
| Selection | 31 lots chosen from 320 samples; 20 winners scoring **87.49% - 91.81%** SCA |
| 2026 sample set | sells at **US$250 per 100g** |
| Altitude / terroir | Nyamasheke, 1,500 - 2,000m, volcanic soil, consistent rainfall |

> 🔴 **USE THIS AS A CEILING PROOF — NEVER AS A PRICE.** The headline $452/kg is a **micro-lot
> Geisha**. Do not quote it as "our price", as "the Rwandan market price", or as a comparable against
> any lot in the table above. It is legitimate to say: *"Rwanda's top lots set the world specialty
> record on 21 October 2026 — the same origin and the same cup profile we export."*
>
> ⏱️ **Fades with time.** This is 3 days old on 24 Oct and still news. It is 12 days old at CIIE and
> will be a footnote. Use it as a **freshness wedge on outreach that goes out this week**, not as
> standing copy for the CIIE landing page — for the landing page, lead with the origin story and
> the live price band.""",
'tab3')

sub(
"""| Competitor | Country | Price (USD/kg) | Notes |
|-----------|---------|---------------|-------|
| Ethiopian naturals | Ethiopia | 6.50-8.00 | Established reputation |
| Kenya AA | Kenya | 7.00-9.50 | High SCA scores, premium |
| Brazil Santos | Brazil | 4.20-5.50 | Volume player, commodity |
| Rwanda A1 (our) | Rwanda | 4.80-5.50 | PROWTC + Rainforest cert, first-mover SA window |""",
"""| Competitor | Country | Price (USD/kg) | Notes |
|-----------|---------|-------------|-------|
| Ethiopian naturals | Ethiopia | 6.50-8.00 | Established reputation |
| Kenya AA | Kenya | 7.00-9.50 | High SCA scores, premium |
| Brazil Santos | Brazil | 4.20-5.50 | Volume player, commodity |
| **ICE Arabica C (benchmark)** | — | **6.75** | **Live, 24 Oct 2026 — the composite our band is anchored to** |
| **Rwanda A1 (our)** | Rwanda | **6.07-6.75** | Live band; Best of Rwanda 2026 top lot proved the ceiling |
| Rwanda A1 (legacy sheet) | Rwanda | ~~4.80-5.50~~ | *Superseded — 29% under benchmark, verification pending* |

> **Read this table with the benchmark row in it.** We are no longer the cheapest-looking option in
> the room without a reason — the reason is the **Best of Rwanda 2026 record lot and 87.49-91.81%
> SCA winners from the same origin**, plus the tariff position. That is a better story than being
> under the exchange composite.""",
'tab5')

# footer note about certifications
old_footer = """*v1 — Robusca VM | Tumelo Ramaphosa | Studex Meat | July 7, 2026*
*To use: Copy each table and paste into the corresponding tab in your Google Sheet*"""
new_footer = """*v2 — Robusca VM | Tumelo Ramaphosa | Studex Meat | 24 October 2026*
*To use: Copy each table and paste into the corresponding tab in your Google Sheet*

---

## ⚠️ BEFORE YOU SEND — three things this file still gets wrong

1. **"PROWTC Certified" / "Rainforest Alliance certified" — remove both.**
   `studex-meat/PRICE-SOURCE-REGISTRY.md` §4f records that **no source document exists for any
   Studex coffee certification**. The Rainforest Alliance claim was stripped from the coffee pages
   on 2026-10-21 precisely because it was unsourced, and "PROWTC" is a **prospect's** brand (an
   exporting house in Rwanda), not ours. Both sit in the EMAIL 1 subject line and bullets in this
   file and in `china-coffee-outreach.md`. A buyer who asks for the certificate and gets nothing
   loses the deal *and* our credibility. Say what is true: **grade, process, cup profile, origin,
   altitude, score** — all of which we can evidence from the cupping table.
2. **"Wildlife Verified"** in the subject lines — same problem, same fix.
3. **The old price sentence** ("FOB Kigali pricing from USD 4.80/kg") — replaced in v2 with the live
   band. See EMAIL 1 below.

> These are **email drafts, not sent copy** — no email was sent by this build. But they are one
> copy-paste from a buyer, so fix them before they go out."""
if s.count(old_footer) != 1:
    print(f"FAIL[footer]: count={s.count(old_footer)}")
    sys.exit(1)
s = s.replace(old_footer, new_footer)
edits.append('footer')

open(P, 'w', encoding='utf-8').write(s)
print("OK ->", P, "edits:", ", ".join(edits))
