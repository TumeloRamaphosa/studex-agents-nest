# LADDER LOCK — price integrity & caviar compliance report

- Generated: 2026-10-28T21:08:31+00:00
- Live storefront products: **48**
- Catalog rows: **66**
- Live pages checked: **4**
- Blocking findings: **15**

## Findings

### [BLOCKING] CAVIAR-SELL-WITHOUT-PERMIT — Retail / biltong landing (nudsduvyrc12): Publishes caviar prices (43 mentions) with an order path while the SA caviar permit stack is unassembled. A caviar sale without the stack is a seizure risk.
- **Evidence:** DFFE; ITAC frozen-fish notification; DAFF importer registration; SARS importer code + duty line; NRCS; CITES export permit + registered exporter code
- **Fix:** Pull the caviar offer from the purchase path until the permit stack exists. Keep the page as a permit-conditioned inquiry desk only.

### [BLOCKING] LADDER-CASE-ARBITRAGE — Wagyu Biltong Gold 7kg Box of 100 x 70g packets of Biltong Gold ! (Default Title) [live-storefront]: The 7.0kg case (R12,500) costs more than 7 x Default Title (R10,150). A buyer can beat the case by 18.8% on our own price sheet.
- **Evidence:** R12,500/7.0kg = R1,785.71/kg  vs  7 x R1,450 = R10,150
- **Fix:** Set the case at or below R10,150. A small bulk discount is fine — it is what makes the case the obvious choice.

### [BLOCKING] LADDER-CASE-ARBITRAGE — Wagyu Biltong Gold — 7kg Box (100 × 70g) (7kg Box) [catalog]: The 7.0kg case (R12,500) costs more than 7 x 1kg Box (R10,150). A buyer can beat the case by 18.8% on our own price sheet.
- **Evidence:** R12,500/7.0kg = R1,785.71/kg  vs  7 x R1,450 = R10,150
- **Fix:** Set the case at or below R10,150. A small bulk discount is fine — it is what makes the case the obvious choice.

### [BLOCKING] LADDER-INVERSION — 1.  AEROBIC FERMENTATION PROCESS (A3 - A4 Other Type of consumption (Low Grade) / 500g) [live-storefront]: A3 - A4 Other Type of consumption (Low Grade) / 500g costs R300.00/kg against R200.00/kg for the larger A3 - A4 Other Type of consumption (Low Grade) / 1kg — a 50% per-kilo penalty (limit for uncategorised: 45%).
- **Evidence:** R150/0.5kg = R300.00/kg  vs  R200/1.0kg = R200.00/kg
- **Fix:** Price A3 - A4 Other Type of consumption (Low Grade) / 500g at or below R200.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Wagyu Flat Iron Steak (500g) [catalog]: 500g costs R1,700.00/kg against R1,150.00/kg for the larger 1kg — a 48% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R850/0.5kg = R1,700.00/kg  vs  R1,150/1.0kg = R1,150.00/kg
- **Fix:** Price 500g at or below R1,150.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Luxury Wagyu Biltong (500g) [catalog]: 500g costs R900.00/kg against R650.00/kg for the larger 1kg — a 38% per-kilo penalty (limit for biltong: 15%).
- **Evidence:** R450/0.5kg = R900.00/kg  vs  R650/1.0kg = R650.00/kg
- **Fix:** Price 500g at or below R650.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A1 Top Speciality / 500g) [catalog]: A1 Top Speciality / 500g costs R500.00/kg against R380.00/kg for the larger A1 Top Speciality / 1kg — a 32% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R250/0.5kg = R500.00/kg  vs  R380/1.0kg = R380.00/kg
- **Fix:** Price A1 Top Speciality / 500g at or below R380.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A1 Top Speciality / 250g) [catalog]: A1 Top Speciality / 250g costs R600.00/kg against R380.00/kg for the larger A1 Top Speciality / 1kg — a 58% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R150/0.25kg = R600.00/kg  vs  R380/1.0kg = R380.00/kg
- **Fix:** Price A1 Top Speciality / 250g at or below R380.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A1 Top Speciality / 250g) [catalog]: A1 Top Speciality / 250g costs R600.00/kg against R500.00/kg for the larger A1 Top Speciality / 500g — a 20% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R150/0.25kg = R600.00/kg  vs  R250/0.5kg = R500.00/kg
- **Fix:** Price A1 Top Speciality / 250g at or below R500.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A2 Commercial / 500g) [catalog]: A2 Commercial / 500g costs R300.00/kg against R250.00/kg for the larger A2 Commercial / 1kg — a 20% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R150/0.5kg = R300.00/kg  vs  R250/1.0kg = R250.00/kg
- **Fix:** Price A2 Commercial / 500g at or below R250.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A2 Commercial / 250g) [catalog]: A2 Commercial / 250g costs R480.00/kg against R250.00/kg for the larger A2 Commercial / 1kg — a 92% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R120/0.25kg = R480.00/kg  vs  R250/1.0kg = R250.00/kg
- **Fix:** Price A2 Commercial / 250g at or below R250.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A2 Commercial / 250g) [catalog]: A2 Commercial / 250g costs R480.00/kg against R300.00/kg for the larger A2 Commercial / 500g — a 60% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R120/0.25kg = R480.00/kg  vs  R150/0.5kg = R300.00/kg
- **Fix:** Price A2 Commercial / 250g at or below R300.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A3-A4 / 500g) [catalog]: A3-A4 / 500g costs R300.00/kg against R200.00/kg for the larger A3-A4 / 1kg — a 50% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R150/0.5kg = R300.00/kg  vs  R200/1.0kg = R200.00/kg
- **Fix:** Price A3-A4 / 500g at or below R200.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A3-A4 / 250g) [catalog]: A3-A4 / 250g costs R400.00/kg against R200.00/kg for the larger A3-A4 / 1kg — a 100% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R100/0.25kg = R400.00/kg  vs  R200/1.0kg = R200.00/kg
- **Fix:** Price A3-A4 / 250g at or below R200.00/kg so the larger pack stays the volume anchor.

### [BLOCKING] LADDER-INVERSION — Aerobic Fermentation Process Coffee (A3-A4 / 250g) [catalog]: A3-A4 / 250g costs R400.00/kg against R300.00/kg for the larger A3-A4 / 500g — a 33% per-kilo penalty (limit for coffee: 15%).
- **Evidence:** R100/0.25kg = R400.00/kg  vs  R150/0.5kg = R300.00/kg
- **Fix:** Price A3-A4 / 250g at or below R300.00/kg so the larger pack stays the volume anchor.

### [WARN] CAVIAR-PERMIT-CONDITIONED — Caviar page (ess0ocgcd9f0): 38 caviar mention(s) published. Copy is permit-conditioned, so this is acceptable — but no purchase path may be added before the stack exists.
- **Evidence:** conditional language detected; no unconditional claim found
- **Fix:** Re-check before adding any caviar checkout or 'order' CTA.

### [WARN] CAVIAR-PERMIT-CONDITIONED — Coffee & hospitality (SA) (psq9xaisb9kf): 5 caviar mention(s) published. Copy is permit-conditioned, so this is acceptable — but no purchase path may be added before the stack exists.
- **Evidence:** conditional language detected; no unconditional claim found
- **Fix:** Re-check before adding any caviar checkout or 'order' CTA.

### [WARN] LADDER-ABOVE-CEILING — Wagyu Biltong Gold — 7kg Box (100 × 70g) (7kg Box) [catalog]: R1,785.71/kg is above the highest openly quoted SA biltong price (R1,053/kg) with no named benchmark.
- **Evidence:** Woolworths chilli snapsticks 150g — R157.99 / 150g = R1,053/kg
- **Fix:** Name the benchmark on the page, or bring the price into the band.

### [WARN] LADDER-ABOVE-CEILING — Wagyu Biltong Gold — 1kg (14 × 70g) (1kg Box) [catalog]: R1,450.00/kg is above the highest openly quoted SA biltong price (R1,053/kg) with no named benchmark.
- **Evidence:** Woolworths chilli snapsticks 150g — R157.99 / 150g = R1,053/kg
- **Fix:** Name the benchmark on the page, or bring the price into the band.

### [WARN] LADDER-INVERSION — 1.  AEROBIC FERMENTATION PROCESS (A1 Top Speciality / 500g) [live-storefront]: A1 Top Speciality / 500g costs R500.00/kg against R380.00/kg for the larger A1 Top Speciality / 1kg — a 32% per-kilo penalty (limit for uncategorised: 45%).
- **Evidence:** R250/0.5kg = R500.00/kg  vs  R380/1.0kg = R380.00/kg
- **Fix:** Price A1 Top Speciality / 500g at or below R380.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — 1.  AEROBIC FERMENTATION PROCESS (A2 Commercial Speciality / 500g) [live-storefront]: A2 Commercial Speciality / 500g costs R300.00/kg against R250.00/kg for the larger A2 Commercial Speciality / 1kg — a 20% per-kilo penalty (limit for uncategorised: 45%).
- **Evidence:** R150/0.5kg = R300.00/kg  vs  R250/1.0kg = R250.00/kg
- **Fix:** Price A2 Commercial Speciality / 500g at or below R250.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Luxury Wagyu Biltong | Buy Premium Wagyu Biltong South Africa | Studex Meat (500g) [live-storefront]: 500g costs R900.00/kg against R650.00/kg for the larger 1kg — a 38% per-kilo penalty (limit for simple: 45%).
- **Evidence:** R450/0.5kg = R900.00/kg  vs  R650/1.0kg = R650.00/kg
- **Fix:** Price 500g at or below R650.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Tomahawk Steak | Buy Premium Tomahawk Steak South Africa | Studex Meat (1kg) [live-storefront]: 1kg costs R350.00/kg against R275.00/kg for the larger 2kg — a 27% per-kilo penalty (limit for variable: 45%).
- **Evidence:** R350/1.0kg = R350.00/kg  vs  R550/2.0kg = R275.00/kg
- **Fix:** Price 1kg at or below R275.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Tri-Tip Steak (500g) [live-storefront]: 500g costs R1,100.00/kg against R950.00/kg for the larger 1kg — a 16% per-kilo penalty (limit for variable: 45%).
- **Evidence:** R550/0.5kg = R1,100.00/kg  vs  R950/1.0kg = R950.00/kg
- **Fix:** Price 500g at or below R950.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Sirloin Steak (500g) [live-storefront]: 500g costs R1,500.00/kg against R1,150.00/kg for the larger 1kg — a 30% per-kilo penalty (limit for variable: 45%).
- **Evidence:** R750/0.5kg = R1,500.00/kg  vs  R1,150/1.0kg = R1,150.00/kg
- **Fix:** Price 500g at or below R1,150.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Picanha Steak (500g) [live-storefront]: 500g costs R1,500.00/kg against R1,350.00/kg for the larger 1kg — a 11% per-kilo penalty (limit for variable: 45%).
- **Evidence:** R750/0.5kg = R1,500.00/kg  vs  R1,350/1.0kg = R1,350.00/kg
- **Fix:** Price 500g at or below R1,350.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Fillet Steak (500g) [live-storefront]: 500g costs R1,900.00/kg against R1,650.00/kg for the larger 1kg — a 15% per-kilo penalty (limit for variable: 45%).
- **Evidence:** R950/0.5kg = R1,900.00/kg  vs  R1,650/1.0kg = R1,650.00/kg
- **Fix:** Price 500g at or below R1,650.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Chuckeye Steak (500g) [live-storefront]: 500g costs R900.00/kg against R750.00/kg for the larger 1kg — a 20% per-kilo penalty (limit for variable: 45%).
- **Evidence:** R450/0.5kg = R900.00/kg  vs  R750/1.0kg = R750.00/kg
- **Fix:** Price 500g at or below R750.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Denver Steak (500g) [live-storefront]: 500g costs R1,500.00/kg against R1,050.00/kg for the larger 1kg — a 43% per-kilo penalty (limit for simple: 45%).
- **Evidence:** R750/0.5kg = R1,500.00/kg  vs  R1,050/1.0kg = R1,050.00/kg
- **Fix:** Price 500g at or below R1,050.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Sirloin Steak (500g) [catalog]: 500g costs R1,500.00/kg against R1,150.00/kg for the larger 1kg — a 30% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R750/0.5kg = R1,500.00/kg  vs  R1,150/1.0kg = R1,150.00/kg
- **Fix:** Price 500g at or below R1,150.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Fillet Steak (500g) [catalog]: 500g costs R1,900.00/kg against R1,650.00/kg for the larger 1kg — a 15% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R950/0.5kg = R1,900.00/kg  vs  R1,650/1.0kg = R1,650.00/kg
- **Fix:** Price 500g at or below R1,650.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Picanha Steak (500g) [catalog]: 500g costs R1,500.00/kg against R1,350.00/kg for the larger 1kg — a 11% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R750/0.5kg = R1,500.00/kg  vs  R1,350/1.0kg = R1,350.00/kg
- **Fix:** Price 500g at or below R1,350.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Rump Steak (500g) [catalog]: 500g costs R900.00/kg against R850.00/kg for the larger 1kg — a 6% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R450/0.5kg = R900.00/kg  vs  R850/1.0kg = R850.00/kg
- **Fix:** Price 500g at or below R850.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Chuckeye Steak (500g) [catalog]: 500g costs R900.00/kg against R750.00/kg for the larger 1kg — a 20% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R450/0.5kg = R900.00/kg  vs  R750/1.0kg = R750.00/kg
- **Fix:** Price 500g at or below R750.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Denver Steak (500g) [catalog]: 500g costs R1,500.00/kg against R1,050.00/kg for the larger 1kg — a 43% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R750/0.5kg = R1,500.00/kg  vs  R1,050/1.0kg = R1,050.00/kg
- **Fix:** Price 500g at or below R1,050.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Tomahawk Steak (1kg) [catalog]: 1kg costs R350.00/kg against R275.00/kg for the larger 2kg — a 27% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R350/1.0kg = R350.00/kg  vs  R550/2.0kg = R275.00/kg
- **Fix:** Price 1kg at or below R275.00/kg so the larger pack stays the volume anchor.

### [WARN] LADDER-INVERSION — Wagyu Tri-Tip Steak (500g) [catalog]: 500g costs R1,100.00/kg against R950.00/kg for the larger 1kg — a 16% per-kilo penalty (limit for beef: 45%).
- **Evidence:** R550/0.5kg = R1,100.00/kg  vs  R950/1.0kg = R950.00/kg
- **Fix:** Price 500g at or below R950.00/kg so the larger pack stays the volume anchor.

## Page exposure matrix

| Deploy | Page | HTTP | Caviar mentions | Unconditional claims | Caviar priced | Order path | Verdict |
|---|---|---|---|---|---|---|---|
| `oi28dhtke3yk` | Corporate gifting | 200 | 0 | 0 | False | True | CLEAN |
| `nudsduvyrc12` | Retail / biltong landing | 200 | 43 | 0 | True | True | BLOCK — caviar for sale |
| `ess0ocgcd9f0` | Caviar page | 200 | 38 | 0 | False | True | REVIEW — caviar, permit-conditioned |
| `psq9xaisb9kf` | Coffee & hospitality (SA) | 200 | 5 | 0 | False | True | REVIEW — caviar, permit-conditioned |
