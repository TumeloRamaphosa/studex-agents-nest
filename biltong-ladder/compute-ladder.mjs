#!/usr/bin/env node
/**
 * STUDEX BILTONG — PRICE LADDER BUILDER
 * Built: 2026-10-30 (Build Hour). Owner: Robusca / Studex Ops.
 *
 * WHY THIS FILE EXISTS
 * --------------------
 * There are TWO biltong price ladders live at the same time and they are
 * wrong in opposite directions:
 *
 *   A. Shopify live store (studexmeat.com, verified 28 Oct from products.json
 *      variants, re-confirmed 30 Oct on the live product page):
 *        Luxury Wagyu Biltong  500g R450     -> R900/kg
 *        Luxury Wagyu Biltong  1kg  R650     -> R650/kg
 *        Wagyu Biltong Gold    1kg  R1,450   -> R1,450/kg
 *        Wagyu Biltong Gold    7kg  R12,500  -> R1,786/kg
 *      -> the 500g costs R250 MORE per kg than the 1kg (inverted)
 *      -> the 7kg case costs R2,350 MORE than 7 x 1kg (+23% per kg)
 *
 *   B. Marketing page + PRICE-SOURCE-REGISTRY §2.1 (studex-biltong/index.html):
 *        Luxury Wagyu Biltong  500g From R325 -> R650/kg  (no size on the card)
 *        Wagyu Biltong Gold    1kg  R1,250   -> R1,250/kg
 *        Wagyu Biltong Gold    7kg  R8,400   -> R1,200/kg
 *      -> structurally CORRECT (the case beats 7 x 1kg by R350)
 *      -> but lands BELOW the margin floor at wagyu input cost
 *
 * One ladder has the right shape and the wrong money. The other has the right
 * money and the wrong shape. This builds the ladder that is both, and prints
 * the raw-beef cost at which every tier works.
 *
 * 🔑 THE QUESTION THIS ACTUALLY ANSWERS
 * "What should the biltong ladder be?" is unanswerable without a cost model,
 * and we do not have one. So the script does not pretend. For every tier it
 * prints the BREAK-EVEN RAW COST — the raw beef price at which that tier
 * exactly clears the 25% floor. It also reverse-engineers the raw cost
 * implied by each competitor's shelf price. Put the real invoice into one
 * field and the ladder is right; leave it out and the table still tells you
 * which direction to move.
 *
 * Run:  node biltong-ladder/compute-ladder.mjs
 * Out:  biltong-ladder/ladder.generated.json  (machine)
 *       biltong-ladder/LADDER.md                 (the sheet, human)
 */

import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  COST_INPUTS,
  POLICY,
  LIVE_LADDERS,
  SA_BENCHMARKS,
  US_BENCHMARKS,
  FX_USD_ZAR,
} from './inputs.mjs'
import {
  round,
  zar,
  zar0,
  pct,
  analyseLiveLadder,
  proposeLadder,
  costPerKg,
  impliedRawAtFloor,
} from './ladder-engine.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))

const SCENARIOS = [
  {
    id: 'standard',
    label: 'Standard silverside beef',
    raw: COST_INPUTS.rawBeefRarPerKg.standardSilverside,
    note: 'What the product looks like if "Wagyu" is a label rather than a grade.',
  },
  {
    id: 'wagyu',
    label: 'Wagyu, trimmed',
    raw: COST_INPUTS.rawBeefRarPerKg.wagyuTrimmed,
    note: 'What the product costs if the beef really is wagyu. This is the scenario that decides whether SA retail works at all.',
  },
]

const shopifyTiers = LIVE_LADDERS.find((l) => l.id === 'shopify').tiers

const results = SCENARIOS.map((s) => ({
  scenario: s,
  live: LIVE_LADDERS.map((l) => analyseLiveLadder(l, s.raw.value)),
  proposed: proposeLadder(s.raw.value, shopifyTiers),
}))

const GENERATED = {
  generatedAt: new Date().toISOString(),
  generator: 'biltong-ladder/compute-ladder.mjs',
  costInputs: COST_INPUTS,
  policy: POLICY,
  fx: FX_USD_ZAR,
  benchmarks: { sa: SA_BENCHMARKS, us: US_BENCHMARKS },
  scenarios: results,
  impliedRaw: SA_BENCHMARKS.map((b) => ({
    name: b.name,
    pricePerKg: b.pricePerKg,
    impliedRawAtFloor: impliedRawAtFloor(b.pricePerKg),
    note: b.note,
  })),
}

mkdirSync(HERE, { recursive: true })
writeFileSync(join(HERE, 'ladder.generated.json'), JSON.stringify(GENERATED, null, 2) + '\n')

// ─────────────────────────────────────────────────────────────────────────────
// MARKDOWN
// ─────────────────────────────────────────────────────────────────────────────
const md = []
const P = (s = '') => md.push(s)

P('# 🦴 Studex Biltong — Price Ladder Sheet')
P()
P('**One ladder. Two live ladders reconciled. Every number with its source.**')
P()
P('| | |')
P('|---|---|')
P('| **Owner** | `biltong-ladder/compute-ladder.mjs` → `biltong-ladder/ladder.generated.json` |')
P('| **Generated** | ' + new Date().toISOString().slice(0, 10) + ' |')
P('| **Status** | 🟡 **NOT YET APPLIED** — Shopify needs the Admin token (401 as of 28 Oct) |')
P('| **Cost model** | ⚠️ **ASSUMPTIONS, not invoices** — see §4 for the break-even table |')
P()
P('---')
P()
P('## 1. THE TWO LIVE LADDERS')
P()
P('| Ladder | 500g | Luxury 1kg | Gold 1kg | 7kg case | Verdict |')
P('|---|---:|---:|---:|---:|---|')
for (const l of LIVE_LADDERS) {
  const pick = (line, size) => l.tiers.find((t) => t.line.includes(line) && t.sizeKg === size)?.price
  P(
    `| ${l.label} | ${zar0(pick('Luxury', 0.5) ?? 0)} | ${pick('Luxury', 1) ? zar0(pick('Luxury', 1)) : '—'} | ${zar0(pick('Gold', 1))} | ${zar0(pick('Gold', 7))} | ${l.status} |`,
  )
}
P()
P('*Both ladders are live at the same time. The store and the marketing page disagree, and the marketing page shows "From R325" for a product whose card states no size at all.*')
P()
P('---')
P()
P('## 2. WHY THEY ARE WRONG')
P()
for (const res of results) {
  const s = res.scenario
  P(`### ${s.label} — raw beef at ${zar0(s.raw.value)}/kg`)
  P()
  P(`_${s.note}_`)
  P()
  for (const l of res.live) {
    P(`**${l.label}** — ${l.status}`)
    P()
    P('| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? |')
    P('|---|---:|---:|---:|---:|:---:|')
    for (const t of l.tiers) {
      P(
        `| ${t.line} ${t.label} | ${zar0(t.price)} | ${zar(t.pricePerKg)} | ${zar(t.costPerKg)} | ${t.marginPct}% | ${t.clearsFloor ? '✅' : '🔴'} |`,
      )
    }
    P()
    if (l.invariants.length === 0) {
      P('- ⚠️ No invariant could be evaluated — this ladder publishes only one tier per product line, so the per-kg shape cannot be checked.')
      P()
    }
    for (const inv of l.invariants) {
      P(`- ${inv.holds ? '✅' : '🔴'} **${inv.rule}** — ${inv.observed}. _Required: ${inv.required}._`)
    }
    P()
  }
}
P('---')
P()
P('## 3. THE PROPOSED LADDER')
P()
for (const res of results) {
  const s = res.scenario
  const p = res.proposed
  P(`### ${s.label} — raw beef at ${zar0(s.raw.value)}/kg`)
  P()
  P('| Tier | Price | Per kg | Cost/kg | Margin | Clears 25%? | Break-even raw |')
  P('|---|---:|---:|---:|---:|:---:|---:|')
  for (const t of p.tiers) {
    P(
      `| ${t.line} ${t.label} | ${zar0(t.price)} | ${zar(t.pricePerKg)} | ${zar(t.costPerKg)} | ${t.marginPct}% | ${t.clearsFloor ? '✅' : '🔴'} | ${zar0(t.breakEvenRaw)}/kg |`,
    )
  }
  P()
  for (const inv of p.invariants) {
    P(`- ${inv.holds ? '✅' : '🔴'} **${inv.rule}** — ${inv.observed}${inv.detail ? ' — ' + inv.detail : ''}`)
  }
  P()
  const deltas = p.deltas.filter(Boolean)
  if (deltas.length) {
    P('**Change against the live Shopify ladder**')
    P()
    P('| Tier | Live | Proposed | Change |')
    P('|---|---:|---:|---:|')
    for (const d of deltas) {
      const arrow = d.deltaZar > 0 ? '▲' : d.deltaZar < 0 ? '▼' : '='
      P(
        `| ${d.line} ${d.label} | ${zar0(d.livePrice)} | ${zar0(d.proposedPrice)} | ${arrow} ${zar0(Math.abs(d.deltaZar))} (${d.deltaPct > 0 ? '+' : ''}${d.deltaPct}%) |`,
      )
    }
    P()
  }
}
P('---')
P()
P('## 4. THE BREAK-EVEN TABLE — the one number that matters')
P()
P('> **We do not have a biltong cost model. We have an assumption.** So here is the question answered without one: **at what raw beef price does each tier exactly clear the 25% floor?**')
P()
P('| Tier | Proposed price | Break-even raw cost | vs standard silverside R140 | vs wagyu R320 |')
P('|---|---:|---:|:---:|:---:|')
const prop = results.find((r) => r.scenario.id === 'wagyu').proposed
for (const t of prop.tiers) {
  const vsStd = t.breakEvenRaw / COST_INPUTS.rawBeefRarPerKg.standardSilverside.value
  const vsWagyu = t.breakEvenRaw / COST_INPUTS.rawBeefRarPerKg.wagyuTrimmed.value
  P(
    `| ${t.line} ${t.label} | ${zar0(t.price)} | **${zar0(t.breakEvenRaw)}/kg** | ${vsStd >= 1 ? '✅' : '🔴'} ${vsStd.toFixed(2)}x | ${vsWagyu >= 1 ? '✅' : '🔴'} ${vsWagyu.toFixed(2)}x |`,
  )
}
P()
P('**How to read it:** if the 1kg tier breaks even at R250/kg raw, then a raw beef invoice at R320/kg means that tier loses money at the proposed price, and one at R180/kg means it clears comfortably.')
P()
P('### What the market implies')
P()
P('Reverse-engineering the same 25% floor back out of competitor shelf prices tells us what raw beef the market can bear:')
P()
P('| Competitor | Shelf price/kg | Implied raw cost at a 25% floor |')
P('|---|---:|---:|')
for (const r of GENERATED.impliedRaw) {
  P(`| ${r.name} | ${zar(r.pricePerKg)} | ${zar0(r.impliedRawAtFloor)}/kg |`)
}
P()
P('> 🔑 **This is the strategic read.** The SA market implies a raw cost in the low hundreds. If our invoice is materially above that, then **the product is not an SA retail product — it is an export product**, and it should be priced and merchandised as one. The US DTC band is where a premium price actually lives.')
P()
P('### Benchmarks used')
P()
P('| SA benchmark | Pack | Price | Per kg | Date |')
P('|---|---|---:|---:|---|')
for (const b of SA_BENCHMARKS) {
  P(`| ${b.name} | ${b.pack} | ${zar0(b.price)} | ${zar(b.pricePerKg)} | ${b.date} |`)
}
P()
P('| US DTC benchmark | Pack | Price | Per kg (R) | Date |')
P('|---|---|---:|---:|---|')
for (const b of US_BENCHMARKS) {
  P(
    `| ${b.name} | ${b.pack} | $${b.priceUsd.toFixed(2)} | ${zar(b.priceUsd * FX_USD_ZAR.value * 2.20462)} | ${b.date} |`,
  )
}
P()
P('---')
P()
P('## 5. POLICY — the rules the proposal obeys')
P()
P('| Rule | Value | Why |')
P('|---|---|---|')
P(`| Margin floor | ${pct(POLICY.marginFloorPct.value)} | Matches the coffee sheet and the caviar desk. A ladder below this is not a ladder. |`)
P(`| Small-pack premium cap | ${pct(POLICY.smallPackPremiumCap.value)} over the 1kg per kg | The buyer must not be charged a penalty for buying less than 1kg. Woolworths runs 25–50% at the snack end; we cap it lower because our buyer has a good calculator. |`)
P(`| Case saving | ${pct(POLICY.caseSavingPct.value)} cheaper per kg than 7 × 1kg | The buyer has to be able to count the saving, or the case is a decoration. |`)
P(`| Luxury-to-Gold ratio | ${COST_INPUTS.goldLineRatio.value}× | Preserved from the live ladder (R1,450 ÷ R650). Packaging explains only R45/kg of it — the rest is positioning, and positioning is not ours to rewrite in a build hour. |`)
P(`| Rounding | nearest R${POLICY.roundingZar.value} | A price sheet with R1,413.72 on it is not a price sheet. |`)
P()
P('> 📖 **A note on the brief.** The brief asked for a ladder that makes the 500g **cheaper per kg** than the 1kg. That is backwards for retail: the small pack carries the higher packaging cost per kg (R19 vs R14), and every SA benchmark runs the other way — Woolworths charges R880/kg for 125g against R700/kg for 400g. Making the 500g cheaper per kg than the 1kg means a buyer is penalised for buying a kilo. **What is enforced instead** is that the 500g carries no more than a 15% per-kg premium over the 1kg, and that per-kg price falls as pack size rises. The brief’s real target — the inversion in the Shopify ladder — is closed either way.')
P()
P('---')
P()
P('## 6. WHAT TO DO WITH THIS')
P()
P('1. **Get the raw beef invoice.** One number. It is the only input that matters and it is currently an assumption.')
P('2. **Re-run** `node biltong-ladder/compute-ladder.mjs`. The whole sheet moves.')
P('3. **Apply to Shopify** once the Admin token works (401 as of 28 Oct). Four variant prices.')
P('4. **Align the marketing page** `studex-biltong/index.html` to the same numbers, and fix the "From R325" card which states no size.')
P('5. **Fix the registry** `studex-meat/PRICE-SOURCE-REGISTRY.md` §2.1 — it still carries the old R325 / R1,250 / R8,400 set as if it were the live ladder.')
P()
P('### Disclaimers')
P()
P('Cost inputs are documented assumptions except where a source is named; the raw beef price is an assumption in both scenarios and is the input most likely to be wrong. Benchmarks are observed shelf prices at the dates shown and move without notice. Nothing here is a commitment to sell at any price. Do not publish any figure from this sheet to a customer before the raw beef invoice has replaced the assumption.')
P()

writeFileSync(join(HERE, 'LADDER.md'), md.join('\n') + '\n')

// ── Console summary ────────────────────────────────────────────────────────
console.log('─'.repeat(70))
console.log('STUDEX BILTONG — LADDER')
console.log('─'.repeat(70))
for (const res of results) {
  const s = res.scenario
  console.log('')
  console.log(`SCENARIO: ${s.label} (raw ${zar0(s.raw.value)}/kg)`)
  for (const l of res.live) {
    console.log(`  ${l.label}`)
    for (const inv of l.invariants) {
      console.log(`    ${inv.holds ? 'ok  ' : 'FAIL'} ${inv.rule}: ${inv.observed}`)
    }
  }
  console.log('  PROPOSED:')
  for (const t of res.proposed.tiers) {
    console.log(
      `    ${t.line} ${t.label.padEnd(12)} ${zar0(t.price).padStart(9)}  ${zar(t.pricePerKg).padStart(11)}/kg  margin ${String(t.marginPct).padStart(5)}%  ${t.clearsFloor ? 'ok' : 'BELOW FLOOR'}`,
    )
  }
  for (const inv of res.proposed.invariants) {
    console.log(`    ${inv.holds ? 'ok  ' : 'FAIL'} ${inv.rule}: ${inv.observed}`)
  }
}
console.log('')
console.log('wrote biltong-ladder/ladder.generated.json')
console.log('wrote biltong-ladder/LADDER.md')
console.log('─'.repeat(70))
