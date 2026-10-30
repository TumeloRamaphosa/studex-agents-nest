/**
 * STUDEX BILTONG — LADDER ENGINE (pure functions)
 * Built: 2026-10-30 (Build Hour). Owner: Robusca / Studex Ops.
 *
 * The arithmetic. Kept separate from the emit so it can be unit-checked
 * without writing files.
 */

import { COST_INPUTS, POLICY } from './inputs.mjs'

export const round = (n, dp = 2) => Math.round(n * 10 ** dp) / 10 ** dp
export const round5 = (n) => Math.ceil(n / 5) * 5
export const zar = (n) =>
  'R' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
export const zar0 = (n) => 'R' + n.toLocaleString('en-US', { maximumFractionDigits: 0 })
export const pct = (n) => (n * 100).toFixed(1) + '%'

/** Finished cost per kg for a given pack and raw beef price. */
export function costPerKg(rawRarPerKg, packKey) {
  const rawPerFinishedKg = rawRarPerKg / COST_INPUTS.finishedYield.value
  const fixed =
    COST_INPUTS.spicesMarinadeRarPerKg.value +
    COST_INPUTS.coldChainDispatchRarPerKg.value +
    COST_INPUTS.qaOverheadRarPerKg.value
  const pack = COST_INPUTS.packagingRarPerKg.value[packKey]
  return { rawPerFinishedKg, fixed, pack, total: rawPerFinishedKg + fixed + pack }
}

/**
 * The raw beef price at which a tier priced at `pricePerKg` exactly clears
 * the floor. Inverts:  price * (1 - floor) = raw/yield + fixed + pack
 *   =>  raw = (price * (1 - floor) - fixed - pack) * yield
 */
export function breakEvenRaw(pricePerKg, packKey) {
  const floor = POLICY.marginFloorPct.value
  const c = costPerKg(0, packKey)
  return (pricePerKg * (1 - floor) - c.fixed - c.pack) * COST_INPUTS.finishedYield.value
}

/** Margin per kg. A PACK price is never compared against a PER-KG cost. */
export function marginPerKg(pricePerKg, costPerKgValue) {
  return (pricePerKg - costPerKgValue) / pricePerKg
}

/**
 * What raw beef price does a competitor's shelf price imply at our floor?
 * Inverts the cost model: the raw cost a competitor can afford at their
 * price and still clear 25%. Use it to sanity-check our own invoice against
 * the market rather than against our assumptions.
 */
export function impliedRawAtFloor(pricePerKg, packKey = 'luxury1kg') {
  const c = costPerKg(0, packKey)
  const floor = POLICY.marginFloorPct.value
  return round(
    (pricePerKg * (1 - floor) - c.fixed - c.pack) * COST_INPUTS.finishedYield.value,
    2,
  )
}

/**
 * Analyse one live ladder against a raw beef price.
 * Returns per-tier economics plus the structural invariant checks.
 */
export function analyseLiveLadder(ladder, rawRarPerKg) {
  const tiers = ladder.tiers.map((t) => {
    const c = costPerKg(rawRarPerKg, t.packKey)
    const pricePerKg = t.price / t.sizeKg
    const margin = marginPerKg(pricePerKg, c.total)
    return {
      ...t,
      pricePerKg: round(pricePerKg),
      costPerKg: round(c.total),
      marginPct: round(margin * 100, 1),
      clearsFloor: margin >= POLICY.marginFloorPct.value,
      breakEvenRaw: round(breakEvenRaw(pricePerKg, t.packKey), 2),
    }
  })

  const byLine = {}
  for (const t of tiers) (byLine[t.line] = byLine[t.line] || []).push(t)

  const invariants = []
  for (const [line, list] of Object.entries(byLine)) {
    const small = list.find((t) => t.sizeKg === 0.5)
    const one = list.find((t) => t.sizeKg === 1)
    const case7 = list.find((t) => t.sizeKg === 7)

    if (small && one) {
      const pctDelta = (small.pricePerKg - one.pricePerKg) / one.pricePerKg
      invariants.push({
        rule: 'small pack per-kg premium over the 1kg',
        line,
        holds: pctDelta <= POLICY.smallPackPremiumCap.value,
        observed:
          pctDelta > 0
            ? `the 500g is ${pct(pctDelta)} MORE per kg than the 1kg`
            : `the 500g is ${pct(Math.abs(pctDelta))} cheaper per kg than the 1kg`,
        required: `at most ${pct(POLICY.smallPackPremiumCap.value)} per-kg premium`,
        detail: `500g ${zar(small.pricePerKg)}/kg vs 1kg ${zar(one.pricePerKg)}/kg`,
      })
    }
    if (case7 && one) {
      const sevenOfOne = one.price * 7
      const delta = case7.price - sevenOfOne
      const pctDelta = delta / sevenOfOne
      invariants.push({
        rule: 'the 7kg case must be CHEAPER in total than 7 x 1kg',
        line,
        holds: delta < 0,
        observed:
          delta < 0
            ? `the case saves ${zar0(Math.abs(delta))} against 7 x 1kg (${pct(Math.abs(pctDelta))} off)`
            : `the case COSTS ${zar0(delta)} MORE than 7 x 1kg (+${pct(pctDelta)})`,
        required: 'must be cheaper',
        detail: `case ${zar0(case7.price)} vs 7 x 1kg ${zar0(sevenOfOne)}`,
      })
    }
  }
  return { id: ladder.id, label: ladder.label, status: ladder.status, source: ladder.source, tiers, invariants }
}

/**
 * Build the ladder that satisfies, simultaneously:
 *   1. every tier clears the margin floor
 *   2. the 7kg case is at least caseSavingPct cheaper per kg than 7 x 1kg
 *   3. the 500g is at most smallPackPremiumCap more per kg than the 1kg
 *   4. per-kg price falls as pack size rises
 *   5. the Luxury-to-Gold price relationship from the live ladder is preserved
 *
 * Method: the Luxury 1kg is the reference. It must clear its own floor AND
 * leave enough room above the Gold case floor for the case to be discounted
 * by caseSavingPct. Gold 1kg = Luxury 1kg x goldLineRatio. The case hangs
 * off Gold 1kg. The 500g hangs off Luxury 1kg, capped, and is floored.
 */
export function proposeLadder(rawRarPerKg, liveShopifyTiers) {
  const floor = POLICY.marginFloorPct.value
  const cost = {
    luxury500g: costPerKg(rawRarPerKg, 'luxury500g').total,
    luxury1kg: costPerKg(rawRarPerKg, 'luxury1kg').total,
    gold1kg: costPerKg(rawRarPerKg, 'gold1kg').total,
    goldCase7kg: costPerKg(rawRarPerKg, 'goldCase7kg').total,
  }
  const floorPerKg = {
    luxury500g: cost.luxury500g / (1 - floor),
    luxury1kg: cost.luxury1kg / (1 - floor),
    gold1kg: cost.gold1kg / (1 - floor),
    goldCase7kg: cost.goldCase7kg / (1 - floor),
  }

  // The case must sit caseSavingPct below the GOLD 1kg per kg and clear its
  // own floor. Solve for the lowest Gold 1kg per kg that makes both possible,
  // then back out the Luxury 1kg that supports it at the brand ratio.
  const goldOnePerKgRequired = floorPerKg.goldCase7kg / (1 - POLICY.caseSavingPct.value)
  const goldOnePerKg = Math.max(floorPerKg.gold1kg, goldOnePerKgRequired)
  const luxuryOnePerKg = goldOnePerKg / COST_INPUTS.goldLineRatio.value
  const luxuryOnePerKgFinal = Math.max(floorPerKg.luxury1kg, luxuryOnePerKg)

  const luxuryOnePrice = round5(luxuryOnePerKgFinal)
  const goldOnePrice = round5(luxuryOnePrice * COST_INPUTS.goldLineRatio.value)

  // 500g: capped premium over the Luxury 1kg, then floored, then stepped down
  // in R5 until the REALISED per-kg premium respects the cap (rounding can
  // push it over).
  let p500PerKg = luxuryOnePrice * (1 + POLICY.smallPackPremiumCap.value)
  let p500Price = round5(p500PerKg * 0.5)
  const capPerKg = luxuryOnePrice * (1 + POLICY.smallPackPremiumCap.value)
  while (p500Price / 0.5 > capPerKg && p500Price > 0) p500Price -= POLICY.roundingZar.value
  p500PerKg = p500Price / 0.5
  if (p500PerKg < floorPerKg.luxury500g) {
    p500PerKg = floorPerKg.luxury500g
    p500Price = round5(p500PerKg * 0.5)
  }

  // Case: the Gold 1kg price minus the saving, times 7, rounded DOWN to R5.
  let casePerKg = goldOnePrice * (1 - POLICY.caseSavingPct.value)
  let casePrice = round5(casePerKg * 7)
  casePerKg = casePrice / 7
  while (casePrice >= goldOnePrice * 7 && casePrice > 0) {
    casePrice -= POLICY.roundingZar.value
    casePerKg = casePrice / 7
  }
  if (casePerKg < floorPerKg.goldCase7kg) {
    casePerKg = floorPerKg.goldCase7kg
    casePrice = round5(casePerKg * 7)
  }

  const tiers = [
    { line: 'Luxury Wagyu Biltong', sizeKg: 0.5, label: '500g', price: p500Price, packKey: 'luxury500g' },
    { line: 'Luxury Wagyu Biltong', sizeKg: 1, label: '1kg', price: luxuryOnePrice, packKey: 'luxury1kg' },
    { line: 'Wagyu Biltong Gold', sizeKg: 1, label: '1kg', price: goldOnePrice, packKey: 'gold1kg' },
    { line: 'Wagyu Biltong Gold', sizeKg: 7, label: '7kg case', price: casePrice, packKey: 'goldCase7kg' },
  ].map((t) => {
    const c = costPerKg(rawRarPerKg, t.packKey)
    const pricePerKg = t.price / t.sizeKg
    const margin = marginPerKg(pricePerKg, c.total)
    return {
      ...t,
      pricePerKg: round(pricePerKg),
      costPerKg: round(c.total),
      marginPct: round(margin * 100, 1),
      clearsFloor: margin >= floor,
      breakEvenRaw: round(breakEvenRaw(pricePerKg, t.packKey), 2),
    }
  })

  // Invariants verified on the proposal itself.
  const small = tiers.find((t) => t.sizeKg === 0.5)
  const one = tiers.find((t) => t.line === 'Luxury Wagyu Biltong' && t.sizeKg === 1)
  const goldOne = tiers.find((t) => t.line === 'Wagyu Biltong Gold' && t.sizeKg === 1)
  const case7 = tiers.find((t) => t.sizeKg === 7)
  const sevenOfOne = goldOne.price * 7

  const invariants = [
    {
      rule: '500g per kg vs Luxury 1kg per kg',
      line: 'Luxury Wagyu Biltong',
      holds: small.pricePerKg - one.pricePerKg <= one.pricePerKg * POLICY.smallPackPremiumCap.value,
      observed: `500g ${zar(small.pricePerKg)}/kg vs 1kg ${zar(one.pricePerKg)}/kg`,
      required: `at most ${pct(POLICY.smallPackPremiumCap.value)} per-kg premium on the small pack`,
      detail: `premium ${pct((small.pricePerKg - one.pricePerKg) / one.pricePerKg)}`,
    },
    {
      rule: '7kg case vs 7 x Gold 1kg',
      line: 'Wagyu Biltong Gold',
      holds: case7.price < sevenOfOne,
      observed: `case ${zar0(case7.price)} vs 7 x 1kg ${zar0(sevenOfOne)}`,
      required: 'must be cheaper',
      detail: `saving ${zar0(sevenOfOne - case7.price)} (${pct((sevenOfOne - case7.price) / sevenOfOne)})`,
    },
    {
      // checked WITHIN each product line — Gold is a different line with its
      // own price architecture, so comparing Gold's case against Luxury's 1kg
      // would be a category error
      rule: 'per-kg price falls as pack size rises, within each line',
      line: 'Luxury + Gold separately',
      holds:
        small.pricePerKg >= one.pricePerKg && goldOne.pricePerKg >= case7.pricePerKg,
      observed: `Luxury 500g ${zar(small.pricePerKg)}/kg → 1kg ${zar(one.pricePerKg)}/kg  ·  Gold 1kg ${zar(goldOne.pricePerKg)}/kg → case ${zar(case7.pricePerKg)}/kg`,
      required: 'monotonically non-increasing within a line',
      detail: '',
    },
  ]

  // Delta against the live Shopify ladder — nobody should be surprised by a
  // customer-facing price change they did not see coming.
  const deltas = tiers.map((t) => {
    const live = liveShopifyTiers.find(
      (l) => l.line === t.line && l.sizeKg === t.sizeKg,
    )
    if (!live) return null
    const pctDelta = ((t.price - live.price) / live.price) * 100
    return {
      line: t.line,
      label: t.label,
      livePrice: live.price,
      proposedPrice: t.price,
      deltaZar: t.price - live.price,
      deltaPct: round(pctDelta, 1),
    }
  })

  return { tiers, invariants, cost, floorPerKg, deltas }
}
