/**
 * STUDEX BILTONG — LADDER INPUTS
 * Built: 2026-10-30 (Build Hour). Owner: Robusca / Studex Ops.
 *
 * Every input carries a source. ASSUMPTION is a label, not a shrug — an
 * assumption with a named owner is a thing Tumelo can close in one phone
 * call. A number with no source is a guess, and a guess that reaches a
 * customer is a liability.
 *
 * Imported by compute-ladder.mjs. Never edit the published ladder here — this
 * file holds the INPUTS, the generator holds the arithmetic.
 */

// ─────────────────────────────────────────────────────────────────────────────
// COST STACK
// ─────────────────────────────────────────────────────────────────────────────

export const COST_INPUTS = {
  rawBeefRarPerKg: {
    standardSilverside: {
      value: 140,
      source:
        'r/southafrica thread, Jul 2026 — "Retail bulk silverside is currently R130-150/kg". Midpoint taken. The same thread also notes "at R599/kg that is based on a raw beef price of around R200/kg", which is a useful independent sanity check.',
      confidence: 'MARKET-ANCHORED — needs Tumelo\u2019s invoice',
    },
    wagyuTrimmed: {
      value: 320,
      source:
        'ASSUMPTION — SA A-grade wagyu strip at wholesale, trimmed for biltong. NOT sourced. This is the number most likely to be wrong, which is exactly why the break-even table is printed.',
      confidence: 'ASSUMPTION — needs Tumelo\u2019s invoice',
    },
  },
  finishedYield: {
    value: 0.35,
    label: 'kg finished biltong per kg raw beef',
    source:
      'ASSUMPTION — wet-to-dry weight loss in curing. 1 kg raw -> 0.35 kg finished. Sensitive: every 0.05 of yield moves finished cost by roughly R130/kg.',
    confidence: 'ASSUMPTION — needs a yield test',
  },
  spicesMarinadeRarPerKg: {
    value: 45,
    source: 'ASSUMPTION — salt, coriander, chilli and cure packaging, per kg finished.',
    confidence: 'ASSUMPTION',
  },
  coldChainDispatchRarPerKg: {
    value: 22,
    source: 'ASSUMPTION — vacuum sealing, cold store, courier dispatch, per kg finished.',
    confidence: 'ASSUMPTION',
  },
  qaOverheadRarPerKg: {
    value: 65,
    source: 'ASSUMPTION — hygiene, QA and labour overhead allocated per kg finished.',
    confidence: 'ASSUMPTION',
  },
  packagingRarPerKg: {
    value: {
      luxury500g: 19,
      luxury1kg: 14,
      gold1kg: 59,
      goldCase7kg: 60,
    },
    label: 'Packaging per kg finished, by line and pack',
    source:
      'ASSUMPTION — Luxury 500g pouch + label R9.50; Luxury 1kg valve bag R14; Gold 1kg = 14 x 70g resealable pouches at R4.20 each (R58.80/kg, so R59); Gold 7kg case = 100 x 70g bulk liners (R420 per 7kg, so R60/kg). The two lines genuinely cost different to pack, which is part of why Gold can carry a premium.',
    confidence: 'ASSUMPTION',
  },
  goldLineRatio: {
    value: 2.2308,
    label: 'Gold 1kg price as a multiple of Luxury 1kg',
    source:
      'DERIVED from the live Shopify ladder: Gold 1kg R1,450 / Luxury 1kg R650 = 2.2308. This is a MARKET/BRAND relationship, not a cost one — the R45/kg packaging gap explains only 5% of it, so the rest is positioning. The proposal preserves the ratio rather than inventing a new architecture, then checks whether the result still clears the floor.',
    confidence: 'derived from live prices',
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// POLICY
// ─────────────────────────────────────────────────────────────────────────────

export const POLICY = {
  marginFloorPct: {
    value: 0.25,
    source:
      'POLICY — 25%, matching the wholesale coffee sheet and the caviar desk floor. A ladder below this is not a ladder.',
    confidence: 'policy',
  },
  smallPackPremiumCap: {
    value: 0.15,
    source:
      'POLICY — the per-kg premium a smaller pack may carry over the 1kg, capped at 15%. Market check: Woolworths charges R157.99 for 150g against R279.99 for 400g — a 50% per-kg premium at the snack end, roughly 25% at the 400g end. 15% is the disciplined number for a fresh-protein brand, not a confection.',
    confidence: 'policy',
  },
  caseSavingPct: {
    value: 0.08,
    source:
      'POLICY — the 7kg case must be at least 8% cheaper per kg than 7 x 1kg. The buyer has to be able to count the saving, or the case is a decoration.',
    confidence: 'policy',
  },
  roundingZar: {
    value: 5,
    source: 'POLICY — published prices round to the nearest R5.',
    confidence: 'policy',
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// THE TWO LIVE LADDERS
// ─────────────────────────────────────────────────────────────────────────────

export const LIVE_LADDERS = [
  {
    id: 'shopify',
    label: 'Shopify live store (studexmeat.com)',
    status: 'LIVE — structurally broken',
    source:
      'products.json variants, verified 28 Oct 2026; re-confirmed 30 Oct on the live product page studexmeat.com/products/wagyu-biltong (sale price R650.00, regular R812.50)',
    tiers: [
      { line: 'Luxury Wagyu Biltong', sizeKg: 0.5, label: '500g', price: 450, packKey: 'luxury500g' },
      { line: 'Luxury Wagyu Biltong', sizeKg: 1, label: '1kg', price: 650, packKey: 'luxury1kg' },
      { line: 'Wagyu Biltong Gold', sizeKg: 1, label: '1kg', price: 1450, packKey: 'gold1kg' },
      { line: 'Wagyu Biltong Gold', sizeKg: 7, label: '7kg case', price: 12500, packKey: 'goldCase7kg' },
    ],
  },
  {
    id: 'marketing',
    label: 'Marketing page + registry §2.1 (studex-biltong/index.html)',
    status: 'LIVE — right shape, thin money',
    source:
      'studex-biltong/index.html product grid, re-read 30 Oct; matches studex-meat/PRICE-SOURCE-REGISTRY.md §2.1. The 500g shows as "From R325" with no size stated on the card.',
    tiers: [
      { line: 'Luxury Wagyu Biltong', sizeKg: 0.5, label: '500g (from, size not stated on the card)', price: 325, packKey: 'luxury500g' },
      { line: 'Wagyu Biltong Gold', sizeKg: 1, label: '1kg', price: 1250, packKey: 'gold1kg' },
      { line: 'Wagyu Biltong Gold', sizeKg: 7, label: '7kg case', price: 8400, packKey: 'goldCase7kg' },
    ],
  },
]

// ─────────────────────────────────────────────────────────────────────────────
// BENCHMARKS — 8 SA, 4 US DTC. Sources and dates on every row.
// ─────────────────────────────────────────────────────────────────────────────

export const SA_BENCHMARKS = [
  {
    name: 'Woolworths — Free Range Chilli Beef Biltong Snapsticks',
    pack: '150g',
    price: 157.99,
    pricePerKg: 1053.27,
    source: 'Woolworths.co.za product page; the R1,053/kg was calculated by Newsday, Jul 2026',
    date: 'Oct 2026',
    note: 'The highest visible SA biltong price per kg. This is the ceiling of the SA retail market.',
  },
  {
    name: 'Woolworths — Free Range Sliced Beef Biltong',
    pack: '400g',
    price: 279.99,
    pricePerKg: 699.98,
    source: 'Woolworths.co.za product page',
    date: 'Oct 2026',
    note: 'The mainstream SA benchmark tier for a decent sliced biltong.',
  },
  {
    name: 'Woolworths — Sliced Beef Biltong (gifting range)',
    pack: '400g',
    price: 219.99,
    pricePerKg: 549.98,
    source: 'Woolworths.co.za gifting range page',
    date: 'Oct 2026',
    note: 'Lower cut / different range, same pack size.',
  },
  {
    name: 'Woolworths — Bulk Original Beef Biltong Snapsticks',
    pack: '500g',
    price: 219.99,
    pricePerKg: 439.98,
    source: 'Woolworths.co.za product A-6009195240318',
    date: 'Oct 2026',
    note: 'The value end of the SA market.',
  },
  {
    name: 'Woolworths — Free Range Sliced Beef Biltong',
    pack: '5 x 25g (125g)',
    price: 109.99,
    pricePerKg: 879.92,
    source: 'Woolworths.co.za product page',
    date: 'Oct 2026',
    note: 'Small-pack per-kg premium benchmark: +26% vs the 400g.',
  },
  {
    name: 'Checkers — Kalahari Biltong Moist Sliced Beef',
    pack: 'per kg',
    price: 429.99,
    pricePerKg: 429.99,
    source: 'Checkers.co.za product 10155402KG',
    date: 'Oct 2026',
    note: 'Mass-retail comparator.',
  },
  {
    name: 'Shoprite — Kalahari Bulk Biltong',
    pack: 'per kg',
    price: 129.99,
    pricePerKg: 129.99,
    source: 'Shoprite.co.za product page',
    date: 'Oct 2026',
    note: 'The floor of the SA market. Below this, nobody can buy.',
  },
  {
    name: 'Biltong Boytjies — Wagyu Biltong / Wagyu Drywors',
    pack: 'per kg',
    price: 549.99,
    pricePerKg: 549.99,
    source: 'biltongboytjies.co.za blog, Apr 2026 — "Most Biltong Shops will sell fresh Wagyu biltong or Wagyu drywors for R499.99-R599.99 Per KG"',
    date: 'Apr 2026',
    note: '🔑 The closest thing to a direct SA competitor on the word "Wagyu". This is the number our SA-facing product has to live with.',
  },
]

export const US_BENCHMARKS = [
  {
    name: 'Biltong Depot — Original Biltong with Fat (slab subscription)',
    pack: '1 lb',
    priceUsd: 35.99,
    source: 'biltongdepot.com product page',
    date: 'Oct 2026',
  },
  {
    name: 'BeefSnacksUSA — Monthly Biltong',
    pack: '1 lb',
    priceUsd: 33.0,
    source: 'beefsnacksusa.com product page — subscribe and save 10%',
    date: 'Oct 2026',
  },
  {
    name: 'Lowfeld Soul Food — Beef Biltong Slices',
    pack: '1 lb',
    priceUsd: 33.99,
    source: 'lowfeld-soul-food.com product page',
    date: 'Oct 2026',
  },
  {
    name: 'The Grub Company — Bulk Biltong',
    pack: '1 lb',
    priceUsd: 58.0,
    source: 'thegrubcompany.com blog, Jul 2026',
    date: 'Oct 2026',
  },
]

export const FX_USD_ZAR = {
  value: 16.64,
  source:
    'frankfurter.dev (ECB reference) 2026-10-29; cross-check exchangerate-api 16.6339 — agree within 0.04%. Higher of the two used.',
  confidence: 'verified',
}
