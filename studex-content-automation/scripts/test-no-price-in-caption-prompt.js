#!/usr/bin/env node
/**
 * The content agent's caption prompt must never order a price into a caption.
 *
 * House rule [10] of skills/studex-daily-posting/SKILL.md: NO price on a
 * public feed (trade pricing stays on the China page). The SKILL states it;
 * the prompt contradicted it - it told the model to "Quote the price EXACTLY
 * as given in the product record" and to "use R for ZAR", which is how a
 * caption arrives at the publish step carrying "R1,450".
 *
 * Two instruction layers, one contradicting the other, and the code wins.
 * This test makes the prompt side of that contradiction impossible to
 * reintroduce.
 *
 * NEGATIVE CONTROL: the pre-fix prompt (and a synthetic stand-in) MUST be
 * flagged. A detector that cannot fail is a comment.
 *
 * Run: node scripts/test-no-price-in-caption-prompt.js
 */
const fs = require('fs');
const path = require('path');

const AGENT = path.join(__dirname, 'daily-content-agent.js');
const src = fs.readFileSync(AGENT, 'utf8');

let failed = 0;
function check(name, cond, extra) {
  if (!cond) failed++;
  console.log((cond ? '\u2705 ' : '\u274c ') + name + (extra ? ' - ' + extra : ''));
}

/**
 * The detector. Scans a prompt for the two ways a price gets ordered in, and
 * for the presence of the rule that forbids it.
 */
function promptViolations(prompt) {
  const bad = [];
  if (/quote the price/i.test(prompt)) {
    bad.push('instructs the model to quote a price');
  }
  if (/use R for ZAR/i.test(prompt)) {
    bad.push('nudges the model towards a ZAR amount');
  }
  if (!/do not put a price|NO price on a public feed/i.test(prompt)) {
    bad.push('does not state the no-price rule');
  }
  return bad;
}

// The real prompt.
const real = promptViolations(src);
check('the live caption prompt orders NO price', real.length === 0, real.join(' | '));
check('the prompt states the no-price rule',
  /NO price on a public feed/i.test(src));
check('the prompt says the product record price is internal-reference only',
  /INTERNAL REFERENCE ONLY/i.test(src));

// NEGATIVE CONTROL 1 - the pre-fix prompt, verbatim.
const PRE_FIX = `- South African flavour (mention SA, use R for ZAR)
- Quote the price EXACTLY as given in the product record above (e.g. "From R650", "R4,200 per 100g"). Never invent, round, adjust or infer a price.`;
const pre = promptViolations(PRE_FIX);
check('NEGATIVE CONTROL: the pre-fix prompt IS flagged', pre.length >= 2, pre.join(' | '));

// NEGATIVE CONTROL 2 - a prompt that only nudges the model towards an amount.
const nudge = '- South African flavour (mention SA, use R for ZAR)';
const nudgeBad = promptViolations(nudge);
check('NEGATIVE CONTROL: a currency nudge alone IS flagged', nudgeBad.length >= 1,
  nudgeBad.join(' | '));

// POSITIVE CONTROL - the corrected shape must not be flagged.
const ok = `- South African flavour (mention SA)
- Do NOT put a price in the caption. NO price on a public feed. The product record contains a price for INTERNAL REFERENCE ONLY.`;
check('POSITIVE CONTROL: a corrected prompt is NOT flagged',
  promptViolations(ok).length === 0, promptViolations(ok).join(' | '));

console.log(failed === 0
  ? '\n\u2705 ALL PROMPT-PRICE TESTS PASSED'
  : '\n\u274c ' + failed + ' PROMPT-PRICE TEST(S) FAILED');
process.exit(failed === 0 ? 0 : 1);
