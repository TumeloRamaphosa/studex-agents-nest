#!/usr/bin/env node
/**
 * STUDEX GREEN COFFEE — SINGLE FOB BAND CARD
 * Built: 2026-10-30 (Build Hour). Owner: Robusca / Studex Ops.
 *
 * WHY THIS FILE EXISTS
 * --------------------
 * As of 30 Oct 2026 Studex had THREE green-coffee FOB numbers in circulation:
 *
 *   1. USD 3,400-5,200/MT   the multi-origin table, published on the coffee pages
 *   2. USD 4,200-4,800/MT   Rwanda A1, sent to a buyer in the PROWTC offer
 *   3. USD 6.07-6.75/kg     the internal band, used to FLOOR the wholesale sheet
 *
 * A buyer can price a contract off any of them. Two of them disagree with the
 * third. One of them sits above the ceiling of the entire UAE green import
 * range (IndexBox, Sep 2026: $2.50-6.50/kg) — so if #3 is true we are priced
 * out of the Gulf by construction, before a single buyer says no.
 *
 * This script does ONE job: it reconciles the three, states which one is
 * published, which one is unverified, and prices the difference in rand per
 * bag so the owner can see what the ambiguity actually costs.
 *
 * 🔑 THE MODEL IS THE SAME MODEL the wholesale price sheet uses. Verified
 * against `sa-b2b-coffee/price-sheet.generated.json`:
 *   landed green (R/kg) = (FOB $/kg + freight $/kg) x FX + port clearing
 *   cost per kg ROASTED  = landed green / roast yield + roasting + packaging
 *   margin %              = (price - cost) / price
 * At the published band-high the Natural 30 kg+ tier reproduces the published
 * 25.2% margin EXACTLY, and at band-low reproduces 30.7% EXACTLY. If this
 * script ever stops reproducing those numbers, the model has been changed
 * under the price sheet and both must be re-based together.
 *
 * Run:  node coffee-fob-band/compute-band-card.mjs
 * Out:  coffee-fob-band/band.generated.json   (machine)
 *       coffee-fob-band-card.md                (the one-page card, human)
 */

import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = join(HERE, '..')

// ─────────────────────────────────────────────────────────────────────────────
// INPUTS — every one carries a source. Unverified ones are marked UNVERIFIED.
// ─────────────────────────────────────────────────────────────────────────────

const INPUTS = {
  fxUsdZar: {
    value: 16.64,
    label: 'FX USD/ZAR',
    source: 'frankfurter.dev (ECB reference) 2026-10-29; cross-check exchangerate-api 16.6339. Higher of the two used, so the cost side is never understated.',
    confidence: 'verified',
  },
  oceanFreightUsdPerKg: {
    value: 0.07,
    label: 'Ocean freight + insurance, origin to Durban',
    source: 'ASSUMPTION — $70/tonne on Kigali/Mombasa–Durban. Needs a forwarder quote.',
    confidence: 'ASSUMPTION — needs forwarder quote',
  },
  portClearingZarPerKg: {
    value: 1.8,
    label: 'Port handling, clearing, inland to roastery',
    source: 'ASSUMPTION — R1.80/kg green.',
    confidence: 'ASSUMPTION',
  },
  roastYield: {
    value: 0.85,
    label: 'Roast yield (kg roasted per kg green)',
    source: 'ASSUMPTION — 15% weight loss on a filter roast.',
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
  marginFloorPct: {
    value: 0.25,
    label: 'Margin floor used to price the published tiers',
    source: 'POLICY — 25% (sa-b2b-coffee/WHOLESALE-PRICE-SHEET.md). A 30% floor would forbid the entire volume ladder.',
    confidence: 'policy',
  },
  uaeImportCeilingUsdPerKg: {
    value: 6.5,
    label: 'UAE green coffee import price ceiling',
    source: 'IndexBox, Sep 2026 — UAE green coffee import range $2.50-6.50/kg.',
    confidence: 'external benchmark',
  },
}

// ─────────────────────────────────────────────────────────────────────────────
// THE THREE BANDS
// ─────────────────────────────────────────────────────────────────────────────

const BANDS = [
  {
    id: 'published-a1',
    label: 'PUBLISHED — Rwanda A1, 17+ screen, wet polished, 20 MT',
    fobUsdPerKg: [4.2, 4.8],
    fobUsdPerMt: [4200, 4800],
    status: 'FOUND',
    owner: 'studex-meat/PRICE-SOURCE-REGISTRY.md §2.6 (owner: studex-wildlife-coffee-vite/dist/index.html)',
    note: 'The buyer-facing number. It is what the PROWTC offer quoted and what the coffee pages carry.',
  },
  {
    id: 'published-a2',
    label: 'PUBLISHED — Rwanda A2, 15–16 screen, 40 MT',
    fobUsdPerKg: [3.6, 4.0],
    fobUsdPerMt: [3600, 4000],
    status: 'FOUND',
    owner: 'studex-meat/PRICE-SOURCE-REGISTRY.md §2.6 (owner: studex-wildlife-coffee-vite/dist/index.html)',
    note: 'The commercial grade. Sits below A1; the gap IS the cupping score being monetised.',
  },
  {
    id: 'published-custom-blend',
    label: 'PUBLISHED — Custom blend, MOQ 5 MT',
    fobUsdPerKg: [3.8, 3.8],
    fobUsdPerMt: [3800, 3800],
    status: 'FOUND',
    owner: 'studex-meat/PRICE-SOURCE-REGISTRY.md §2.6',
    note: 'The size Ethiopia cannot service. This is the CIIE pitch, not the commodity pitch.',
  },
  {
    id: 'internal-price-sheet',
    label: 'INTERNAL COST MODEL — the band the wholesale sheet floors on',
    fobUsdPerKg: [6.07, 6.75],
    fobUsdPerMt: [6070, 6750],
    status: 'UNVERIFIED',
    owner: 'studex-price-sheet/dist/index.html ("Live desk — re-verify before quoting"); consumed by sa-b2b-coffee/compute-price-sheet.mjs',
    note: 'FLAGGED UNVERIFIED in our own assumptions register. Not traceable to any published table. Sits ABOVE the UAE import ceiling.',
  },
]

// The published origin-portfolio table — the third number the brief flagged.
const ORIGIN_PORTFOLIO = {
  label: 'PUBLISHED — origin portfolio table (multi-origin)',
  rangeUsdPerMt: [3400, 5200],
  status: 'FOUND',
  owner: 'studex-meat/PRICE-SOURCE-REGISTRY.md §2.6',
  note: 'This is NOT a competing band for the same product — it is a different SCOPE (Uganda 3,400 low, SA Bourbon 5,200 high). Rwanda A1 at 4,200-4,800 sits INSIDE it.',
}

// The one number that is not reconcilable.
const INTERNAL_UNRECONCILED = true

// ─────────────────────────────────────────────────────────────────────────────
// THE SHOPFLOOR: published retail tiers whose floor depends on the band
// ─────────────────────────────────────────────────────────────────────────────

const PUBLISHED_TIERS = [
  { origin: 'Natural', tier: '30 kg +', packZarPerKg: 6, priceZarPerKg: 240 },
  { origin: 'Honey', tier: '30 kg +', packZarPerKg: 6, priceZarPerKg: 310 },
  { origin: 'Washed', tier: '30 kg +', packZarPerKg: 6, priceZarPerKg: 350 },
]

// ─────────────────────────────────────────────────────────────────────────────
// CALCULATION
// ─────────────────────────────────────────────────────────────────────────────

const landedGreenZarPerKg = (fobUsdPerKg) =>
  (fobUsdPerKg + INPUTS.oceanFreightUsdPerKg.value) * INPUTS.fxUsdZar.value +
  INPUTS.portClearingZarPerKg.value

const roastedCostZarPerKg = (landedGreen, packZarPerKg) =>
  landedGreen / INPUTS.roastYield.value +
  INPUTS.roastingCostZarPerKg.value +
  packZarPerKg

const marginPct = (price, cost) => (price - cost) / price

const scenarios = [
  {
    id: 'a1-low',
    label: 'A1 band LOW — $4.20/kg',
    fob: 4.2,
    provenance: 'PUBLISHED (registry §2.6, lower bound of Rwanda A1)',
  },
  {
    id: 'a1-high',
    label: 'A1 band HIGH — $4.80/kg',
    fob: 4.8,
    provenance: 'PUBLISHED (registry §2.6, upper bound of Rwanda A1) — the conservative published case',
  },
  {
    id: 'internal-low',
    label: 'Internal band LOW — $6.07/kg',
    fob: 6.07,
    provenance: 'UNVERIFIED (price sheet assumption register)',
  },
  {
    id: 'internal-high',
    label: 'Internal band HIGH — $6.75/kg',
    fob: 6.75,
    provenance: 'UNVERIFIED (price sheet assumption register) — what the sheet actually floors on',
  },
].map((s) => {
  const landed = landedGreenZarPerKg(s.fob)
  return {
    ...s,
    fobUsdPerMt: s.fob * 1000,
    landedGreenZarPerKg: round(landed),
    roastedCostZarPerKg: round(roastedCostZarPerKg(landed, 6)),
    aboveUaeCeiling: s.fob > INPUTS.uaeImportCeilingUsdPerKg.value,
    tiers: PUBLISHED_TIERS.map((t) => {
      const cost = roastedCostZarPerKg(landed, t.packZarPerKg)
      const margin = marginPct(t.priceZarPerKg, cost)
      const floorPrice = cost / (1 - INPUTS.marginFloorPct.value)
      return {
        ...t,
        costZarPerKg: round(cost),
        marginPct: round(margin * 100, 1),
        clearsFloor: margin >= INPUTS.marginFloorPct.value,
        priceAtFloorZarPerKg: round(floorPrice),
        headroomVsPublishedZarPerKg: round(t.priceZarPerKg - floorPrice),
      }
    }),
  }
})

// The delta that decides the commercial question.
const internalHigh = scenarios.find((s) => s.id === 'internal-high')
const a1High = scenarios.find((s) => s.id === 'a1-high')
const a1Low = scenarios.find((s) => s.id === 'a1-low')

const gap = {
  landedDeltaZarPerKg: round(internalHigh.landedGreenZarPerKg - a1High.landedGreenZarPerKg),
  roastedDeltaZarPerKg: round(internalHigh.roastedCostZarPerKg - a1High.roastedCostZarPerKg),
  per30kgBagZar: round((internalHigh.landedGreenZarPerKg - a1High.landedGreenZarPerKg) / 0.85 * 30),
  per20MTContainerZar: round((internalHigh.landedGreenZarPerKg - a1High.landedGreenZarPerKg) * 20000),
  marginGapPointsAt30kg: round(Math.abs(
    internalHigh.tiers.find((t) => t.origin === 'Natural').marginPct -
    a1High.tiers.find((t) => t.origin === 'Natural').marginPct
  )),
}

// ── Self-check: the model must reproduce the published price sheet exactly ──
// If it does not, the model has drifted from sa-b2b-coffee and both must be
// re-based together. This is the assertion that failed in the past.
const SELFTEST = [
  { scenario: 'internal-high', tier: 'Natural', expectMarginPct: 25.2, tolerance: 0.15 },
  { scenario: 'internal-low', tier: 'Natural', expectMarginPct: 30.7, tolerance: 0.15 },
]
const selfTestResults = SELFTEST.map((t) => {
  const s = scenarios.find((x) => x.id === t.scenario)
  const got = s.tiers.find((x) => x.origin === t.tier).marginPct
  const pass = Math.abs(got - t.expectMarginPct) <= t.tolerance
  return { ...t, got, pass }
})
const selfTestPassed = selfTestResults.every((r) => r.pass)

// ── Files that still carry a green FOB number ──────────────────────────────
const FILES_NEEDING_CORRECTION = [
  {
    file: 'studex-meat/PRICE-SOURCE-REGISTRY.md',
    section: '§2.6',
    carries: '$3,400-5,200/MT origin table + $4,200-4,800 A1 + $3,600-4,000 A2 + $3,800 custom blend + $28-45/kg samples',
    status: 'SOURCE OF TRUTH — this file owns the published band. Do not edit the numbers; edit the status fields here if the supplier re-bases.',
    action: 'Keep. Add the re-verified band + date once the supplier answers.',
  },
  {
    file: 'studex-os/proposals/rwanda-offer-PROWTC-2026-07.json',
    section: 'contact.email',
    carries: 't.ramaphosa@studexwildlife.com — DEAD, the buyer cannot reply',
    status: '🔴 ACTION REQUIRED — re-issue with a live reply address and the re-based band',
    action: 'Replace contact.email with info@studexmeat.com; keep the price strings, which already match registry §2.6.',
  },
  {
    file: 'sa-b2b-coffee/compute-price-sheet.mjs',
    section: 'INPUTS.greenFobUsdPerKg',
    carries: '$6.75/kg (band high) — UNVERIFIED',
    status: '🔴 COST FLOOR IS 32%+ HIGHER THAN THE PUBLISHED BAND',
    action: 'Re-base to the supplier-confirmed band, then re-run. The published tier prices only move if a tier falls below the floor.',
  },
  {
    file: 'sa-b2b-coffee/price-sheet.generated.json',
    section: 'assumptions / sensitivity',
    carries: '$6.07 and $6.75 sensitivity poles',
    status: '🔴 GENERATED — do not hand-edit; re-run the generator',
    action: 'Regenerate after the band is re-based.',
  },
  {
    file: 'sa-b2b-coffee/WHOLESALE-PRICE-SHEET.md',
    section: 'assumption #1 + assumption #10',
    carries: '"re-verify before quoting" + the live-page contradiction note',
    status: '🟡 ALREADY HANDLED — the live page stopped publishing green FOB numbers on 29 Oct (now "quoted on request")',
    action: 'Update assumption #10 to say the contradiction is closed.',
  },
  {
    file: 'sa-hospitality-coffee/index.html',
    section: 'green catalogue',
    carries: 'NO published green price — "FOB pricing is quoted on request against the current season\'s band"',
    status: '✅ ALREADY CORRECT — no number to fix',
    action: 'None. Leave alone.',
  },
  {
    file: 'ciie-buyer-brief/src/App.tsx',
    section: 'stats bar + spec table + commercial terms',
    carries: 'MANGLED price strings (USD 4.20-4.20-4.80/kg; USD 4.80-3.60-4.00/kg) and unsourced tiers ($4.60/kg, from $4.30/kg)',
    status: '🔴 FIXED 2026-10-30 — realigned to this band card',
    action: 'Already corrected by tonight\'s build. Re-verify after deploy.',
  },
  {
    file: 'studex-wildlife-coffee-vite/dist/index.html',
    section: 'green catalogue',
    carries: 'The published origin portfolio table',
    status: '🟡 OWNER of the published band — changes only via the registry',
    action: 'Re-check when the band is re-based.',
  },
]

// ── The live contact that replaces the dead one ────────────────────────────
const CONTACT = {
  supportEmail: 'info@studexmeat.com',
  supportEmailOwner: 'studex-meat/PRICE-SOURCE-REGISTRY.md §4b — the asserted support email on every coffee page',
  giftingEmail: 'info@studex-group.com',
  orderLine: '+27 83 593 2577',
  storePhone: '+27 84 421 6035',
  storeWhatsapp: '+27 94 988 8737',
  whatsappLink: 'https://wa.me/27794988737',
  entity: 'Studex Meat (Pty) Ltd',
  locations: 'Cape Town, South Africa & Kigali, Rwanda',
  deadOnes: [
    { value: 't.ramaphosa@studexwildlife.com', where: 'studex-os/proposals/rwanda-offer-PROWTC-2026-07.json', note: 'Dead. The PROWTC buyer cannot reply to the offer that names them.' },
    { value: 'tumelo@studexmeat.com', where: 'ciie-buyer-brief/src/App.tsx (before tonight)', note: 'Not an asserted contact anywhere in the registry.' },
    { value: 'coffee@studexmeat.com', where: 'ciie-buyer-brief/src/App.tsx (before tonight)', note: 'Not an asserted contact anywhere in the registry.' },
    { value: 'ceo@agent.studexmeat.com', where: 'superseded China lead page', note: 'No DNS. Already retired from the registry.' },
  ],
}

// ── The one question that closes this ──────────────────────────────────────
const SUPPLIER_QUESTION = [
  '1. FOB Kigali (and FOB Djibouti if that is the contract) — USD per kg, for A1 and for A2, current crop.',
  '2. Is the $6.07-6.75/kg band we have on file (a) green FOB, (b) something else entirely (landed, roasted, CIF), or (c) a stale figure?',
  '3. Confirm the lot structure: A1 20 MT, A2 40 MT, custom blend 5 MT, samples 5-10 kg.',
  '4. Screen size, moisture %, water activity, process, and the cupping score you will stand behind for each lot.',
  '5. Who signs the phytosanitary certificate and the certificate of origin, and at what cost?',
]

const OPEN_ITEMS = [
  {
    item: 'China registration gate for a Rwandan green-coffee exporter',
    status: 'NOT VERIFIED',
    detail: 'From 20 Jul 2026 China runs a single continent-wide approval regime for qualified coffee beans from all 53 African countries. That is NOT the same as the overseas-establishment registration/certification a specific Rwandan exporter must hold to clear customs. Do not assume one implies the other.',
    owner: 'Tumelo / freight forwarder',
  },
  {
    item: 'Tariff date wording',
    status: 'FOUND — and two dates are being conflated',
    detail: 'Zero tariff for all 53 African countries from 1 May 2026 (that is the TARIFF). 20 Jul 2026 is the unified PHYTOsanitary approval regime (that is not a tariff date). A Rwandan LDC origin has no expiry; the 30 Apr 2028 window belongs to the 20 non-LDC African countries.',
    owner: 'copy — corrected 2026-10-30',
  },
  {
    item: 'Green coffee to SA: duty rate',
    status: 'ASSUMPTION 0%',
    detail: 'Not broker-confirmed. The whole SA landed-cost floor rests on it.',
    owner: 'broker',
  },
  {
    item: 'Ocean freight + insurance',
    status: 'ASSUMPTION $0.07/kg',
    detail: 'Needs a forwarder quote.',
    owner: 'forwarder',
  },
]

// ─────────────────────────────────────────────────────────────────────────────
// EMIT
// ─────────────────────────────────────────────────────────────────────────────

function round(n, dp = 2) {
  const f = 10 ** dp
  return Math.round(n * f) / f
}

const GENERATED = {
  generatedAt: new Date().toISOString(),
  generator: 'coffee-fob-band/compute-band-card.mjs',
  selfTest: { passed: selfTestPassed, results: selfTestResults },
  inputs: INPUTS,
  bands: BANDS,
  originPortfolio: ORIGIN_PORTFOLIO,
  scenarios,
  gap,
  publishedTiers: PUBLISHED_TIERS,
  filesNeedingCorrection: FILES_NEEDING_CORRECTION,
  contact: CONTACT,
  supplierQuestion: SUPPLIER_QUESTION,
  openItems: OPEN_ITEMS,
  reconciliation: {
    publishedSetConsistent: true,
    publishedSetNote:
      'The published numbers reconcile: the origin portfolio table ($3,400-5,200/MT) is a DIFFERENT SCOPE, not a competing band, and Rwanda A1 ($4,200-4,800) sits inside it. The PROWTC offer quoted the A1/A2 rows correctly.',
    unreconciled: 'the internal $6.07-6.75/kg cost band — not traceable to any published table and flagged UNVERIFIED in our own register',
  },
}

mkdirSync(HERE, { recursive: true })
writeFileSync(join(HERE, 'band.generated.json'), JSON.stringify(GENERATED, null, 2) + '\n')

// ─────────────────────────────────────────────────────────────────────────────
// THE CARD — the one page a buyer, a broker or a supplier can be handed.
// ─────────────────────────────────────────────────────────────────────────────

// Price format rule (registry, 2026-10-21): comma thousands separator, no space.
// Rand decimals use a DOT — en-ZA would render R72,85, and that is not a price.
const zar = (n) =>
  'R' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const usd2 = (n) => '$' + n.toFixed(2)
const usd0 = (n) => '$' + n.toLocaleString('en-US')
// adaptive: $4,200 (int) vs $4.20 (fraction)
const usd = (n) => (Number.isInteger(n) ? usd0(n) : usd2(n))
// A single-value band is a point, not a range.
const range = (lo, hi, fmt) => (lo === hi ? fmt(hi) : `${fmt(lo)}–${fmt(hi)}`)

const md = []
const P = (s = '') => md.push(s)

P('# ☕ Studex Green Coffee — FOB BAND CARD')
P()
P('**One page. One band. Every number with its source and its status.**')
P()
P('| | |')
P('|---|---|')
P('| **Owner** | `coffee-fob-band/compute-band-card.mjs` → `coffee-fob-band/band.generated.json` |')
P('| **Generated** | ' + new Date().toISOString().slice(0, 10) + ' |')
P('| **Band authority** | `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.6 |')
P('| **Model self-test** | ' + (selfTestPassed ? '✅ PASS — reproduces the published price sheet exactly' : '🔴 FAIL — the model has drifted from sa-b2b-coffee') + ' |')
P('| **Status of the band** | ⚠️ **PARTIALLY VERIFIED** — the published set is internally consistent; the internal cost band is not |')
P()
P('---')
P()
P('## 1. THE BAND')
P()
P('### 1.1 Published — what buyers see')
P()
P('| Lot | Screen | Lot size | FOB USD/MT | FOB USD/kg | Status |')
P('|---|---|---|---:|---:|---|')
for (const b of BANDS.filter((b) => b.status === 'FOUND')) {
  const screen = b.id === 'published-a1' ? '17+' : b.id === 'published-a2' ? '15–16' : 'custom'
  const lot = b.id === 'published-a1' ? '20 MT' : b.id === 'published-a2' ? '40 MT' : '5 MT'
  P(`| ${b.label.replace('PUBLISHED — ', '')} | ${screen} | ${lot} | ${range(b.fobUsdPerMt[0], b.fobUsdPerMt[1], usd0)} | ${range(b.fobUsdPerKg[0], b.fobUsdPerKg[1], usd2)} | ✅ ${b.status} |`)
}
P(`| ${ORIGIN_PORTFOLIO.label.replace('PUBLISHED — ', '')} | — | per container | ${range(ORIGIN_PORTFOLIO.rangeUsdPerMt[0], ORIGIN_PORTFOLIO.rangeUsdPerMt[1], usd0)} | $3.40–$5.20 | ✅ ${ORIGIN_PORTFOLIO.status} |`)
P()
P('### 1.2 Internal — what our cost model floors on')
P()
P('| Band | FOB USD/kg | Status | Source |')
P('|---|---:|---|---|')
for (const b of BANDS.filter((b) => b.status === 'UNVERIFIED')) {
  P(`| ${b.label.replace('INTERNAL COST MODEL — ', '')} | ${usd(b.fobUsdPerKg[0])}–${usd(b.fobUsdPerKg[1])} | 🔴 **${b.status}** | ${b.owner} |`)
}
P()
P('> ⚠️ **The internal band is above the UAE import ceiling.** IndexBox (Sep 2026) puts UAE green coffee imports at **$2.50–6.50/kg**. Our internal high of $6.75/kg is *above* that ceiling. If the internal band is the true one, we are priced out of the Gulf by construction — before a single buyer says no.')
P()
P('### 1.3 The reconciliation')
P()
P('The brief flagged **three live green FOB bands**. On inspection, **two of the three reconcile**, and only one number is actually orphaned:')
P()
P('1. **$3,400–5,200/MT** — the origin portfolio table (Uganda low, SA Bourbon high). This is a **different scope**, not a competing price for the same product. Rwanda A1 at $4,200–4,800 **sits inside it**. ✅ consistent')
P('2. **$4,200–4,800/MT (A1) and $3,600–4,000/MT (A2)** — the registry-owned Rwanda rows, correctly quoted in the PROWTC offer. ✅ consistent')
P('3. **$6.07–6.75/kg** — the internal cost band. **Not traceable to any published table.** Flagged UNVERIFIED in our own assumptions register. 🔴 orphaned')
P()
P('> 💡 **This is the good news, and it is also the risk.** The published set is coherent. So the exposure is not *"we are contradicting ourselves publicly"* — it is *"our internal floor is probably too high, and we have been pricing to it."*')
P()
P('---')
P()
P('## 2. WHAT THE AMBIGUITY COSTS')
P()
P('Landed green cost `= (FOB $/kg + freight $/kg) × FX + port clearing` · cost per kg roasted `= landed ÷ 0.85 + R38 roasting + packaging`')
P()
P('| Scenario | FOB $/kg | Landed green R/kg | Cost/kg roasted | Natural 30 kg+ margin |')
P('|---|---:|---:|---:|---:|')
for (const s of scenarios) {
  const t = s.tiers.find((x) => x.origin === 'Natural')
  P(`| ${s.label} | ${usd(s.fob)} | ${zar(s.landedGreenZarPerKg)} | ${zar(s.roastedCostZarPerKg)} | **${t.marginPct}%** ${t.clearsFloor ? '✅' : '🔴'} |`)
}
P()
P(`### 🔴 The headline`)
P()
P(`> At the **published** A1 band-high ($4.80/kg) our landed green is **${zar(a1High.landedGreenZarPerKg)}/kg**. At the **internal** band-high ($6.75/kg) it is **${zar(internalHigh.landedGreenZarPerKg)}/kg**.`)
P('>')
P(`> **That is ${zar(gap.landedDeltaZarPerKg)}/kg of landed green we may be over-paying for — ${zar(gap.per30kgBagZar)} per 30 kg roasted bag, and ${zar(gap.per20MTContainerZar)} per 20 MT container.**`)
P('>')
P(`> On the published tier prices, Natural at 30 kg+ earns **${a1High.tiers.find((t) => t.origin === 'Natural').marginPct}%** margin at the published band but only **${internalHigh.tiers.find((t) => t.origin === 'Natural').marginPct}%** at the internal band — a **${gap.marginGapPointsAt30kg}-point** difference.`)
P('>')
P('> **We are pricing the published sheet on the pessimistic number.** If the published band is right, the 30 kg+ tier could carry **' + zar(a1High.tiers.find((t) => t.origin === 'Natural').priceAtFloorZarPerKg) + '/kg** and still clear the 25% floor — we are leaving margin on the table on every bag we sell. If the internal band is right, we are nearly at the floor and the sheet is correct.')
P()
P('> 🔑 Either way **the current published prices are safe** — they clear the floor under the *worst* case. What is at risk is **opportunity**, not solvency. Which is the better problem.')
P()
P('---')
P()
P('## 3. THE ONE CALL THAT CLOSES THIS')
P()
P('Send this to the supplier today. Five questions, one email, one phone call:')
P()
for (const q of SUPPLIER_QUESTION) P(q)
P()
P('**Until question 2 is answered, the band card above is the answer — and the internal band stays flagged.**')
P()
P('---')
P()
P('## 4. CONTACT — use these, not the dead ones')
P()
P('| Field | Value |')
P('|---|---|')
P(`| Support email | \`${CONTACT.supportEmail}\` |`)
P(`| Order line | ${CONTACT.orderLine} |`)
P(`| Store phone | ${CONTACT.storePhone} |`)
P(`| Store WhatsApp | ${CONTACT.storeWhatsapp} |`)
P(`| Trading entity | ${CONTACT.entity} |`)
P(`| Locations | ${CONTACT.locations} |`)
P()
P('### 🔴 Dead contacts — must not appear on any buyer-facing document')
P()
P('| Dead value | Where it is | Note |')
P('|---|---|---|')
for (const d of CONTACT.deadOnes) P(`| \`${d.value}\` | ${d.where} | ${d.note} |`)
P()
P('---')
P()
P('## 5. FILES THAT STILL CARRY A GREEN FOB NUMBER')
P()
P('| File | Carries | Status | Action |')
P('|---|---|---|---|')
for (const f of FILES_NEEDING_CORRECTION) P(`| \`${f.file}\` | ${f.carries} | ${f.status} | ${f.action} |`)
P()
P('---')
P()
P('## 6. OPEN ITEMS')
P()
P('| Item | Status | Detail | Owner |')
P('|---|---|---|---|')
for (const o of OPEN_ITEMS) P(`| ${o.item} | ${o.status} | ${o.detail} | ${o.owner} |`)
P()
P('---')
P()
P('### Disclaimers')
P()
P('Prices are the published Studex band as at the generation date, sourced to `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.6. The internal cost band is **UNVERIFIED** and is used only for internal margin floors — never quote it. FX, freight, duty, port, roast and packaging figures are documented assumptions, not quotes. Nothing here is a commitment to buy, sell or ship. No trade price should be issued to a buyer until the band is re-based and this card is regenerated.')
P()

writeFileSync(join(ROOT, 'coffee-fob-band-card.md'), md.join('\n') + '\n')

console.log('─'.repeat(68))
console.log('STUDEX GREEN COFFEE — FOB BAND CARD')
console.log('─'.repeat(68))
console.log(`self-test: ${selfTestPassed ? 'PASS' : 'FAIL'}`)
for (const r of selfTestResults) {
  console.log(`  ${r.pass ? 'ok  ' : 'FAIL'} ${r.scenario}/${r.tier}: expected ${r.expectMarginPct}% got ${r.got}%`)
}
console.log('')
console.log(`landed green  A1 high $4.80/kg -> R${a1High.landedGreenZarPerKg.toFixed(2)}/kg`)
console.log(`landed green  internal  $6.75/kg -> R${internalHigh.landedGreenZarPerKg.toFixed(2)}/kg`)
console.log(`gap: R${gap.landedDeltaZarPerKg.toFixed(2)}/kg green | R${gap.per30kgBagZar.toFixed(0)} per 30kg bag | R${gap.per20MTContainerZar.toFixed(0)} per 20MT container`)
console.log(`Natural 30kg+ margin: ${a1High.tiers[0].marginPct}% (published band) vs ${internalHigh.tiers[0].marginPct}% (internal band) = ${gap.marginGapPointsAt30kg} pts`)
console.log('')
console.log('wrote coffee-fob-band/band.generated.json')
console.log('wrote coffee-fob-band-card.md')
console.log('─'.repeat(68))