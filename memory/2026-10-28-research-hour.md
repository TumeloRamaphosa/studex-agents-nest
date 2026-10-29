# 2026-10-28 — Research Hour (22:00 SAST)

**Brief:** `/workspace/research/2026-10-28.md`
**Topics:** Coffee board + China 2nd gate | Luxury meat e-commerce ladder

## Lead finding
`studex-corporate-gifting/src/App.tsx` = Silver R3,000 / Gold R7,000 / Platinum R15,000, **caviar in Gold + Platinum**. Live page + `dist/` = R1,299 / R2,499 / R4,999, no caviar. **Source never built/deployed.** SA caviar permit stack unassembled → do not ship as-is.

## Coffee
- ICE Arabica C **$285.69/lb (28 Oct)** — lowest since 9 Oct, −26.9% YoY. Brazil crop +34.8%; global consumption falling.
- Benchmarks to quote against: **C = $6.30/kg = $6,298/MT**; **NAEB Best of Rwanda 2026 auction (21 Oct) top lot $452/kg, average ≈$205/kg**. Our FOB $4.20–4.80/kg sits between them — **say which benchmark**.
- **China 2nd gate:** unified phytosanitary for all 53 African countries from **20 Jul 2026** (tariff gate was 1 May). Not on our sheet.
- **EUDR:** soluble coffee added to scope (~21 Oct). Large/medium **30 Dec 2026**, micro/small 30 Jun 2027. EU = 40% of global coffee imports, ~4/5 supplied by a handful of firms → relationship market.
- **GCC is the growing corridor:** SA→UAE +2.69% to ZAR 4.05bn; SA ag exports record US$4.1bn Q2 2026; SA biltong→ME +14% (2024), UAE+Saudi = 60%. Rwanda **DUBUY** (DP World) = free Kigali→UAE lane.

## Biltong / gifting
- Price defects: **500g R450 = R900/kg vs 1kg R650 = R650/kg (inverted)**; **7kg case R12,500 vs 7×1kg = R10,150 (19% arbitrage)**. Wagyu Gold at R1,785/kg has no visible benchmark (Woolworths tops out R1,053/kg).
- Festive window **opened 29 Oct, closes 13–15 Nov 2026**.
- Wedge: nobody in SA curates biltong + single-origin African coffee + caviar as a corporate box. **Caviar-free box is the 2026 product.**

## Build Hour assigned
1. Fix biltong ladder (500g → ≤R325; 7kg case → ≤R10,150) after verifying live storefront prices.
2. Quarantine gifting src + draft caviar-stripped tier variant in a branch file.
3. Browser-check studexmeat.com for purchasable caviar; re-base China FOB to "C + differential" with both benchmarks; add 20 Jul phytosanitary line.

## Notes
- `studex-products-catalog.csv` has **zero caviar rows**. Shopify Admin API still 401 → verify prices via public storefront only.
- memory_search unavailable (OpenAI embedding quota exhausted). Read files directly.
