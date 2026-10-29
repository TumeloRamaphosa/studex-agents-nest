#!/usr/bin/env node
/**
 * STUDEX SA B2B COFFEE — WHOLESALE PRICE SHEET CALCULATOR
 * Built: 2026-10-29 (Build Hour). Owner: Robusca / Studex Ops.
 *
 * WHY THIS FILE EXISTS
 * --------------------
 * A published price sheet and the internal cost model that floors it are two
 * numbers that must never disagree. Last night the house was bitten by a
 * source/deploy divergence where the sheet said one thing and the live page
 * said another. So: every published number in `sa-hospitality-coffee/index.html`
 * and every number in `sa-b2b-coffee/WHOLESALE-PRICE-SHEET.md` is emitted from
 * THIS FILE. Change an input here, re-run, and both move together.
 *
 * 🔑 COST DISCIPLINE
 * The floor is computed from a landed-cost model built on the CURRENT published
 * green FOB band ($6.07-6.75/kg, studex-price-sheet). That band is ~40% above
 * the older $3,400-5,200/MT table still sitting on the live hospitality page.
 * We cost on the HIGH end of the band on purpose: a floor that is only true at
 * the low end is not a floor. The band itself is flagged "re-verify before
 * quoting" on the price sheet and is reconciled in the Assumptions Register.
 *
 * NEVER publish landed cost, farm-gate cost, duty/VAT/FX assumptions or the
 * margin floor on a public page (studex-meat/PRICE-SOURCE-REGISTRY.md §5).
 * This script emits a PUBLIC table and an INTERNAL table separately.
 *
 * Run:  node sa-b2b-coffee/compute-price-sheet.mjs
 * Out:  sa-b2b-coffee/price-sheet.generated.json  (both tables + every input)
 */

import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))

// ─────────────────────────────────────────────────────────────────────────────
// INPUTS — every one carries a source and a date. Unverified ones are marked.
// ─────────────────────────────────────────────────────────────────────────────

const INPUTS = {
  // ── Market ──────────────────────────────────────────────────────────────
  fxUsdZar: {
    value: 16.64,
    label: 'FX USD/ZAR',
    source: 'frankfurter.dev (ECB reference) 2026-10-29; cross-check exchangerate-api 16.6339 — agree within 0.04%. Higher of the two used, so the cost side is never understated.',
    confidence: 'verified',
  },
  greenFobUsdPerKg: {
    value: 6.75,
    label: 'Green coffee FOB, high end of our band',
    source: 'Our published Kigali FOB band $6.07-6.75/kg (studex-price-sheet/dist/index.html, "Live desk — re-verify before quoting"). TOP of band used: a floor is only a floor at worst-case cost.',
    confidence: 'UNVERIFIED — band pending re-verification',
  },
  greenFobBandLowUsdPerKg: {
    value: 6.07,
    label: 'Green coffee FOB, low end of band',
    source: 'Same source as above. Used only for the sensitivity table.',
    confidence: 'UNVERIFIED',
  },
  oceanFreightUsdPerKg: {
    value: 0.07,
    label: 'Ocean freight + insurance, origin → Durban',
    source: 'ASSUMPTION — $70/tonne on Kigali/Mombasa–Durban. Needs a forwarder quote.',
    confidence: 'ASSUMPTION — needs forwarder quote',
  },
  importDutyRate: {
    value: 0,
    label: 'Import duty on green coffee',
    source: 'ASSUMPTION — treated as 0% for green coffee into SA. NOT broker-confirmed. If this is wrong the whole floor moves.',
    confidence: 'ASSUMPTION — broker to confirm',
  },
  portClearingZarPerKg: {
    value: 1.8,
    label: 'Port handling, clearing, inland to roastery',
    source: 'ASSUMPTION — R1.80/kg green.',
    confidence: 'ASSUMPTION',
  },
  // ── Roasting ────────────────────────────────────────────────────────────
  roastYield: {
    value: 0.85,
    label: 'Roast yield (kg roasted per kg green)',
    source: 'ASSUMPTION — 15% weight loss on a filter roast. 1 kg green -> 0.85 kg roasted.',
    confidence: 'ASSUMPTION',
  },
  roastingCostZarPerKg: {
    value: 38,
    label: 'Roasting cost',
    source: 'ASSUMPTION — R38/kg roasted (energy, labour, depreciation, roast loss).',
    confidence: 'ASSUMPTION — needs roastery quote',
  },
  packZarPerKg: {
    value: { bag1kg: 11, bulk5kg: 8, bulk20kg: 6, bulk30kg: 6 },
    label: 'Packaging per kg roasted',
    source: 'ASSUMPTION — 1kg valve bag + label R11; 5kg R8; 20kg/30kg R6.',
    confidence: 'ASSUMPTION',
  },
  // ── Commercial policy ───────────────────────────────────────────────────
  targetMarginPct: {
    value: 0.25,
    label: 'Target gross margin used to set the floor',
    source: 'POLICY — 25%. Lower than the 30% used on the caviar desk, because a volume-tiered wholesale sheet with no headroom is not a wholesale sheet. The margin actually achieved at every published tier is printed in the internal sheet.',
    confidence: 'policy',
  },
  roundingZar: {
    value: 5,
    label: 'Published prices round to the nearest R5',
    source: 'POLICY — a price sheet with R396.32 on it is not a price sheet.',
    confidence: 'policy',
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// PUBLISHED LIST PRICES — what is already live on sa-hospitality-coffee.
// Changing these changes a published price. They are inputs, not outputs.
// ─────────────────────────────────────────────────────────────────────────────

const ORIGINS = [
  { key: 'washed', name: 'Washed', profile: 'Clean, bright, classic body — the everyday house coffee', listZarPerKg: 400 },
  { key: 'honey', name: 'Honey', profile: 'Sweet, rounded, gentle fruit — a step up on filter', listZarPerKg: 350 },
  { key: 'aerobic', name: 'Aerobic', profile: 'Winey, wine-like depth, high clarity — specialty menu', listZarPerKg: 380 },
  { key: 'natural', name: 'Natural', profile: 'Fruity, full, syrupy — espresso and signature brews', listZarPerKg: 270 },
]

const TIERS = [
  { key: 'bag1kg', label: '1 kg', discountPct: 0, pack: 'bag1kg', moq: '5 kg', note: 'Sample & small accounts' },
  { key: 'bulk5kg', label: '5 kg', discountPct: 0.04, pack: 'bulk5kg', moq: '5 kg', note: 'Café accounts' },
  { key: 'bulk20kg', label: '20 kg', discountPct: 0.08, pack: 'bulk20kg', moq: '20 kg', note: 'Restaurant & boutique hotel' },
  { key: 'bulk30kg', label: '30 kg +', discountPct: 0.12, pack: 'bulk30kg', moq: '30 kg', note: 'Hotel group & scheduled supply' },
]

const VAT_RATE = 0.15

// ─────────────────────────────────────────────────────────────────────────────
// MODEL
// ─────────────────────────────────────────────────────────────────────────────

const roundTo = (n, step) => Math.round(n / step) * step

function landedCost({ fobUsd = INPUTS.greenFobUsdPerKg.value } = {}) {
  const fx = INPUTS.fxUsdZar.value
  const freight = INPUTS.oceanFreightUsdPerKg.value
  const duty = INPUTS.importDutyRate.value
  const greenLandedZarPerKg =
    (fobUsd + freight) * (1 + duty) * fx + INPUTS.portClearingZarPerKg.value
  const greenPerKgRoasted = greenLandedZarPerKg / INPUTS.roastYield.value
  return { greenLandedZarPerKg, greenPerKgRoasted }
}

function buildTable(fobUsd = INPUTS.greenFobUsdPerKg.value) {
  const { greenLandedZarPerKg, greenPerKgRoasted } = landedCost({ fobUsd })
  const target = INPUTS.targetMarginPct.value

  const tiers = TIERS.map((t) => {
    const pack = INPUTS.packZarPerKg.value[t.pack]
    const landed = greenPerKgRoasted + INPUTS.roastingCostZarPerKg.value + pack
    const floor = landed / (1 - target)
    return { ...t, packZarPerKg: pack, landedZarPerKg: round(landed, 2), floorZarPerKg: round(floor, 2) }
  })

  const origins = ORIGINS.map((o) => {
    const cells = tiers.map((t) => {
      const discounted = o.listZarPerKg * (1 - t.discountPct)
      const rounded = roundTo(discounted, INPUTS.roundingZar.value)
      const floorRounded = roundTo(t.floorZarPerKg, INPUTS.roundingZar.value)
      const floorBinds = rounded < floorRounded
      const price = floorBinds ? floorRounded : rounded
      const margin = (price - t.landedZarPerKg) / price
      return {
        tier: t.key,
        listZarPerKg: o.listZarPerKg,
        priceZarPerKg: price,
        priceZarPerKgVatIncl: round(price * (1 + VAT_RATE), 2),
        landedZarPerKg: t.landedZarPerKg,
        floorZarPerKg: t.floorZarPerKg,
        floorBinds,
        marginPct: round(margin * 100, 1),
      }
    })
    return { ...o, cells }
  })

  return { fobUsd, greenLandedZarPerKg: round(greenLandedZarPerKg, 2), greenPerKgRoasted: round(greenPerKgRoasted, 2), tiers, origins }
}

const round = (n, d = 2) => Math.round(n * 10 ** d) / 10 ** d

// ─────────────────────────────────────────────────────────────────────────────
// SERVICE LINES — priced separately, each with its own cost basis.
// ─────────────────────────────────────────────────────────────────────────────

const SERVICES = [
  {
    key: 'sample-pack',
    name: 'Sample pack — 5 x 250 g cupping set',
    price: 'R495',
    priceVatIncl: 'R569',
    unit: 'per pack (5 origins x 250 g)',
    credit: 'Fully credited against your first order of 20 kg or more.',
    costBasis:
      'Product at list R350 (5 x 250 g across the four origins) + R85 sample packing = R435. Priced at R495 to cover the pack, and credited back so the acquisition cost is recovered on the first real order.',
    confidence: 'COSTED from published list prices + packing assumption',
  },
  {
    key: 'training-workshop',
    name: 'Barista training — foundations workshop',
    price: 'R7,500',
    priceVatIncl: 'R8,625',
    unit: 'per on-site day, up to 8 staff',
    credit: 'Travel outside Gauteng quoted separately, at cost.',
    costBasis:
      'Trainer day R2,500 + travel/accommodation R1,000 + materials R750 + consumables R1,000 = R5,250. Priced at R7,500 (~30% margin). Benchmarked against SA barista schools at R1,500-3,000 per person — R938 per head here.',
    confidence: 'ASSUMPTION — trainer day rate not confirmed',
  },
  {
    key: 'training-retainer',
    name: 'Barista training — monthly retainer',
    price: 'R3,500',
    priceVatIncl: 'R4,025',
    unit: 'per month, quarterly minimum',
    credit: 'One on-site half-day per month, up to 6 staff. 3-month minimum: R10,500.',
    costBasis:
      'Half-day session ~R1,800 (trainer R1,250 + travel R550). Priced at R3,500/month. The retainer is the wedge: it turns a transactional bean sale into a recurring account, and it is the one thing the office-coffee-service majors do not offer.',
    confidence: 'ASSUMPTION — trainer day rate not confirmed',
  },
  {
    key: 'in-room-sachet',
    name: 'In-room single-serve sachet',
    price: 'R3.95',
    priceVatIncl: 'R4.54',
    unit: 'per 2 g sachet, 1,000+ units',
    credit: 'R4.20 each at 500-999 units. R1,500 one-off print setup. Case of 1,000: R3,950.',
    costBasis:
      'Coffee at the 30 kg tier (R240/kg) = R0.48 per 2 g sachet + sachet film, print and fill R1.20 = R1.67. Priced at R3.95. Custom-printed with the hotel brand — the hotel keeps the margin on the cup and the room sees the brand, not ours.',
    confidence: 'COSTED from the 30 kg tier price + packaging assumption',
  },
]

const LOGISTICS = [
  { label: 'Roasting', value: 'Roasted to order. Dispatched within 2 business days of order.' },
  { label: 'Delivery', value: 'Free on orders over R850 in Gauteng, over R1,500 nationally. Below that R95 (Gauteng) / R135 (national).' },
  { label: 'Delivery time', value: '48 hours Gauteng, KZN, Cape Town. 72 hours nationally.' },
  { label: 'Payment', value: '30-day terms on account after the first order; card or EFT for the first order.' },
  { label: 'Green stock', value: 'Green lots land Durban on a 3-4 week cycle from FOB. Stock dates quoted per order.' },
]

// ─────────────────────────────────────────────────────────────────────────────
// SENSITIVITY — what breaks the floor
// ─────────────────────────────────────────────────────────────────────────────

function sensitivity() {
  const cases = [
    { label: 'Band low (green $6.07/kg)', fob: INPUTS.greenFobBandLowUsdPerKg.value },
    { label: 'Band high (green $6.75/kg) — published floor', fob: INPUTS.greenFobUsdPerKg.value },
    { label: 'Stress (green $7.50/kg)', fob: 7.5 },
  ]
  return cases.map((c) => {
    const t = buildTable(c.fob)
    const worst = t.origins
      .flatMap((o) => o.cells.map((cell) => ({ origin: o.name, tier: cell.tier, margin: cell.marginPct, floorBinds: cell.floorBinds })))
      .sort((a, b) => a.margin - b.margin)[0]
    return { ...c, greenLandedZarPerKg: t.greenLandedZarPerKg, worstCell: worst }
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// EMIT
// ─────────────────────────────────────────────────────────────────────────────

const table = buildTable()
const out = {
  generatedAt: new Date().toISOString(),
  publicSheet: { origins: table.origins, tiers: table.tiers },
  internalModel: {
    inputs: INPUTS,
    greenLandedZarPerKg: table.greenLandedZarPerKg,
    greenPerKgRoasted: table.greenPerKgRoasted,
    landedByTier: table.tiers.map((t) => ({ tier: t.key, landedZarPerKg: t.landedZarPerKg, floorZarPerKg: t.floorZarPerKg })),
    floorBinds: table.origins.flatMap((o) =>
      o.cells.filter((c) => c.floorBinds).map((c) => ({ origin: o.name, tier: c.tier, price: c.priceZarPerKg, floor: c.floorZarPerKg }))),
    services: SERVICES,
    logistics: LOGISTICS,
    sensitivity: sensitivity(),
  },
}

mkdirSync(HERE, { recursive: true })
writeFileSync(join(HERE, 'price-sheet.generated.json'), JSON.stringify(out, null, 2))

// ── Console summary ────────────────────────────────────────────────────────
const pad = (s, n) => String(s).padEnd(n)
const padL = (s, n) => String(s).padStart(n)
console.log('\n=== STUDEX SA B2B COFFEE — WHOLESALE PRICE SHEET ===')
console.log(`generated ${out.generatedAt}`)
console.log(`\nFX ${INPUTS.fxUsdZar.value} | green FOB $${INPUTS.greenFobUsdPerKg.value}/kg (band top)`)
console.log(`green landed R${table.greenLandedZarPerKg}/kg -> R${table.greenPerKgRoasted}/kg roasted equivalent\n`)
console.log('LANDED BY TIER (internal):')
for (const t of table.tiers) {
  console.log(`  ${pad(t.label, 8)} landed R${padL(t.landedZarPerKg, 7)}  floor@25% R${padL(t.floorZarPerKg, 7)}`)
}
console.log('\nPUBLIC TIER TABLE (ex VAT):')
console.log(`  ${pad('Origin', 10)} ${TIERS.map((t) => padL(t.label, 9)).join('')}`)
for (const o of table.origins) {
  const cells = o.cells.map((c) => padL('R' + c.priceZarPerKg.toLocaleString('en-ZA') + (c.floorBinds ? '*' : ''), 9)).join('')
  console.log(`  ${pad(o.name, 10)} ${cells}`)
}
console.log('  * = margin floor binds (discount capped)')
console.log('\nMARGIN AT EACH PUBLISHED TIER (internal):')
for (const o of table.origins) {
  console.log(`  ${pad(o.name, 10)} ${o.cells.map((c) => padL(c.marginPct + '%', 9)).join('')}`)
}
console.log('\nSENSITIVITY:')
for (const s of out.internalModel.sensitivity) {
  console.log(`  ${pad(s.label, 42)} green landed R${padL(s.greenLandedZarPerKg, 7)}  worst cell ${pad(s.worstCell.origin + ' ' + s.worstCell.tier, 18)} ${s.worstCell.margin}%${s.worstCell.floorBinds ? ' (floor binds)' : ''}`)
}
console.log(`\nFloor-binding cells: ${out.internalModel.floorBinds.length}`)
console.log(`written: ${join(HERE, 'price-sheet.generated.json')}\n`)
