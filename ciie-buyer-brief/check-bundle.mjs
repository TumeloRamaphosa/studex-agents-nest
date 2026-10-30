#!/usr/bin/env node
/**
 * CIIE BUYER BRIEF — BUNDLE ASSERTION HARNESS
 * Built: 2026-10-30 (Build Hour). Owner: Robusca / Studex Ops.
 *
 * WHY THIS FILE EXISTS
 * --------------------
 * `studex-meat/PRICE-SOURCE-REGISTRY.md` §4b records the lesson we already
 * paid for once: "CLIENT-RENDERED PAGES (React SPAs) — asserted against the
 * BUILT BUNDLE, not the HTML. A React page returns ~150 characters of HTML
 * shell, so a text assertion against the fetched page proves nothing."
 *
 * The CIIE card is a React SPA. Before tonight it shipped:
 *   - "PROWTC (Premium Rwandan Organic Whole Trade Coffee)" as a CERTIFICATION
 *   - "Fully Certified for China Entry"
 *   - "South African registered exporter"      (registry §4f forbidden)
 *   - "USD 4.60/kg"                            (registry §4f forbidden)
 *   - a cupping score of 87-90+ against our own registry's 84-87
 *   - two mailto addresses asserted nowhere in the registry
 * and NOTHING watched it. This harness is what watches it now.
 *
 * Run:  node ciie-buyer-brief/check-bundle.mjs
 * Exit: 0 = clean, 1 = at least one assertion failed
 */

import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
// Optional path override so the harness can be negative-tested against a COPY
// of the bundle. A checker that has only ever returned green is not a checker.
const DIST = process.argv[2] ? process.argv[2] : join(HERE, 'dist')

if (!existsSync(DIST)) {
  console.error('✖ dist/ not found — run `npm run build` in ciie-buyer-brief/ first')
  process.exit(1)
}

// ── Collect the whole built bundle ────────────────────────────────────────
const assetDir = join(DIST, 'assets')
const files = [join(DIST, 'index.html')]
if (existsSync(assetDir)) {
  for (const f of readdirSync(assetDir)) {
    if (/\.(js|css|html)$/.test(f)) files.push(join(assetDir, f))
  }
}
const BUNDLE = files.map((f) => readFileSync(f, 'utf8')).join('\n')

// ─────────────────────────────────────────────────────────────────────────────
// FORBIDDEN — must NOT appear. Sourced from PRICE-SOURCE-REGISTRY.md §4f.
// ─────────────────────────────────────────────────────────────────────────────
const FORBIDDEN = [
  // §4f registry list
  ['agent.studexmeat.com', 'dead domain, no DNS'],
  ['charlie@agent.studexmeat.com', 'dead domain'],
  ['27 82 555 0194', 'unverified phone, replaced'],
  ['per 250g', 'wrong caviar unit'],
  ['0% window runs to 30 April 2028', 'the 30 Apr 2028 expiry was THEIRS, not ours'],
  ['Zero Tariff — to 30 Apr 2028', 'the 30 Apr 2028 expiry was THEIRS, not ours'],
  ['tariff window closes on 30 April 2028', 'the 30 Apr 2028 expiry was THEIRS, not ours'],
  ['0% for all 53 African countries, 1 May 2026 – 30 April 2028', 'expiry was theirs, not ours'],
  ['June 2026', 'stale date'],
  ['Coming Soon', 'stale'],
  ['500+ MT', 'unverified volume claim'],
  ['svetlana@prowtc.com', 'a real prospect, not our contact'],
  ['PROWTC', 'PROWTC is a Dubai BUYER, not a certifier'],
  ['expressed interest', 'forbidden'],
  ['4.60/kg', 'forbidden price — no longer in the band'],
  ['5.50/kg', 'forbidden price'],
  ['69,000', 'forbidden'],
  ['USD 18/tin', 'forbidden'],
  ['registered exporter', 'forbidden claim'],
  ['HACCP', 'forbidden'],
  ['ISO 22000', 'forbidden'],
  ['cold-chain certified', 'forbidden'],
  ['Experience supplying', 'forbidden'],
  ['meeting point to be confirmed', 'forbidden'],
  ['CIIE Special', 'forbidden'],
  ['Halaal certified', 'forbidden — no certification claim'],
  ['100% Halaal', 'forbidden — no certification claim'],
  ['Rainforest Alliance', 'forbidden — the RA claim was fabricated and removed'],
  ['ethically sourced', 'forbidden — unsourced claim'],
  ['certified Russian caviar', 'forbidden — unsourced claim'],
  ['Cotti Coffee', 'competitor/partner reference — not our claim to make'],
  ['Premier Origins', 'unsourced claim'],
  // Dead contacts
  ['t.ramaphosa@studexwildlife.com', 'dead — PROWTC cannot reply to their own offer'],
  ['tumelo@studexmeat.com', 'not an asserted contact in the registry'],
  ['coffee@studexmeat.com', 'not an asserted contact in the registry'],
  // Mangled price strings from the pre-rebuild page
  ['4.20-4.20-4.80', 'mangled price string'],
  ['4.80–3.60-4.00', 'mangled price string'],
  // Fabricated / unverified claims removed tonight
  ['Premium Rwandan Organic Whole Trade Coffee', 'fabricated acronym expansion'],
  ['Fully Certified for China Entry', 'unsourced certification claim'],
  ['all documentation required for China import already in place', 'unsourced claim'],
  ['CIIE exhibitor since 2024', 'unverified'],
  ['CITES', 'wildlife convention — irrelevant to coffee'],
  ['869', 'unverified export volume'],
  ['87–90+', 'cupping inflation — our own registry says 84-87'],
  ['87-90+', 'cupping inflation — our own registry says 84-87'],
  // Secret leak guard — no key may ever be built into a browser bundle
  ['AGENTMAIL_API_KEY', 'key name in bundle'],
  ['sk_live_', 'stripe key in bundle'],
  ['pk_live_', 'stripe key in bundle'],
]

// ─────────────────────────────────────────────────────────────────────────────
// REQUIRED — must appear. Traceable to the band card + registry §2.6/§2.7/§4b.
// ─────────────────────────────────────────────────────────────────────────────
const REQUIRED = [
  // The band (coffee-fob-band-card.md §1.1)
  ['4,200–4,800/MT', 'A1 FOB band'],
  ['3,600–4,000/MT', 'A2 FOB band'],
  ['3,800/MT', 'custom blend 5 MT'],
  ['28–45/kg', 'sample shipment 5–10 kg'],
  ['4,800–5,400/MT', 'A1 CIF Shanghai'],
  ['4,200–4,700/MT', 'A2 CIF Shanghai'],
  // Lot structure (§2.6)
  ['20 MT', 'A1 lot size'],
  ['40 MT', 'A2 lot size'],
  ['5 MT', 'custom blend lot size'],
  ['5–10 kg', 'sample lot size'],
  ['0901', 'HS code'],
  ['FOB Djibouti', 'incoterm'],
  // Truthful facts
  ['1 May 2026', 'zero-tariff start date'],
  ['20 July 2026', 'unified phytosanitary regime date'],
  ['no expiry', 'Rwandan LDC origin has no tariff expiry'],
  ['84–87', 'cupping score per registry §2.6'],
  ['17+', 'A1 screen size'],
  ['15–16', 'A2 screen size'],
  // Contacts (registry §4b)
  ['info@studexmeat.com', 'support email'],
  ['+27 84 421 6035', 'store phone'],
  ['27794988737', 'store WhatsApp'],
  ['Studex Meat (Pty) Ltd', 'trading entity'],
  ['Kigali', 'location'],
  // Documents
  ['phytosanitary', 'document list'],
  ['certificate of origin', 'document list'],
  ['certificate of analysis', 'document list'],
  ['fumigation', 'document list'],
  // China registration gate must be visible as an open item
  ['registration', 'China overseas-establishment registration checklist'],
  // Sourced market facts — these must never be quietly softened
  ['2.56 billion', 'Kunshan green-bean import value 2025'],
  ['56.4%', 'Kunshan green-bean import growth'],
  ['$227m', 'Rwanda exports to China 2025'],
  ['Kunshan', 'the corridor we are pitching into'],
]

// ─────────────────────────────────────────────────────────────────────────────
// Run
// ─────────────────────────────────────────────────────────────────────────────
let failed = 0

console.log('─'.repeat(70))
console.log('CIIE BUYER BRIEF — BUNDLE ASSERTIONS')
console.log('─'.repeat(70))
console.log(`bundle: ${files.length} file(s), ${BUNDLE.length.toLocaleString()} chars`)
console.log('')

console.log(`FORBIDDEN STRINGS (${FORBIDDEN.length} checked)`)
for (const [needle, why] of FORBIDDEN) {
  const hit = BUNDLE.includes(needle)
  if (hit) {
    failed++
    console.log(`  ✖ FOUND    "${needle}" — ${why}`)
  } else {
    console.log(`  ✓ absent   "${needle}"`)
  }
}

console.log('')
console.log(`REQUIRED STRINGS (${REQUIRED.length} checked)`)
for (const [needle, why] of REQUIRED) {
  const hit = BUNDLE.includes(needle)
  if (!hit) {
    failed++
    console.log(`  ✖ MISSING  "${needle}" — ${why}`)
  } else {
    console.log(`  ✓ present  "${needle}"`)
  }
}

console.log('')
console.log('─'.repeat(70))
if (failed === 0) {
  console.log('✅ CIIE BUNDLE CLEAN — all assertions passed')
  console.log('─'.repeat(70))
  process.exit(0)
} else {
  console.log(`🔴 ${failed} ASSERTION(S) FAILED — the bundle is NOT shippable`)
  console.log('─'.repeat(70))
  process.exit(1)
}
